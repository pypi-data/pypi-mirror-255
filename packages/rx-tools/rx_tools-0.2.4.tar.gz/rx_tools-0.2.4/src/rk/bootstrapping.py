import ROOT
import os
import numpy  as np
import random as rd
import scipy.stats

import utils
import utils_noroot as utnr

#-------------------------------------------
class reader:
    log=utnr.getLogger(__name__)
    #-------------------------------------------
    def __init__(self):
        # self.n_test = -1
        self.d_map={}
        self.d_bound={}
        self.epsilon=1e-8
        # self.storage=collector()
        self.cached_maps=False
        self.year_list = { "r1"  : ["2011", "2012"],  
                           "r2p1": ["2015", "2016"], 
                           "2017": ["2017"], 
                           "2018": ["2018"] }
    #-------------------------------------------
    def _getRandomPoissonVar(seld, lam, seed):
        x = 0
        rd.seed(seed)
        pmf_gen = rd.uniform(0, 1)
        pmf_x   = scipy.stats.poisson.pmf(x, lam)
        while(pmf_gen >= pmf_x):
            x = x + 1
            pmf_x = pmf_x + scipy.stats.poisson.pmf(x, lam)
        return x
    #-------------------------------------------
    def _szudzikPairing(self, x, y):
        return x**2 + x + y if x >= y else y**2 + x
        # x**2 + x + y, if x >= y
        # y**2 + x    , else
    #-------------------------------------------
    def setYear(self, year):
        self.year = year
    #-------------------------------------------
    def __setYearLabel(self, year):
        if   year == "2011" or year == "2012":
            self.year_tag = "r1"
        elif year == "2015" or year == "2016":
            self.year_tag = "r2p1"
        elif year == "2017" or year == "2018":
            self.year_tag = year
        else:
            raise Exception("yearLabel:{} is not in the range of 2011-12 or 2015-18".format(year))
    #-------------------------------------------
    def __getTargetWeight(self):
        wgt = []
        arr_points = utils.getMatrix(self.df, [ 'eventNumber' ])
        self.__setYearLabel(self.year)
        
        for [evt_num] in arr_points:
            year_index = self.year_list[self.year_tag].index(self.year)
            seed = self._szudzikPairing(self._szudzikPairing( int(year_index), int(self.n_test) ), int(evt_num))
            wgt.append(self._getRandomPoissonVar(1, seed))
            
        return np.array(wgt)
    #-------------------------------------------
    def getWeight(self, df, n_test):
        self.df       = df
        n_test        = str(n_test)

        if n_test == '0':
            nevents = df.Count().GetValue()
            arr_wgt = np.ones(nevents)
            return arr_wgt

        self.n_test   = n_test

        self.log.debug(f'Retrieving bootstrapping weights for toy/year: {n_test}/{self.year}')

        wgt           = self.__getTargetWeight()

        return wgt
#-------------------------------------------

