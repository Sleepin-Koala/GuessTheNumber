
from all import *

def getPlayerbyId(session , id):
    player = session.query(Player).filter_by(id = id).first()
    if not player:
        return
    return player