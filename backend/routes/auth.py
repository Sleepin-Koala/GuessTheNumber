# type: ignore
"""Identite des joueurs.

Chaque joueur possede un jeton secret (donne une seule fois a la creation du compte). Le serveur ne garde que
son empreinte SHA-256. Le jeton est envoye dans `Authorization: Bearer <jeton>` (HTTP) ou dans le sous-protocole
WebSocket (`Sec-WebSocket-Protocol: gtn.v1, <jeton>`), jamais dans l'URL.

Regle par defaut: TOUTE route HTTP exige un jeton valide, sauf celles listees dans PUBLIC. Une route ajoutee plus tard
est donc protegee d'office. `acting(player_id)` verifie ensuite que l'identifiant fourni dans la requete est bien celui
du proprietaire du jeton (on ne peut agir qu'en son propre nom).
"""
import hashlib
import secrets

from fastapi import HTTPException
from starlette.requests import HTTPConnection

from all import *

PUBLIC = {
    ("GET", "/health"), ("GET", "/whatsup"), ("GET", "/whoami"),
    ("POST", "/user/new_player"), ("POST", "/user/claim"),
    ("GET", "/docs"), ("GET", "/redoc"), ("GET", "/openapi.json"),
}
WS_SUBPROTOCOL = "gtn.v1"


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def player_for_token(token: str):
    if not token or len(token) > 200:
        return None
    return session.query(Player).filter_by(token_hash=hash_token(token)).first()


def _bearer(conn: HTTPConnection):
    header = conn.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    return token.strip() if scheme.lower() == "bearer" else None


def authenticate(conn: HTTPConnection):
    """Dependance globale (apres `db_guard`): refuse les requetes sans jeton valide."""
    if conn.scope["type"] != "http":
        return
    if (conn.scope["method"], conn.scope["path"]) in PUBLIC:
        return
    player = player_for_token(_bearer(conn))
    if player is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    current.player_id = player.id


def acting(player_id: str):
    """On ne peut agir qu'au nom du joueur authentifie."""
    if current.player_id is None or player_id != current.player_id:
        raise HTTPException(status_code=403, detail="You can only act as yourself")


# ---- WebSocket ----
def ws_token(ws) -> str:
    """Jeton transmis comme sous-protocole: `Sec-WebSocket-Protocol: gtn.v1, <jeton>`."""
    parts = [p.strip() for p in ws.headers.get("sec-websocket-protocol", "").split(",")]
    return parts[1] if len(parts) >= 2 and parts[0] == WS_SUBPROTOCOL else ""


def ws_player_id(ws):
    """Identifiant du joueur de la socket (verrou BD pris a la main: les sockets n'ont pas `db_guard`)."""
    token = ws_token(ws)
    with db_lock:
        try:
            player = player_for_token(token)
            return player.id if player else None
        finally:
            session.rollback()       # relache la connexion (voir db_guard)
