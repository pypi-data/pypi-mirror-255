import os
import numpy
import logging

from itertools  import combinations
from logzero    import logger  as log
from rk.wgt_mgr import wgt_mgr

#-------------------------------------
class check:
    """
    Description:

    This class is used to test the effect of systematic variations
    in the calibration maps on the calibration weights

    Attributes:

    cal_dir: If set, it will override the place where calibration maps are found.
    """
    #-------------------------------
    def __init__(self, rdf, out_dir):
        self._rdf     = rdf
        self._out_dir = out_dir

        self._file_path= None
        self._treename = None
        self._trigger  = None

        self._initialized = False
    #-------------------------------
    @property
    def cal_dir(self):
        return self._cal_dir

    @cal_dir.setter
    def cal_dir(self, value):
        if not os.path.isdir(value):
            log.error(f'Directory not found: {value}')
            raise FileNotFoundError

        os.environ['CALDIR'] = value
        log.warning(f'Using custom calibration directory: {value}')
    #-------------------------------
    def _initialize(self):
        if self._initialized:
            return

        try:
            os.makedirs(self._out_dir, exist_ok=True)
        except PermissionError:
            raise PermissionError(f'Cannot make: {self._out_dir}')

        self._file_path= self._get_atr('filepath')
        self._treename = self._get_atr('treename')
        self._trigger  = self._get_atr('trigger')

        self._initialized = True
    #-------------------------------
    def _get_atr(self, name):
        if not hasattr(self._rdf, name):
            raise AttributeError(f'Cannot find attribute: {name} in RDF')

        return getattr(self._rdf, name)
    #-------------------------------
    def _get_settings(self):
        d_set            = {}
        d_set['val_dir'] = self._out_dir 
        d_set['channel'] = 'electron'  if self._trigger == 'MTOS' else 'muon'
        d_set['replica'] = 0 
    
        d_set['bts_ver'] = 200
        d_set['bts_sys'] ='nom'
        d_set['pid_sys'] ='nom'
        d_set['bdt_sys'] ='nom'

        d_set['trk_sys'] ='all'
        d_set['gen_sys'] ='all'
        d_set['lzr_sys'] ='all'
        d_set['hlt_sys'] ='all'
        d_set['rec_sys'] ='all'
        d_set['qsq_sys'] ='all'
    
        return d_set
    #-------------------------------
    def _check_variations(self, kind, d_arr_wgt):
        """
        Will check if for a given kind of correction, two systematic variations have the same
        array of weights. If so, print a warning.
        """
        l_systema    = list(d_arr_wgt.keys())
        l_arr_wgt    = list(d_arr_wgt.values())

        l_tp_systema = list(combinations(l_systema, 2))
        l_tp_arr_wgt = list(combinations(l_arr_wgt, 2))

        for (syst_1, syst_2), (arr_wgt_1, arr_wgt_2) in zip(l_tp_systema, l_tp_arr_wgt):
            if numpy.array_equal(arr_wgt_1, arr_wgt_2):
                log.warning(f'Equal weights found for kind/syst: {kind}; {syst_1} <---> {syst_2}')
    #-------------------------------
    def run(self):
        self._initialize()

        d_set = self._get_settings()
        obj   = wgt_mgr(d_set)
        obj.log_lvl = logging.WARNING
        rsl   = obj.get_reader('sel', self._rdf)

        d_d_arr_wgt = rsl.get_wgt_sys_fac()
        rsl.get_weights()
        for kind, d_arr_wgt in d_d_arr_wgt.items():
            self._check_variations(kind, d_arr_wgt)
#-------------------------------------
