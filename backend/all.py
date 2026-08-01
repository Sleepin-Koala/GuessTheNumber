from database import *
from uuid import uuid4
from sqlalchemy.orm import sessionmaker
from models import *
import time
import engine

GIVEN_UP = "abandoned"
LOSE_STATE = "lose"
WIN_STATE = "win"

SOLO_MODE = "solo"
ENDLESS_MODE = "endless"


db = make_db()
session_ = sessionmaker(bind=db)
session = session_()