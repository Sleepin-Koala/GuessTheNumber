# type: ignore
"""Inscription et connexion par e-mail + mot de passe, et liaison avec un compte Google.

Un joueur peut jouer en invite (compte anonyme lie a l'appareil). S'il s'inscrit ou se connecte avec Google alors qu'il joue
deja, l'identite est RATTACHEE a son compte actuel: il garde sa progression. Se connecter sur un autre appareil emet un
nouveau jeton (les autres appareils doivent se reconnecter).
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import time
import urllib.parse
import urllib.request

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from all import *
from routes.auth import new_token, hash_token, player_for_token, _bearer
from routes.user import create_player, _public

router = APIRouter(prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s.]{2,}$")
MIN_PASSWORD, MAX_PASSWORD = 8, 128
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_TOKENINFO = "https://oauth2.googleapis.com/tokeninfo?id_token="
SCRYPT = dict(n=2 ** 14, r=8, p=1, dklen=32)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def check_password(password: str, stored) -> bool:
    try:
        _, salt, digest = (stored or "").split("$")
        probe = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), **SCRYPT)
        return hmac.compare_digest(probe, bytes.fromhex(digest))
    except Exception:
        return False


_DUMMY = hash_password("dummy-password-for-timing")


class Credentials(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=MAX_PASSWORD)


class GoogleData(BaseModel):
    credential: str = Field(max_length=4096)


def _email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Enter a valid email address")
    return email


def _guest(request: Request):
    """Compte invite (sans e-mail ni Google) qui fait la requete, s'il y en a un."""
    player = player_for_token(_bearer(request))
    return player if player is not None and not player.email and not player.google_sub else None


def _reissue(user):
    token = new_token()
    user.token_hash = hash_token(token)
    session.commit()
    return _public(user, token)


@router.get("/config")
def config():
    return {"google_client_id": GOOGLE_CLIENT_ID or None}


@router.post("/register")
def register(data: Credentials, request: Request):
    email = _email(data.email)
    if len(data.password) < MIN_PASSWORD:
        raise HTTPException(422, f"Password must have at least {MIN_PASSWORD} characters")
    if session.query(Player).filter_by(email=email).first():
        raise HTTPException(409, "This email already has an account. Log in instead.")
    guest = _guest(request)
    if guest:                                   # on rattache l'e-mail au compte en cours: progression conservee
        guest.email, guest.password_hash = email, hash_password(data.password)
        session.commit()
        return _public(guest)
    user, token = create_player(email=email, password_hash=hash_password(data.password))
    return _public(user, token)


@router.post("/login")
def login(data: Credentials):
    email = data.email.strip().lower()
    user = session.query(Player).filter_by(email=email).first()
    ok = check_password(data.password, user.password_hash if user else _DUMMY)     # meme duree si l'e-mail est inconnu
    if not user or not ok:
        raise HTTPException(401, "Invalid email or password")
    return _reissue(user)


def _verify_google(credential: str) -> dict:
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(503, "Google sign-in is not configured")
    try:
        with urllib.request.urlopen(GOOGLE_TOKENINFO + urllib.parse.quote(credential, safe=""), timeout=5) as r:
            info = json.loads(r.read())
    except Exception:
        raise HTTPException(401, "Google could not verify this sign-in")
    if info.get("aud") != GOOGLE_CLIENT_ID or info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(401, "Google sign-in was issued for another application")
    if str(info.get("email_verified")).lower() != "true" or not info.get("sub") or not info.get("email"):
        raise HTTPException(401, "Your Google email is not verified")
    if float(info.get("exp", 0)) < time.time():
        raise HTTPException(401, "Google sign-in expired")
    return info


@router.post("/google")
def google(data: GoogleData, request: Request):
    info = _verify_google(data.credential)
    sub, email = info["sub"], info["email"].strip().lower()
    existing = session.query(Player).filter_by(google_sub=sub).first()
    if existing:
        return _reissue(existing)
    by_email = session.query(Player).filter_by(email=email).first()
    guest = _guest(request)
    if guest and not by_email:                  # un invite relie son compte Google: il garde sa progression
        guest.google_sub, guest.email = sub, email
        session.commit()
        return _public(guest)
    if by_email:                                # meme adresse que le compte e-mail: les deux se rejoignent
        by_email.google_sub = sub
        session.commit()
        return _reissue(by_email)
    user, token = create_player(email=email, google_sub=sub)
    return _public(user, token)
