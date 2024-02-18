import jacobi            as jac
import math
import numpy
import utils_noroot      as utnr
import matplotlib.pyplot as plt
import zfit

from logzero       import logger  as log
from stats.average import average as avg

#-----------------------------------------
class mass:
    def __init__(self, dt=None, mc=None):
        self._d_par_dt = dt
        self._d_par_mc = mc 

        self._scale_v  = None
        self._scale_e  = None

        self._reso_v   = None
        self._reso_e   = None

        self._initialized = False
    #--------------------------------
    @property
    def scale(self):
        self._initialize()
        return self._scale_v, self._scale_e 
    #--------------------------------
    @property
    def resolution(self):
        self._initialize()
        return self._reso_v, self._reso_e 
    #--------------------------------
    def combine(self, l_mscale):
        '''
        Will combine scales and resolutions from current object with other objects

        Parameters:
        -----------------
        l_mscale (list): List of mass instances

        Returns
        -----------------
        d_data (dict): Dictionary with { name : (value, error, pval)} where the quantity is the mass "scale" and "resolution"
        '''
        self._initialize()

        l_reso_v = [self._reso_v]
        l_reso_e = [self._reso_e]

        l_scal_v = [self._scale_v]
        l_scal_e = [self._scale_e]

        for mscale in l_mscale:
            reso_v, reso_e = mscale.resolution
            scal_v, scal_e = mscale.scale

            l_reso_v.append(reso_v)
            l_reso_e.append(reso_e)

            l_scal_v.append(scal_v)
            l_scal_e.append(scal_e)

        reso_v, reso_e, reso_p = avg(numpy.array(l_reso_v), numpy.array(l_reso_e))
        scal_v, scal_e, scal_p = avg(numpy.array(l_scal_v), numpy.array(l_scal_e))

        self._check_pval(reso_p, 'resolution')
        self._check_pval(scal_p, 'scale')

        d_data = {'resolution' : (reso_v, reso_e, reso_p), 'scale' : (scal_v, scal_e, scal_p)}

        return d_data
    #--------------------------------
    def _check_pval(self, pval, kind):
        if pval < 0.05:
            log.warning(f'Pvalue of kind {kind} is {pval:.3f}')
    #--------------------------------
    def __str__(self):
        self._initialize()

        line =f'------------------------------------------------------------\n'
        line+=f'{"Kind":<20}{"Value":<20}{"Error":<20}\n'
        line+=f'------------------------------------------------------------\n'
        line+=f'{"Scale":<20}{self._scale_v:<20.3f}{self._scale_e:<20.3f}\n'
        line+=f'{"Resolution":<20}{self._reso_v:<20.3f}{self._reso_e:<20.3f}\n'
        line+=f'------------------------------------------------------------\n'

        return line
    #--------------------------------
    def yld(self, kind):
        self._initialize()

        return self._d_par_mc['yld_sig'] if kind == 'mc' else self._d_par_dt['yld_sig']
    #--------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_keys(self._d_par_dt)
        self._check_keys(self._d_par_mc)

        self._calculate_scales()

        self._initialized = True
    #--------------------------------
    def _check_keys(self, d_par):
        for key in ['mu', 'sg', 'yld_sig']:
            if key not in d_par:
                log.error(f'Parameter {key} not found in: {d_par}')
                raise

            val = d_par[key]
            try:
                num, err = val
            except:
                log.error(f'Not found a tuple for {key}, instead {val}')
                raise
    #--------------------------------
    def _calculate_scales(self):
        mc_mu_val, mc_mu_err = self._d_par_mc['mu']
        mc_sg_val, mc_sg_err = self._d_par_mc['sg']

        dt_mu_val, dt_mu_err = self._d_par_dt['mu']
        dt_sg_val, dt_sg_err = self._d_par_dt['sg']

        scale_v, scale_e2= jac.propagate(lambda x : x[0] - x[1], [dt_mu_val, mc_mu_val], [[dt_mu_err**2, 0],[0, mc_mu_err**2]])
        reso_v , reso_e2 = jac.propagate(lambda x : x[0] / x[1], [dt_sg_val, mc_sg_val], [[dt_sg_err**2, 0],[0, mc_sg_err**2]])

        self._scale_v = float(scale_v) 
        self._reso_v  = float(reso_v) 

        self._scale_e = math.sqrt(scale_e2)
        self._reso_e  = math.sqrt(reso_e2)
#-----------------------------------------
class fraction:
    def __init__(self, d_mscale):
        self._d_mscale    = d_mscale

        self._d_scale     = None
        self._initialized = False
    #-----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._d_scale = self._get_scales()

        self._initialized = True
    #-----------------------------------
    def _get_fraction(self, cat, d_yld):
        l_cat = list(d_yld.keys())
        l_var = list(d_yld.values())

        cat_i = l_cat.index(cat)
        l_val = [ val for val, _ in l_var ]

        nvar  = len(l_var)
        row_z = [0] * nvar
        l_row = []
        for index in range(nvar):
            row_v  = list(row_z)
            _, err = l_var[index]
            row_v[index] = err ** 2

            l_row.append(row_v)

        frc_val, frc_err2 = jac.propagate(lambda x : x[cat_i] / sum(x), l_val, l_row)
        frc_err = math.sqrt(frc_err2)

        return frc_val, frc_err
    #-----------------------------------
    def _get_fractions(self, kind):
        d_yld = { cat : mscale.yld(kind) for cat, mscale in self._d_mscale.items() } 
        d_frc = { cat : self._get_fraction(cat, d_yld) for cat in d_yld}

        return d_frc
    #-----------------------------------
    def _get_scales(self):
        d_frc_mc = self._get_fractions('mc')
        d_frc_dt = self._get_fractions('dt')

        d_scl = {}
        for cat, (mc_frc_val, mc_frc_err) in d_frc_mc.items():
            dt_frc_val, dt_frc_err = d_frc_dt[cat]

            arr_val, arr_err2 = jac.propagate(lambda x : x[0] / x[1], [dt_frc_val, mc_frc_val], [[dt_frc_err**2, 0], [0, mc_frc_err**2 ]])
            d_scl[cat] = float(arr_val), math.sqrt(float(arr_err2))

        return d_scl
    #-----------------------------------
    @property
    def scales(self):
        self._initialize()
        return self._d_scale
#-----------------------------------------
class plotter:
    def __init__(self, dmu=None, ssg=None, dfr=None):
        self._dmu = dmu
        self._ssg = ssg 
        self._d_fr= dfr 

        self._d_scale = None 

        self._initialized = False
    #-----------------------------------
    @property
    def scales(self):
        return self._d_scale
    #-----------------------------------
    @scales.setter
    def scales(self, value):
        if not isinstance(value, dict):
            log.error(f'Input is not a dictionary: {value}')
            raise

        if self._d_fr.keys() != value.keys():
            log.error(f'Categories from fractons and scales differ: {self._d_fr.keys()}/{value.keys()}')
            raise

        self._d_scale = value
    #-----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._d_scale is None:
            log.error(f'Scales were not passed')
            raise

        self._initialized = True
    #-----------------------------------
    def _get_scales(self):
        fr   = fraction(self._d_scale)
        d_fr = fr.scales

        d_sc = {}
        for cat, msc in self._d_scale.items():
            d_sc[cat] = (msc.scale, msc.resolution, d_fr[cat])

        return d_sc
    #-----------------------------------
    def _plot(self, cat, sc, rs, fr):
        sc_v, sc_e = sc
        sc_p       = (sc_v - self._dmu) / sc_e

        rs_v, rs_e = rs
        rs_p       = (rs_v - self._ssg) / rs_e

        fr_v, fr_e = fr 
        fr_p       = (fr_v - self._d_fr[cat]) / fr_e

        plt.errorbar(['Scale', 'Reso', 'Brem frac'], [sc_p, rs_p, fr_p], yerr=[1, 1, 1], marker='o', capsize=10, linestyle='None', label=cat)
    #-----------------------------------
    def save_to(self, plot_dir):
        self._initialize()
        utnr.make_dir_path(plot_dir)

        d_sc = self._get_scales()
        for cat, (sc, rs, fr) in d_sc.items():
            self._plot(cat, sc, rs, fr)

        plt.legend()
        plt.axhline(color='black', linestyle=':')
        plt.savefig(f'{plot_dir}/scales.png')
        plt.close('all')
#-----------------------------------------
def dump_scales(d_scale, json_path):
    fr   = fraction(d_scale)
    d_fr = fr.scales
    
    d_scl = {} 
    for cat, msc in d_scale.items():
        d_scl[f'scl_{cat}'] = msc.scale
        d_scl[f'res_{cat}'] = msc.resolution
        d_scl[f'frc_{cat}'] = d_fr[cat]

    log.info(f'Saving to: {json_path}')
    
    utnr.dump_json(d_scl, json_path) 
#-----------------------------------------
class load_scales:
    def __init__(self, trig=None, dset=None, brem=None):
        self._trig = trig
        self._dset = dset
        self._brem = brem 

        self._l_par_name = ['scale', 'resolution', 'brem_frac'] 
        self._l_brem     = ['z', 'o', 't']
        self._d_par      = {}

        self._d_data     = None
        self._scale_dir  = None
        self._json_path  = None

        self._initialized = False
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        for par_name in self._l_par_name:
            if par_name not in self._d_par:
                log.error(f'Parameter {par_name} not specified')
                raise

        if self._brem not in self._l_brem:
            log.error(f'Brem {self._brem} not among: {self._l_brem}')
            raise

        self._json_path = f'{self._scale_dir}/{self._dset}_{self._trig}.json'
        utnr.check_file(self._json_path)

        self._d_data = utnr.load_json(self._json_path)

        self._initialized = True
    #-----------------------------------------
    def __setitem__(self, key, parameter):
        if key not in self._l_par_name:
            log.error(f'Invalid parameter: {key}')
            raise

        self._d_par[key] = parameter
    #-----------------------------------------
    @property
    def scale_dir(self):
        return self._scale_dir

    @scale_dir.setter
    def scale_dir(self, value):
        utnr.check_file(f'{value}/{self._dset}_{self._trig}.json')
        self._scale_dir = value
    #-----------------------------------------
    def _get_const(self, name_1, name_2):
        par      = self._d_par[name_1]
        val, err = self._d_data[f'{name_2}_{self._brem}']

        const    = zfit.constraint.GaussianConstraint(par, val, err)

        return const
    #-----------------------------------------
    def get_constraints(self):
        self._initialize()

        c_scl = self._get_const('scale'     , 'scl')
        c_res = self._get_const('resolution', 'res')
        c_frc = self._get_const('brem_frac' , 'frc')

        return {'scl' : c_scl, 'res' : c_res, 'frc' : c_frc}
#-----------------------------------------

