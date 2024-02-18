import ROOT
import os
import math 
import numpy as np

import utils
import utils_noroot as utnr

from rk.oscillator import oscillator as osc

#-------------------------------------------
class reader:
    log=utnr.getLogger(__name__)
    def __init__(self):
        self.d_map   = {}
        self.d_bound = {}
        self.map_histname = { 'etra' : 'heffratio',
                              'mtra' : 'Ratio'}
        self.epsilon  = 1e-8
        self.map_hist = None
        self._maps    = None
    #-------------------------------------------
    def setMapPath(self, mapdir):
        if not os.path.isdir(mapdir):
            self.log.error(f'Cannot find {mapdir}')
            raise
        self.mapdir = mapdir
    #-------------------------------------------
    def _setHist(self):
        if self.map_hist is not None:
            return

        self._maps = f"{self.mapdir}/{self.cate}_{self.year:.0f}.root"
        self.log.info(f'Using map in: {self._maps}')
        try:
            temFile       = ROOT.TFile(self._maps)
            self.map_hist = temFile.Get(self.map_histname[self.cate])
            self.map_hist.SetDirectory(0)
        except:
            self.log.error(f'Cannot open: {self._maps}')
            raise
    #-------------------------------------------
    @property
    def maps(self):
        return self._maps
    #-------------------------------------------
    def _adjust_point(self, phi, eta, pt, p):
        if phi < - math.pi or phi > math.pi and self.cate == 'etra':
            self.log.error(f'Invalid value of phi: {phi:.3f}')
            raise

        if eta < 1.9:
            self.log.debug(f'Eta: {eta:.3f} ---> {1.9:.3f}')
            eta = 1.9 + 0.1

        elif eta > 4.5 and self.cate == 'etra':
            self.log.debug(f'Eta_e: {eta:.3f} ---> {4.5:.3f}')
            eta = 4.5 - 0.1
            
        elif eta > 4.9 and self.cate == 'mtra':
            self.log.debug(f'Eta_m: {eta:.3f} ---> {4.9:.3f}')
            eta = 4.9 - 0.1

        if pt < 150 and self.cate == 'etra':
            self.log.debug(f'Pt_e: {pt:.0f} ---> {150:.0f}')
            pt = 150   + 1

        elif pt > 50000 and self.cate == 'etra':
            self.log.debug(f'Pt_e: {pt:.0f} ---> {50000:.0f}')
            pt = 50000 - 1
            
        if p < 5000 and self.cate == 'mtra':
            self.log.debug(f'P_m: {p:.0f} ---> {5000:.0f}')
            p = 5000   + 1

        elif p > 200000 and self.cate == 'mtra' and not (self.year == 2011 or self.year == 2012):
            self.log.debug(f'P_m: {p:.0f} ---> {200000:.0f}')
            p = 200000 - 1

        elif p > 201000 and self.cate == 'mtra' and (self.year == 2011 or self.year == 2012):
            self.log.debug(f'P_m: {p:.0f} ---> {201000:.0f}')
            p = 201000 - 1
        
        if (self.year == 2011 or self.year == 2012) and self.cate == 'mtra':
            p = p/1000
            # Unit of p in 2011 and 2012 maps are GeV, and it is MeV in other maps. 

        return (phi, eta, pt, p)
    #-------------------------------------------
    def __getTargetWeight(self, prefix):
        wgt = []
        arr_points = utils.getMatrix(self.df, [ f'{prefix}_Phi', f'{prefix}_ETA', f'{prefix}_PT', f'{prefix}_P', "yearLabbel"])
        self.year = arr_points[0][4]
        self._setHist()
        
        tem_osc_obj = osc()
        self.map_hist = tem_osc_obj.get_oscillated_map(self._maps, self.map_hist)
        
        for [phi, eta, pt, p, yr] in arr_points:
            phi, eta, pt, p = self._adjust_point(phi, eta, pt, p)
            
            if   self.cate == 'etra':
                var_array = (phi, eta, pt)
            elif self.cate == 'mtra':
                var_array = (p, eta)
                
            curr_globalbin = self.map_hist.FindBin(*var_array)
            
            curr_wgt = self.map_hist.GetBinContent(curr_globalbin)
        
            if curr_wgt <= 0:
                if self.cate == 'etra':
                    self.log.warning(f'{curr_wgt:<20.3f}{pt:<20.3f}{eta:<20.3f}{phi:<20.3f}')
                elif self.cate == 'mtra':
                    self.log.warning(f'{curr_wgt:<20.3f}{p:<20.3f}{eta:<20.3f}')

            wgt.append(curr_wgt)
        return np.array(wgt)
    #-------------------------------------------
    def _add_var(self, df, var, lep):
        if var == 'Phi':
            df = df.Define(f'{lep}_{var}', f'TVector3 v({lep}_PX, {lep}_PY, {lep}_PZ); return v.Phi();')
        else:
            self.log.error(f'Cannot define {var} for {lep}')
            raise

        return df
    #-------------------------------------------
    def _preprocess_df(self, df):
        l_col = df.GetColumnNames()

        if 'L1_Phi' not in l_col:
            df = self._add_var(df, 'Phi', 'L1')

        if 'L2_Phi' not in l_col:
            df = self._add_var(df, 'Phi', 'L2')

        return df
    #-------------------------------------------
    def _get_cate(self, df):
        if not hasattr(df, 'treename'):
            self.log.error(f'DataFrame does not contain "treename" attribute')
            raise

        if   df.treename in ['ETOS', 'GTIS']:
            cate = 'etra'
        elif df.treename == 'MTOS': 
            cate = 'mtra'
        else:
            self.log.error(f'Invalid treename {df.treename}')
            raise

        return cate
    #-------------------------------------------
    def getWeight(self, df):
        self.cate = self._get_cate(df)
        self.df   = self._preprocess_df(df)

        wgt1 = self.__getTargetWeight("L1")
        wgt2 = self.__getTargetWeight("L2")

        return wgt1, wgt2
#-------------------------------------------

