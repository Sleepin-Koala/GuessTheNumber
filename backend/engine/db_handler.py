import all as _app   # import tardif: `all` importe `engine`, la session n'existe pas encore a ce stade
from database import Player, GameSession, UserTries
from .exeptions import *

FINISHED = ("won", "lose")


class Statistics:
    """Statistiques d'un joueur, calculees a partir de ses sessions."""

    # type de session (base) -> nom affiche par le front
    TYPE_LABELS = {"solo": "classic", "discover": "discovery", "endless": "endless"}

    def __init__(self, player_id) -> None:
        self.player = _app.session.query(Player).filter_by(id = player_id).first()

        if not self.player:
            raise DataNotFound()

        self.sessions = _app.session.query(GameSession).filter_by(player_id = self.player.id).all()
        self.tries_per_session = {}
        for (sid,) in _app.session.query(UserTries.session_id).filter_by(player_id = self.player.id).all():
            self.tries_per_session[sid] = self.tries_per_session.get(sid, 0) + 1

    def _finished(self):
        return [s for s in self.sessions if s.status in FINISHED]

    @staticmethod
    def _duration(s):
        if s.ended_time is None or s.started_time is None:
            return None
        return max(0.0, s.ended_time - s.started_time)

    def getTotalGames(self):
        return len(self.sessions)

    def getTotalGameFinished(self):
        return len(self._finished())

    def getTotalWin(self):
        return len([s for s in self.sessions if s.status == "won"])

    def getNbTry(self):
        return sum(self.tries_per_session.values())

    def getMeanTries(self):
        finished = self._finished()
        if not finished:
            return 0.0
        return round(sum(self.tries_per_session.get(s.id, 0) for s in finished) / len(finished), 1)

    def getTotalTime(self):
        return float(sum(d for d in map(self._duration, self._finished()) if d is not None))

    def getFastestTime(self):
        durations = [d for d in (self._duration(s) for s in self.sessions if s.status == "won") if d is not None]
        return min(durations) if durations else None

    def getHistory(self, rows: int = 10):
        last = sorted(self.sessions, key = lambda s: s.started_time or 0, reverse = True)[:rows]
        return [{
            "id": i,
            "type": self.TYPE_LABELS.get(s.type, s.type),
            "result": s.status,
            "attemps": self.tries_per_session.get(s.id),
            "date": s.started_time or 0,
        } for i, s in enumerate(last)]
