from logzero import logger as log

import os
import glob
import logzero

from version_management import get_last_version 

import utils_noroot as utnr
#-----------------------------------------
class set_pdf:
    #--------------------------
    def __init__(self, pdf):
        self._pdf     = pdf
        self._fit_dir = None
        self._log_level = logzero.INFO
        self._d_par   = {}
        self._data_ver= 'v10.18is'

        self._initialized = False
    #--------------------------
    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, value):
        self._log_level = value
        log.setLevel(value)
    #--------------------------
    def _initialize(self):
        if self._initialized:
            return

        try:
            self._fit_dir = os.environ['FITDIR']
        except:
            log.error(f'Cannot extract FITDIR from environment')
            raise

        if self._log_level is not None:
            log.setLevel(self._log_level)

        self._d_par = self._get_params()

        self._initialized = True
    #--------------------------
    def _get_params(self):
        s_par_flt = self._pdf.get_params(floating= True)
        s_par_fix = self._pdf.get_params(floating=False)

        d_par = {}
        for par in s_par_fix:
            d_par[par.name.replace('_dt', '')] = par

        for par in s_par_flt:
            d_par[par.name.replace('_dt', '')] = par

        return d_par
    #--------------------------
    def _get_json(self, fit_version, kind):
        if fit_version is None:
            fit_dir = get_last_version(dir_path=self._fit_dir, version_only=False)
        else:
            log.warning(f'Using custom fit version "{fit_version}" instead of latest')
            fit_dir = f'{self._fit_dir}/{fit_version}'

        if not os.path.isdir(fit_dir):
            log.error(f'Directory not found: {fit_dir}')
            raise FileNotFoundError

        json_wc = f'{fit_dir}/{kind}/{self._data_ver}/{self._pdf.proc}*/{self._pdf.year}/pars_{self._pdf.trig}.json'

        l_json  = glob.glob(json_wc)

        if len(l_json) == 0:
            log.error(f'Cannot find any JSON file in: {json_wc}')
            raise FileNotFoundError

        return l_json
    #--------------------------
    def _list_to_dict(self, l_json):
        l_d_par = []
        for json_path in l_json:
            log.debug(f'Loading parameters from: {json_path}')
            d_par = utnr.load_json(json_path)
            l_d_par.append(d_par)

        d_par_all = l_d_par[0]
        l_d_par   = l_d_par[1:]

        for d_par  in l_d_par:
            d_par_all.update(d_par)

        d_par_out = { name.replace('_dt', '') : value for name, value in d_par_all.items()}

        return d_par_out
    #--------------------------
    def _set_pars(self, d_par, floating=None):
        for par_name, (par_val, _) in d_par.items():
            if par_name not in self._d_par:
                log.error(f'Cannot find {par_name} among:')
                log.error(self._d_par.keys())
                raise ValueError

            par = self._d_par[par_name]

            par.set_value(par_val)
            par.floating = floating 

            if floating:
                log.info(f'{par_name:<20}{par_val:<20.3f}{floating:<20}')
            else:
                log.debug(f'{par_name:<20}{par_val:<20.3f}{floating:<20}')
    #--------------------------
    def get_pdf(self, fit_version = None):
        self._initialize()

        l_json_mc = self._get_json(fit_version, 'simulation')
        l_json_dt = self._get_json(fit_version,       'data')

        d_mc = self._list_to_dict(l_json_mc)
        d_dt = self._list_to_dict(l_json_dt)

        log.info(f'{"Name":<20}{"Value":<20}{"Floating":<20}')
        self._set_pars(d_dt, floating= True)
        self._set_pars(d_mc, floating=False)

        return self._pdf
#-----------------------------------------
