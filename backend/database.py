
from sqlalchemy.orm import declarative_base , relationship
from sqlalchemy import Column , Integer , String ,Float, ForeignKey , create_engine
from typing import Optional

Base = declarative_base()

class Player(Base):
    __tablename__ = "player"
    id = Column(String , primary_key=True)
    name = Column(String)
    level = Column(Integer , default=1)
    created_at = Column(Integer)
    xp = Column(Integer , default=0)
    coins = Column(Integer , default=500)
    gems = Column(Integer , default=10)

    # Relationships
    #sent_friends = relationship("Friend", foreign_keys="Friend.sender_id", backref="sender")
    #received_friends = relationship("Friend", foreign_keys="Friend.receiver_id", backref="receiver")
    #session_pl = relationship("session")




class GameSession(Base):
    __tablename__ =  "sessions"

    id = Column(String , primary_key=True)
    number = Column(Integer)
    status = Column(String)
    started_time = Column(Float)
    ended_time = Column(Float , nullable=True)
    player_id = Column(String , ForeignKey("player.id"))
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_on' : type
    }
    
class EndlessSession(GameSession):
    __tablename__ = "endless"
    id = Column(String  , ForeignKey("sessions.id"),primary_key=True)
    bet = Column(Integer , default=None , nullable=True)
    stage =  Column(Integer)
    max_attempt = Column(Integer)
    attempt_left = Column(Integer)

    __mapper_args__ = {
        "polymorphic_identity" : "endless"
    }

class SoloSession(GameSession):
    __tablename__ = "solo"
    id = Column(String  , ForeignKey("sessions.id"),primary_key=True)
    max_attempt = Column(Integer)
    attempt_left = Column(Integer)
    time_limit = Column(Integer)

    __mapper_args__ = {
            "polymorphic_identity" : "solo"
        }

class DiscoverSession(GameSession):
    __tablename__ = "discover"
    id = Column(String  , ForeignKey("sessions.id"),primary_key=True)
    __mapper_args__ = {
                "polymorphic_identity" : "discover"
            }

class UserTries(Base):
    __tablename__ =  "essais"
    id = Column(String , primary_key=True)
    session_id = Column(String , ForeignKey("sessions.id"))
    number = Column(Integer)
    player_id = Column(String , ForeignKey("player.id"))
    session_type = Column(String)
    session = relationship("GameSession")



class Duel(Base):
    __tablename__ = "duel"
    id = Column(String ,ForeignKey("sessions.id") ,primary_key=True)
    host_id = Column(String , ForeignKey("player.id"))
    guest_id = Column(String ,ForeignKey("player.id"), nullable=True , default=None)
    room_name = Column(String)
    bet_amount = Column(Integer)
    status = Column(String)
    max_range = Column(Integer)
    hider_number = Column(Integer , nullable=True , default=None)
    guesser_number = Column(Integer , nullable=True , default=None)
    guesser_id = Column(String , nullable=True)   
    hider_id = Column(String , nullable=True)   

    #mettre dans userTries apres 
    last_distance = Column(Float, nullable=True , default=None)
    last_feedback = Column(String, nullable=True , default=None)

    round1_attempts_used = Column(Integer , nullable = True,default=0) 
    round2_attempts_used  = Column(Integer , nullable = True,default=0) 
    winner_id = Column(String , nullable = True,default=None) 

class Items(Base):
    __tablename__ = "items"
    id = Column(Integer , primary_key=True)
    name = Column(String)
    price = Column(Integer)

class PlayerItems(Base):
    __tablename__ = "hold"
    id = Column(Integer , autoincrement=True , primary_key=True)
    playerId = Column(String , ForeignKey("player.id"))
    itemId = Column(Integer , ForeignKey("items.id"))
    amount = Column(Integer , default=0)







def make_db():
    engine = create_engine("sqlite:///main.db")
    Base.metadata.create_all(engine)
    return engine