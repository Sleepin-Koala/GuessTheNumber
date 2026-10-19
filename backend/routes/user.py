from fastapi import APIRouter  ,HTTPException
import engine.props as gen
from engine.db_handler import *
from all import *
from routes.auth import new_token , hash_token , acting
from routes.utils import get_player_or_404

import time


router = APIRouter(prefix="/user")

def _public(user, token=None):
    data = PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level).model_dump() # type: ignore
    if token:
        data["token"] = token
    return data


def _give_starting_items(user):
    for items_id in [d.id for d in session.query(Items).all()]:
        session.add(PlayerItems(playerId = user.id , itemId = items_id))


@router.post("/new_player")
def new_player():
    """Cree un compte. Le jeton secret n'est renvoye qu'ici: le client doit le garder (seule son empreinte est stockee)."""
    token = new_token()
    user = Player(
            name = gen.getName() , 
            id =  str(uuid4()),
            level = 1,
            created_at = time.time(),
            xp = 0,
            coins = 500,
            gems = 5,
            token_hash = hash_token(token))
    
    session.add(user)
    _give_starting_items(user)
    session.commit()

    return _public(user , token)


@router.post("/claim")
def claim_legacy_account(data: ClaimData):
    """Migration: un compte cree avant l'arrivee des jetons (sans empreinte) peut en recevoir un, une seule fois.
    Une fois reclame, ce chemin est ferme pour ce compte."""
    user = session.query(Player).filter_by(id = data.player_id).first()
    if user is None or user.token_hash is not None:
        raise HTTPException(409 , "This account cannot be claimed")
    token = new_token()
    user.token_hash = hash_token(token)
    session.commit()
    return _public(user , token)


# /me doit etre declare AVANT /{user_id}
@router.get("/me")
def me():
    return _public(get_player_or_404(current.player_id))


@router.get("/{user_id}")
def get_user(user_id : str):
    return _public(get_player_or_404(user_id))   # uniquement son propre compte

MAX_NAME_LENGTH = 20

@router.post("/rename")
def editPlayer(editData : RenameData):
    user = get_player_or_404(editData.player_id)

    name = editData.name.strip()
    if not 1 <= len(name) <= MAX_NAME_LENGTH:
        raise HTTPException(422 , f"name must be between 1 and {MAX_NAME_LENGTH} characters")

    user.name = name
    session.commit()

    return _public(user)


@router.get("/stats/{user_id}")
def getStats(user_id: str):
    acting(user_id)
    try:
        info = Statistics(user_id)
    except DataNotFound:
        raise HTTPException(404 , "user not found")

    return StatsData(fatestWin = info.getFastestTime() , TotalTime = info.getTotalTime() ,
                     TotalTries = info.getNbTry() , meanTries = info.getMeanTries() ,
                     winGames = info.getTotalWin() , TotalGames = info.getTotalGames() ,
                     endedGames = info.getTotalGameFinished())


@router.get("/stats/history/{user_id}")
def getHistory(user_id: str):
    acting(user_id)
    try:
        info = Statistics(user_id)
    except DataNotFound:
        raise HTTPException(404 , "user not found")

    return info.getHistory(10)
