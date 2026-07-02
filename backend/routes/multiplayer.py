from fastapi import APIRouter , HTTPException 
from all import *
import engine

router = APIRouter(prefix="/multiplayer")


@router.post("/host/{host_id}")
def hostServer(host_id: str):
    for s in session.query(Versus).filter_by(player_1 = host_id).all():
        s.status = "aborted"

    new_game = Versus(id = str(uuid4()),player_1 = host_id , status = "waiting")
    session.add(new_game)
    session.commit()

    return new_game.id

@router.get("/servers")
def getServers():
    res = session.query(Versus).filter_by(status = "waiting").all()
    return [{"id": i.id , "host" : i.player_1_rel.name} for i in res]

@router.get("/status/{room_id}")
def getStatus(room_id : str):
    server = session.query(Versus).filter_by(id=room_id).first()
    if not server:
        raise HTTPException(404 , "not server found")
    
    if server.player_2_rel:
        current = len(session.query(UserTries).filter_by(session_id = room_id).all()) % 2
        return VersusData(room_id = server.id ,
                        player_1 = PlayerData(id = server.player_1_rel.id , name = server.player_1_rel.name , gems = server.player_1_rel.gems , coins = server.player_1_rel.coins , xp = server.player_1_rel.xp , level=server.player_1_rel.level) ,
                        player_2 = PlayerData(id = server.player_2_rel.id , name = server.player_2_rel.name , gems = server.player_2_rel.gems , coins = server.player_2_rel.coins , xp = server.player_2_rel.xp , level=server.player_2_rel.level) ,
                        status = server.status,
                        PlayerPlaying = [server.player_1_rel.id ,server.player_2_rel.id][current])  # type: ignore
    else :
        print(server.player_1_rel.id)
        return VersusData(room_id = server.id ,
                        player_1 = PlayerData(id = server.player_1_rel.id , name = server.player_1_rel.name , gems = server.player_1_rel.gems , coins = server.player_1_rel.coins , xp = server.player_1_rel.xp , level=server.player_1_rel.level) ,
                        player_2 = PlayerData(id = None , name = None , gems = None , coins = None , xp = None , level=None) ,
                        status = server.status,
                        PlayerPlaying = server.player_1_rel.id)  # type: ignore
 
@router.post("/join")
def joinServer(JoinData : JoinData):

    server = session.query(Versus).filter_by(id=JoinData.server_id).first()
    if not server:
        raise HTTPException(404 , "not server found")
    
    if server.status == "waiting":
        server.player_2 = JoinData.player_id
        server.status = "begin"


        multi_sessson = GameSession(
            id = JoinData.server_id,
            max_attempt = 5,
            attempt_left = 5,
            number = engine.Multi.getNumber(),
            status = "continued",
            started_time = time.time(),
            end_time = 0,
            player_id = JoinData.player_id,
            type = "multi",
            time_limit = 30
        )
        print(multi_sessson.number)
        session.add(multi_sessson)
        session.commit()


    return server.id