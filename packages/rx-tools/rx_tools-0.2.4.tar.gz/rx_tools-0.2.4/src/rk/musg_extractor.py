import utils_noroot      as utnr
import matplotlib.pyplot as plt
import zfit
import math
import numpy
import re
import os

from zutils.plot import plot     as zfp
from logzero     import logger   as log
from rk.scales   import mass     as mscale
from fitter      import zfitter

#-----------------------------------------
class extractor:
    def __init__(self, mc=None, dt=None, names={}):
        self._arr_mc     = mc
        self._arr_dt     = dt
        self._d_name     = names

        self._sig_pdf    = None
        self._ful_pdf    = None

        self._cache_dir  = None 
        self._plot_dir   = None
        self._stop_at    = None

        self._sig_pref   = None
        self._mu_name    = None
        self._sg_name    = None

        self._d_mc_pars  = {}

        self._initialized = False
    #-----------------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, plot_dir):
        try:
            self._plot_dir = utnr.make_dir_path(plot_dir)
        except:
            log.error(f'Cannot make: {plot_dir}')
            raise
    #-----------------------------------------
    @property
    def cache_dir(self):
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, value):
        try:
            self._cache_dir = utnr.make_dir_path(value)
        except:
            log.error(f'Cannot make cache directory: {value}')
            raise ValueError
    #-----------------------------------------
    @property
    def model(self):
        self._initialize()
        return self._ful_pdf

    @model.setter
    def model(self, ful_pdf):
        self._initialize()

        if not isinstance(ful_pdf, zfit.pdf.SumPDF):
            log.error(f'Model is not a zfit.pdf.SumPDF: {ful_pdf}')
            raise

        l_name = [ model.name for model in ful_pdf.models if model.name.startswith(self._sig_pref)]
        if len(l_name) != 1:
            log.error(f'Single signal component not found among: {l_name}')
            raise
        else:
            [self._sig_pdf] = [ model for model in ful_pdf.models if model.name.startswith(self._sig_pref)]
            log.info(f'Using signal: {self._sig_pdf.name})')

        s_par      = self._sig_pdf.get_params(floating=True)
        l_par_name = [par.name for par in s_par]

        if self._mu_name not in l_par_name:
            log.error(f'Missing {self._mu_name} floating parameter in signal component: {l_par_name}')
            raise

        if self._sg_name not in l_par_name:
            log.error(f'Missing {self._sg_name} floating parameter in signal component: {l_par_name}')
            raise

        self._ful_pdf  = ful_pdf
    #-----------------------------------------
    @property
    def stop_at(self):
        return self._stop_at

    @stop_at.setter
    def stop_at(self, value):
        if value not in ['mc_fit', 'dt_fit']:
            log.error(f'Stopping value {value} invalid')
            raise ValueError

        self._stop_at = value 
    #-----------------------------------------
    def _set_name(self, name, default):
        if name in self._d_name:
            var = self._d_name[name]
        else:
            var = default

        return var
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._sig_pref = self._set_name('sname', 'Signal')
        self._mu_name  = self._set_name('mu'   ,     'mu')
        self._sg_name  = self._set_name('sg'   ,     'sg')

        self._initialized = True
    #-----------------------------------------
    def _load(self, name):
        if self._cache_dir is None:
            return

        data_path = f'{self._cache_dir}/{name}.json'
        if not os.path.isfile(data_path):
            return

        d_data = utnr.load_json(data_path)

        log.info(f'Loading from: {data_path}')

        return d_data
    #-----------------------------------------
    def _dump(self, obj, name):
        if self._cache_dir is None:
            return

        data_path = f'{self._cache_dir}/{name}.json'
        utnr.dump_json(obj, data_path)

        log.info(f'Dumping to: {data_path}')
    #-----------------------------------------
    def _fit(self, name, pdf, arr_mass, ntries=None):
        obj=self._load(name) if name in ['signal', 'data'] else None
        if obj is not None:
            return obj

        log.info(f'Fitting {arr_mass.size} entries')
        obj=zfitter(pdf, arr_mass)
        res=obj.fit(ntries=ntries)

        if self._plot_dir:
            self._plot_fit(name, model=pdf, data=arr_mass, result=res)

        if res.status != 0:
            log.error(f'Failed fit, status: {res.status}')
            print(res)
            raise

        res.hesse()
        res.freeze()

        try:
            d_par = { name : (d_val['value'], d_val['hesse']['error']) for name, d_val in res.params.items()}
        except:
            log.error(f'Cannot extract fit parameters:') 
            print(res)
            print(res.params.items())
            raise

        self._dump(d_par, name)

        return d_par
    #-----------------------------------------
    def _plot_fit(self, name, model=None, data=None, result=None):
        obj=zfp(data=data, model=model, result=result)
        obj.plot(ext_text=f'Kind: {name}')

        plot_dir  = utnr.make_dir_path(f'{self._plot_dir}/fits')
        plot_path = f'{plot_dir}/{name}.png'
        log.info(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
    #-----------------------------------------
    def _fix_pdf(self, pdf, d_par):
        s_par_flt = pdf.get_params(floating=True )
        s_par_fix = pdf.get_params(floating=False)

        d_par_pdf = {par.name : par for par in list(s_par_flt) + list(s_par_fix)}

        log.info(f'Fixing parameters:')
        for name, (value, _) in d_par.items():
            if name in [self._mu_name, self._sg_name] or name.startswith('yld_') or name.startswith('nsig_'):
                continue

            par = d_par_pdf[name]
            par.set_value(value)
            par.floating = False

            log.info(f'{"":<4}{name:<10}{"->":<10}{value:<10.3e}')

        return
    #-----------------------------------------
    def get_scales(self): 
        self._initialize()

        d_par_mc = self._fit('signal', self._sig_pdf, self._arr_mc, ntries=10)

        if self._stop_at == 'mc_fit':
            log.info(f'Stopping after fitting MC signal')
            return

        self._fix_pdf(self._ful_pdf, d_par_mc)
        d_par_dt = self._fit('data'  , self._ful_pdf, self._arr_dt)

        if self._stop_at == 'dt_fit':
            log.info(f'Stopping after fitting MC full signal')
            return

        return mscale(dt=d_par_dt, mc=d_par_mc) 
#-----------------------------------------

