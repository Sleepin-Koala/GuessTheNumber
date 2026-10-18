from database import *
from uuid import uuid4
from sqlalchemy.orm import sessionmaker
from models import *
import time
import threading
import engine

GIVEN_UP = "abandoned"
LOSE_STATE = "lose"
WIN_STATE = "win"

SOLO_MODE = "solo"
ENDLESS_MODE = "endless"


db = make_db()
session_ = sessionmaker(bind=db)
session = session_()

# La session SQLAlchemy est partagee: on serialise les requetes et on
# rollback en cas d'erreur pour ne jamais laisser la session dans un etat casse.
db_lock = threading.Lock()

def db_guard():
    db_lock.acquire()
    try:
        yield
    except BaseException:
        session.rollback()
        raise
    finally:
        db_lock.release()
