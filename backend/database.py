
from sqlalchemy.orm import declarative_base , relationship
from sqlalchemy import Column , Integer , String , ForeignKey , create_engine
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
    max_attempt = Column(Integer)
    attempt_left = Column(Integer)
    number = Column(Integer)
    status = Column(String)
    started_time = Column(Integer)
    end_time = Column(Integer)
    player_id = Column(String , ForeignKey("player.id"))
    type = Column(String)
    player = relationship("Player")
    time_limit = Column(Integer)
    stage = Column(Integer , nullable=True)
    result = Column(String , nullable=False)

class UserTries(Base):

    __tablename__ =  "essais"
    id = Column(String , primary_key=True)
    session_id = Column(String , ForeignKey("sessions.id"))
    number = Column(Integer)
    player_id = Column(String , ForeignKey("player.id"))
    session = relationship("GameSession")
    player = relationship("Player")

class Versus(Base):
    __tablename__ = "versus"
    id = Column(String , primary_key=True)
    player_1 = Column(String , ForeignKey("player.id"))
    player_2 = Column(String, ForeignKey("player.id") , default=None)
    status = Column(String)
    winner = Column(String, nullable=True)
    player_1_rel = relationship("Player", foreign_keys= player_1)
    player_2_rel = relationship("Player", foreign_keys= player_2)

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