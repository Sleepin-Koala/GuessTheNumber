from fastapi import APIRouter , HTTPException
from all import *
import json

router = APIRouter(prefix="/shop")
 
def fillItems():
    elements = json.load(open("./assets/Powerup.json" , "r" , encoding="utf-8"))
    for element in elements:
        elem = Items(id = element.get("id") , 
                    name = element.get("name"),
                    price = element.get("price"))
        session.add(elem)
        session.commit()

if len(session.query(Items).all()) == 0:
    fillItems()

@router.post("/buy")
def buy(data: BuyData):
    player = session.query(Player).filter_by(id = data.playerId).first()
    currentItem = session.query(Items).filter_by(id = data.itemId).first()

    if not player or not currentItem:
        return HTTPException(404 , "not found")

    if player.coins >= currentItem.price:
        player.coins -= currentItem.price

    holding = session.query(PlayerItems).filter_by(playerId = data.playerId , itemId = data.itemId).first()

    holding.amount += 1   

    session.commit()

    return PlayerData(id= player.id , name=player.name , gems=player.gems , coins = player.coins , xp = player.xp , level=player.level) # type: ignore

@router.post("/count")
def getCount(data: BuyData):
    player = session.query(Player).filter_by(id = data.playerId).first()
    currentItem = session.query(Items).filter_by(id = data.itemId).first()

    if not player or not currentItem:
        return HTTPException(404 , "not found")

    c = session.query(PlayerItems).filter_by(playerId = data.playerId , itemId = data.itemId).all()

    return len(c)
    
