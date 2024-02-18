import random as rd
import copy
import os

import utils_noroot as utnr

import rk.hist_map
import cppyy
import hep_cl
import trgwgt

#-------------------------------------------
class oscillator:
    log=utnr.getLogger(__name__)
    
    ntest = 0
    #-------------------------------------------
    def __init__(self):
        self._is_efficiency = False
    #-------------------------------------------
    def is_efficiency(self, flag):
        self._is_efficiency = flag
    #-------------------------------------------
    def _get_gauss_rv(self, mu, sigma, seed):
        rd.seed(seed)
        RV = -1
        debugFlag = 0
        if self._is_efficiency == True:
            while RV < 0 or RV > 1:
                debugFlag += 1
                RV = rd.gauss(mu, sigma)
                if debugFlag%1000 == 0 and debugFlag <= 10000:
                    self.log.warning(f'Resampled too many times when oscillating, please check whether the weight is far away from 0 or 1.')
                    self.log.warning(f'Map of {self._map_path} contents mean value {mu} with error of {sigma}.')
                if debugFlag == 10000 and RV < 0:
                    RV = 0
                    break
                elif debugFlag == 10000 and RV > 1:
                    RV = 1
                    break
        elif self._is_efficiency == False:
            while RV < 0:
                debugFlag += 1
                RV = rd.gauss(mu, sigma)
                if debugFlag%1000 == 0 and debugFlag <= 10000:
                    self.log.warning(f'Resampled too many times when oscillating, please check whether the weight is for smaller than 0')
                    self.log.warning(f'Map of {self._map_path} contents mean value {mu} with error of {sigma}.')
                if debugFlag==10000:
                    RV = 0
                    break
        return RV
    #-------------------------------------------
    def get_oscillated_weight(self, map_tag, map_hist, gloabal_bin):
        return self.get_oscillated_map(map_tag, map_hist).GetBinContent(gloabal_bin)
    #-------------------------------------------
    def get_oscillated_map(self, map_path, map_hist):
        if self.ntest == 0:
            self.log.info(f'Not oscillating map, ntest={self.ntest}')
            return map_hist

        self._map_hist = copy.deepcopy(map_hist)
        
        map_tag = os.path.basename(map_path)
        self._map_path = map_path
        
        if type(map_tag) is not str:
            self.log.error(f'map_tag should be \'str\' type.')
            raise
        
        if any( key in map_tag for key in ["PerfHists", "PArange"]  ):
            self._clean_pid_map()

        if   isinstance(self._map_hist, cppyy.gbl.TH2Poly):
            self._map_hist = self._oscillating_root_map_poly(map_tag, self._map_hist)
        elif isinstance(self._map_hist, (cppyy.gbl.TH1, cppyy.gbl.TH2, cppyy.gbl.TH3)):
            self._map_hist = self._oscillating_root_map(map_tag, self._map_hist)
        elif isinstance(self._map_hist, (rk.hist_map.hist_map, trgwgt.trg_rwt)):
            self._oscillating_pickle_hist_map(map_tag)
        elif isinstance(self._map_hist, (hep_cl.HIS)):
            self._oscillating_pickle_hepcl_map(map_tag)
        else:
            self.log.error(f'Type of map_hist: {type(map_hist)} is not supported.')
            raise

        return self._map_hist
    #-------------------------------------------
    def _clean_pid_map(self):
        Nx = self._map_hist.GetNbinsX() + 1
        Ny = self._map_hist.GetNbinsY() + 1
        
        for x in range(1, Nx):
            for y in range(1, Ny):
                BCxy = self._map_hist.GetBinContent(x, y)
                BExy = self._map_hist.GetBinError(x, y)
                if BCxy <= 0:
                    self._map_hist.SetBinContent(x, y, 0.0)
                    self._map_hist.SetBinError(x, y, 0.0)
                    self.log.warning(f'Reseting ({x},{y}) bin: ({BCxy},{BExy}) -----> (0, 0)')
                elif BExy == 0:
                    self._map_hist.SetBinError(x, y, 1e-6)
                    self.log.warning(f'Reseting ({x},{y}) bin: ({BCxy},{BExy}) -----> (0, 1e-6)')
    #-------------------------------------------
    def _oscillating_root_map(self, map_tag, map_hist):
        if self.ntest == 0:
            pass
        else:
            self.log.info(f'Oscillating {map_tag} map')
            seed = map_tag + "-" + str(self.ntest)

            if map_hist.GetDimension() == 1:
                Nx = map_hist.GetNbinsX() + 1
                
                for x in range(1, Nx):
                    temRV = self._get_gauss_rv(map_hist.GetBinContent(x), map_hist.GetBinError(x), seed)
                    map_hist.SetBinContent(x, temRV)

            elif map_hist.GetDimension() == 2:
                Nx = map_hist.GetNbinsX() + 1
                Ny = map_hist.GetNbinsY() + 1
                
                for x in range(1, Nx):
                    for y in range(1, Ny):
                        temRV = self._get_gauss_rv(map_hist.GetBinContent(x, y), map_hist.GetBinError(x, y), seed)
                        map_hist.SetBinContent(x, y, temRV)
                    
            elif map_hist.GetDimension() == 3:
                Nx = map_hist.GetNbinsX() + 1
                Ny = map_hist.GetNbinsY() + 1
                Nz = map_hist.GetNbinsZ() + 1
                
                for x in range(1, Nx):
                    for y in range(1, Ny):
                        for z in range(1, Nz):
                            temRV = self._get_gauss_rv(map_hist.GetBinContent(x, y, z), map_hist.GetBinError(x, y, z), seed)
                            map_hist.SetBinContent(x, y, z, temRV)
            else:
                self.log.error(f'Histogram\'s dimension is incorrect.')
                raise
        return map_hist
    #-------------------------------------------
    def _oscillating_root_map_poly(self, map_tag, map_hist):
        if self.ntest == 0:
            pass
        else:
            self.log.info(f'Oscillating {map_tag} map')
            seed = map_tag + "-" + str(self.ntest)

            NBins = map_hist.GetNumberOfBins()
            
            for x in range(0, NBins + 1):
                temRV = self._get_gauss_rv(map_hist.GetBinContent(x), map_hist.GetBinError(x), seed)
                map_hist.SetBinContent(x, temRV)
        return map_hist
    #-------------------------------------------
    def _oscillating_pickle_hist_map(self, map_tag):
        if self.ntest == 0:
            pass
        else:
            self.log.info(f'Oscillating {map_tag} map')
            map_hist_1, map_hist_2, map_hist_3 = self._map_hist.maps
            
            map_hist_1 = self._oscillating_root_map_poly(f'{map_tag}-h1', map_hist_1)
            map_hist_2 = self._oscillating_root_map_poly(f'{map_tag}-h2', map_hist_2)
            map_hist_3 = self._oscillating_root_map_poly(f'{map_tag}-h3', map_hist_3)
            
            self._map_hist.maps = (map_hist_1, map_hist_2, map_hist_3)
    #-------------------------------------------
    def _oscillating_pickle_hepcl_map(self, map_tag):
        if self.ntest == 0:
            pass
        else:
            self.log.info(f'Oscillating {map_tag} map')
            seed = map_tag + "-" + str(self.ntest)
            rat_hist, err_hist = self._map_hist.get_ratio_hist()
            
            if rat_hist.GetDimension() == 1:
                Nx = rat_hist.GetNbinsX() + 1
                
                for x in range(1, Nx + 1):
                    temRV = self._get_gauss_rv(rat_hist.GetBinContent(x), err_hist.GetBinError(x), seed)
                    rat_hist.SetBinContent(x, temRV)

            elif rat_hist.GetDimension() == 2:
                Nx = rat_hist.GetNbinsX() + 1
                Ny = rat_hist.GetNbinsY() + 1
                
                for x in range(1, Nx + 1):
                    for y in range(1, Ny + 1):
                        temRV = self._get_gauss_rv(rat_hist.GetBinContent(x, y), err_hist.GetBinError(x, y), seed)
                        rat_hist.SetBinContent(x, y, temRV)
                    
            elif rat_hist.GetDimension() == 3:
                Nx = rat_hist.GetNbinsX() + 1
                Ny = rat_hist.GetNbinsY() + 1
                Nz = rat_hist.GetNbinsZ() + 1
                
                for x in range(1, Nx + 1):
                    for y in range(1, Ny + 1):
                        for z in range(1, Nz + 1):
                            temRV = self._get_gauss_rv(rat_hist.GetBinContent(x, y, z), err_hist.GetBinError(x, y, z), seed)
                            rat_hist.SetBinContent(x, y, z, temRV)
            else:
                self.log.error(f'Histogram\'s dimension is incorrect.')
                raise
            self._map_hist.set_ratio_hist(rat_hist)
#-------------------------------------------
