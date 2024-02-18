from logzero        import logger     as log
from rk.pidreader   import reader     as pidrdr
from rk.oscillator  import oscillator as osc
from rk.trackreader import reader     as trkrdr 

from hep_cl import hist_reader as hrdr

from version_management import get_last_version 

import os
import glob
import ROOT
import numpy
import utils
import uproot 
import logging
#------------------------------------------------------------
class calculator:
    def __init__(self, year=None, trigger=None, version=None):
        self._year = year
        self._trig = trigger
        self._vers = version

        self._caldir = None
        self._casdir = None
        self._rdf    = None

        self._d_map       = {} 
        self._d_wgt       = {} 

        self._arr_pid_wgt = None
        self._arr_trk_wgt = None

        self._initialized = False
    #------------------------------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._caldir = os.environ['CALDIR']
        self._casdir = os.environ['CASDIR']

        self._set_log_lvl()
        self._check_args()
        self._load_rdf()
        self._load_pid_wgt()
        self._load_trk_wgt()

        self._load_original_map('gen')

        self._initialized = True
    #------------------------------------------------------------
    def _set_log_lvl(self):
        pidrdr.log.setLevel(logging.WARNING)
        trkrdr.log.setLevel(logging.WARNING)
        osc.log.setLevel(logging.WARNING)
        utils.log.setLevel(logging.WARNING)
    #------------------------------------------------------------
    def _load_pid_wgt(self):
        pid_path = get_last_version(f'{self._caldir}/PID', version_only=False)
        pid_path = f'{pid_path}/nom'

        log.warning(f'Loading nominal PID from: {pid_path}')

        rdr=pidrdr()
        rdr.setMapPath(pid_path)
        arr_l1, arr_l2, arr_kp = rdr.predict_weights(self._rdf)

        self._arr_pid_wgt = arr_l1 * arr_l2 * arr_kp
    #------------------------------------------------------------
    def _load_trk_wgt(self):
        trk_path = get_last_version(f'{self._caldir}/TRK', version_only=False)

        log.warning(f'Loading nominal TRK from: {trk_path}')

        rdr = trkrdr()
        rdr.setMapPath(trk_path)
        arr_l1, arr_l2 = rdr.getWeight(self._rdf)

        self._arr_trk_wgt = arr_l1 * arr_l2
    #------------------------------------------------------------
    def _check_args(self):
        if self._year not in ['2011', '2012', '2015', '2016', '2017', '2018']:
            log.error(f'Invalid year: {self._year}')
            raise

        if self._trig not in ['MTOS', 'ETOS', 'GTIS']:
            log.error(f'Invalid trigger: {self._trig}')
            raise

        if self._vers not in ['v10.18is']:
            log.error(f'Invalid version: {self._vers}')
            raise
    #------------------------------------------------------------
    def _load_original_map(self, kind):
        map_dir = f'{self._caldir}/{kind}'
        map_path=get_last_version(dir_path=map_dir, version_only=False, main_only=True)

        if kind == 'gen':
            h_dat, h_sim = self._get_original_gen_map(map_path)

        self._d_map[kind] = h_dat, h_sim
    #------------------------------------------------------------
    def _get_original_gen_map(self, map_path):
        path_wc = f'{map_path}.1/MTOS_{self._year}*.root'
        l_path  = glob.glob(path_wc)
        if len(l_path) != 1:
            log.error(f'Not found one and only one file in {path_wc}')
            raise

        log.warning(f'Loading original, nominal, gen map: {l_path[0]}')

        ifile=ROOT.TFile(l_path[0])
        l_h_sim=[key.ReadObj() for key in ifile.GetListOfKeys() if key.GetName().startswith('h_den') ]
        l_h_dat=[key.ReadObj() for key in ifile.GetListOfKeys() if key.GetName().startswith('h_num') ]

        h_sim = l_h_sim[0]
        h_dat = l_h_dat[0]

        h_sim.SetDirectory(0)
        h_dat.SetDirectory(0)

        return h_dat, h_sim
    #------------------------------------------------------------
    def _get_gen_map(self):
        '''Creates gen histogram
        Returns
        ---------------
        TH3F with weighted (PID, TRK) entries
        '''
        _, h_sim  = self._d_map['gen'] 

        h_sim_cpy = h_sim.Clone()
        h_sim_cpy.Reset() 

        d_data = self._rdf.AsNumpy(['B_PT', 'B_ETA'])

        arr_pt, arr_et = d_data['B_PT'], d_data['B_ETA']
        arr_wt = self._arr_pid_wgt * self._arr_trk_wgt

        for pt, et, wt in zip(arr_pt, arr_et, arr_wt):
            h_sim_cpy.Fill(pt, et, 1, wt)

        return h_sim_cpy
    #------------------------------------------------------------
    def _load_gen_wgt(self, h_sim):
        h_dat, _       = self._d_map['gen']

        d_data         = self._rdf.AsNumpy(['B_PT', 'B_ETA'])
        arr_pt, arr_et = d_data['B_PT'], d_data['B_ETA']
        arr_on         = numpy.ones_like(arr_pt)
        arr_point      = numpy.array([arr_pt, arr_et, arr_on]).T

        rdr     = hrdr(dt=h_dat, mc=h_sim)
        arr_wgt = rdr.predict_weights(arr_point)

        self._d_wgt['gen'] = arr_wgt
    #------------------------------------------------------------
    def _get_lzr_map(self):
        return
    #------------------------------------------------------------
    def _get_hlt(self):
        return
    #------------------------------------------------------------
    def _get_rec(self):
        return
    #------------------------------------------------------------
    def _load_rdf(self):
        file_wc = f'{self._casdir}/tools/apply_selection/mc_maps/ctrl/{self._vers}/{self._year}_{self._trig}/*.root'

        log.info(f'Loading: {file_wc}:{self._trig}')

        self._rdf = ROOT.RDataFrame(self._trig, file_wc)
        self._rdf = self._rdf.Range(10000)

        self._rdf.treename = self._trig
    #------------------------------------------------------------
    def get_maps(self):
        self._initialize()

        h_gen = self._get_gen_map()
        self._load_gen_wgt(h_gen)

        h_lzr = self._get_lzr_map()
        h_hlt = self._get_hlt()
        h_rec = self._get_rec()

        return {'gen' : h_gen, 'lzr' : h_lzr, 'hlt' : h_hlt, 'rec' : h_rec}
#------------------------------------------------------------

