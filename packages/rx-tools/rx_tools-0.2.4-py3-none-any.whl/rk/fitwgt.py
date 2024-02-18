import utils_noroot      as utnr
import read_selection    as rs
import pandas            as pnd

import utils
import os
import re 
import ROOT
import numpy
import logging

from version_management  import get_last_version 
from importlib.resources import files
from hep_cl              import hist_reader as hr
from rk.fithst           import extractor

#----------------------------------------
class rwt(extractor):
    log=utnr.getLogger('rwt')
    #----------------------------------------
    @property
    def one_dim(self):
        return self._one_dim

    @one_dim.setter
    def one_dim(self, value):
        self._one_dim = value
    #----------------------------------------
    @property
    def maxentries(self):
        return self._maxentries

    @maxentries.setter
    def maxentries(self, value):
        self._maxentries = value
    #----------------------------------------
    @property
    def wgt_ver(self):
        return self._wgt_ver

    @wgt_ver.setter
    def wgt_ver(self, value):
        self._wgt_ver = value
    #----------------------------------------
    @property
    def set_dir(self):
        return self._set_dir

    @set_dir.setter
    def set_dir(self, value):
        self._set_dir = value
    #----------------------------------------
    @property
    def wgt_dir(self):
        return self._wgt_dir

    @wgt_dir.setter
    def wgt_dir(self, value):
        self._wgt_dir = value
    #----------------------------------------
    def __init__(self, dt=None, mc=None):
        self._rdf_dt      = dt
        self._rdf_mc      = mc 

        self._preffix     = None 
        self._out_id      = None
        self._set_key     = None
        self._root_dir    = None
        self._root_path   = None
        self._set_dir     = None
        self._wgt_dir     = None
        self._wgt_ver     = None
        self._bin_ver     = None
        self._syst        = None
        self._h_mc        = None
        self._h_dt        = None

        self._maxentries  = -1

        super().__init__()

        self._initialized = False
    #----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        super()._initialize()

        self._wgt_dir  = self._get_wgt_dir()
        self._root_dir = self._get_root_dir()
        self._root_path= f'{self._root_dir}/{self._out_id}.root'
        self._res_dir  = self._root_path.replace('.root', '')
        os.makedirs(self._res_dir, exist_ok=True)

        if self._set_dir is None:
            self._set_dir = files('kinematics').joinpath('share') 

        self.log.info(f'Using settings from: {self._set_dir}')

        utnr.check_dir(self._set_dir)

        utnr.check_none(self._wgt_ver)

        self._prepare_rdf()
        self._set_binning()

        self._h_mc, self._h_dt = self.get_histograms()

        self._initialized=True
    #----------------------------------------
    def _prepare_rdf(self):
        d_bin            = self._get_binning()
        rdf_mc, l_var_mc = self._add_vars(self._rdf_mc)
        rdf_dt, l_var_dt = self._add_vars(self._rdf_dt)

        if l_var_mc != l_var_dt:
            self.log.error(f'Variables added to data and MC differ:')
            self.log.error(l_var_mc)
            self.log.error(l_var_dt)
            raise
        else:
            self._l_var = l_var_mc

        self._d_bin  = { var : arr_bin for var, (_, arr_bin) in zip(l_var_mc, d_bin.items()) }

        self._rdf_mc = self._add_cuts(rdf_mc)
        self._rdf_dt = self._add_cuts(rdf_dt)
    #----------------------------------------
    def _set_binning(self):
        self._arr_all = numpy.array([-self._fmax, +self._fmax])
        self._arr_xax = numpy.array( list(self._d_bin.values())[0] ).astype(float)
        self._arr_yax = numpy.array( list(self._d_bin.values())[1] ).astype(float)
        self._arr_zax = numpy.array( list(self._d_bin.values())[2] ).astype(float)
    #----------------------------------------
    def _check_pid(self, rdf):
        '''Checks that PID was not applied to original dataset
        Takes RDF, makes small RDF and applies PID, if efficiency is 100% raises exception
        '''
        rdf_tot = rdf.Range(1000)
        rdf_cut = rdf_tot.Filter(self._pid_cut, 'PID')

        ntot = rdf_tot.Count().GetValue()
        npas = rdf_cut.Count().GetValue()

        if ntot == npas:
            self.log.error(f'PID cut {self._pid_cut} already applied')
            rep = rdf_cut.Report()
            rep.Print()
            raise
    #----------------------------------------
    def _add_vars(self, rdf):
        '''Takes RDF, ads expression columns and returns (rdf, list of variable names)'''
        l_col = rdf.GetColumnNames()
        if 'mass' not in l_col:
            rdf = rdf.Define('mass', self._mass_var)

        l_var = []
        for exp in self._l_exp:
            rdf, var = utils.add_column_df(rdf, exp)
            l_var.append(var)

        return rdf, l_var
    #----------------------------------------
    def _add_cuts(self, rdf):
        '''Takes RDF applies boundary cuts and prints report'''
        rdf = self._bound_filter_rdf(rdf)
        rep = rdf.Report()
        rep.Print()

        df_eff   = utils.rdf_report_to_df(rep)
        eff_path = f'{self._res_dir}/eff.json'
        self.log.visible(f'Saving to: {eff_path}')
        df_eff.to_json(eff_path)

        return rdf
    #----------------------------------------
    def _get_wgt_dir(self):
        if self._wgt_dir is None:
            wgt_dir = os.environ['CALDIR']
        else:
            wgt_dir = self._wgt_dir

        return wgt_dir
    #----------------------------------------
    def _get_root_dir(self):
        '''Get path to output ROOT file''' 
        root_dir = utnr.make_dir_path(f'{self._wgt_dir}/{self._wgt_ver}')
        
        return root_dir 
    #----------------------------------------
    def _get_bin_vers(self):
        '''Get binning version from vX.(Y)'''
        regex = 'v\d+\.(\d+)'
        mtch  = re.match(regex, self._wgt_ver)

        if not mtch:
            self.log.error(f'Cannot extract binning version from: {self._wgt_ver} with {regex}')
            raise

        vers = mtch.group(1)

        return str(vers)
    #----------------------------------------
    def _get_binning(self):
        '''Get exp -> Array of boundaries dictionary by loading JSON and dropping entries'''

        version  = get_last_version(dir_path=self._set_dir, version_only=True)
        self.log.info(f'Using kinematic binning version {version}')

        set_path = f'{self._set_dir}/{version}/kinematics_{self._syst}.json'
        d_set    = utnr.load_json(set_path)
        d_bin    = d_set[self._set_key]

        self._l_exp = d_bin['rwt_vars']
        bin_vers    = self._get_bin_vers()
        d_bin       = {key : val for key, val in d_bin.items() if key.endswith(f'_{bin_vers}')}

        if len(d_bin) != len(self._l_exp):
            self.log.error(f'Inconsistent number of axes and expressions: {len(d_bin)}/{len(self._l_exp)}')
            raise

        self.log.debug(f'Using variables: {self._l_exp}')
        self.log.debug(f'Using binning:')
        for _, arr in d_bin.items():
            self.log.debug(f'   {arr}')

        return d_bin
    #----------------------------------------
    def _get_names(self, name):
        rgx = '(.*)_(.*)_(.*)_(.*)$'
        mtc = re.match(rgx, name)
        if not mtc:
            log.error(f'Cannot match {rgx} to {name}')
            raise

        trig = mtc.group(1)
        year = mtc.group(2) 
        pref = mtc.group(3) 
        syst = mtc.group(4) 

        self._out_id = f'{trig}_{year}_{pref}_{syst}' 
        self._set_key= f'{pref}_{trig}_{year}' 
        self._syst   = 'trg' if syst == 'nom' else syst
        self._preffix= pref 
    #----------------------------------------
    def save_reweighter(self, name=None):
        self._get_names(name)
        self._initialize()

        self.log.visible(f'Saving to: {self._root_path}')
        ofile= ROOT.TFile(self._root_path, 'recreate')
        self._h_mc.Write()
        self._h_dt.Write()
        ofile.Close()

        return self._root_path
#----------------------------------------

