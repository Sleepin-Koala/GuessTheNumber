# type: ignore
from fastapi import APIRouter
from fastapi import APIRouter , HTTPException 
from all import *


router = APIRouter(prefix="/duel")

def create_room(room: Duel):
    return RoomData(
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

@router.post("/host")
def hostServer(HostRoomData: HostRoomData):

    new_game = Duel(
        id = str(uuid4()), 
        host_id = HostRoomData.host_id,
        guest_id = None,
        room_name = HostRoomData.name,
        bet_amount = HostRoomData.amount,
        status = "waiting",
        max_range = HostRoomData.max_range,
        hider_id = HostRoomData.host_id,
        guesser_id = None,
        hider_number = None,
        guesser_number = None,
        last_distance = None,
        last_feedback = None,
        round1_attempts_used = None,
        round2_attempts_used = None,
        winner_id = None
    )


    session.add(new_game)
    session.commit()

    return create_room(new_game)

@router.post("/status")
def checkStatus(CheckRoomData: CheckRoomData):
    room = session.query(Duel).filter_by(id = CheckRoomData.room_id).first()
    if not room:
        HTTPException(status_code=404, detail="Room introuvable")

    return create_room(room)

@router.post("/join")
def joinRoom(JoinData : JoinData):
    room = session.query(Duel).filter_by(id = JoinData.room_id).first() 

    if not room:
        raise HTTPException(status_code=404, detail="Room introuvable")
    
    room.status = "round1_hide"
    room.guest_id = JoinData.player_id
    room.guesser_id = JoinData.player_id

    session.commit()

    return create_room(room)


@router.post("/rooms/{roomId}/hide")
def hideNumber(HideNumberData : HidenGuessNumberData, roomId: str):
    room = session.query(Duel).filter_by(id = roomId).first()
    if not room :
        raise HTTPException(status_code=404, detail="Room introuvable")
    if HideNumberData.player_id != room.hider_id:
            raise HTTPException(status_code=403, detail="Ce n'est pas ton tour de cacher un nombre")


    if room.host_id == HideNumberData.player_id:
        room.hider_number = HideNumberData.number
    else:
        room.guesser_number = HideNumberData.number

    if room.status == "round1_hide":
        room.status = "round1_guess"
    elif room.status == "round2_hide":
        room.status = "round2_guess"

    session.commit()
    

    return create_room(room)

@router.post("/rooms/{roomId}/guess")
def GuessNumber(GuessNumberData : HidenGuessNumberData, roomId: str):
    room = session.query(Duel).filter_by(id = roomId).first()
    if not room :
        raise HTTPException(status_code=404, detail="Room introuvable")

    if room.guesser_id != GuessNumberData.player_id:
        raise HTTPException(status_code=403, detail="Ce n'est pas ton tour de deviner")

    if room.status == "round1_guess":
        room.round1_attempts_used += 1
    if room.status == "round2_guess":
            room.round2_attempts_used += 1


    hider_id = room.hider_id
    his_number = int(room.hider_number if hider_id == room.host_id else room.guesser_number)

    room.last_distance = float(abs(his_number-GuessNumberData.number))
    room.last_feedback = engine.checkResult(his_number , GuessNumberData.number)


    round_over = room.last_feedback == "OK" 
    
    if round_over:
        if room.status == "round1_guess":
            room.status = "round2_hide"
            temp = room.guesser_id

            room.guesser_id = room.hider_id
            room.hider_id = temp

        elif room.status == "round2_guess":    
            if room.round1_attempts_used < room.round2_attempts_used:
                winner_id = room.host_id            
            elif room.round2_attempts_used < room.round1_attempts_used:
                winner_id = room.guesser_id          
            else:
                winner_id = room.host_id            

            room.winner_id = winner_id
            room.status = "finished"

    session.commit()


    return create_room(room)
 
