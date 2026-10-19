from fastapi import HTTPException
from all import *
from routes.auth import acting

# "abandonned" = ancienne orthographe encore presente dans d'anciennes bases
OPEN_STATES = (GIVEN_UP, "abandonned")


def getPlayerbyId(session , id):
    player = session.query(Player).filter_by(id = id).first()
    if not player:
        return
    return player


def get_player_or_404(player_id: str):
    """Le joueur qui agit: doit etre le proprietaire du jeton de la requete."""
    acting(player_id)
    player = session.query(Player).filter_by(id = player_id).first()
    if not player:
        raise HTTPException(status_code=404 , detail="Player not found")
    return player


def get_owned_session(session_id: str , player_id: str):
    """Session existante qui appartient bien a ce joueur (qui doit etre celui authentifie)."""
    acting(player_id)
    that_session = session.query(GameSession).filter_by(id = session_id).first()
    if not that_session:
        raise HTTPException(status_code=404 , detail="Session not found")
    if that_session.player_id != player_id:
        raise HTTPException(status_code=403 , detail="This session belongs to another player")
    return that_session


def ensure_open(that_session):
    if that_session.status not in OPEN_STATES:
        raise HTTPException(status_code=409 , detail="Session already finished")
