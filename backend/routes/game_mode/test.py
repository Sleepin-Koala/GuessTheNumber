# type: ignore
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from all import *

# RoomData est different de la base de donne

# CURRENT_DATA devient la mémoire vive COMPLÈTE d'un duel en cours — pas
# seulement qui hide/guess, mais aussi le dernier feedback (pour que
# /status puisse le RENVOYER plutôt que le cacher derrière None), le
# nombre d'essais restants sur la manche en cours, et les scores des deux
# manches une fois connus.
#
# ⚠️ Un dict Python en mémoire = tout est perdu si le serveur redémarre.
# Acceptable pour développer, mais à migrer vers la DB (colonnes sur Duel)
# avant la mise en prod — sinon un simple redéploiement casse tous les
# duels en cours.   x
CURRENT_DATA = {}

MAX_ATTEMPTS_PER_ROUND = 6  # à ajuster selon max_range si tu veux le rendre variable



@router.post("/rooms/{roomId}/hide")
def hideNumber(HideNumberData: HidenGuessNumberData, roomId: str):
    room = session.query(Duel).filter_by(id=roomId).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room introuvable")

    live = CURRENT_DATA[roomId]

    # Seul le hider désigné a le droit de cacher un nombre maintenant —
    # ça manquait : n'importe quel joueur pouvait appeler cet endpoint.
    if HideNumberData.player_id != live["CURRENT_HIDER_ID"]:
        raise HTTPException(status_code=403, detail="Ce n'est pas ton tour de cacher un nombre")

    if room.host_id == HideNumberData.player_id:
        room.host_number = HideNumberData.number
    else:
        room.guesser_number = HideNumberData.number

    # La transition dépend de la manche EN COURS, pas d'un test sur les 2
    # colonnes en même temps (qui ne sont jamais remplies simultanément
    # dans un flux asymétrique).
    if room.status == "round1_hide":
        room.status = "round1_guess"
    elif room.status == "round2_hide":
        room.status = "round2_guess"

    # Pas de switch_hideguess() ici ! Le hider/guesser de CETTE manche ne
    # change pas juste parce qu'un nombre a été caché — seulement l'état
    # "ATTEMPTS_LEFT" doit repartir à zéro pour la phase de devinette qui
    # commence.
    live["ATTEMPTS_LEFT"] = MAX_ATTEMPTS_PER_ROUND
    live["LAST_DISTANCE"] = None
    live["LAST_FEEDBACK"] = None

    session.commit()
    return _build_room_data(room)


@router.post("/rooms/{roomId}/guess")
def GuessNumber(GuessNumberData: HidenGuessNumberData, roomId: str):
    room = session.query(Duel).filter_by(id=roomId).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room introuvable")

    live = CURRENT_DATA[roomId]

    if GuessNumberData.player_id != live["CURRENT_GUESSER_ID"]:
        raise HTTPException(status_code=403, detail="Ce n'est pas ton tour de deviner")

    hider_id = live["CURRENT_HIDER_ID"]
    his_number = int(room.host_number if hider_id == room.host_id else room.guesser_number)

    distance = float(abs(his_number - GuessNumberData.number))
    feedback = engine.checkResult(his_number, GuessNumberData.number)

    live["ATTEMPTS_LEFT"] -= 1
    live["LAST_DISTANCE"] = distance
    live["LAST_FEEDBACK"] = feedback

    round_over = feedback == "OK" or live["ATTEMPTS_LEFT"] <= 0

    if round_over:
        # "Raté" = on compte comme si tous les essais avaient été
        # utilisés (pire score possible), pour ne jamais avantager un
        # joueur qui n'a simplement pas trouvé.
        attempts_used = (
            MAX_ATTEMPTS_PER_ROUND - live["ATTEMPTS_LEFT"]
            if feedback == "OK"
            else MAX_ATTEMPTS_PER_ROUND
        )

        if room.status == "round1_guess":
            # Fin de la manche 1 : ICI, et seulement ici, on échange les
            # rôles pour la manche 2.
            live["ROUND1_ATTEMPTS_USED"] = attempts_used
            room.status = "round2_hide"
            new_hider = live["CURRENT_GUESSER_ID"]   # celui qui devinait cache maintenant
            new_guesser = live["CURRENT_HIDER_ID"]   # celui qui cachait devine maintenant
            _init_round_state(roomId, hider_id=new_hider, guesser_id=new_guesser)
            # _init_round_state écrase LAST_DISTANCE/LAST_FEEDBACK à None
            # et ATTEMPTS_LEFT au max — on remet ROUND1_ATTEMPTS_USED
            # après, puisqu'il vient d'être écrasé par le update() interne.
            live = CURRENT_DATA[roomId]
            live["ROUND1_ATTEMPTS_USED"] = attempts_used

        elif room.status == "round2_guess":
            # Fin de la manche 2 : la partie se termine, on détermine le
            # vainqueur. Le guesser de la manche 1 est le joueur qui a
            # rejoint (guess_id) ; celui de la manche 2 est le host.
            live["ROUND2_ATTEMPTS_USED"] = attempts_used
            room1_used = live["ROUND1_ATTEMPTS_USED"]
            room2_used = live["ROUND2_ATTEMPTS_USED"]

            if room2_used < room1_used:
                winner_id = room.host_id            # a deviné en manche 2
            elif room1_used < room2_used:
                winner_id = room.guess_id           # a deviné en manche 1
            else:
                winner_id = room.host_id            # égalité : règle simple par défaut

            live["WINNER_ID"] = winner_id
            room.status = "finished"

    session.commit()
    return _build_room_data(room)


@router.post("/rooms/{roomId}/leave")
def leaveRoom(LeaveData: JoinData, roomId: str):
    room = session.query(Duel).filter_by(id=roomId).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room introuvable")

    if room.status == "waiting":
        # Room vide : suppression pure, personne n'a encore misé quoi
        # que ce soit d'engagé face à un adversaire.
        session.delete(room)
    else:
        # Duel en cours : forfait, l'adversaire remporte le pot.
        live = CURRENT_DATA.get(roomId, {})
        winner_id = room.guess_id if LeaveData.player_id == room.host_id else room.host_id
        live["WINNER_ID"] = winner_id
        room.status = "finished"

    session.commit()
    return {"ok": True}