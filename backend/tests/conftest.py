"""Tests de l'API: base SQLite temporaire, lancer depuis n'importe ou: `pytest backend/tests`."""
import os
import re
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
os.environ["GTN_RATE_LIMIT"] = "off"       # les tests creent beaucoup de comptes; test_security.py reactive la limitation
# Pour tester sur une vraie base Postgres: GTN_TEST_DATABASE_URL=postgresql://user:mdp@hote/base pytest backend/tests
if os.environ.get("GTN_TEST_DATABASE_URL"):
    os.environ["GTN_DATABASE_URL"] = os.environ["GTN_TEST_DATABASE_URL"]
os.environ["DUEL_SWEEP_INTERVAL"] = "3600"  # les tests appellent sweep() eux-memes: pas de balayeur concurrent
_tmp = tempfile.mkdtemp(prefix="gtn-tests-")
os.chdir(_tmp)                      # `sqlite:///main.db` est relatif au dossier courant
sys.path.insert(0, str(BACKEND))

import contextlib

import pytest
from fastapi.testclient import TestClient

from main import app
import all as A

if os.environ.get("GTN_TEST_DATABASE_URL"):
    # une base partagee garde les donnees d'un lancement a l'autre: on repart de zero (et on recharge le catalogue)
    from routes.shop import fillItems
    A.Base.metadata.drop_all(A.db)
    A.Base.metadata.create_all(A.db)
    fillItems()


UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


class AuthedClient(TestClient):
    """Client de test qui s'authentifie comme le joueur designe dans la requete (id dans le JSON ou dans l'URL),
    sinon comme le dernier joueur cree. Les tests de securite passent leurs propres en-tetes."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.tokens = {}
        self.default = None

    def token_for(self, url, body=None):
        if isinstance(body, dict):
            for key in ("player_id", "host_id", "playerId"):
                if body.get(key) in self.tokens:
                    return self.tokens[body[key]]
        for found in UUID.findall(url):
            if found in self.tokens:
                return self.tokens[found]
        return self.default

    def request(self, method, url, **kw):
        headers = dict(kw.pop("headers", None) or {})
        if not any(k.lower() == "authorization" for k in headers):
            token = self.token_for(url, kw.get("json"))
            if token:
                headers["Authorization"] = f"Bearer {token}"
        resp = super().request(method, url, headers=headers, **kw)
        if url.endswith("/user/new_player") and resp.status_code == 200:
            data = resp.json()
            self.tokens[data["id"]] = data["token"]
            self.default = data["token"]
        return resp

    def websocket_connect(self, url, subprotocols=None, **kw):
        if subprotocols is None:
            token = self.token_for(url)
            subprotocols = ["gtn.v1", token] if token else None
        return super().websocket_connect(url, subprotocols=subprotocols, **kw)


@pytest.fixture(scope="session")
def client():
    with AuthedClient(app) as c:         # `with` lance le lifespan (hub temps reel + balayeur)
        yield c
@pytest.fixture()
def player(client):
    return client.post("/user/new_player").json()["id"]


@contextlib.contextmanager
def db():
    """Acces direct a la base depuis un test. La session SQLAlchemy est partagee avec les threads du serveur
    (routes, sockets, balayeur): comme eux, on prend le verrou, sinon deux threads l'utiliseraient en meme temps."""
    with A.db_lock:
        try:
            yield A.session
            A.session.commit()
        except BaseException:
            A.session.rollback()
            raise


def give(player_id, item_id, amount=1):
    """Met des objets dans l'inventaire sans passer par la boutique."""
    with db() as s:
        row = s.query(A.PlayerItems).filter_by(playerId=player_id, itemId=item_id).first()
        if row is None:
            row = A.PlayerItems(playerId=player_id, itemId=item_id, amount=0)
            s.add(row)
        row.amount = (row.amount or 0) + amount


def secret(session_id):
    with db() as s:
        return s.query(A.GameSession).filter_by(id=session_id).first().number
