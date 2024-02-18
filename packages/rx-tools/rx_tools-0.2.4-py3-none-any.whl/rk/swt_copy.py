from logzero import logger as log

import numpy
import utils

from atr_mgr import mgr as amgr

#-----------------------------
class copy:
    def __init__(self, src=None, tgt=None):
        self._rdf_src = src
        self._rdf_tgt = tgt
        self._smass   = 'mass_swt'

        self._amg_tgt = amgr(tgt)
    #-----------------------------
    def _add_columns(self, rdf):
        v_col = rdf.GetColumnNames()
        l_col = [ col.c_str() for col in v_col ]

        if self._smass not in l_col:
            rdf = rdf.Define(self._smass, 'B_const_mass_M[0]')
        else:
            log.error(f'Column {self._smass} already in dataframe')
            raise

        return rdf
    #-----------------------------
    def _extract_weights(self, wgt_name):
        log.info(f'Extracting {wgt_name} weights')

        rdf_src  = self._rdf_src.Filter(f'{wgt_name} != 0', 'no_zeros')
        rep      = rdf_src.Report()
        rep.Print()

        arr_mass = rdf_src.AsNumpy([self._smass])[self._smass]
        arr_wgt  = rdf_src.AsNumpy([wgt_name])[wgt_name]
        arr_dat  = numpy.array([arr_mass, arr_wgt]).T
        arr_dat  = arr_dat[arr_dat[:, 0].argsort()]

        return arr_dat
    #-----------------------------
    def _get_weights(self, arr_wgt_src, arr_mass_tgt):
        [arr_mass_src, arr_swt_src] = arr_wgt_src.T

        arr_ind = numpy.searchsorted(arr_mass_src, arr_mass_tgt, side='right')
        arr_ind = numpy.where(arr_ind < arr_swt_src.size, arr_ind, arr_swt_src.size - 1)

        arr_swt_tgt = arr_swt_src[arr_ind]

        return arr_swt_tgt
    #-----------------------------
    def attach_swt(self, l_wgt_name=None):
        self._rdf_src = self._add_columns(self._rdf_src)
        self._rdf_tgt = self._add_columns(self._rdf_tgt)

        arr_mass  = self._rdf_tgt.AsNumpy([self._smass])[self._smass]
        d_wgt_src = { wgt_name : self._extract_weights(wgt_name)          for wgt_name              in l_wgt_name }
        d_wgt_tgt = { wgt_name : self._get_weights(arr_wgt_src, arr_mass) for wgt_name, arr_wgt_src in d_wgt_src.items() }
        rdf       = utils.add_columns_df(self._rdf_tgt, d_wgt_tgt)

        return self._amg_tgt.add_atr(rdf)
#-----------------------------

