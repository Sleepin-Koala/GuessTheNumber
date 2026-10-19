# type: ignore
from fastapi import APIRouter
from fastapi import APIRouter , HTTPException 
from all import *
import engine
from routes.utils import get_player_or_404


router = APIRouter(prefix="/duel")

def _name(player_id):
    player = session.query(Player).filter_by(id = player_id).first() if player_id else None
    return player.name if player else None


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
        winner_id = room.winner_id
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
    for old in session.query(Duel).filter_by(host_id = host.id , status = "waiting").all():
        old.status = "cancelled"

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
        winner_id = None
    )


    session.add(new_game)
    session.commit()

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

    session.commit()

    return create_room(room)


@router.post("/rooms/{roomId}/hide")
def hideNumber(HideNumberData : HidenGuessNumberData, roomId: str):
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

    session.commit()
    

    return create_room(room)

@router.post("/rooms/{roomId}/guess")
def GuessNumber(GuessNumberData : HidenGuessNumberData, roomId: str):

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

            room.winner_id = winner_id

            winner = session.query(Player).filter_by(id = winner_id).first()
            loser = session.query(Player).filter_by(id = loser_id).first()
            # transfert a somme nulle, borne par le solde du perdant
            amount = min(room.bet_amount or 0, loser.coins)
            loser.coins -= amount
            winner.coins += amount

            room.status = "finished"

    session.commit()

    return create_room(room)


@router.post("/rooms/{roomId}/leave")
def leaveRoom(LeaveData : LeaveData, roomId: str):
    """Annule une salle encore en attente. (L'abandon d'une partie en cours n'est pas gere ici.)"""
    room = get_room_or_404(roomId)
    if LeaveData.player_id not in (room.host_id , room.guest_id):
        raise HTTPException(status_code=403, detail="Tu ne fais pas partie de cette salle")
    if room.status != "waiting":
        raise HTTPException(status_code=409, detail="La partie est deja commencee")

    room.status = "cancelled"
    session.commit()

    return create_room(room)
