import ROOT 

import logging
import pickle
import numpy
import math
import os

import utils_noroot as utnr

from rk.collector   import collector
from trgwgt         import trg_rwt

from rk.oscillator import oscillator as osc

#-----------------------
class reader:
    log = utnr.getLogger(__name__)
    #--------------------------------
    def __init__(self, year, map_dir):
        l_tag_m=[]
        l_tag_e=[]
        l_tag_h=[]
        l_tag_t=[]
        if True:
            l_tag_e.append('L0ElectronTIS')
            l_tag_e.append('L0ElectronFAC')
            l_tag_e.append('L0ElectronHAD')

            l_tag_h.append('L0HadronMuMU')
            l_tag_h.append('L0HadronMuTIS')
            l_tag_h.append('L0HadronElEL')
            l_tag_h.append('L0HadronElTIS')

            l_tag_t.append('L0TIS_EMMH')
            l_tag_t.append('L0TIS_MMMH')
            l_tag_t.append('L0TIS_EMBN')

            l_tag_m.append('L0MuonTIS')
            l_tag_m.append('L0MuonMU1')
            l_tag_m.append('L0MuonMU2')
            l_tag_m.append('L0MuonHAD')
            l_tag_m.append('L0MuonALL1')
            l_tag_m.append('L0MuonALL2')

        l_tag = []
        for tag_e in l_tag_e:
            l_tag.append((tag_e,))
            for tag_h in l_tag_h:
                l_tag.append((tag_h, tag_e))
                for tag_t in l_tag_t:
                    l_tag.append((tag_t, tag_h, tag_e))

        for tag_m in l_tag_m:
            l_tag.append((tag_m,))

        l_tag.sort()
        self.log.debug(f'Defined {len(l_tag)} tags')
        for tag in l_tag:
            self.log.debug(f'      {str(tag)}')

        self.l_tag   = l_tag
        self.d_map   = {}
        self.d_wgt   = {}
        self.year    = year
        self._map_dir= map_dir
        self.storage = collector()
    #--------------------------------
    def predict_weights(self, tp_tag, df, replica=0):
        self.tp_tag=tp_tag
        if not hasattr(df, 'treename'):
            self.log.error('Dataframe does not have the treename as attribute')
            raise

        self.df       = df 
        self.treename = df.treename
        self.replica  = replica

        if tp_tag not in self.l_tag:
            self.log.error(f'Invalid tag: {str(tp_tag)}')
            for tag in self.l_tag:
                self.log.error(tag)
            raise

        self._load_maps(tp_tag)

        d_eff   = self._get_all_efficiencies(tp_tag)
        arr_wgt = self._calculate_weights(d_eff)

        df_size = df.Count().GetValue()
        if df_size != len(arr_wgt):
            self.log.error(f'Weights and dataframe differ in size: {df_size}/{len(arr_wgt)}')
            raise

        return arr_wgt 
    #--------------------------------
    def _get_all_efficiencies(self, tp_tag):
        d_eff={}
        for tag in tp_tag:
            arr_point_1 = self.__getPoints(tag,  True)
            arr_point_2 = self.__getPoints(tag, False)

            if   tag == 'L0TIS_EMMH':
                d_eff[    'L0TIS_EM'] = self.__getEfficiencies('L0TIS_EM', arr_point_1, 1)
                d_eff[    'L0TIS_MH'] = self.__getEfficiencies('L0TIS_MH', arr_point_2, 2)
            elif tag == 'L0TIS_MMMH':
                d_eff[    'L0TIS_MM'] = self.__getEfficiencies('L0TIS_MM', arr_point_1, 1)
                d_eff[    'L0TIS_MH'] = self.__getEfficiencies('L0TIS_MH', arr_point_2, 2)
            elif tag == 'L0TIS_EMBN':
                d_eff[    'L0TIS_EM'] = self.__getEfficiencies('L0TIS_EM', arr_point_1, 1)
                d_eff[    'L0TIS_BN'] = self.__getEfficiencies('L0TIS_BN', arr_point_2, 2)
            elif tag == 'L0ElectronFAC':
                d_eff['L0Electron_p'] = self.__getEfficiencies(       tag, arr_point_1, 1)
                d_eff['L0Electron_m'] = arr_point_2 
            elif tag.startswith('L0Electron'):
                d_eff['L0Electron_p'] = self.__getEfficiencies(       tag, arr_point_1, 1)
                d_eff['L0Electron_m'] = self.__getEfficiencies(       tag, arr_point_2, 2)
            elif tag.startswith('L0Muon'):
                d_eff[    'L0Muon_p'] = self.__getEfficiencies(       tag, arr_point_1, 1)
                d_eff[    'L0Muon_m'] = self.__getEfficiencies(       tag, arr_point_2, 2)
            elif tag.startswith('L0Hadron'):
                d_eff[    'L0Hadron'] = self.__getEfficiencies(       tag, arr_point_1, 1)
            else:
                self.log.error(f'Unrecognized tag {tag}')
                raise

        return d_eff
    #--------------------------------
    def _load_maps(self, tp_tag):
        for tag in tp_tag: 
            if   tag == 'L0TIS_EMMH':
                self._cache_map('L0TIS_EM')
                self._cache_map('L0TIS_MH')
            elif tag == 'L0TIS_MMMH':
                self._cache_map('L0TIS_MM')
                self._cache_map('L0TIS_MH')
            elif tag == 'L0TIS_EMBN':
                self._cache_map('L0TIS_EM')
                self._cache_map('L0TIS_BN')
            else:
                self._cache_map(       tag)
    #--------------------------------
    def __getPoints(self, tag, first):
        if   tag.startswith('L0TIS_') and     first:
            xvar='B_PT'
            yvar='B_ETA'
        elif tag.startswith('L0TIS_') and not first:
            self.df = self.df.Define('x', 'L1_PT > L2_PT ? L1_PT  : L2_PT ')
            self.df = self.df.Define('y', 'L1_PT > L2_PT ? L1_ETA : L2_ETA')

            xvar='x'
            yvar='y'
        elif tag == 'L0ElectronFAC'       and     first:
            xexp='TMath::Max(L1_L0Calo_ECAL_realET, L2_L0Calo_ECAL_realET)'
            yexp='TVector3 e_1(L1_L0Calo_ECAL_xProjection, L1_L0Calo_ECAL_yProjection, 0); TVector3 e_2(L2_L0Calo_ECAL_xProjection, L2_L0Calo_ECAL_yProjection, 0); return (e_1 - e_2).Mag();'

            self.df = self.df.Define('max_et', xexp)
            self.df = self.df.Define('deltaR', yexp)

            xvar = 'max_et'
            yvar = 'deltaR'
        elif tag == 'L0ElectronFAC'       and not first:
            size = self.df.Count().GetValue()
            arr_point = numpy.zeros(size)
            return arr_point
        elif tag.startswith('L0Electron') and     first:
            xvar='L1_L0Calo_ECAL_realET'
            yvar='L1_L0Calo_ECAL_region'
        elif tag.startswith('L0Electron') and not first:
            xvar='L2_L0Calo_ECAL_realET'
            yvar='L2_L0Calo_ECAL_region'
        elif tag.startswith('L0Muon')     and     first:
            xvar='L1_PT'
            yvar='L1_ETA'
        elif tag.startswith('L0Muon')     and not first:
            xvar='L2_PT'
            yvar='L2_ETA'
        elif tag.startswith('L0Hadron')   and     first:
            xvar='H_L0Calo_HCAL_realET'
            yvar='H_L0Calo_HCAL_region'
        elif tag.startswith('L0Hadron')   and not first:
            return
        else:
            self.log.error('Wrong tag ' + tag)
            raise

        d_val = self.df.AsNumpy([xvar, yvar])
        arr_x = d_val[xvar]
        arr_y = d_val[yvar]

        arr_point = numpy.vstack((arr_x, arr_y)).T

        return arr_point
    #--------------------------------
    def __getEfficiencies(self, tag, arr_point, index):
        try:
            rwt=self.d_map[tag]
        except:
            self.log.error('Cannot find map for tag: ' + tag) 
            raise

        tem_osc_obj = osc()
        rwt     = tem_osc_obj.get_oscillated_map(f'{self._map_dir}_{tag}_{index}', rwt)
        arr_eff = rwt.get_efficiencies(arr_point, self.treename)

        arr_eff_d=arr_eff.T[0]
        arr_eff_s=arr_eff.T[1]

        nd_neg = numpy.count_nonzero(arr_eff_d <  0)
        nd_zer = numpy.count_nonzero(arr_eff_d == 0)
        nd_one = numpy.count_nonzero(arr_eff_d == 1)
        nd_pos = numpy.count_nonzero(arr_eff_d >  1)

        ns_neg = numpy.count_nonzero(arr_eff_s <  0)
        ns_zer = numpy.count_nonzero(arr_eff_s == 0)
        ns_one = numpy.count_nonzero(arr_eff_s == 1)
        ns_pos = numpy.count_nonzero(arr_eff_s >  1)

        #Store stats
        if True:
            key='trg_dat_{}_{}_{}_{}'.format(self.treename, tag, index, 'neg_eff')
            self.storage.add(key, nd_neg)

            key='trg_dat_{}_{}_{}_{}'.format(self.treename, tag, index, 'zer_eff')
            self.storage.add(key, nd_zer)

            key='trg_dat_{}_{}_{}_{}'.format(self.treename, tag, index, 'one_eff')
            self.storage.add(key, nd_one)

            key='trg_dat_{}_{}_{}_{}'.format(self.treename, tag, index, 'pos_eff')
            self.storage.add(key, nd_pos)

            key='trg_sim_{}_{}_{}_{}'.format(self.treename, tag, index, 'neg_eff')
            self.storage.add(key, ns_neg)

            key='trg_sim_{}_{}_{}_{}'.format(self.treename, tag, index, 'zer_eff')
            self.storage.add(key, ns_zer)

            key='trg_sim_{}_{}_{}_{}'.format(self.treename, tag, index, 'one_eff')
            self.storage.add(key, ns_one)

            key='trg_sim_{}_{}_{}_{}'.format(self.treename, tag, index, 'pos_eff')
            self.storage.add(key, ns_pos)

        #Print stats
        if True:
            self.log.debug('-----------------------------------------')
            self.log.debug('Tag: ' + tag)
            self.log.debug('-----------------------------------------')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format(   'Value', 'Frequency', 'Total'))
            self.log.debug('')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Data < 0'      , nd_neg, arr_eff_d.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Data = 0'      , nd_zer, arr_eff_d.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Data = 1'      , nd_one, arr_eff_d.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Data > 1'      , nd_pos, arr_eff_d.size))
            self.log.debug('')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Simulation < 0', ns_neg, arr_eff_s.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Simulation = 0', ns_zer, arr_eff_s.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Simulation = 1', ns_one, arr_eff_s.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Simulation > 1', ns_pos, arr_eff_s.size))
            self.log.debug('-----------------------------------------')

        return arr_eff
    #--------------------------------
    def _calculate_weights(self, d_eff):
        lp_eff_p=None
        lm_eff_m=None
        
        hd_eff_p=None

        ev_eff_e=None
        ev_eff_n=None

        flag = 0
        for key, arr_eff in d_eff.items():
            self.storage.add('trg_eff_' + key, arr_eff)

            if   key in ['L0Electron_p', 'L0Muon_p']:
                arr_lp_eff_p = arr_eff
                flag += 1
            elif key in ['L0Electron_m', 'L0Muon_m']:
                arr_lm_eff_m = arr_eff
                flag += 1
            elif key ==     'L0Hadron':
                arr_hd_eff_p = arr_eff
                flag += 1
            elif key in ['L0TIS_EM', 'L0TIS_MM']:
                arr_ev_eff_e = arr_eff
                flag += 1
            elif key in ['L0TIS_MH', 'L0TIS_BN']:
                arr_ev_eff_n = arr_eff
                flag += 1
            else:
                self.log.error(f'Unrecognized key {key}')
                raise

        if   flag == 2:
            arr_wgt     = self.__candidateWgt(arr_lp_eff_p, arr_lm_eff_m, kind='lep', eff= True)
        elif flag == 3:
            arr_lep_wgt = self.__candidateWgt(arr_lp_eff_p, arr_lm_eff_m, kind='lep', eff=False)
            arr_had_wgt = self.__candidateWgt(arr_hd_eff_p,               kind='had', eff= True) 

            arr_wgt     = arr_had_wgt * arr_lep_wgt 

            nz_had = numpy.count_nonzero(arr_had_wgt == 0)
            nz_lep = numpy.count_nonzero(arr_lep_wgt == 0)

            self.log.debug('-----------------------------')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Factor', 'Zeros', 'Total'))
            self.log.debug('')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Hadron', nz_had, arr_had_wgt.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Lepton', nz_lep, arr_lep_wgt.size))
            self.log.debug('-----------------------------')

            self.d_wgt['lep'] = arr_lep_wgt
            self.d_wgt['had'] = arr_had_wgt
            self.d_wgt['tis'] = None 
        elif flag == 5:
            arr_lep_wgt = self.__candidateWgt(arr_lp_eff_p, arr_lm_eff_m, kind = 'lep', eff=False)
            arr_had_wgt = self.__candidateWgt(arr_hd_eff_p,               kind = 'had', eff=False) 
            arr_tis_wgt = self.__candidateWgt(arr_ev_eff_e, arr_ev_eff_n, kind = 'tis', eff= True)

            arr_wgt     = arr_tis_wgt * arr_had_wgt * arr_lep_wgt 

            nz_tis = numpy.count_nonzero(arr_tis_wgt == 0)
            nz_had = numpy.count_nonzero(arr_had_wgt == 0)
            nz_lep = numpy.count_nonzero(arr_lep_wgt == 0)

            self.log.debug('-----------------------------')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Factor', 'Zeros', 'Total'))
            self.log.debug('')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('TIS'   , nz_tis, arr_tis_wgt.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Hadron', nz_had, arr_had_wgt.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Lepton', nz_lep, arr_lep_wgt.size))
            self.log.debug('-----------------------------')

            self.log.debug('-----------------------------'                                                  )
            self.log.debug('{0:<20}{1:<20}{2:<20}{3:<20}'.format('TIS size', 'Hadron size', 'Lepton size', 'Candidate size'   ))
            self.log.debug('{0:<20}{1:<20}{2:<20}{3:<20}'.format(len(arr_tis_wgt), len(arr_had_wgt), len(arr_lep_wgt), len(arr_wgt) ))
            self.log.debug('-----------------------------'                                                  )

            self.d_wgt['lep'] = arr_lep_wgt
            self.d_wgt['had'] = arr_had_wgt
            self.d_wgt['tis'] = arr_tis_wgt
        else:
            self.log.error('Unsupported flag ' + str(flag))
            raise

        self.log.debug('{"Candidate weight":20}{"--->":20}{arr_wgt[0]:20.3}')

        return arr_wgt 
    #--------------------------------
    def _divide_arrays(self, arr_1, arr_2):
        """
        Will clean numerator and denominator arrays, replacing NaN and Inf with 1.
        Then it will divide arrays.
        """
        s_inv_num_ind = { index for index, value in enumerate(arr_1) if value in [   math.nan, +math.inf, -math.inf ] }
        s_inv_den_ind = { index for index, value in enumerate(arr_2) if value in [0, math.nan, +math.inf, -math.inf ] }

        s_inv_ind = s_inv_num_ind.union(s_inv_den_ind)

        ntot = arr_1.size
        ninv = len(s_inv_ind)
        if ninv / ntot > 0.01:
            self.log.warning(f'Found large number of invalid values: {ninv}/{ntot}')
        else:
            self.log.debug(f'Invalid values: {ninv}/{ntot}')

        for inv_ind in s_inv_ind:
            arr_1[inv_ind] = 1
            arr_2[inv_ind] = 1

        return arr_1 / arr_2
    #--------------------------------
    def __candidateWgt(self, *arrays, kind = None, eff = True):
        self.log.debug('Calculating inclusive={} efficiency weights for {}'.format(eff, kind))
        if kind is None:
            self.log.error('Kind argument not initialized')
            raise

        if   len(arrays) == 2:
            arr_eff_p = arrays[0]
            arr_eff_m = arrays[1]

            arr_eff_p_d = arr_eff_p.T[0]
            arr_eff_p_s = arr_eff_p.T[1]

            arr_eff_m_d = arr_eff_m.T[0]
            arr_eff_m_s = arr_eff_m.T[1]

            arr_eff_d = self.__candidateEff(arr_eff_p_d, arr_eff_m_d, eff)
            arr_eff_s = self.__candidateEff(arr_eff_p_s, arr_eff_m_s, eff)
            arr_eff_r = self._divide_arrays(arr_eff_d, arr_eff_s)

        elif len(arrays) == 1:
            arr_eff   = arrays[0]
            arr_eff_d = arr_eff.T[0]
            arr_eff_s = arr_eff.T[1]

            if eff:
                arr_eff_r = (    arr_eff_d)/(    arr_eff_s)
            else:
                arr_eff_r = (1 - arr_eff_d)/(1 - arr_eff_s)
        else:
            self.log.error('Introduced {} arrays'.format(len(arrays)))
            raise

        nz_nan = numpy.count_nonzero(numpy.isnan(arr_eff_r))
        nz_inf = numpy.count_nonzero(numpy.isinf(arr_eff_r))
        nz_zer = numpy.count_nonzero(arr_eff_r == 0)

        #Store quality stats
        if True:
            key='trg_qual_{}_{}_{}'.format(self.treename, 'nan', kind)
            self.storage.add(key, nz_nan)

            key='trg_qual_{}_{}_{}'.format(self.treename, 'inf', kind)
            self.storage.add(key, nz_inf)

            key='trg_qual_{}_{}_{}'.format(self.treename, 'zer', kind)
            self.storage.add(key, nz_zer)

        #Print quality stats
        if True:
            self.log.debug('-----------------------------------------')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Value', 'Frequency', 'Total'))
            self.log.debug('')
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format( 'NaN', nz_nan, arr_eff_r.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format( 'Inf', nz_inf, arr_eff_r.size))
            self.log.debug('{0:<20}{1:<20}{2:<20}'.format('Zero', nz_zer, arr_eff_r.size))
            self.log.debug('-----------------------------------------')

        #Weights with undefined values will be zero
        arr_eff_r[numpy.isnan(arr_eff_r)] = 0
        arr_eff_r[numpy.isinf(arr_eff_r)] = 0

        return arr_eff_r
    #--------------------------------
    def __candidateEff(self, arr_eff_p, arr_eff_m, eff):
        if eff:
            return 1 - (1 - arr_eff_p) * (1 - arr_eff_m)
        else:
            return     (1 - arr_eff_p) * (1 - arr_eff_m)
    #--------------------------------
    def _cache_map(self, tag):
        if tag not in self.d_map:
            self.d_map[tag] = trg_rwt(tag, self.year, self._map_dir)
    #-------------------------------------------
    def save_storage(self, storepath):
        storedir=os.path.dirname(storepath)
        if not os.path.isdir(storedir):
            self.log.error('Directory {} does not exist'.format(storedir))
            raise

        self.log.visible('Saving storage object to ' + storepath)
        pickle.dump(self.storage, open(storepath, 'wb'))
#------------------------------------------------------

