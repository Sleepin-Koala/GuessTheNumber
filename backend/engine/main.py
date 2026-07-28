import random as rd
import math


class GameMode:

    @property
    def WIN(cls):
        return "win"

    @property
    def LOSE(cls):
        return "lose"


class SoloMode(GameMode):
    AVERAGE_SECOND_PER_RESPONSE = 5 
    poids_essais = 0.6
    poids_precision = 0.3
    poids_temps = 0.1

    def __init__(self , level) -> None:
        self.level = level
        self.max_tries = self.get_max_try()
        self.max_time = self.get_max_time()
        
    
    def get_max_try(self):
        maxTry = math.ceil(math.log2(self.level * 10))
        return maxTry if self.level < 20 else maxTry+2

    def get_max_time(self):
        return self.get_max_try() * self.AVERAGE_SECOND_PER_RESPONSE

    def get_number(self):
        return rd.randint(1 , 10*self.level)
    


    def calcul_precision(self , inputs , TrueNumber):
        precision = 0
        for x in inputs:
            if x <= TrueNumber:
                precision += x/TrueNumber
            else:
                precision += TrueNumber/x
        return precision/len(inputs)

    def calcul_score(self ,inputs,time_s , TrueNumber):

        score_essais = (self.max_tries - len(inputs)) / (self.max_tries - 1)
        score_precision = self.calcul_precision(inputs,TrueNumber)
        score_temps = (self.max_time - time_s) / (self.max_time - self.get_min_time())

        score_total = (self.poids_essais * score_essais) + \
                    (self.poids_precision * score_precision) + \
                    (self.poids_temps * score_temps)

        print(score_total)
        return score_total
        # deepseek dit que cest entre O et 1 mais je pense que cest entre 0 et 3 mais je garde ça la au cas ou 
        # je me dis si 0<a<1 et 0<b<1 et 0<c<1 alors 0<a+b+c<1+1+1=3

    def get_min_time(self):
        max_range = self.level * 10
        min_attempts = math.ceil(math.log2(max_range))  
        seconds_per_attempt = 2.0 
        return min_attempts * seconds_per_attempt

    def getRewardCoin(self , inputs , time_s , TrueNumber):
        boost_level = self.level * 100 if self.level < 5 else self.level * 50
        base = 100 + boost_level
        return int(base + (boost_level * self.calcul_score(inputs , time_s,TrueNumber)))
    
    def getStars(self , inputs , time_s,TrueNumber):
        score = self.calcul_score(inputs , time_s,TrueNumber)
        if score <= 0.3 :
            return 1
        elif 0.3 < score <= 0.5:
            return 2
        else :
            return 3

    def getXP(self, inputs, time_s , TrueNumber):
        base_xp = self.level * 10
        bonus = self.calcul_score(inputs, time_s , TrueNumber) * 50
        return int(base_xp + bonus)

    def getDaimond(self,inputs , time_s , TrueNumber):
        if self.getStars(inputs , time_s , TrueNumber) == 3:
            return 1
        else :
            return 0

class Multi:

    @classmethod
    def getNumber(cls):
        return rd.randint(1 , 500)  

class DiscoverMode(GameMode):

    @classmethod
    def number(cls):
        return rd.randint(1,50)
    
    @classmethod
    def get_random(cls , max):
        return rd.randint(0 , max)

class EndlessMode(GameMode):

    @property
    def MODE(cls):
        return "endless"

    @property
    def STAGEPASSED(cls):
        return "won"
    
    @staticmethod
    def newSession(stage: int):
        return rd.randint(1 , stage * 10)


def checkResult(real_number , nb_user):
    if real_number > nb_user:
        return "MOINS"
    elif real_number < nb_user:
        return "PLUS"
    else:
        return "OK"
