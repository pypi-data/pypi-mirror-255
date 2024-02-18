import os
import ROOT
import utils
import numpy
import logging
import logzero

import read_selection     as rs
import read_calibration   as rc
import version_management as vm

from rk.wgt_mgr          import wgt_mgr
from collector           import collector

from logzero import logger as log

#----------------------------------------
class cal_rdf:
    def __init__(self, pref, trig, year):
        self._pref = pref
        self._trig = trig
        self._year = year

        self._cal_sys    = None
        self._out_dir    = None
        self._cas_dir    = None
        self._dat_ver    = None
        self._l_weight   = None

        self._maxentries = -1 
        self._store      = collector() 

        self._initialized = False
    #----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._out_dir is None:
            log.error(f'out_dir attribute not set')
            raise
        else:
            log.info(f'Out dir: {self._out_dir}')

        if self._pref not in ['gen', 'rec', 'bdt']:
            log.error(f'Invalid preffix: {self._pref}')
            raise ValueError

        self._cas_dir = os.environ['CASDIR']

        #rs.log.setLevel(logzero.WARNING)
        #vm.log.setLevel(logzero.WARNING)

        self._initialized = True
   #----------------------------------------
    @property
    def weights(self):
        return self._l_weight

    @weights.setter
    def weights(self, value):
        self._l_weight = value
   #----------------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        self._out_dir = value
   #----------------------------------------
    @property
    def cal_sys(self):
        return self._cal_sys

    @cal_sys.setter
    def cal_sys(self, value):
        self._cal_sys = value
   #----------------------------------------
    @property
    def dat_ver(self):
        return self._dat_ver

    @dat_ver.setter
    def dat_ver(self, value):
        self._dat_ver = value
    #----------------------------------------
    @property
    def maxentries(self):
        return self._maxentries

    @maxentries.setter
    def maxentries(self, value):
        self._maxentries = value
    #----------------------------------------
    def _get_selection(self):
        d_cut = {}
        if   self._trig in ['MTOS', 'GTIS_mm']:
            d_cut['pid'] = rs.get('pid', 'MTOS', q2bin='jpsi', year = self._year)
        elif self._trig in ['ETOS', 'GTIS_ee', 'GTIS']:
            d_cut['pid'] = rs.get('pid', 'ETOS', q2bin='jpsi', year = self._year)
        else:
            log.error(f'Invalid trigger: {self._trig}')
            raise ValueError

        if   self._trig == 'GTIS_ee':
            trigger = 'GTIS'
            lzr     = 'gtis_inclusive'
            hl1     = 'hlt1'
            hl2     = 'hlt2'
        elif self._trig == 'GTIS_mm':
            trigger = 'MTOS'
            lzr     = 'gtis_inclusive'
            hl1     = 'Hlt1'
            hl2     = 'Hlt2'
        elif self._trig in ['ETOS', 'GTIS']:
            trigger = self._trig 
            lzr     = self._trig.lower()
            hl1     = 'hlt1'
            hl2     = 'hlt2'
        elif self._trig == 'MTOS':
            trigger = self._trig 
            lzr     = self._trig.lower()
            hl1     = 'Hlt1'
            hl2     = 'Hlt2'
        else:
            log.error(f'Invalid trigger: {self._trig}')
            raise ValueError
  
        if lzr == 'gtis_inclusive':
            d_cut['lzr' ] = rc.get(   lzr, year = self._year)
        else:
            d_cut['lzr' ] = rs.get(   lzr, self._trig, q2bin='jpsi', year = self._year)

        d_cut['hlt1'] = rs.get(hl1, trigger, q2bin='jpsi', year = self._year)
        d_cut['hlt2'] = rs.get(hl2, trigger, q2bin='jpsi', year = self._year)
   
        return d_cut
    #----------------------------------------
    def _filter_rdf(self, rdf, kind, is_sim=None):
        log.info('Filtering dataframe')
        d_cut = self._get_selection()

        if is_sim:
            del(d_cut['pid'])

        for key, cut in d_cut.items():
            rdf = rdf.Filter(cut, key)
            self._store[f'{key} cut {kind}'] = cut

        rep = rdf.Report()
        rep.Print()

        return rdf
    #----------------------------------------
    def _get_rdf_ysswt(self, kind, sweights):
        tree_name = 'KMM'        if self._trig in ['MTOS', 'GTIS_mm'] else 'KEE'
        sample    = f'{kind}_mm' if self._trig in ['MTOS', 'GTIS_mm'] else f'{kind}_ee'
        file_path = f'{os.environ["DATDIR"]}/{sample}/{self._dat_ver}/sweights_{sweights}/{self._year}.root'
        if not os.path.isfile(file_path):
            log.error(f'Cannot find: {file_path}')
            raise FileNotFoundError

        log.info(f'{kind}: {file_path}:{tree_name}')
        rdf = ROOT.RDataFrame(tree_name, file_path)
        rdf.tree_name = tree_name
        rdf.file_path = file_path 

        return rdf
    #----------------------------------------
    def _get_rdf_noswt(self, kind):
        file_wc   = f'{self._cas_dir}/tools/apply_selection/data_mc/{kind}/v10.21p2/{self._year}_{self._trig}/*.root'
        log.info(f'{kind}: {file_wc}:{self._trig}')
        rdf = ROOT.RDataFrame(self._trig, file_wc)
        rdf.tree_name = self._trig 
        rdf.file_path = file_wc

        return rdf
    #----------------------------------------
    def _get_rdf(self, kind, sweights):
        if sweights == 'none':
            rdf = self._get_rdf_noswt(kind)
        else:
            rdf = self._get_rdf_ysswt(kind, sweights)

        self._store[f'tree_name {kind}']   = rdf.tree_name
        self._store[f'file_path {kind}']   = rdf.file_path
        self._store[f'max_entries {kind}'] = self._maxentries 

        if self._maxentries > 0:
            totentries = rdf.Count().GetValue()
            log.warning(f'Using {self._maxentries}/{totentries}')
            rdf = rdf.Range(self._maxentries)

        rdf = self._add_weights(rdf, kind, sweights)

        return rdf
    #----------------------------------------
    def _add_weights(self, rdf, kind, sweights):
        if   kind == 'data' and sweights != 'none':
            wgt = f'sw_{self._trig}'
            rdf = rdf.Define('weight', wgt)
            log.info(f'Using data weight: {wgt}')
        elif kind == 'data' and sweights == 'none':
            wgt = '(1)'
            rdf = rdf.Define('weight', wgt)
            rdf = self._filter_rdf(rdf, kind, is_sim=False)
            log.info(f'Using data weight: {wgt}')
        else:
            rdf = self._filter_rdf(rdf, kind, is_sim=True)
            log.info(f'Adding calibration weights: {self._l_weight}')
            rdf = self._add_calibration_weights(rdf, 'weight')

        return rdf
    #----------------------------------------
    def _add_calibration_weights(self, rdf, wgt_name):
        if   self._trig == 'GTIS_ee':
            trigger = 'GTIS'
        elif self._trig == 'GTIS_mm':
            trigger = 'MTOS'
        else:
            trigger = self._trig

        rdf.filepath = 'no-path'
        rdf.treename = trigger 
        rdf.trigger  = trigger 
        rdf.year     = self._year

        d_set            = {}
        d_set['val_dir'] = f'{self._out_dir}/cal_wgt'
        d_set['replica'] = 0
        d_set['bts_ver'] ='10'
        d_set['bts_sys'] ='nom'
        d_set['pid_sys'] = self._cal_sys 
        d_set['trk_sys'] = self._cal_sys 
        if   self._pref == 'gen':
            pass
        elif self._pref == 'rec':
            d_set['gen_sys'] = self._cal_sys 
            d_set['lzr_sys'] = self._cal_sys 
            d_set['hlt_sys'] = self._cal_sys 
        elif self._pref == 'bdt':
            d_set['gen_sys'] = self._cal_sys 
            d_set['lzr_sys'] = self._cal_sys 
            d_set['hlt_sys'] = self._cal_sys 
            d_set['rec_sys'] = self._cal_sys 
        else:
            log.error(f'Invalid preffix: {self._pref}')
            raise ValueError

        obj         = wgt_mgr(d_set)
        obj.log_lvl = logging.WARNING
        rsl         = obj.get_reader('sel', rdf)
        nentries    = rdf.Count().GetValue()
        arr_cal     = self._get_cal_wgt(rsl, nentries)

        rdf = utils.add_df_column(rdf, arr_cal,  'weight', d_opt = {'exclude_re'  : 'tmva_.*'})

        return rdf
    #----------------------------------------
    def _get_cal_wgt(self, rsl, nentries):
        gen_syst, lzr_syst, hlt_syst = self._get_syst()

        arr_cal = numpy.ones(nentries) 
        if 'pid' in self._l_weight:
            log.debug('Adding PID weights')
            arr_cal = arr_cal * rsl('pid', self._cal_sys)

        if 'trk' in self._l_weight:
            log.debug('Adding TRK weights')
            arr_cal = arr_cal * rsl('trk', self._cal_sys)

        if 'gen' in self._l_weight:
            log.debug('Adding GEN weights')
            arr_cal = arr_cal * rsl('gen', gen_syst)

        if 'lzr' in self._l_weight:
            log.debug('Adding LZR weights')
            arr_cal = arr_cal * rsl('lzr', lzr_syst)

        if 'hlt' in self._l_weight:
            log.debug('Adding HLT weights')
            arr_cal = arr_cal * rsl('hlt', hlt_syst)

        return arr_cal
    #----------------------------------------
    def _get_syst(self):
        '''Will return systematic for L0 and GEN weights corresponding to _cal_sys [nom, 000]
        '''
        if   self._trig == 'GTIS_ee':
            trigger = 'GTIS'
        elif self._trig == 'GTIS_mm':
            trigger = 'MTOS'
        else:
            trigger = self._trig
            
        if   self._cal_sys == 'nom':
            gen_syst = 'MTOS'
        elif self._cal_sys == '000':
            gen_syst = '000'
        else:
            log.error(f'Invalid systematic: {self._cal_sys}')
            raise

        if   self._cal_sys == '000':
            lzr_syst = '000'
        elif trigger == 'MTOS':
            lzr_syst = 'L0MuonTIS'
        elif trigger == 'ETOS':
            lzr_syst = 'L0ElectronTIS'
        elif trigger == 'GTIS':
            lzr_syst = 'L0TIS_EMMH.L0HadronElEL.L0ElectronTIS'
        else:
            log.error(f'Invalid HLT tag: {trigger}')
            raise

        if   self._cal_sys == 'nom':
            hlt_syst = trigger 
        elif self._cal_sys == '000':
            hlt_syst = '000'
        else:
            log.error(f'Invalid systematic: {self._cal_sys}')
            raise

        return gen_syst, lzr_syst, hlt_syst
    #----------------------------------------
    def get_rdf(self, sweights=None):
        self._initialize()

        if sweights is None:
            log.error(f'No sweights specified')
            raise

        rdf_dt = self._get_rdf('data', sweights)
        rdf_mc = self._get_rdf('ctrl', sweights)

        self._store.save(f'{self._out_dir}/settings.json', sort_keys=True)

        return rdf_dt, rdf_mc 
#----------------------------------------

