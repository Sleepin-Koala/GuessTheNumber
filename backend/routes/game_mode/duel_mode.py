# type: ignore
from fastapi import APIRouter
from fastapi import APIRouter , HTTPException 
from all import *
import engine
import asyncio
import os
import logging
from fastapi import WebSocket , WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from routes.utils import get_player_or_404
from routes.auth import acting , ws_player_id , WS_SUBPROTOCOL
from security import origin_allowed , client_ip , MAX_WS_PER_IP
from routes.realtime import hub


router = APIRouter(prefix="/duel")
log = logging.getLogger("duel")

# Delais (secondes). Surchargeables par variables d'environnement.
TURN_TIMEOUT = float(os.environ.get("DUEL_TURN_TIMEOUT", 90))          # inactivite max du joueur dont c'est le tour
WAIT_TIMEOUT = float(os.environ.get("DUEL_WAIT_TIMEOUT", 600))         # salle en attente d'un adversaire
DISCONNECT_GRACE = float(os.environ.get("DUEL_DISCONNECT_GRACE", 30))  # temps pour revenir apres une deconnexion
SWEEP_INTERVAL = float(os.environ.get("DUEL_SWEEP_INTERVAL", 1))       # frequence du balayeur de delais

ACTIVE = ("waiting" , "round1_hide" , "round1_guess" , "round2_hide" , "round2_guess")
IN_PROGRESS = ACTIVE[1:]


def touch(room: Duel , now: float = None):
    room.updated_at = now if now is not None else time.time()


def turn_actor(room: Duel):
    """Le joueur dont on attend une action (cacher ou deviner), ou None."""
    if room.status.endswith("_hide"):
        return room.hider_id
    if room.status.endswith("_guess"):
        return room.guesser_id
    return None


def turn_deadline(room: Duel):
    if room.status not in ACTIVE or room.updated_at is None:
        return None
    return room.updated_at + (WAIT_TIMEOUT if room.status == "waiting" else TURN_TIMEOUT)


def settle(room: Duel , winner_id: str , loser_id: str , reason: str):
    """Termine la partie: designe le gagnant et deplace la mise (bornee par le solde du perdant)."""
    room.winner_id = winner_id
    room.status = "finished"
    room.end_reason = reason
    winner = session.query(Player).filter_by(id = winner_id).first()
    loser = session.query(Player).filter_by(id = loser_id).first()
    amount = min(room.bet_amount or 0 , loser.coins)
    loser.coins -= amount
    winner.coins += amount


def forfeit_player(room: Duel , loser_id: str , reason: str):
    winner_id = room.guest_id if loser_id == room.host_id else room.host_id
    settle(room , winner_id , loser_id , reason)


def cancel(room: Duel , reason: str):
    room.status = "cancelled"
    room.end_reason = reason

def _name(player_id):
    player = session.query(Player).filter_by(id = player_id).first() if player_id else None
    return player.name if player else None


def open_rooms():
    return [create_room(r).model_dump() for r in session.query(Duel).filter_by(status = "waiting").all()]


def notify(room: Duel):
    """Pousse l'etat de la salle (et la liste du lobby si elle a change) aux sockets connectees."""
    hub.publish_room(room.id , {"type": "room" , "room": create_room(room).model_dump()})
    if room.status in ("waiting" , "cancelled" , "round1_hide"):
        hub.publish_lobby({"type": "lobby" , "rooms": open_rooms()})


def create_room(room: Duel):
    return RoomData(
        host_name = _name(room.host_id),
        guest_name = _name(room.guest_id),
        room_id =  room.id,
        host_id =  room.host_id ,
        guest_id  = room.guest_id,
        room_name =  room.room_name,
        bet_amount = room.bet_amount,
        status = room.status,
        max_range =  room.max_range,
        current_hider_id = room.hider_id,
        current_guesser_id = room.guesser_id,
        last_distance = room.last_distance,
        last_feedback = room.last_feedback,
        round1_attempts_used = room.round1_attempts_used,
        round2_attempts_used = room.round2_attempts_used,
        winner_id = room.winner_id,
        end_reason = room.end_reason,
        turn_deadline = turn_deadline(room),
        server_time = time.time(),
    )



@router.get("/rooms")
def getLobby():
    return [create_room(i) for i in session.query(Duel).filter_by(status = "waiting").all()] 

MAX_DUEL_RANGE = 10_000

def get_room_or_404(room_id: str):
    room = session.query(Duel).filter_by(id = room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room introuvable")
    return room


@router.post("/host")
def hostServer(HostRoomData: HostRoomData):

    host = get_player_or_404(HostRoomData.host_id)
    if not 0 <= HostRoomData.amount <= host.coins:
        raise HTTPException(status_code=402, detail="Mise invalide ou pas assez de pieces")
    if not 1 <= HostRoomData.max_range <= MAX_DUEL_RANGE:
        raise HTTPException(status_code=422, detail=f"max_range doit etre entre 1 et {MAX_DUEL_RANGE}")

    # une seule salle en attente par joueur: l'ancienne est annulee
    replaced = session.query(Duel).filter_by(host_id = host.id , status = "waiting").all()
    for old in replaced:
        cancel(old , "replaced")

    new_game = Duel(
        id = str(uuid4()), 
        host_id = host.id,
        guest_id = None,
        room_name = HostRoomData.name.strip()[:30] or "Salle",
        bet_amount = HostRoomData.amount,
        status = "waiting",
        max_range = HostRoomData.max_range,
        hider_id = host.id,
        guesser_id = None,
        hider_number = None,
        guesser_number = None,
        last_distance = None,
        last_feedback = None,
        round1_attempts_used = 0,
        round2_attempts_used = 0,
        winner_id = None,
        updated_at = time.time()
    )


    session.add(new_game)
    session.commit()
    for old in replaced:
        notify(old)
    notify(new_game)

    return create_room(new_game)

@router.post("/status")
def checkStatus(CheckRoomData: CheckRoomData):
    return create_room(get_room_or_404(CheckRoomData.room_id))

@router.post("/join")
def joinRoom(JoinData : JoinData):
    room = get_room_or_404(JoinData.room_id)
    guest = get_player_or_404(JoinData.player_id)

    if room.status != "waiting" or room.guest_id is not None:
        raise HTTPException(status_code=409, detail="La room n'est plus disponible")
    if guest.id == room.host_id:
        raise HTTPException(status_code=403, detail="Tu ne peux pas rejoindre ta propre room")
    if guest.coins < room.bet_amount:
        raise HTTPException(status_code=402, detail="Pas assez de pieces pour la mise")
    
    room.status = "round1_hide"
    room.guest_id = guest.id
    room.guesser_id = guest.id
    touch(room)

    session.commit()
    notify(room)

    return create_room(room)


@router.post("/rooms/{roomId}/hide")
def hideNumber(HideNumberData : HidenGuessNumberData, roomId: str):
    acting(HideNumberData.player_id)
    room = get_room_or_404(roomId)
    if room.status not in ("round1_hide", "round2_hide"):
        raise HTTPException(status_code=409, detail="Ce n'est pas le moment de cacher un nombre")
    if HideNumberData.player_id != room.hider_id:
        raise HTTPException(status_code=403, detail="Ce n'est pas ton tour de cacher un nombre")
    if not 1 <= HideNumberData.number <= room.max_range:
        raise HTTPException(status_code=422, detail="Nombre hors de la plage")

    if room.host_id == HideNumberData.player_id:
        room.hider_number = HideNumberData.number
    else:
        room.guesser_number = HideNumberData.number

    room.status = "round1_guess" if room.status == "round1_hide" else "round2_guess"
    touch(room)

    session.commit()
    notify(room)

    return create_room(room)

@router.post("/rooms/{roomId}/guess")
def GuessNumber(GuessNumberData : HidenGuessNumberData, roomId: str):
    acting(GuessNumberData.player_id)
    room = get_room_or_404(roomId)

    if room.status not in ("round1_guess", "round2_guess"):
        raise HTTPException(status_code=409, detail="Ce n'est pas le moment de deviner")
    if room.guesser_id != GuessNumberData.player_id:
        raise HTTPException(status_code=403, detail="Ce n'est pas ton tour de deviner")

    his_number = room.hider_number if room.hider_id == room.host_id else room.guesser_number
    if his_number is None:
        raise HTTPException(status_code=409, detail="Aucun nombre cache")
    his_number = int(his_number)

    if room.status == "round1_guess":
        room.round1_attempts_used = (room.round1_attempts_used or 0) + 1
    else:
        room.round2_attempts_used = (room.round2_attempts_used or 0) + 1

    touch(room)
    room.last_distance = float(abs(his_number-GuessNumberData.number))
    room.last_feedback = engine.checkResult(his_number , GuessNumberData.number)

    if room.last_feedback == "OK":
        if room.status == "round1_guess":
            room.status = "round2_hide"
            room.guesser_id, room.hider_id = room.hider_id, room.guesser_id

        else:
            # round 1: l'invite devine, round 2: l'hote devine -> le moins d'essais gagne, egalite = hote
            if room.round1_attempts_used < room.round2_attempts_used:
                winner_id, loser_id = room.guest_id, room.host_id
            else:
                winner_id, loser_id = room.host_id, room.guest_id

            settle(room , winner_id , loser_id , "solved")

    session.commit()
    notify(room)

    return create_room(room)


@router.post("/rooms/{roomId}/leave")
def leaveRoom(LeaveData : LeaveData, roomId: str):
    """Annule une salle encore en attente. Pour une partie en cours: voir /forfeit."""
    acting(LeaveData.player_id)
    room = get_room_or_404(roomId)
    if LeaveData.player_id not in (room.host_id , room.guest_id):
        raise HTTPException(status_code=403, detail="Tu ne fais pas partie de cette salle")
    if room.status != "waiting":
        raise HTTPException(status_code=409, detail="La partie est deja commencee")

    cancel(room , "cancelled")
    session.commit()
    notify(room)

    return create_room(room)


@router.post("/rooms/{roomId}/forfeit")
def forfeitRoom(LeaveData : LeaveData, roomId: str):
    """Abandon volontaire d'une partie en cours: l'adversaire gagne et recoit la mise."""
    acting(LeaveData.player_id)
    room = get_room_or_404(roomId)
    if LeaveData.player_id not in (room.host_id , room.guest_id):
        raise HTTPException(status_code=403, detail="Tu ne fais pas partie de cette salle")
    if room.status not in IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Aucune partie en cours dans cette salle")

    forfeit_player(room , LeaveData.player_id , "forfeit")
    session.commit()
    notify(room)

    return create_room(room)


# ---------------------------------------------------------------------------
# Delais: inactivite, salles abandonnees, deconnexions
# ---------------------------------------------------------------------------
def sweep(now: float = None):
    """Applique les delais echus (appele chaque seconde par `sweeper`; `now` permet de tester sans attendre)."""
    now = time.time() if now is None else now
    with db_lock:
        try:
            changed = []
            for room in session.query(Duel).filter(Duel.status.in_(ACTIVE)).all():
                if room.updated_at is None:                 # ligne creee avant l'ajout de la colonne
                    touch(room , now)
                    continue
                if now < room.updated_at + (WAIT_TIMEOUT if room.status == "waiting" else TURN_TIMEOUT):
                    continue
                if room.status == "waiting":
                    cancel(room , "expired")
                else:
                    forfeit_player(room , turn_actor(room) , "timeout")
                changed.append(room)

            for room_id , player_id , _deadline in hub.expired_graces(now):
                hub.clear_grace(room_id , player_id)
                room = session.query(Duel).filter_by(id = room_id).first()
                if room is None or room.status not in ACTIVE or hub.is_online(room_id , player_id):
                    continue
                other = room.guest_id if player_id == room.host_id else room.host_id
                if room.status == "waiting" or other is None or not hub.is_online(room_id , other):
                    cancel(room , "abandoned")              # salle vide, ou les deux joueurs sont partis: personne ne gagne
                else:
                    forfeit_player(room , player_id , "disconnect")
                changed.append(room)

            session.commit()
            for room in changed:
                notify(room)
        except BaseException:
            session.rollback()
            raise
        finally:
            session.rollback()       # relache la connexion (voir db_guard)


async def sweeper():
    """Tache de fond lancee avec l'application."""
    while True:
        await asyncio.sleep(SWEEP_INTERVAL)
        try:
            await run_in_threadpool(sweep)
        except Exception:
            log.exception("sweep failed")


def _start_grace(room_id: str , player_id: str):
    """Un joueur vient de perdre sa connexion: il a DISCONNECT_GRACE secondes pour revenir."""
    with db_lock:
        try:
            room = session.query(Duel).filter_by(id = room_id).first()
            if room is None or room.status not in ACTIVE:
                return
            deadline = time.time() + DISCONNECT_GRACE
            hub.set_grace(room_id , player_id , deadline)
            hub.publish_room(room_id , {"type": "grace" , "player_id": player_id , "deadline": deadline , "server_time": time.time()})
        except BaseException:
            session.rollback()
            raise
        finally:
            session.rollback()       # relache la connexion (voir db_guard)


# ---------------------------------------------------------------------------
# WebSocket: le serveur pousse chaque changement (les actions restent en HTTP)
# ---------------------------------------------------------------------------
IDLE_TIMEOUT = 60      # secondes sans message (ping inclus) avant de fermer une socket morte


def _room_snapshot(room_id: str , player_id: str):
    """(code_de_fermeture, payload): verifie que le joueur appartient a la salle. Verrou BD pris a la main."""
    with db_lock:
        try:
            room = session.query(Duel).filter_by(id = room_id).first()
            if room is None:
                return 4404 , None
            if player_id not in (room.host_id , room.guest_id):
                return 4403 , None
            return None , {"type": "room" , "room": create_room(room).model_dump()}
        except BaseException:
            session.rollback()
            raise
        finally:
            session.rollback()       # relache la connexion (voir db_guard)


def _lobby_snapshot():
    with db_lock:
        try:
            return {"type": "lobby" , "rooms": open_rooms()}
        except BaseException:
            session.rollback()
            raise
        finally:
            session.rollback()       # relache la connexion (voir db_guard)


_detached: set = set()


def _detach(coro):
    """Lance `coro` hors de la tache de la socket. Quand une connexion est coupee par annulation de tache (arret du
    serveur, fermeture brutale...), TOUS les `await` d'un `finally` sont annules: le nettoyage doit donc tourner
    dans une tache independante, sinon le delai de grace ne demarrerait jamais."""
    task = asyncio.get_running_loop().create_task(coro)
    _detached.add(task)                      # reference forte: sinon la tache peut etre ramassee avant la fin
    task.add_done_callback(_detached.discard)


async def _after_disconnect(room_id: str , ws: WebSocket , player_id: str):
    await hub.leave_room(room_id , ws)                             # annonce la presence a l'autre joueur
    if not hub.is_online(room_id , player_id):                     # plus aucune connexion de ce joueur
        await run_in_threadpool(_start_grace , room_id , player_id)


async def _pump(ws: WebSocket):
    """Boucle commune: repond aux ping, ignore le reste, ferme apres IDLE_TIMEOUT de silence."""
    while True:
        try:
            msg = await asyncio.wait_for(ws.receive_json() , timeout = IDLE_TIMEOUT)
        except asyncio.TimeoutError:
            await ws.close(code = 1001)
            return
        if isinstance(msg , dict) and msg.get("type") == "ping":
            await ws.send_json({"type": "pong"})


async def _admit(ws: WebSocket):
    """Controles communs avant d'accepter une socket. Retourne l'id du joueur, ou None (la socket est alors fermee)."""
    if not origin_allowed(ws.headers.get("origin")):
        await ws.close(code = 4403)
        return None
    if hub.connections_from(client_ip(ws.scope)) >= MAX_WS_PER_IP:
        await ws.close(code = 4429)
        return None
    player_id = await run_in_threadpool(ws_player_id , ws)
    if player_id is None:
        await ws.close(code = 4401)
        return None
    return player_id


@router.websocket("/ws/{room_id}")
async def room_socket(ws: WebSocket , room_id: str):
    player_id = await _admit(ws)
    if player_id is None:
        return
    code , snapshot = await run_in_threadpool(_room_snapshot , room_id , player_id)
    if code:
        await ws.close(code = code)
        return
    await ws.accept(subprotocol = WS_SUBPROTOCOL)
    ip = client_ip(ws.scope)
    hub.track(ws , ip)
    await ws.send_json(snapshot)
    for other , deadline in hub.graces_for(room_id):               # qui est deja en train de decrocher
        if other != player_id:
            await ws.send_json({"type": "grace" , "player_id": other , "deadline": deadline , "server_time": time.time()})
    await hub.join_room(room_id , ws , player_id)
    if hub.clear_grace(room_id , player_id):                       # il est revenu a temps
        hub.publish_room(room_id , {"type": "grace_cleared" , "player_id": player_id})
    try:
        await _pump(ws)
    except (WebSocketDisconnect , RuntimeError):
        pass
    finally:
        hub.drop(ws)                                               # synchrone: la presence est exacte tout de suite
        _detach(_after_disconnect(room_id , ws , player_id))


@router.websocket("/ws-lobby")
async def lobby_socket(ws: WebSocket):
    if await _admit(ws) is None:
        return
    await ws.accept(subprotocol = WS_SUBPROTOCOL)
    hub.track(ws , client_ip(ws.scope))
    await ws.send_json(await run_in_threadpool(_lobby_snapshot))
    hub.lobby.add(ws)
    try:
        await _pump(ws)
    except (WebSocketDisconnect , RuntimeError):
        pass
    finally:
        hub.drop(ws)
