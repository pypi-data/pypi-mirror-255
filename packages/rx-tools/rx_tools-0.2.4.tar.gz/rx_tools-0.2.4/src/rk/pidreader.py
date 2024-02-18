import ROOT
import os
import numpy
import glob
import pickle

import utils
import utils_noroot as utnr

from rk.collector import collector

from rk.oscillator import oscillator as osc

#-------------------------------------------
class reader:
    log=utnr.getLogger(__name__)
    def __init__(self):
        self.d_map={}
        self.d_path={}
        self.d_bound={}
        self.epsilon=1e-8
        self.storage=collector()
        self.cached_maps=False
    #-------------------------------------------
    def setMapPath(self, mapdir):
        if not os.path.isdir(mapdir):
            self.log.error(f'Cannot find {mapdir}')
            raise

        self.mapdir = mapdir
    #-------------------------------------------
    def __getYear(self):
        try:
            d_year=self.df.AsNumpy(['yearLabbel'])
            arr_year=d_year['yearLabbel']
            self.year = int(arr_year[0])
        except:
            self.log.error('Cannot extract year')
            raise
    #-------------------------------------------
    def __defineVars(self):
        l_colname = self.df.GetColumnNames()
        if 'H_P' not in l_colname:
            self.df = self.df.Define('H_P', 'TVector3 v_h(H_PX, H_PY, H_PZ); return v_h.Mag();')
    #-------------------------------------------
    def __show_settings(self):
        self.log.info('-----------------------')
        self.log.info('{0:<20}{1:<20}'.format('Replica'   ,     self.replica))
        self.log.info('{0:<20}{1:<20}'.format('isElectron', self.is_electron))
        self.log.info('{0:<20}{1:<20}'.format('Year'      ,        self.year))
        self.log.info('-----------------------')
    #-------------------------------------------
    def __cacheMaps(self):
        if self.cached_maps:
            return

        self.log.info('---------------------------------------')
        self.log.info('Caching maps')
        self.log.info('')

        self.__do_cacheMaps(True)
        self.__do_cacheMaps(False)

        self.cached_maps = True

        self.log.info('---------------------------------------')
    #-------------------------------------------
    def __do_cacheMaps(self, is_electron):
        if is_electron:
            lep_map_path='{}/{}/{}'.format(self.mapdir, 'Electron', 'PArange_Fit_PolBoth_Year{}_nBrem*_merge_toys.root'.format(self.year))
            had_map_path='{}/{}/{}'.format(self.mapdir,     'Kaon', 'PerfHists_K_{}_Mag*_D0K_probNN_ee_P_ETA_updated_toys.root'.format(self.year))
        else:
            lep_map_path='{}/{}/{}'.format(self.mapdir,     'Muon', 'PerfHists_Mu_{}_Mag*_JpsiMu_DLLmu_ismuon_P_ETA_updated_toys.root'.format(self.year))
            had_map_path='{}/{}/{}'.format(self.mapdir,     'Kaon', 'PerfHists_K_{}_Mag*_D0K_probNN_P_ETA_updated_toys.root'.format(self.year))

        l_lep_map_path=glob.glob(lep_map_path)
        l_had_map_path=glob.glob(had_map_path)

        if len(l_lep_map_path) != 2:
            self.log.error('Found invalid number of lepton maps:')
            print(l_lep_map_path)
            self.log.error('Key: ' + lep_map_path)
            raise

        if len(l_had_map_path) != 2:
            self.log.error('Found invalid number of hadron maps:')
            print(l_had_map_path)
            self.log.error('Key: ' + had_map_path)
            raise

        for lep_map_path in l_lep_map_path:
            if   'nBrem0' in lep_map_path:
                key='el_nobrem'
                mapname='XXX_All_{}'.format(self.replica)
            elif 'nBrem1' in lep_map_path:
                key='el_brem'
                mapname='XXX_All_{}'.format(self.replica)
            elif 'MagUp' in lep_map_path:
                key='mu_magup'
                mapname='Mu_DLLmu>-3 && IsMuon==1_All_{}'.format(self.replica)
            elif 'MagDown' in lep_map_path:
                key='mu_magdown'
                mapname='Mu_DLLmu>-3 && IsMuon==1_All_{}'.format(self.replica)
            else:
                self.log.error('Unexpected map path {} found'.format(lep_map_path))
                raise

            self.log.info('{0:<20}{1:<130}{2:<20}'.format(key, lep_map_path, mapname))
            if key not in self.d_map:
                h_lep_map=self.__getMap(lep_map_path, mapname)
                self.d_map[key]  = h_lep_map
                self.d_path[key] = lep_map_path

            self.storage.add('pid_map_{}_{}'.format(key, self.treename), (lep_map_path, mapname) )

        mc_ver = '12' if self.year < 2015 else '15'
        tune   = 'V2' if self.year < 2015 else 'V1'
        for had_map_path in l_had_map_path:
            if   'MagUp'   in had_map_path and     is_electron:
                mapname='K_MC{}Tune{}_ProbNNK>0.2 && DLLe<0_All_{}'.format(mc_ver, tune, self.replica)
                key='hd_el_magup'
            elif 'MagUp'   in had_map_path and not is_electron:
                mapname='K_MC{}Tune{}_ProbNNK>0.2_All_{}'.format(mc_ver, tune, self.replica)
                key='hd_mu_magup'
            elif 'MagDown' in had_map_path and     is_electron:
                mapname='K_MC{}Tune{}_ProbNNK>0.2 && DLLe<0_All_{}'.format(mc_ver, tune, self.replica)
                key='hd_el_magdown'
            elif 'MagDown' in had_map_path and not is_electron:
                mapname='K_MC{}Tune{}_ProbNNK>0.2_All_{}'.format(mc_ver, tune, self.replica)
                key='hd_mu_magdown'
            else:
                self.log.error('Unexpected map path {} found'.format(had_map_path))
                raise

            self.log.info('{0:<20}{1:<130}{2:<20}'.format(key, had_map_path, mapname))
            if key not in self.d_map:
                h_had_map=self.__getMap(had_map_path, mapname)
                self.d_map[key]  = h_had_map
                self.d_path[key] = had_map_path 

            self.storage.add('pid_map_{}_{}'.format(key, self.treename), (had_map_path, mapname) )
    #-------------------------------------------
    def __getMap(self, filepath, histname):
        ifile=ROOT.TFile(filepath)
        try:
            hist=ifile.Get(histname)
            hist.SetDirectory(0)
            ifile.Close()
            return hist
        except:
            self.log.error('Canot retrieve map {} from {}'.format(histname, filepath))
            ifile.Close()
            raise
    #-------------------------------------------
    def predict_weights(self, df, replica=0) -> tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]:
        if not hasattr(df, 'treename'):
            self.log.error('Dataframe does not contain treename')
            raise

        self.df       = df
        self.treename = df.treename
        self.replica  = replica

        if  self.treename in ['KEE', 'ETOS', 'HTOS', 'GTIS']:
            self.is_electron = True
        else:
            self.is_electron = False

        self.__defineVars()
        self.__getYear()
        self.__show_settings()
        self.__cacheMaps()

        arr_lep_1 = self.__getLeptonPID('L1')
        arr_lep_2 = self.__getLeptonPID('L2')
        arr_had   = self.__getHadronPID()

        key = 'pid_stat_size_{}'.format(self.treename)
        self.storage.add(key, arr_lep_1.size)

        return (arr_lep_1, arr_lep_2, arr_had)
    #-------------------------------------------
    def __getLeptonPID(self, prefix):
        if self.is_electron:
            key_1     = 'el_nobrem'
            key_2     = 'el_brem'
            third_var = prefix + '_HasBremAdded'
        else:
            key_1     = 'mu_magup'
            key_2     = 'mu_magdown'
            third_var = 'Polarity'

        arr_points = utils.getMatrix(self.df, [prefix + '_P', prefix + '_ETA', third_var])

        try:
            h_1 = self.d_map[key_1]
            h_2 = self.d_map[key_2]
        except:
            self.log.error('Cannot retrieve map for keys {},{}'.format(key_1, key_2) )
            self.log.error('keys: ' + str(self.d_map.keys()) )
            raise

        l_eff=[]

        self.log.info('-----------------------------------------')
        self.log.info('Reading lepton map')
        self.log.info('{0:<20}{1:<50}'.format('1', h_1.GetName()))
        self.log.info('{0:<20}{1:<50}'.format('2', h_2.GetName()))
        self.log.info('-----------------------------------------')

        above=0
        below=0
        
        tem_osc_obj = osc()
        tem_osc_obj.is_efficiency(True)
        
        h_1 = tem_osc_obj.get_oscillated_map(self.d_path[key_1], h_1)
        h_2 = tem_osc_obj.get_oscillated_map(self.d_path[key_2], h_2)
        
        for point in arr_points:
            xval = point[0]
            yval = point[1]
            thir = point[2]

            if       self.is_electron and thir == 1:
                hist=h_2
            elif     self.is_electron and thir == 0:
                hist=h_1
            elif not self.is_electron and thir >  0:
                hist=h_1
            elif not self.is_electron and thir <  0:
                hist=h_2
            
            xval, yval = self.__adjustBoundaries(xval, yval, hist, is_lepton=True)

            i_bin= hist.FindBin(xval, yval)
            eff  = hist.GetBinContent(i_bin)
            if   eff > 1:
                key='eff_lep_above_' + self.treename
                self.storage.add_list(key, eff)
                self.log.debug('For tree {}, {:.3e} -> 1'.format(self.treename, eff))
                above+=1
                eff = 1
            elif eff < 0:
                key='eff_lep_below_' + self.treename
                self.storage.add_list(key, eff)
                self.log.debug('For tree {}, {:.3e} -> 0'.format(self.treename, eff))
                below+=1
                eff = 0

            l_eff.append(eff)

        self.log.debug('Unphysical above 1 for tree {}: {}'.format(self.treename, above))
        self.log.debug('Unphysical below 1 for tree {}: {}'.format(self.treename, below))

        arr_eff = numpy.array(l_eff)

        return arr_eff
    #-------------------------------------------
    def __getHadronPID(self):
        arr_points = utils.getMatrix(self.df, ['H_P', 'H_ETA', 'Polarity'])
        if arr_points.size == 0:
            self.log.error('Found no entries for tree {} and year {}'.format(self.treename, self.year))
            raise

        channel = 'el' if self.is_electron else 'mu'

        key_up='hd_{}_magup'.format(channel)
        key_dn='hd_{}_magdown'.format(channel)
        try:
            h_magup = self.d_map[key_up]
            h_magdn = self.d_map[key_dn]
        except:
            self.log.error('Cannot retrieve map for keys {},{}'.format(key_up, key_dn) )
            self.log.error('keys: ' + str(self.d_map.keys()) )
            raise

        l_eff=[]

        self.log.info('------------------')
        self.log.info('Reading hadron map')
        self.log.info('{0:<20}{1:<50}'.format(  'Up', h_magup.GetName() ))
        self.log.info('{0:<20}{1:<50}'.format('Down', h_magdn.GetName() ))
        self.log.info('------------------')

        above=0
        below=0
        
        tem_osc_obj = osc()
        tem_osc_obj.is_efficiency(True)
        
        h_magup = tem_osc_obj.get_oscillated_map(self.d_path[key_up], h_magup)
        h_magdn = tem_osc_obj.get_oscillated_map(self.d_path[key_up], h_magdn)
        
        for point in arr_points:
            xval = point[0]
            yval = point[1]
            pola = point[2]

            hist = h_magup if pola > 0 else h_magdn

            xval, yval = self.__adjustBoundaries(xval, yval, hist, is_lepton=False)

            i_bin= hist.FindBin(xval, yval)
            eff  = hist.GetBinContent(i_bin)
            if   eff > 1:
                above+=1
                key='eff_had_above_' + self.treename
                self.storage.add_list(key, eff)
                self.log.debug('Efficiency above 1 for tree {}: {}'.format(self.treename, eff))
                eff = 1
            elif eff < 0:
                below+=1
                key='eff_had_below_' + self.treename
                self.storage.add_list(key, eff)
                self.log.debug('Efficiency below 0 for tree {}: {}'.format(self.treename, eff))
                eff = 0

            l_eff.append(eff)

        self.log.debug('Unphysical above 1 for tree {}: {}'.format(self.treename, above))
        self.log.debug('Unphysical below 1 for tree {}: {}'.format(self.treename, below))

        arr_eff = numpy.array(l_eff)

        return arr_eff
    #-------------------------------------------
    def __adjustBoundaries(self, xval, yval, hist, is_lepton=None):
        histname=hist.GetName()
        if histname not in self.d_bound:
            self.__cacheBoundaries(hist)

        xmin, xmax, ymin, ymax = self.d_bound[histname]

        self.__store_boundary('xmin', None, None, is_lepton=is_lepton)
        self.__store_boundary('ymin', None, None, is_lepton=is_lepton)
        self.__store_boundary('xmax', None, None, is_lepton=is_lepton)
        self.__store_boundary('ymax', None, None, is_lepton=is_lepton)

        if (xmin < xval < xmax) and (ymin < yval < ymax):
            return (xval, yval)

        if xval < xmin:
            self.__store_boundary('xmin', xval, xmin, is_lepton=is_lepton)
            xval = xmin + self.epsilon

        if yval < ymin:
            self.__store_boundary('ymin', yval, ymin, is_lepton=is_lepton)
            yval = ymin + self.epsilon

        if xval > xmax:
            self.__store_boundary('xmax', xval, xmax, is_lepton=is_lepton)
            xval = xmax - self.epsilon

        if yval > ymax:
            self.__store_boundary('ymax', yval, ymax, is_lepton=is_lepton)
            yval = ymax - self.epsilon

        return (xval, yval)
    #-------------------------------------------
    def __store_boundary(self, prefix, value, bound, is_lepton=None):
        if is_lepton is None:
            self.log.error('is_lepton flag is not set')
            raise

        if self.storage is None:
            self.log.error('Storage object not found')
            raise

        if       is_lepton and     self.is_electron:
            self.particle='el'
        elif     is_lepton and not self.is_electron:
            self.particle='mu'
        else:
            self.particle='kp'

        key = 'pid_bound_{}_{}_{}'.format(self.treename, self.particle, prefix)

        if value is None and bound is None:
            val=None
        else:
            val = (value, bound)

        self.storage.add_list(key, val)
    #-------------------------------------------
    def save_storage(self, storepath):
        storedir=os.path.dirname(storepath)
        if not os.path.isdir(storedir):
            self.log.error('Directory {} does not exist'.format(storedir))
            raise

        self.log.visible('Saving storage object to ' + storepath)
        pickle.dump(self.storage, open(storepath, 'wb'))
    #-------------------------------------------
    def __cacheBoundaries(self, hist):
        xaxis=hist.GetXaxis()
        yaxis=hist.GetYaxis()

        xmin = xaxis.GetXmin()
        xmax = xaxis.GetXmax()

        ymin = yaxis.GetXmin()
        ymax = yaxis.GetXmax()

        tp_bound = (xmin, xmax, ymin, ymax)

        histname = hist.GetName()

        self.d_bound[histname] = tp_bound
#-------------------------------------------

