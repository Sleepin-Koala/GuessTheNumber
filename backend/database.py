import os
import re

from sqlalchemy.orm import declarative_base , relationship
from sqlalchemy import Column , Integer , BigInteger , String ,Float, ForeignKey , create_engine
from typing import Optional

Base = declarative_base()

class Player(Base):
    __tablename__ = "player"
    id = Column(String , primary_key=True)
    name = Column(String)
    level = Column(Integer , default=1)
    created_at = Column(Float)                         # time.time(): une date en secondes avec decimales
    xp = Column(BigInteger , default=0)                # BigInteger: Postgres limite Integer a ~2,1 milliards
    coins = Column(BigInteger , default=500)
    gems = Column(BigInteger , default=10)
    token_hash = Column(String , nullable=True, index=True)    # sha256 du jeton secret du joueur (le jeton lui-meme n'est jamais stocke)

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
    max_range = Column(Integer, nullable=True)   # plage du nombre mystere (pour les power-ups)

    __mapper_args__ = {
        'polymorphic_on' : type
    }
    
class EndlessSession(GameSession):
    __tablename__ = "endless"
    id = Column(String  , ForeignKey("sessions.id"),primary_key=True)
    bet = Column(BigInteger , default=None , nullable=True)
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
    id = Column(String , primary_key=True)             # (n'est PAS une session: Postgres verifie les cles etrangeres)
    host_id = Column(String , ForeignKey("player.id"))
    guest_id = Column(String ,ForeignKey("player.id"), nullable=True , default=None)
    room_name = Column(String)
    bet_amount = Column(BigInteger)
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
    updated_at = Column(Float, nullable=True)          # derniere action (sert aux delais d'inactivite)
    end_reason = Column(String, nullable=True)         # solved | forfeit | disconnect | timeout | abandoned | expired | cancelled

class Items(Base):
    __tablename__ = "items"
    id = Column(Integer , primary_key=True)
    name = Column(String)
    price = Column(Integer)

class SessionPowerup(Base):
    """Un power-up utilise pendant une partie (au plus un de chaque sorte par partie)."""
    __tablename__ = "session_powerups"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    player_id = Column(String, ForeignKey("player.id"))
    item_id = Column(Integer)
    created_at = Column(Float)


class PlayerItems(Base):
    __tablename__ = "hold"
    id = Column(Integer , autoincrement=True , primary_key=True)
    playerId = Column(String , ForeignKey("player.id"))
    itemId = Column(Integer , ForeignKey("items.id"))
    amount = Column(Integer , default=0)







_POSTGRES_URL = re.compile(r"postgres(?:ql)?(?:\+\w+)?://[^\s'\"`]+")


def database_url() -> str:
    """Adresse de la base. `GTN_DATABASE_URL` (ex. Postgres heberge: postgresql://user:mdp@hote/base) prend le dessus;
    sinon un fichier SQLite (`GTN_DB_PATH`, par defaut `main.db`)."""
    raw = os.environ.get("GTN_DATABASE_URL", "").strip()
    if not raw:
        return f"sqlite:///{os.environ.get('GTN_DB_PATH', 'main.db')}"
    if raw.startswith("sqlite"):
        return raw
    # tolere les erreurs de copier-coller: guillemets, `DATABASE_URL=postgresql://...`, `psql 'postgresql://...'`, espaces
    found = _POSTGRES_URL.search(raw)
    if not found:
        # message sans afficher la valeur (elle contient un mot de passe)
        raise RuntimeError(
            "GTN_DATABASE_URL est definie mais ce n'est pas une adresse PostgreSQL: elle doit commencer par "
            f"postgresql:// (la valeur fait {len(raw)} caracteres{'' if '://' in raw else ' et ne contient pas ://'}). "
            "Colle l'adresse seule, sans guillemets ni nom de variable.")
    url = found.group(0)
    # les hebergeurs donnent postgres:// ou postgresql://; SQLAlchemy doit savoir quel pilote utiliser (psycopg 3)
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def make_db():
    url = database_url()
    if url.startswith("sqlite"):
        engine = create_engine(url)
    else:
        # pre_ping: un hebergeur gratuit coupe les connexions inactives (la base se met en veille); on verifie avant usage
        engine = create_engine(url , pool_pre_ping=True , pool_recycle=240 , pool_size=3 , max_overflow=2 ,
                               # prepare_threshold=None: pas de requetes preparees cote serveur (incompatibles avec le "pooler"
                               # des hebergeurs en mode transaction); connect_timeout: une base en veille met un instant a repondre
                               connect_args={"prepare_threshold": None , "connect_timeout": 20})
    Base.metadata.create_all(engine)
    if engine.dialect.name == "sqlite":
        _migrate(engine)       # anciennes bases SQLite uniquement: Postgres est cree d'un coup avec toutes les colonnes
    return engine


# colonnes ajoutees apres coup: (table, colonne, type SQL)
_NEW_COLUMNS = [
    ("sessions", "max_range", "INTEGER"),
    ("player", "token_hash", "VARCHAR"),
    ("duel", "updated_at", "FLOAT"),
    ("duel", "end_reason", "VARCHAR"),
]


def _migrate(engine):
    """Ajoute les colonnes apparues apres la creation d'une base existante (SQLite)."""
    with engine.begin() as conn:
        for table, column, sql_type in _NEW_COLUMNS:
            cols = [row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")]
            if cols and column not in cols:
                conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
