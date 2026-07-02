from all import * 
from .exeptions import *




class Statistics:

    def __init__(self, player_id) -> None:
        self.player = session.query(Player).filter_by(id = player_id).first()

        if not self.player:
            raise DataNotFound()

    def getTotalGameFinished(self):
        return len(session.query(GameSession).filter_by(player_id = self.player.id , status = "ended").all())
    
    def getNbGameContinued(self):
        return len(session.query(GameSession).filter_by(player_id = self.player.id , status = "continued").all())
    
    def getTotalWin(self):
        datas = session.query(GameSession).filter_by(player_id = self.player.id , result = "won").all()
        return len(datas)
    
    def getTotalGames(self):
        datas = session.query(GameSession).filter_by(player_id = self.player.id).all()
        return len(datas)

    def getNbTry(self):
        return len(session.query(UserTries).filter_by(player_id = self.player.id).all())
    
    def getMeanTries(self):
        datas = session.query(GameSession).filter_by(player_id = self.player.id , status = "ended").all()
        return sum([d.max_attempt - d.attempt_left for d in datas])//len(datas)


    
    def getTotalTime(self):#seuelemnet pour les jeux qui sont fini
        datas = session.query(GameSession).filter_by(player_id = self.player.id , status = "ended").all()
        t = 0
        for d in datas:
            t += (d.end_time - d.started_time)
        return float(t)
    
    def getFastestTime(self):#seuelemnet pour les jeux qui sont fini
        datas = session.query(GameSession).filter_by(player_id = self.player.id , status = "ended").all()
        if len(datas) == 0:
            return -1
        return abs(min([d.end_time - d.started_time for d in datas]))
    
    def getLongestTime(self):#seuelemnet pour les jeux qui sont fini
        datas = session.query(GameSession).filter_by(player_id = self.player.id , status = "ended").all()
        return max([d.end_time - d.started_time for d in datas])


def CropTable(rows: int):
    return session.query(GameSession).all()[-rows:]
    
    






