from logzero     import logger  as log
from zutils.plot import plot    as zfp
from fitter      import zfitter

import zfit
import math
import pandas            as pnd
import utils_noroot      as utnr
import matplotlib.pyplot as plt

#---------------------------
class calculator:
    def __init__(self, pdf, poi_name = 'n_sig'):
        self._pdf         = pdf
        self._poi_name    = poi_name

        self._d_par       = {} 
        self._d_par_val   = {}
        self._d_const     = {}
        self._d_const_fit = {}
        self._dat         = None
        self._plot_dir    = None

        self._initialized = False
    #------------------------
    def _initialize(self):
        if self._initialized:
            return

        if not self._pdf.is_extended:
            log.error(f'PDF introduced is not extended')
            raise

        self._d_par_val   = self._store_pars()
        self._dat         = self._pdf.create_sampler()
        self._d_par       = self._get_nuisance_pars()
        self._d_const_fit = self._get_constraints()
        self._check_poi()

        self._initialized = True
    #------------------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, plot_dir):
        self._plot_dir = utnr.make_dir_path(plot_dir)
    #------------------------
    def _get_constraints(self):
        if len(self._d_const) == 0:
            log.info('Not using constraints')
            return

        d_const_fit = {}
        log.info('All constraints:')
        for name, par_sg in self._d_const.items():
            par = self._d_par[name]
            if math.isinf(par_sg):
                continue

            par_mu = self._d_par_val[name] 

            d_const_fit[name] = (par_mu, par_sg)

            log.info(f'{"":<4}{name:<20}{par_mu:<10.3e}{par_sg:<10.3e}')

        return d_const_fit
    #------------------------
    def __setitem__(self, name, value):
        s_par      = self._pdf.get_params(floating=True)
        l_par_name = [ par.name for par in s_par]

        if name not in l_par_name:
            log.error(f'Parameter {name} cannot be found among:')
            log.error(l_par_name)
            raise ValueError

        if not isinstance(value, float):
            log.error(f'Constraint for {name} is not a float: {value}')
            raise ValueError

        if value < 0:
            log.error(f'Constraint for {name} is not positive: {value}')
            raise ValueError

        self._d_const[name] = value
    #------------------------
    def _store_pars(self):
        s_par_shp = self._pdf.get_params(is_yield=False)
        s_par_yld = self._pdf.get_params(is_yield=True )

        d_par = {}
        for par in list(s_par_shp) + list(s_par_yld):
            name = par.name
            val  = par.value().numpy()

            d_par[name] = val

        return d_par
    #------------------------
    def _check_poi(self):
        s_par = self._pdf.get_params(is_yield=True)
        g_par = filter(lambda par : par.name == self._poi_name, s_par)
        try:
            [poi] = list(g_par) 
        except:
            log.error(f'Cannot extract POI={self._poi_name} from model')
            raise
    #------------------------
    def _fit(self, fix_par_name=None, d_const={}):
        obj = zfitter(self._pdf, self._dat)
        res = obj.fit(d_const = d_const)

        if res.status != 0:
            log.warning(f'Fit failed')
            return 0, 0

        res.hesse()
        res.freeze()

        self._plot_fit(res, fix_par_name)

        try:
            val = res.params[self._poi_name]['value']
            err = res.params[self._poi_name]['hesse']['error']
        except:
            log.warning(f'Cannot extract value and/or error of {self._poi_name} from:')
            print(res.params[self._poi_name])
            return 0, 0

        return val, err
    #------------------------
    def _plot_fit(self, res, par_name):
        obj   = zfp(data=self._dat, model=self._pdf, result=res)
        obj.plot(ext_text=f'Fixing: {par_name}')

        plot_path = f'{self._plot_dir}/{par_name}.png'
        log.info(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
    #------------------------
    def _get_nuisance_pars(self):
        s_par = self._pdf.get_params(is_yield=False, floating=True)
        s_par = filter(lambda par: not par.name.startswith('n_'), s_par)

        log.debug('Nuisance parameters:')

        d_par = {}
        for par in s_par:
            log.debug(f'{"":<4}{par.name:<20}')
            d_par[par.name] = par

        return d_par
    #------------------------
    def _reset_pars(self, fix_par=None):
        '''
        1. Float all parameters.
        2. Set values to model values.
        3. Fix `fix_par`, if not None.
        '''
        for par in self._d_par.values():
            par.floating = True
            val=self._d_par_val[par.name]
            par.set_value(val)

        if fix_par is None:
            log.info('All parameters floating')
            return

        log.info(f'Fixing {fix_par.name}')
        for par in self._d_par.values():
            if par.name != fix_par.name:
                continue

            par.floating = False
    #------------------------
    def _plot_unc(self, df):
        if self._plot_dir is None:
            return

        ax=df.plot(x='Parameter', y='Uncertainty', legend=None)
        ax.set_ylim(bottom=0)
        ax.set_ylabel(r'$100 \cdot \varepsilon(POI)/POI$')
        plt.grid() 
        plt.tight_layout()
        plt.savefig(f'{self._plot_dir}/uncertainty.png')
        plt.close('all')
    #------------------------
    def _fill_df_fix_par(self, df):
        poi_ini = self._d_par_val[self._poi_name]
        l_par   = list(self._d_par.values())
        for par in [None] + l_par:
            self._reset_pars(par)

            name             = 'none' if par is None else par.name
            poi_fit, err_fit = self._fit(fix_par_name=name)

            df.loc[-1] = [name, err_fit, poi_ini, poi_fit]
            df.index   = df.index + 1
            df         = df.sort_index()

        df['Uncertainty'] = 100 * df.Error / df.Model
        df['Bias']        = (df.Fit - df.Model) / df.Error

        df = df.sort_values(by='Uncertainty', ascending=False)
        df = df.reset_index(drop=True)

        return df
    #------------------------
    def _fill_df_const(self, df):
        poi_ini = self._d_par_val[self._poi_name]
        d_const = {}
        l_par_name = [None] + list(self._d_const_fit.keys())

        for par_name in l_par_name:
            if par_name is None:
                par_name = 'none'
            else:
                const= self._d_const_fit[par_name]
                d_const[par_name] = const

            self._reset_pars()

            poi_fit, err_fit = self._fit(fix_par_name=par_name, d_const=d_const)

            df.loc[-1] = [par_name, err_fit, poi_ini, poi_fit]
            df.index   = df.index + 1
            df         = df.sort_index()

        df['Uncertainty'] = 100 * df.Error / df.Model
        df['Bias']        = (df.Fit - df.Model) / df.Error
        df                = df.reindex(index=df.index[::-1])

        return df
    #------------------------
    def get_df(self):
        self._initialize()
        df = pnd.DataFrame(columns=['Parameter', 'Error', 'Model', 'Fit'])

        if len(self._d_const) == 0:
            df = self._fill_df_fix_par(df)
        else:
            df = self._fill_df_const(df)

        self._plot_unc(df)

        return df
#---------------------------

