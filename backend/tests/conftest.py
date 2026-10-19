"""Tests de l'API: base SQLite temporaire, lancer depuis n'importe ou: `pytest backend/tests`."""
import os
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
_tmp = tempfile.mkdtemp(prefix="gtn-tests-")
os.chdir(_tmp)                      # `sqlite:///main.db` est relatif au dossier courant
sys.path.insert(0, str(BACKEND))

import pytest
from fastapi.testclient import TestClient

from main import app
import all as A


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture()
def player(client):
    return client.get("/user/new_player").json()["id"]


def give(player_id, item_id, amount=1):
    """Met des objets dans l'inventaire sans passer par la boutique."""
    row = A.session.query(A.PlayerItems).filter_by(playerId=player_id, itemId=item_id).first()
    if row is None:
        row = A.PlayerItems(playerId=player_id, itemId=item_id, amount=0)
        A.session.add(row)
    row.amount = (row.amount or 0) + amount
    A.session.commit()


def secret(session_id):
    return A.session.query(A.GameSession).filter_by(id=session_id).first().number
