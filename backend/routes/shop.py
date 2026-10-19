from pathlib import Path
from fastapi import APIRouter , HTTPException
from all import *
from routes.auth import acting
import json

router = APIRouter(prefix="/shop")

ITEMS_FILE = Path(__file__).resolve().parent.parent / "assets" / "Powerup.json"

def fillItems():
    """Synchronise la table Items avec Powerup.json (le catalogue fait foi pour les prix)."""
    elements = json.loads(ITEMS_FILE.read_text(encoding="utf-8"))
    for element in elements:
        item = session.get(Items , element["id"])
        if item is None:
            session.add(Items(id = element["id"] , name = element["name"] , price = element["price"]))
        else:
            item.name = element["name"]
            item.price = element["price"]
    session.commit()

fillItems()


def _player_data(player):
    return PlayerData(id = player.id , name = player.name , gems = player.gems , coins = player.coins , xp = player.xp , level = player.level) # type: ignore


def _holding(player_id , item_id):
    return session.query(PlayerItems).filter_by(playerId = player_id , itemId = item_id).first()


@router.post("/buy")
def buy(data: BuyData):
    acting(data.playerId)
    player = session.query(Player).filter_by(id = data.playerId).first()
    item = session.get(Items , data.itemId)

    if not player or not item:
        raise HTTPException(404 , "not found")

    if player.coins < item.price:
        raise HTTPException(402 , "Not enough coins")

    holding = _holding(player.id , item.id)
    if holding is None:
        holding = PlayerItems(playerId = player.id , itemId = item.id , amount = 0)
        session.add(holding)

    player.coins -= item.price
    holding.amount = (holding.amount or 0) + 1

    session.commit()

    return _player_data(player)


@router.post("/count")
def getCount(data: BuyData):
    acting(data.playerId)
    player = session.query(Player).filter_by(id = data.playerId).first()
    item = session.get(Items , data.itemId)

    if not player or not item:
        raise HTTPException(404 , "not found")

    holding = _holding(player.id , item.id)

    return holding.amount or 0 if holding else 0


@router.get("/inventory/{player_id}")
def getInventory(player_id: str):
    acting(player_id)
    player = session.query(Player).filter_by(id = player_id).first()
    if not player:
        raise HTTPException(404 , "not found")

    rows = session.query(PlayerItems).filter_by(playerId = player.id).all()
    return {"items": {str(r.itemId): r.amount for r in rows if (r.amount or 0) > 0}}
