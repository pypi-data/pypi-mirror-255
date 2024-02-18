import os
import re
import tqdm
import numpy
import numexpr
import random
import logging
import logzero
import collections

import ROOT

import matplotlib.pyplot  as plt
import pandas             as pnd
import utils_noroot       as utnr
import read_selection     as rs

import utils

from ndict            import ndict
from hep_cl           import hist_reader as hr
from rk.oscillator    import oscillator  as osc
from rk.collector     import collector
from rk.hist_map      import hist_map

from rk.bootstrapping import reader  as btsrd
from rk.trackreader   import reader  as trard
from rk.trgreader     import reader  as trgrd
from rk.pidreader     import reader  as pidrd 
from rk.q2smear       import q2smear

from rk.decaymodel_reader import dcm_reader as dcmrd

from stats.correlations import corr as scor
from atr_mgr            import mgr

#------------------------------
class weight_reader:
    turn_on  =True
    replica  =None

    log=utnr.getLogger(__name__)
    #------------------------------
    def __init__(self, df, kind):
        self._man_df                  = mgr(df)
        self._df                      = df
        self._kind                    = kind
        self._d_wgt_ver               = {}
        self._d_wgt_pat               = {}
        self._d_d_arr_wgt             = {} 
        self._l_supported_weight      = ['pid', 'trk', 'gen', 'lzr', 'hlt', 'rec', 'qsq', 'bts', 'bdt', 'dcm']
        self._l_supported_kind        = ['gen', 'rec', 'raw', 'sel']

        self._l_ee_trigger            = ['ETOS', 'GTIS']
        self._l_mm_trigger            = ['MTOS']
        self._l_trigger               = self._l_ee_trigger + self._l_mm_trigger 

        self._l_occ                   = ['npv', 'nsp'] # Occupacy parametrizations only used for systematics
        self._l_trg                   = ['GTIS_ee', 'GTIS_mm', 'ETOS_ee'] # Triggers only used for systematics
        self._l_gen_treename          = ['truth', 'gen'] 
        self._l_ee_treename           = ['KEE', 'ETOS', 'GTIS']
        self._l_mm_treename           = ['KMM', 'MTOS']
        self._l_treename              = self._l_gen_treename + self._l_ee_treename + self._l_mm_treename

        self._l_year                  = ['2011', '2012', '2015', '2016', '2017', '2018']
        self._min_plt_wgt             = 0
        self._max_plt_wgt             = 3
        self._no_corr                 = False
        self._initialized             = False
        self._l_supported_return_type = ['product', 'dict']
        self._d_sys_occ               = {} 
         
        self._d_zeros        = None
        self._nboots         = None
        self._nosc           = None
        self._d_arr_wgt_nom  = None
        self._df_stat        = None
        self._kin_dir        = None

        self._size           = None

        self._mode           = None

        self._arr_wgt_cur    = None
        self._filepath       = None
        self._treename       = None
        self._trigger        = None
        self._year           = None
        self._after_sel      = None
        self._pick_attr()

        self.valdir          = None
        self.file            = None
        self.tree            = None
        self.noweights       = False
        self.storage         = collector()
        self.d_storage       = {'weight_reader' : self.storage }
        #-------------------------
        self._d_syst = {}

        self._add_gen_syst()
        self._add_rec_syst()
        self._add_pid_syst()
        self._add_lzr_syst()
        self._add_hlt_syst()
        self._add_qsq_syst()
        self._add_trk_syst()
        self._add_bts_syst()
        self._add_bdt_syst()
        self._add_dcm_syst()
    #------------------------------
    @property
    def no_corr(self):
        return self._no_corr

    @no_corr.setter
    def no_corr(self, value):
        if value not in [True, False]:
            log.error(f'Invalid no_corr flag value: {value}')
            raise ValueError

        self._no_corr= value
    #------------------------------
    @property
    def df(self):
        return self._df
    #------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_rdf()
        self._set_level()

        utnr.check_included(self._kind, self._l_supported_kind)
        #-------------------------
        self._set_sys_occ()
        self._add_df_cols()
        #-------------------------
        if len(self._d_wgt_ver) == 0:
            self.noweights    = True
            self.identifier   = 'nokeys'
        else:
            l_key=list(self._d_wgt_ver.keys())
            l_key.sort()
            self.identifier = '_'.join(l_key)
        #-------------------------
        self._get_kin_dir()
        self._check_valdir()
        #-------------------------
        self._size=self._df.Count().GetValue()

        l_col = ['Weight',      'Sum', 'Cummulative', 'Zeros[\%]', 'NaNs[\%]', 'Infs[\%]']
        l_val = [  'none', self._size,    self._size,          0 ,         0 ,         0 ]

        self._df_stat        = pnd.DataFrame(columns=l_col)
        self._df_stat.loc[0] = l_val 
        #-------------------------
        if self.replica is None:
            self.log.error('Replica not specified')
            raise
        #-------------------------
        self._check_qsq()
        self._check_sel_quant('pid')

        if self._after_sel:
            self.log.info(f'Extracting mode for trigger "{self._treename}"')
            self._find_mode()
        else:
            self.log.info(f'Not extracting mode for trigger "{self._treename}"')

        self._check_corrections()

        #Version of bootstrapping "maps" is used to pass number of bootstrapping replicas
        if 'bts' in self._d_wgt_ver:
            ver, _ = self._d_wgt_ver['bts']
            self._nboots = int(ver)

        self._trigger     = self._get_trigger()

        self._print_settings()
        self._calculate_weights()
        self._calculate_correlations()
        self._save()

        self._initialized = True
    #----------------------------------------------
    @property
    def zeros(self):
        '''Returns statistics on number of weights that are zero
        Returns
        --------------
        {name -> number_of_zeros} 

        Where name is [gen, rec, trg...] and determines the stage at which these weigths are calculated
        and the number of zeros is the _cumulative_ number of zeros as we multiply weights
        '''
        return self._d_zeros
    #----------------------------------------------
    def _check_rdf(self):
        nentries = self._df.Count().GetValue()

        if nentries == 0:
            self.log.error('Input dataframe is empty')
            raise
        else:
            self.log.info(f'Getting weights for {nentries} entries')
    #----------------------------------------------
    def _print_kind_syst(self, lvl=logging.INFO):
        for kind in self._d_d_arr_wgt:
            d_arr_wgt = self._d_d_arr_wgt[kind]
            l_syst = list(d_arr_wgt.keys())

            if   lvl == logging.INFO:
                self.log.info(kind)
                self.log.info(l_syst)
            elif lvl == logging.ERROR:
                self.log.error(kind)
                self.log.error(l_syst)
            else:
                self.log.error(f'Invalid info level: {lvl}')
                raise
    #----------------------------------------------
    def __call__(self, kind, syst):
        self._initialize()

        '''Will return array for specific kind/syst combination 
        Parameters
        -------------------
        kind (str): Type of weight, e.g. gen, rec, lzr
        syst (str): Systematic fluctuation

        Returns:
        -------------------
        1D array of floats representing weights
        '''
        if syst == '000':
            syst = '0'

        if kind not in self._d_d_arr_wgt:
            self.log.error(f'Weight of kind: {kind} not found among:')
            self._print_kind_syst()
            raise

        d_arr_wgt = self._d_d_arr_wgt[kind]

        if syst not in d_arr_wgt:
            self.log.error(f'Systematic of kind {syst} for weight {kind} not found among:')
            self._print_kind_syst(lvl=logging.ERROR)
            raise

        arr_wgt = d_arr_wgt[syst]

        return arr_wgt
    #----------------------------------------------
    def _get_trigger(self):
        if self._kind not in ['raw', 'sel']:
            return

        if not hasattr(self._df, 'trigger'):
            self.log.error(f'Dataframe has no trigger attribute for kind {self._kind}')
            raise

        trigger = self._df.trigger
        if trigger not in self._l_trigger:
            self.log.error(f'Invalid trigger {trigger} for kind {kind}')
            raise

        return trigger
    #----------------------------------------------
    def _set_sys_occ(self):
        #Occupacy variable for REC
        self._d_sys_occ['MTOS'   ] = 'nTracks'
        self._d_sys_occ['ETOS'   ] = 'nTracks'
        self._d_sys_occ['GTIS'   ] = 'nTracks'
        self._d_sys_occ['GTIS_ee'] = 'nTracks'
        self._d_sys_occ['GTIS_mm'] = 'nTracks'
        self._d_sys_occ['ETOS_ee'] = 'nTracks'

        #Occupacy variable for GEN 
        self._d_sys_occ['nom'    ] = 'nTracks'
        self._d_sys_occ['npv'    ] = 'nPVs'
        self._d_sys_occ['nsp'    ] = 'nSPDHits'

        #Occupacy variable for BDT 
        self._d_sys_occ['nom'    ] = 'TMath::ACos(B_DIRA_OWNPV)'
    #----------------------------------------------
    def _check_corrections(self):
        weights = self._d_wgt_ver.keys()
        l_wgt   = list(weights)
        l_wgt   = sorted(l_wgt)
        l_sup   = sorted(self._l_supported_weight)

        if   self._kind == 'gen' and l_wgt == ['bts', 'gen']:
            return
        elif self._kind == 'rec' and l_wgt == ['bts', 'gen']:
            return
        elif self._kind == 'raw' and l_wgt == ['bts', 'gen', 'rec']:
            return
        elif self._kind == 'sel' and l_wgt == l_sup:
            return
        else:
            self.log.warning(f'For kind {self._kind} found weights:')
            self.log.warning(l_wgt)
    #----------------------------------------------
    def _pick_attr(self):
        self._filepath = utnr.get_attr(self._df, 'filepath')
        self._treename = utnr.get_attr(self._df, 'treename')
        self._year     = utnr.get_attr(self._df, 'year')

        if self._treename not in self._l_treename: 
            self.log.error(f'Unrecognized trigger: {self._df.treename}')
            raise

        self._after_sel = self._treename in self._l_trigger
    #------------------------------
    def _add_gen_syst(self):
        d_gen_syst = {}

        for treename in self._l_treename:
            d_gen_syst[ ('gen', treename, '000') ] = None
            d_gen_syst[ ('gen', treename, 'all') ] = None
            d_gen_syst[ ('gen', treename, 'nom') ] = None

        self._d_syst.update(d_gen_syst)
    #------------------------------
    def _add_rec_syst(self):
        d_rec_syst = {}

        for treename in self._l_treename:
            d_rec_syst[ ('rec', treename, '000') ] = None
            d_rec_syst[ ('rec', treename, 'all') ] = None
            d_rec_syst[ ('rec', treename, 'nom') ] = None

        self._d_syst.update(d_rec_syst)
    #------------------------------
    def _add_pid_syst(self):
        d_pid_syst = {}

        for trg in ['MTOS', 'ETOS', 'GTIS']:
            d_pid_syst[ ('pid', trg, '000') ] = None
            d_pid_syst[ ('pid', trg, 'all') ] = None
            d_pid_syst[ ('pid', trg, 'nom') ] = None

            if trg in ['ETOS', 'GTIS']:
                d_pid_syst[ ('pid', trg, 'kpeltis') ]  = None
                d_pid_syst[ ('pid', trg, 'kpelbin1') ] = None
                d_pid_syst[ ('pid', trg, 'kpelbin2') ] = None 
                d_pid_syst[ ('pid', trg, 'kpelbin3') ] = None 
                d_pid_syst[ ('pid', trg, 'kpelbin4') ] = None

                d_pid_syst[ ('pid', trg, 'eltis') ]  = None
                d_pid_syst[ ('pid', trg, 'elbin1') ] = None
                d_pid_syst[ ('pid', trg, 'elbin2') ] = None
            elif trg in ['MTOS']:
                d_pid_syst[ ('pid', trg, 'kpmutis') ]  = None
                d_pid_syst[ ('pid', trg, 'kpmubin1') ] = None
                d_pid_syst[ ('pid', trg, 'kpmubin2') ] = None 
                d_pid_syst[ ('pid', trg, 'kpmubin3') ] = None 
                d_pid_syst[ ('pid', trg, 'kpmubin4') ] = None

                d_pid_syst[ ('pid', trg, 'mutis') ]  = None
                d_pid_syst[ ('pid', trg, 'mubin1') ] = None
                d_pid_syst[ ('pid', trg, 'mubin2') ] = None 
                d_pid_syst[ ('pid', trg, 'mubin3') ] = None 
                d_pid_syst[ ('pid', trg, 'mubin4') ] = None
            else:
                self.log(f'Systematic of trigger {trg} is not supported.')
                raise
            
        self._d_syst.update(d_pid_syst)
    #------------------------------
    def _add_lzr_syst(self):
        d_lzr_syst = {}

        for trg in self._l_trigger: 
            d_lzr_syst[('lzr', trg, '000')] = None 
            d_lzr_syst[('lzr', trg, 'all')] = None 
            d_lzr_syst[('lzr', trg, 'nom')] = None 

        self._d_syst.update(d_lzr_syst)
    #------------------------------
    def _add_hlt_syst(self):
        d_hlt_syst = {}

        for trg in self._l_trigger: 
            d_hlt_syst[('hlt', trg, '000')] = None
            d_hlt_syst[('hlt', trg, 'all')] = None
            d_hlt_syst[('hlt', trg, 'nom')] = None

        self._d_syst.update(d_hlt_syst)
    #------------------------------
    def _add_qsq_syst(self):
        d_qsq_syst = {}

        for trg in ['MTOS', 'ETOS', 'GTIS']:
            for sys in ['000', 'nom', 'all']:
                d_qsq_syst[('qsq',  trg,  sys)] = None

        self._d_syst.update(d_qsq_syst)
    #------------------------------
    def _add_trk_syst(self):
        d_trk_syst = {}

        for trg in ['MTOS', 'ETOS', 'GTIS']:
            d_trk_syst[ ('trk', trg, '000') ] = None
            d_trk_syst[ ('trk', trg, 'all') ] = None
            d_trk_syst[ ('trk', trg, 'nom') ] = None

        self._d_syst.update(d_trk_syst)
    #------------------------------
    def _add_bts_syst(self):
        d_bts_syst = {}

        for trg in ['gen', 'KEE', 'KMM', 'MTOS', 'ETOS', 'GTIS']:
            d_bts_syst[ ('bts', trg, 'nom') ] = None
            d_bts_syst[ ('bts', trg, 'all') ] = None

        self._d_syst.update(d_bts_syst)
    #------------------------------
    def _add_bdt_syst(self):
        d_bdt_syst = {}

        for trg in ['gen', 'KEE', 'KMM', 'MTOS', 'ETOS', 'GTIS']:
            d_bdt_syst[ ('bdt', trg, 'nom') ] = None
            d_bdt_syst[ ('bdt', trg, '000') ] = None

        self._d_syst.update(d_bdt_syst)
    #------------------------------
    def _add_dcm_syst(self):
        d_gen_syst = {}

        for treename in self._l_treename:
            d_gen_syst[ ('dcm', treename, '000') ] = None
            d_gen_syst[ ('dcm', treename, 'all') ] = None
            # d_gen_syst[ ('dcm', treename, 'nom') ] = None

        self._d_syst.update(d_gen_syst)
    #------------------------------
    def __setitem__(self, sys, value):
        '''Configure weight reader

        Parameters
        --------------------
        sys (str): Specifies kind of weight, e.g. gen, pid, qsq, lzr...

        value (tuple): Specifies the version of the weights and the systematic, e.g. ('v22', 'nom')
        '''

        if sys not in self._l_supported_weight:
            self.log.error(f'Weight {sys} is not supported')
            self.log.info(self._l_supported_weight)
            raise

        try:
            _, sys_set = value
        except:
            self.log.error(f'Value for key {key} is {value}, expected tuple (version, systematic)')
            raise

        self._check_sys(sys, sys_set)
        self._d_wgt_ver[sys] = value
    #------------------------------
    def _check_sys(self, sys, sys_set):
        tp_sys = (sys, self._treename, sys_set)

        if tp_sys not in self._d_syst:
            self.log.error(f'{tp_sys} setting not allowed by:')
            for wgt, trg, sys in self._d_syst:
                if trg != self._treename:
                    continue
                self.log.info(f'{wgt:<10}{trg:<10}{sys:<10}')
            raise
    #----------------------------------------------
    def _add_df_cols(self):
        l_col = self._df.GetColumnNames()
        if 'B_TRUEETA' not in l_col:
            df       = self._df.Define('B_TRUEETA', 'TVector3 b(B_TRUEP_X, B_TRUEP_Y, B_TRUEP_Z); return b.Eta();')
            self._df = self._man_df.add_atr(df)
    #----------------------------------------------
    def _get_kin_dir(self):
        try:
            self._kin_dir = os.environ['CALDIR']
            self.log.info(f'Using calibration path: {self._kin_dir}')
        except:
            self.log.error(f'Cannot find directory with calibration maps in {CALDIR}')
            raise
    #----------------------------------------------
    def _check_valdir(self):
        if self.valdir is not None and not os.path.isdir(self.valdir):
            try:
                self.log.info('Making validation directory: ' + self.valdir)
                utnr.make_dir_path(self.valdir)
            except:
                self.log.info('Could not make validation directory: ' + self.valdir)
                raise
    #----------------------------------------------
    def _check_qsq(self):
        self._check_sel_quant('qsq')

        if not self._after_sel: 
            return

        _, sys_set = self._d_wgt_ver['qsq']

        if sys_set != '000' and self._treename == 'MTOS':
            self.log.error(f'Using setting {sys_set} for q2 weights and trigger {self._treename}, only setting "0" can be used.')
            raise
    #----------------------------------------------
    def _check_sel_quant(self, quant):
        if  not self._after_sel and quant in self._d_wgt_ver:
            self.log.error(f'Selection weight, {quant}, specified for trigger {self._treename} (before selection)')
            raise

        if self._after_sel and quant not in self._d_wgt_ver:
            self.log.error(f'Selection weight, {quant}, not specified for trigger {self._treename}')
            utnr.pretty_print(self._d_wgt_ver)
            raise
    #----------------------------------------------
    def _find_mode(self):
        try:
            arr_jpsi_id = self._df.AsNumpy(['Jpsi_TRUEID'])['Jpsi_TRUEID']
        except:
            self.log.error('Cannot read "Jpsi_TRUEID" from')
            self.log.error('{0:<20}{1:<100}'.format('Filepath', self._filepath))
            self.log.error('{0:<20}{1:<100}'.format('Tree'    , self._treename))
            raise

        arr_jpsi_id = numpy.absolute(arr_jpsi_id)

        if   numpy.all(arr_jpsi_id ==    443):
            self._mode = 'jpsi'
        elif numpy.all(arr_jpsi_id == 100443):
            self._mode = 'psi2'
        elif numpy.all(arr_jpsi_id ==    521):
            self._mode = 'high'
        else:
            #Rare mode needs to be implemented
            self.log.error('Unsuppored channel for dilepton ID:')
            print(arr_jpsi_id)
            raise
    #----------------------------------------------
    def _get_kin_path(self, kind, ver, sys_set):
        """
        Will build path to efficiency maps and check if they exist
        Will return path to pickle or ROOT file 
        """
        binning = '3'     if sys_set in self._l_occ else '1'
        end_nam = sys_set if sys_set in self._l_occ else 'nom'

        if   kind == 'gen':
            trigger = 'MTOS'  if sys_set in self._l_occ else sys_set
            pref_path = f'{self._kin_dir}/{kind}/{ver}.{binning}/{trigger}_{self._year}_{kind}_{end_nam}'
        elif kind in ['rec', 'bdt']:
            trigger = sys_set if sys_set in self._l_trg else self._trigger 
            pref_path = f'{self._kin_dir}/{kind}/{ver}.{binning}/{trigger}_{self._year}_{kind}_{end_nam}'
        else:
            log.error(f'Invalid kind: {kind}')
            raise

        if   os.path.isfile(f'{pref_path}.root'):
            path = f'{pref_path}.root' 
        elif os.path.isfile(f'{pref_path}.pickle'):
            path = f'{pref_path}.pickle' 
        else:
            self.log.error(f'Neither ROOT nor pickle file found: {pref_path}.(root|pickle)')
            raise

        self.log.debug(f'Picking up {kind} weights from: {path}')

        return path
    #----------------------------------------------
    def _get_wgt_args(self, kind, ver, sys_set):
        if   kind in ['gen', 'rec', 'bdt']:
            wgt_path = self._get_kin_path(kind, ver, sys_set)
        elif kind == 'qsq':
            wgt_path = f'{self._kin_dir}/{kind}/{ver}.{sys_set}'
        elif kind in ['lzr', 'hlt']:
            wgt_path = f'{self._kin_dir}/trg/{ver}.1'
            tp_tag   = tuple(sys_set.split('.'))
        elif kind == 'pid':
            wgt_path = f'{self._kin_dir}/{kind}/{ver}/{sys_set}'
        elif kind == 'trk':
            wgt_path = f'{self._kin_dir}/{kind}/{ver}.{sys_set}'
        elif kind == 'dcm':
            wgt_path = f'/afs/ihep.ac.cn/users/x/xzh6313/xzh/RK/dev_zhihao/q2_model/test/json/{ver}'
        else:
            self.log.error(f'Unsupported weight kind/sys: {kind}/{sys_set}')
            raise

        wgt_path = wgt_path.replace(' ', '')

        if kind == 'lzr':
            self._d_wgt_pat[f'{kind}_{sys_set}'] = [wgt_path, tp_tag]
            return tp_tag, wgt_path
        else:
            self._d_wgt_pat[f'{kind}_{sys_set}'] = wgt_path
            return wgt_path
    #------------------------------
    def _is_data_hist(self, hist):
        name = hist.GetName() 

        if   name == 'h_data' or name.startswith('h_num'):
            return True
        elif name == 'h_ctrl' or name.startswith('h_den'):
            return False 
        else:
            self.log.error('Histogram is neither data nor MC:')
            hist.Print()
            raise
    #------------------------------
    def _get_kin_hist(self, path):
        '''Get numerator and denominator histograms from ROOT file in path'''
        utnr.check_file(path)

        ifile = ROOT.TFile(path)
        l_key = ifile.GetListOfKeys()
        h_1, h_2 = [ key.ReadObj() for key in l_key]

        h_num = h_1 if self._is_data_hist(h_1) else h_2
        h_den = h_2 if self._is_data_hist(h_1) else h_1

        h_num.SetDirectory(0)
        h_den.SetDirectory(0)

        ifile.Close()

        return [h_num, h_den]
    #------------------------------
    def _get_hist_gen_rwt(self, wgt_path):
        h_num, h_den = self._get_kin_hist(wgt_path)

        obj   = osc()
        h_num = obj.get_oscillated_map('num', h_num)
        h_den = obj.get_oscillated_map('den', h_den)

        rwt = hr(dt=h_num, mc=h_den)

        return rwt
    #------------------------------
    def _get_kin_weights(self, kind, ver, sys_set):
        self.log.info(f'Calculating {kind} weights for systematic {sys_set}')
        wgt_path=self._get_wgt_args(kind, ver, sys_set)

        if   wgt_path.endswith('.root'):
            self.log.info(f'Reading {kind} weights from histograms')
            rwt = self._get_hist_gen_rwt(wgt_path)
        else:
            self.log.info(f'Reading {kind} weights from hep_ml BDT')
            rwt = utnr.load_pickle(wgt_path) 

        occ_var=utnr.get_from_dic(self._d_sys_occ, sys_set)
        if   kind == 'gen':
            arr_val=utils.getMatrix(self._df, ['B_TRUEPT', 'B_TRUEETA', occ_var])
        elif kind == 'rec':
            arr_val=utils.getMatrix(self._df, ['log(B_ENDVERTEX_CHI2)', 'log(B_IPCHI2_OWNPV)', 'TMath::ACos(B_DIRA_OWNPV)'])
        elif kind == 'bdt':
            arr_val=utils.getMatrix(self._df, ['BDT_cmb', 'BDT_prc', occ_var])
        else:
            self.log.error(f'Invalid kind: {kind}')
            raise

        arr_wgt = rwt.predict_weights(arr_val)
        #arr_wgt = utnr.normalize_weights(arr_wgt, kind='area')

        return arr_wgt
    #------------------------------
    def _get_pid_sim(self):
        self.log.info(f'Calculating PID weights from simulation')

        l_col_name = self._df.GetColumnNames()
        if 'pid_sim' not in l_col_name:
            pid_sel  = rs.get('pid', self._treename, q2bin=self._mode, year = self._year)
            self.log.info(f'Defining pid_sim as: {pid_sel} == 1')
            df = self._df.Define('pid_sim', f'{pid_sel} == 1')
        else:
            self.log.info(f'pid_sim found')
            df = self._df

        arr_wgt = df.AsNumpy(['pid_sim'])['pid_sim']
        arr_wgt = arr_wgt.astype(int)

        wgt_sum = numpy.sum(arr_wgt)
        wgt_len = len(arr_wgt)

        if wgt_sum >= wgt_len:
            self.log.error(f'Weight sum is larger or equal than number of weights: {wgt_sum} >= {wgt_len}')
            self.log.error(f'Filename: {self._filepath}[{self._treename}]')
            raise

        return arr_wgt
    #------------------------------
    def _get_pid_weights(self, ver, sys_set):
        self.log.info(f'Calculating PID weights for systematic {sys_set}')

        dirpath = self._get_wgt_args('pid', ver, sys_set)

        reweighter=pidrd()
        reweighter.setMapPath(dirpath)
        arr_pid_l1, arr_pid_l2, arr_pid_hd=reweighter.predict_weights(self._df, replica=self.replica)

        self._plot_wgt(f'pid_lp1_{sys_set}', {sys_set : arr_pid_l1             })
        self._plot_wgt(f'pid_lp2_{sys_set}', {sys_set : arr_pid_l2             })
        self._plot_wgt(f'pid_lep_{sys_set}', {sys_set : arr_pid_l1 * arr_pid_l2})
        self._plot_wgt(f'pid_had_{sys_set}', {sys_set : arr_pid_hd             })

        self.d_storage['pid'] = reweighter.storage
        arr_wgt = arr_pid_l1 * arr_pid_l2 * arr_pid_hd

        return arr_wgt
    #------------------------------
    def _get_lzr_weights(self, ver, sys_set):
        self.log.info(f'Calculating L0 weights for systematic {sys_set}')

        tp_tag, wgt_dir = self._get_wgt_args('lzr', ver, sys_set)

        reweighter=trgrd(self._year, wgt_dir)
        arr_wgt = reweighter.predict_weights(tp_tag, self._df, replica=self.replica) 

        return arr_wgt
    #------------------------------
    def _get_hlt_rwt(self, mappath):
        ifile = ROOT.TFile(mappath)
        h_pas_dat = ifile.h_data_pass
        h_fal_dat = ifile.h_data_fail
        h_pas_sim = ifile.h_sim_pass
        h_fal_sim = ifile.h_sim_fail

        h_pas_dat.SetDirectory(0)
        h_fal_dat.SetDirectory(0)
        h_pas_sim.SetDirectory(0)
        h_fal_sim.SetDirectory(0)

        title = h_pas_dat.GetTitle()
        if title == '':
            xvar, yvar = 'B_PT', 'B_ETA'
        else:
            regex= '(.*):(.*)'
            mtch = re.match(regex, title)
            if not mtch:
                log.error(f'Cannot extract variables from title {title} with {regex}')
                raise
            xvar = mtch.group(1)
            yvar = mtch.group(2)

        ifile.Close()

        obj       = osc()
        h_pas_dat = obj.get_oscillated_map('h_pas_dat', h_pas_dat)
        h_fal_dat = obj.get_oscillated_map('h_fal_dat', h_fal_dat)
        h_pas_sim = obj.get_oscillated_map('h_pas_sim', h_pas_sim)
        h_fal_sim = obj.get_oscillated_map('h_fal_sim', h_fal_sim)

        rwt = hist_map()
        rwt.add_hist(h_pas_dat, h_fal_dat, data=True)
        rwt.add_hist(h_pas_sim, h_fal_sim, data=False)

        rwt.xvar = xvar
        rwt.yvar = yvar

        return rwt
    #----------------------------------------------
    def _get_hlt_weights(self, ver, sys_set):
        self.log.info(f'Calculating HLT weights for systematic {sys_set}')

        dirpath     = self._get_wgt_args('hlt', ver, sys_set)
        mappath     = f'{dirpath}/HLT_{self._treename}_{self._year}.root'
        rwt         = self._get_hlt_rwt(mappath)

        d_data    = self._df.AsNumpy([rwt.xvar, rwt.yvar])
        arr_pt    = d_data[rwt.xvar]
        arr_et    = d_data[rwt.yvar]
        arr_point = numpy.array([arr_pt, arr_et]).T

        arr_eff     = rwt.get_efficiencies(arr_point) 

        arr_eff_dat = arr_eff.T[0]
        arr_eff_sim = arr_eff.T[1]

        arr_wgt = arr_eff_dat / arr_eff_sim

        return arr_wgt
    #----------------------------------------------
    def _get_qsq_weights(self, ver, sys_set, smear=True):
        self.log.info(f'Calculating Q2 weights for systematic {sys_set}')

        treename=self._df.treename
        #-------------------------
        if smear:
            q2dir=self._get_wgt_args('qsq', ver, sys_set)
            smr=q2smear(self._df, q2dir)
            smr.out_dir = f'{self.valdir}/q2smearing/{sys_set}'
            self.log.visible(f'Applying q2 smearing for trigger/systematic: {treename}/{sys_set}')
            storage=smr.storage

            arr_smr=smr.get_q2_smear(self.replica)
        else:
            arr_smr = self._df.AsNumpy(['Jpsi_M'])['Jpsi_M']
            storage=collector()
        #-------------------------

        q2_sel  = rs.get('q2', self._treename, q2bin=self._mode, year = self._year)
        q2_sel  = q2_sel.replace('&&', '&')

        arr_wgt = numexpr.evaluate(q2_sel, {'Jpsi_M' : arr_smr})

        arr_wgt = arr_wgt.astype(float)

        self._check_eff(arr_wgt, q2_sel, max_eff=0.999, min_eff=0.900)
        #-------------------------
        storage.add('qsq_jpsi_mass_smr', arr_smr)
        storage.add('qsq_jpsi_mass_wgt', arr_wgt)

        self.d_storage['qsq'] = storage
        #-------------------------

        return arr_wgt
    #------------------------------
    def _get_trk_weights(self, ver, sys_set):
        self.log.info(f'Calculating TRK weights for systematic {sys_set}')

        rdr                    = trard()
        dirpath                = self._get_wgt_args('trk', ver, sys_set)
        rdr.setMapPath(dirpath)
        wgt_l1, wgt_l2         = rdr.getWeight(self._df)
        self._d_wgt_pat[f'trk_{sys_set}'] = rdr.maps

        arr_wgt = numpy.multiply(wgt_l1, wgt_l2) 

        return arr_wgt
    #------------------------------
    def _get_dcm_weights(self, ver, sys_set):
        self.log.info(f'Calculating alternative decay model weights for systematic {sys_set}')

        rdr          = dcmrd()
        dirpath      = self._get_wgt_args('dcm', ver, sys_set)
        rdr.map_path = dirpath
        wgt          = rdr.get_target_weight(self._df)

        self._d_wgt_pat[f'dcm_{sys_set}'] = rdr.map_path

        return wgt 
    #------------------------------
    def _get_bts_weights(self, version, syst):
        rdr = btsrd()
        rdr.setYear(self._year)
        arr_wgt = rdr.getWeight(self._df, syst)

        return arr_wgt
    #------------------------------
    def _get_weights(self, kind, ver, sys_set):
        self.log.visible(f'Getting {kind} weights')

        l_syst = self._get_syst(kind, sys_set)

        if   kind not in ['pid', 'qsq'] and sys_set == '000':
            d_arr_wgt = {'000' : numpy.ones(self._size)}
        elif kind == 'pid'              and sys_set == '000': 
            d_arr_wgt = {'000' : self._get_pid_sim() }
        elif kind == 'qsq'              and sys_set == '000':
            d_arr_wgt = {'000' : self._get_qsq_weights(ver, sys_set, smear=False)}
        #----------------------------
        elif kind in ['gen', 'rec', 'bdt']:
            d_arr_wgt = { syst : self._get_kin_weights(kind, ver, syst) for syst in l_syst}
        elif kind == 'lzr':
            d_arr_wgt = { syst : self._get_lzr_weights(      ver, syst) for syst in l_syst}
        elif kind == 'hlt':
            d_arr_wgt = { syst : self._get_hlt_weights(      ver, syst) for syst in l_syst}
        elif kind == 'pid': 
            d_arr_wgt = { syst : self._get_pid_weights(      ver, syst) for syst in l_syst}
        elif kind == 'qsq':
            d_arr_wgt = { syst : self._get_qsq_weights(      ver, syst) for syst in l_syst}
        elif kind == 'trk':
            d_arr_wgt = { syst : self._get_trk_weights(      ver, syst) for syst in l_syst}
        elif kind == 'dcm':
            d_arr_wgt = { syst : self._get_dcm_weights(      ver, syst) for syst in l_syst}
        elif kind == 'bts':
            d_arr_wgt = { syst : self._get_bts_weights(      ver, syst) for syst in tqdm.tqdm(l_syst, ascii=' -')} 
        #----------------------------
        else:
            self.log.error(f'Wrong kind or setting: {kind}/{sys_set}')
            raise

        for syst, arr_wgt in d_arr_wgt.items():
            self._check_weights(arr_wgt, kind, syst)

        self._plot_wgt(kind, d_arr_wgt)
        #self._add_stat(kind, d_arr_wgt)

        return d_arr_wgt 
    #------------------------------
    def _add_stat(self, kind, d_arr_wgt):
        keys    = d_arr_wgt.keys()
        nom_key = list(keys)[0]
        arr_wgt = d_arr_wgt[nom_key]
        if self._arr_wgt_cur is None:
            self._arr_wgt_cur  = arr_wgt
        else:
            self._arr_wgt_cur *= arr_wgt 

        try:
            nwgt = arr_wgt.size
            nz   = 100. * numpy.count_nonzero(arr_wgt       < 1e-5) / nwgt 
            nn   = 100. * numpy.count_nonzero(numpy.isnan(arr_wgt)) / nwgt 
            ni   = 100. * numpy.count_nonzero(numpy.isinf(arr_wgt)) / nwgt 
        except:
            self.log.error(f'Could not extract information from kind: {kind}')
            print(arr_wgt)
            raise

        sum_wgt = numpy.sum(arr_wgt)
        cum_wgt = numpy.sum(self._arr_wgt_cur)

        l_val = [kind, f'{sum_wgt:.0f}', f'{cum_wgt:.0f}', f'{nz:.3f}', f'{nn:.3f}', f'{ni:.3f}'] 

        self._df_stat = utnr.add_row_to_df(self._df_stat, l_val)
    #------------------------------
    def _calculate_weights(self):
        '''Calculates dictionary of arrays of weights

        It will build a dictionary like:

        {weight_kind -> dic}

        where:

        dic = {systematic : array_of_weights}
        '''
        d_d_arr_wgt = {}
        for kind, (ver, sys) in self._d_wgt_ver.items():
            d_d_arr_wgt[kind] = self._get_weights(kind, ver, sys)

        self._d_d_arr_wgt= {kind : d_d_arr_wgt[kind] for kind in self._l_supported_weight if kind in d_d_arr_wgt}
    #----------------------------------------------
    def _check_eff(self, arr_wgt, sel, min_eff = 0.10, max_eff = 0.99):
        eff = numpy.sum(arr_wgt) / float(arr_wgt.size)

        if  (eff > 0.00 and eff < min_eff) or (eff > max_eff and eff < 1.00):
            self.log.warning('{0:<20}{1:40.3e}'.format('Efficiency', eff))
            self.log.warning('{0:<20}{1:40}'.format('Selection' , sel))
            self.log.warning(self._filepath)
        elif eff <= 0.00 or eff >  1.00:
            self.log.error('{0:<20}{1:40.3e}'.format('Efficiency', eff))
            self.log.error('{0:<20}{1:40}'.format('Selection' , sel))
            self.log.error(self._filepath)

            d_freq = collections.Counter(arr_wgt)
            nzero  = d_freq[0.]
            nones  = d_freq[1.]

            self.log.error('{0:<20}{1:40}'.format('Fail freq' , nzero))
            self.log.error('{0:<20}{1:40}'.format('Pass freq' , nones))

            raise
        else:
            self.log.debug('{0:<20}{1:40.3e}'.format('Efficiency', eff))
            self.log.debug('{0:<20}{1:40}'.format('Selection' , sel))
    #------------------------------
    def _get_syst(self, kind, sys_set):
        if   kind == 'gen':
            l_sys = ['MTOS', 'GTIS_mm', 'npv', 'nsp']
        #---------------------
        elif kind == 'rec' and self._trigger == 'MTOS':
            l_sys = ['MTOS', 'GTIS_mm']
        elif kind == 'rec' and self._trigger == 'ETOS':
            l_sys = ['ETOS', 'GTIS_ee']
        elif kind == 'rec' and self._trigger == 'GTIS':
            l_sys = ['GTIS', 'ETOS_ee']
        #---------------------
        elif kind == 'pid' and self._treename in ['ETOS', 'GTIS']:
            #l_sys = ['nom', 'kpelbin1', 'kpelbin2', 'kpelbin3', 'kpelbin4', 'kpeltis', 'elbin1', 'eltis']
            l_sys = ['nom', 'kpelbin1', 'kpelbin2', 'elbin1', 'elbin2']
            self.log.warning(f'Not using all PID systematics for electron')
            if sys_set == 'all':
                pass
            elif sys_set in l_sys[1:]:
                l_sys = [sys_set]
            elif sys_set in ['nom', '000']:
                l_sys = [sys_set]
            else:
                self.log.error(f"PID systematic option {sys_set} is not supported.")
        elif kind == 'pid' and self._treename == 'MTOS':
            #l_sys = ['nom', 'kpmubin1', 'kpmubin2', 'kpmubin3', 'kpmubin4', 'kpmutis', 'mubin1', 'mubin2', 'mubin3', 'mubin4', 'mu_tis']
            l_sys = ['nom', 'kpmubin1', 'kpmubin2', 'mubin1', 'mubin2']
            self.log.warning(f'Not using all PID systematics for muon')
            if sys_set == 'all':
                pass
            elif sys_set in l_sys[1:]:
                l_sys = [sys_set]
            elif sys_set in ['nom', '000']:
                l_sys = [sys_set]
            else:
                self.log.error(f"PID systematic option {sys_set} is not supported.")
        #---------------------
        elif kind == 'lzr' and self._treename == 'MTOS':
            l_sys = ['L0MuonTIS', 'L0MuonHAD', 'L0MuonMU1']
        elif kind == 'lzr' and self._treename == 'ETOS':
            l_sys = ['L0ElectronTIS', 'L0ElectronHAD', 'L0ElectronFAC']
        elif kind == 'lzr' and self._treename == 'GTIS':
            l_tag_1 = ['L0TIS_EMMH.L0HadronElEL.L0ElectronTIS', 'L0TIS_MMMH.L0HadronElEL.L0ElectronTIS', 'L0TIS_EMBN.L0HadronElEL.L0ElectronTIS']
            l_tag_2 = ['L0TIS_EMMH.L0HadronElEL.L0ElectronHAD', 'L0TIS_EMMH.L0HadronElEL.L0ElectronFAC']

            l_sys = l_tag_1 + l_tag_2
        #---------------------
        elif kind == 'hlt':
            l_sys = [self._treename]
        #---------------------
        elif kind == 'trk':
            l_sys = ['nom']
        #---------------------
        elif kind == 'dcm':
            l_sys = ['nom', 'BSZ']
            if sys_set == 'all':
                pass
            elif sys_set == 'nom':
                l_sys = ['000']
        #---------------------
        elif kind == 'qsq':
            #l_sys = ['nom', 'lsh', 'mom', 'trg']
            l_sys = ['nom', 'mom']
            self.log.warning('Not using all systematics for q2')
        #---------------------
        elif kind == 'bts':
            l_sys = list(range(self._nboots)) 
        #---------------------
        elif kind == 'bdt':
            l_sys = ['nom']
        #---------------------
        else:
            self.log.error(f'Invalid kind: {kind}')
            raise

        if sys_set == 'nom':
            l_sys = l_sys[:1]

        return l_sys
    #------------------------------
    def _plot_wgt(self, kind, d_arr_wgt):
        if   self.valdir is None: 
            return 

        plot_path=f'{self.valdir}/{kind}_{self._treename}.png'

        if   kind.startswith('pid'):
            yrange = 0, 1
            nbins  = 100
        elif kind.startswith('bts'):
            yrange = 0, 10
            nbins  = 10
        elif kind.startswith('hlt'):
            yrange = 0.75, 1.25
            nbins  = 100
        elif kind.startswith('qsq'):
            yrange = 0, 2
            nbins  = 2 
        else:
            yrange = 0, 2
            nbins  = 100

        if kind == 'bts' and len(d_arr_wgt) > 5:
            l_key = random.sample(d_arr_wgt.keys(), 5)
            d_tmp = {key : d_arr_wgt[key] for key in l_key}
            d_arr_wgt = d_tmp

        for sys, arr_wgt in d_arr_wgt.items():
            plt.hist(arr_wgt, range=yrange, bins=nbins, histtype='step', label=sys)

        key  = kind if not kind.startswith('pid_') else 'pid'
        if key == 'total':
            vers = 'total'
        else:
            vers = self._d_wgt_ver[key]

        plt.xlabel('Weight')
        plt.ylabel('Entries')
        plt.title(f'{kind}; {vers}')
        plt.legend()
        plt.savefig(plot_path)
        plt.close('all')
    #------------------------------
    def _check_weights(self, arr_wgt, kind, sys):
        self._check_wgt_size(arr_wgt, kind, sys)
        arr_unique_wgt = numpy.unique(arr_wgt)
        if kind != 'bts' and len(arr_unique_wgt) == 1 and sys != '000':
            self.log.warning(f'For {kind} correction, systematic {sys} found only one weight: {arr_wgt[0]}')
    #------------------------------
    def _print_settings(self):
        l_str_sys = list(self._d_wgt_ver.keys())
        l_str_val = list(self._d_wgt_ver.values())

        self.log.visible('-' * 20)
        self.log.visible(f'Getting {self._kind} weights for')
        self.log.visible('-' * 20)
        self.log.visible(f'{"Mode":<15}{str(self._mode):<50}') 
        self.log.visible(f'{"Tree":<15}{self._treename :<50}') 
        self.log.visible(f'{"Year":<15}{self._year     :<50}') 
        self.log.visible('-' * 20)
        for sys, val in zip(l_str_sys, l_str_val):
            sys = str(sys)
            val = str(val)
            self.log.visible(f'{sys:<15}{val:<50}')
    #------------------------------
    def _check_wgt_size(self, arr_wgt, kind, syst):
        size_arr = numpy.size(arr_wgt, axis=0)
        if size_arr != self._size:
            self.log.error(f'Weights of kind/syst {kind}/{syst} are not compatible with input data')
            self.log.error(f'{"Weight size":<20}{size_arr:<20}')
            self.log.error(f'{"Data size  ":<20}{self._size:<20}')
            raise
    #------------------------------
    def _save(self):
        self.storage.add('weight_flow', self._df_stat)
        self._save_wf()
        self._save_paths()
    #------------------------------
    def _save_wf(self):
        if self.valdir is None:
            return

        table_path = f'{self.valdir}/stats_{self.identifier}_{self._treename}.tex'
        self._df_stat.style.to_latex(table_path)
    #------------------------------
    def _save_paths(self):
        if self.valdir is None:
            return

        pathspath=f'{self.valdir}/paths_{self.identifier}_{self._treename}.json'
        d_info             = {}
        d_info['versions'] = self._d_wgt_ver
        d_info['paths']    = self._d_wgt_pat

        utnr.dump_json(d_info, pathspath, sort_keys=True)
    #------------------------------
    def _get_ext_columns(self, l_ext_col):
        if len(l_ext_col) == 0:
            d_data = {}
        else:
            self.log.info('Adding extra columns')
            utils.check_df_has_columns(self._df, l_ext_col)
            d_data = self._df.AsNumpy(l_ext_col)

        return d_data
    #------------------------------
    def _multiply_arrays(self, d_arr_wgt):
        '''Multiply arrays and return summary of where zeros are introduced
        '''
        arr_wgt_tot = None

        self.log.info('-' * 20)
        self.log.info(f'{"Weight":<20}{"#Zeros":>20}')
        self.log.info('-' * 20)

        d_zeros = {}
        for name, arr_wgt in d_arr_wgt.items():
            if arr_wgt_tot is None:
                arr_wgt_tot = arr_wgt
            else:
                arr_wgt_tot = arr_wgt * arr_wgt_tot

            nzero = numpy.count_nonzero(arr_wgt_tot == 0)

            self.log.info(f'{name:<20}{nzero:>20}')
            d_zeros[name] = nzero

        return arr_wgt_tot, d_zeros
    #------------------------------
    def _multiply_weights(self):
        #Build dictionary of nominal (first among arrays for each kind) weights
        d_arr_wgt_nom = {} 
        for wgt, d_arr_wgt in self._d_d_arr_wgt.items():
            l_arr_wgt = list(d_arr_wgt.values())
            try:
                arr_wgt_nom = l_arr_wgt[0]
            except:
                self.log.error(f'For {wgt} correction, cannot extract any weights')
                utnr.pretty_print(self._d_d_arr_wgt)
                raise

            d_arr_wgt_nom[wgt] = arr_wgt_nom

        d_arr_wgt_sys_all = {}
        for wgt, d_arr_wgt in self._d_d_arr_wgt.items():
            d_arr_wgt_sys = self._multiply_syst(wgt, d_arr_wgt_nom, d_arr_wgt)
            d_arr_wgt_sys_all.update(d_arr_wgt_sys)

        arr_wgt, d_zeros         = self._multiply_arrays(d_arr_wgt_nom) 
        d_arr_wgt_sys_all['nom'] = arr_wgt

        self._d_arr_wgt_nom = d_arr_wgt_nom

        return d_arr_wgt_sys_all, d_zeros
    #------------------------------
    def _multiply_syst(self, wgt, d_arr_wgt_nom, d_arr_wgt):
        d_arr_wgt_sys = {}
        first         = True

        self.log.info(f'For {wgt}, systematics calculated:')
        for sys, arr_wgt_sys in d_arr_wgt.items():
            if first:
                first=False
                continue

            l_sys = [sys]
            arr_wgt_tot = numpy.copy(arr_wgt_sys)
            for key, arr_wgt_nom in d_arr_wgt_nom.items():
                if key == wgt:
                    continue

                l_sys.append(key)
                arr_wgt_tot = utnr.numpy_multiply(arr_wgt_tot, arr_wgt_nom, same_size=True)

            self._print_list(l_sys, col_width = 20)
            d_arr_wgt_sys[f'{wgt}_{sys}'] = arr_wgt_tot

        return d_arr_wgt_sys
    #------------------------------
    def _print_list(self, l_data, col_width = 20):
        line = f''
        for data in l_data:
            line += f'{data:<{col_width}}'
        self.log.info(line)
    #------------------------------
    def _skip_corr(self):
        '''Decides when to calculate correlations between weights
        Will calculate correlations between weights only:

        1. When doing selection weights
        2. When none of the weights are 1s, except for bootstrapping, q2 smearing and alternative decay model weight.
        3. no_corr has been set to True with obj.no_corr = True
        '''
        if self._no_corr:
            return True

        if self._kind != 'sel':
            return True 

        for wgt, (ver, sys) in self._d_wgt_ver.items():
            if wgt not in ['bts', 'qsq', 'dcm'] and sys == '000':
                return True 

        return False
    #------------------------------
    def _set_level(self):
        scor.log.setLevel(logging.WARNING)
        osc.log.setLevel(logging.WARNING)
        rs.log.setLevel(logzero.WARNING)
    #------------------------------
    def _calculate_correlations(self):
        if self._skip_corr():
            return

        self.log.visible(f'Calculating correlations for {self._kind} weights')

        d_d_arr_wgt_cor = dict()
        d_d_arr_wgt_cor.update(self._d_d_arr_wgt)

        try:
            del(d_d_arr_wgt_cor['bts'])
            del(d_d_arr_wgt_cor['qsq'])
            del(d_d_arr_wgt_cor['dcm'])
        except:
            self.log.error(f'Cannot remove bootstrapping and/or qsq keys from:')
            self.log.error(list(d_d_arr_wgt_cor.keys()))
            raise

        d_arr_wgt_nom = {}
        l_wgt = []
        for kind, d_arr_wgt in d_d_arr_wgt_cor.items():
            arr_wgt_nom = list(d_arr_wgt.values())[0]
            d_arr_wgt_nom[kind] = arr_wgt_nom
            l_wgt.append(kind)

        rdf = ROOT.RDF.FromNumpy(d_arr_wgt_nom)

        cor = scor(l_wgt, l_wgt, rdf)

        cor_dir = f'{self.valdir}/correlations'
        cor.save(cor_dir, title='weight correlations')
    #------------------------------
    def get_wgt_sys_fac(self, nested_dict = True):
        """
        Will return dictionary with kind of weight and systematic mapped to array of weights.

        Parameters
        -------------------------
        nested_dict (bool) : Bool that controls how dictionary is returned

        Returns
        -------------------------
        If nested_dict == True will return {kind : dict} dictionary, where kind is among ['gen', 'pid',...]
        and dict is {syst : arr_wgt} where syst is a systematic associated to a given kind.

        If nested_dict == False will return {kind, syst : arr_wgt} dictionary of ndict type
        """
        self._initialize()

        if nested_dict:
            return self._d_d_arr_wgt 

        nd_wgt = ndict()
        for kind, d_arr_wgt in self._d_d_arr_wgt.items():
            for syst, arr_wgt in d_arr_wgt.items():
                nd_wgt[kind, syst] = arr_wgt

        return nd_wgt
    #------------------------------
    def get_weights(self, l_ext_col=None):
        '''Provides dictionary of weights

        Parameters
        --------------------
        l_ext_col (list): List of variables that need to be added in form of arrays to the output dictionary

        Returns
        --------------------
        Dictionary {sys -> arr_wgt, var -> arr_val} where `sys` is a string symbolizing a systematics and arr_wgt is an array of
        correction weights, the product of all the kinds of corrections. 
        Optionally an array of values `arr_val` corresponding to the column (branch) `var` is added.
        '''
        self._initialize()

        d_wgt, self._d_zeros = self._multiply_weights()

        self._plot_wgt('total', d_wgt)

        return d_wgt
    #------------------------------
    def get_wgt_fac(self):
        '''
        Returns
        ------------------
        Dictionary {str -> arr_wgt} where str is type of weight and arr_wgt is the nominal weight
        '''
        if self._d_arr_wgt_nom is None:
            self.get_weights()

        d_fac = self._d_arr_wgt_nom
        if 'bts' not in d_fac:
            self.log.error(f'Not found bts entry in nominal weight dictionary:')
            print(d_fac.keys())
            raise

        del(d_fac['bts'])

        return d_fac
#------------------------------

