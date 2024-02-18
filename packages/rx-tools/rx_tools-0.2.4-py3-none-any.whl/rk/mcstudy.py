
import logging 
import logzero
import numpy
import ROOT
import tqdm
import zfit
import sys
import os

import utils
import utils_noroot as utnr

from fitter      import zfitter
from zutils.plot import plot    as zfp

import matplotlib.pyplot as plt
from rk.snap_pdf import snap_pdf

#----------------------------------------
class mcstudy:
    log=utnr.getLogger('mcstudy')
    #----------------------------------------
    def __init__(self, pdf, d_opt={}):
        self._pdf      = pdf 
        self._obs      = pdf.space 
        self._obs_name = pdf.space.name 

        self._mod_name = 'model' 
        self._ful_mod  = None
        self._gen_mod  = None
        self._fit_mod  = None
        self._snp      = None
        self._plot_dir = None
        self._d_opt    = d_opt
        self._d_res    = {} 
        

        self._mod             = None
        self._spread_scale    = 1
        self._max_smear_count = 100
        self._nfit_plots      = 30
        self._nfit_saved      = 0
        self._binned          = None

        self._initialized = False
    #----------------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
            self.log.debug(f'Plots directory: {value}')
        except:
            self.log.error(f'Cannot create {value}')
            raise

        self._plot_dir = value
    #----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if not self._pdf.is_extended:
            self.log.error(f'PDF is not extended, yield is needed to produce toys')
            raise


        self._snp           = snap_pdf(self._pdf)
        self._snp.log_level = logzero.WARNING
        self._snp.save('generate')

        zfit.settings.changed_warnings.hesse_name = False

        zfitter.log.setLevel(logging.WARNING)

        utnr.check_type(self._obs_name,               str) 
        utnr.check_type(self._d_opt   ,              dict) 

        self._gen_mod   = self._pdf
        self._fit_mod   = self._pdf
        self._d_var_gen = self._get_gen_val()
        #-------------------------------------------------------------------
        self._spread_scale = utnr.get_from_dic(self._d_opt, 'initial_spread_factor') 

        self._initialzed = True
    #----------------------------------------
    def _get_gen_val(self):
        s_par = self._pdf.get_params(floating=True)

        d_par = { par.name : par.value().numpy() for par in s_par}

        return d_par
    #----------------------------------------
    def run(self, ndatasets=None):
        self._initialize()

        utnr.check_type(ndatasets, int)

        arr_fit = numpy.linspace(0, ndatasets - 1, ndatasets)
        arr_fit = numpy.random.choice(arr_fit, size=self._nfit_plots)

        iterator = tqdm.trange(ndatasets, file=sys.stdout, ascii=' -')
        for i_dataset in iterator:
            index = i_dataset if i_dataset in arr_fit else None
            self._d_res[i_dataset] = self._run_dataset(index)
    #----------------------------------------
    def _plot_fit(self, data, res, i_fit):
        if self._nfit_saved >= 20:
            return

        if self._plot_dir is None:
            return

        obj   = zfp(data=data, model=self._pdf, result=res)
        obj.plot(nbins=50, add_pars='all')
        plt.savefig(f'{self._plot_dir}/fit_{i_fit:03}_lin.png') 

        obj.axs[0].set_yscale('log')
        plt.savefig(f'{self._plot_dir}/fit_{i_fit:03}_log.png') 

        self._nfit_saved += 1
    #----------------------------------------
    def _run_dataset(self, i_fit=None):
        self._snp.load('generate')
        data = self._pdf.create_sampler() 

        self._smear_init_pars()
        obj=zfitter(self._pdf, data)
        res=obj.fit()

        try:
            res.hesse(method='minuit_hesse')
        except:
            self.log.warning(f'Could not run Hesse')
            return {}

        if i_fit is not None:
            self._plot_fit(data, res, i_fit)

        d_par = self._get_parameters(res)

        return d_par
    #----------------------------------------
    def _get_parameters(self, res):
        d_par = {}
        for par, d_val in res.params.items():
            nam = par.name
            val = d_val['value']
            err = d_val['hesse']['error'] 

            d_par[f'{nam}_fit'] = val
            d_par[f'{nam}_err'] = err 
            d_par[f'{nam}_gen'] = self._d_var_gen[nam] 

        d_par['valid' ]    = res.valid
        d_par['status']    = res.status
        d_par['converged'] = res.converged

        return d_par 
    #----------------------------------------
    def _smear_init_pars(self):
        return
    #----------------------------------------
    def _smear_par(self, par):
        return
    #----------------------------------------
    def results(self):
        return self._d_res
#----------------------------------------

