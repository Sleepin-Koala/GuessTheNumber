from database import *
from uuid import uuid4
import time
from sqlalchemy.orm import sessionmaker
from DataModels import *

db = make_db()
session_ = sessionmaker(bind=db)
session = session_()