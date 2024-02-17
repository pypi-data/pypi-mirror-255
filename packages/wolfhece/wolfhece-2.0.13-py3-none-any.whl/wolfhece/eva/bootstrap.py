"""
Boostraping

@author : Pierre Archambeau - ULiege - HECE
@date   : 2023
"""
import numpy as np

class Bootstrap():

    def __init__(self,data,seed=None) -> None:

        # Initilisation d'un générateur aléatoire
        self.rnd = np.random.default_rng(seed)

        self.data=data

    def generate(self,nb):

        self.series = self.rnd.choice(self.data,(nb,len(self.data)),True)
        for i in range(nb):
            self.series[i,:].sort()

if __name__=='__main__':

    mydata = np.arange(10)
    my = Bootstrap(mydata)
    my.generate(100)

    pass


