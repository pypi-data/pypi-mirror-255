import utils_noroot      as utnr
import matplotlib.pyplot as plt

import math
import os 
import logging 
import numpy 

from ndict                 import ndict
from atr_mgr               import mgr               as amgr
from rk.calc_utility       import getGeomEff        as get_geo_eff
from rk.efficiency         import efficiency
from rk.df_getter          import df_getter 
from rk.cutflow            import cutflow 
from rk.differential_yield import dyield_calculator as dyc

from rk.binning            import binning

#-----------------------------------------
class calculator:
    log=utnr.getLogger(__name__)
    '''
    Class used to return efficiencies
    '''
    #------------------------------------
    def __init__(self, sample, year, version=None, partition=None):
        self._sample      = sample
        self._year        = year 
        self._version     = version
        self._partition   = partition 

        self._dfg         = None
        self._out_dir     = None 
        self._binning     = None 

        self._cal_dir     = os.environ['CALDIR']

        self._initialized = False
    #------------------------------------
    def _initialize(self):
        if self._initialized:
            return 

        utnr.check_none(self._version)
        self._dfg = df_getter(self._sample, self._year, self._version, self._partition)

        if self._binning is not None:
            l_var_arr = self._binning.arr_vars
            self._binning.arr_to_var()
            self._dfg.var_arr['sel'] = l_var_arr

            self.log.debug(f'Binning efficiencies with:')
            self.log.debug(self._binning)
        else:
            self.log.warning(f'Binning not found, calculating integrated efficiencies')

        #In case this is a test file, e.g. 2016_test.root
        #_test is not needed after this
        self._year= self._year.replace('_test', '')

        self._initialized = True
    #------------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, dir_path):
        self._out_dir = dir_path
    #------------------------------------
    def add_var(self, var_name, arr_bins):
        '''
        Will take binning corresponding to variable to bin efficincies on
        '''
        if self._binning is None:
            self._binning = binning()

        self._binning[var_name] = arr_bins
    #------------------------------------
    def _plot_arrays(self, d_array, nbins, min_x, max_x, l_line=[]):
        if self._out_dir is None:
            self.log.debug('Skipping array plotting')
            return

        plt.close('all')
        utnr.plot_arrays(d_array, nbins, min_x, max_x)

        for line in l_line:
            plt.axvline(x=line)

        out_dir  = utnr.make_dir_path(self._out_dir)
        img_path = f'{out_dir}/q2_{self._sample}_{self._year}.png'

        self.log.visible(f'Saving to: {img_path}')
        plt.legend()
        plt.savefig(img_path)
    #------------------------------------
    def _save_cutflow(self, selection, cf, trigger):
        '''
        Saving cutflow object to pickle file
        '''
        if self.log.level <= logging.DEBUG:
            self.log.debug(cf.df_eff)

        if self._out_dir is None:
            self.log.warning(f'out_dir attribute not set, not saving cutflow')
            return

        out_dir = utnr.make_dir_path(self._out_dir)

        pik_path = f'{out_dir}/cf_{selection}_{self._sample}_{self._year}_{trigger}.pickle'
        cut_path = pik_path.replace('.pickle', '_cut.json')
        eff_path = pik_path.replace('.pickle', '_eff.json')

        cf.df_eff.to_json(eff_path)
        cf.df_cut.to_json(cut_path)
        utnr.dump_pickle(cf, pik_path)

        self.log.visible(f'Saving to: {pik_path}')
        self.log.visible(f'Saving to: {cut_path}')
        self.log.visible(f'Saving to: {eff_path}')
    #------------------------------------
    def _get_lines(self, cut):
        regex='\(Jpsi_M_smeared \* Jpsi_M_smeared > ([\d,.]+)\) && \(Jpsi_M_smeared \* Jpsi_M_smeared < ([\d,.]+)\)'
        dn = utnr.get_regex_group(cut, regex, i_group=1)
        up = utnr.get_regex_group(cut, regex, i_group=2)

        dn = float(dn)
        dn = math.sqrt(dn)

        up = float(up)
        up = math.sqrt(up)

        return [dn, up]
    #------------------------------------
    def _get_sys_eff_int(self, d_pas=None, d_tot=None):
        '''
        Takes {sys -> arr_wgt} dictionaries with passed and total arrays of weights.
        Returns {sys -> eff } dictionary with efficiency object as value.
        '''
        s_pas = set(d_pas.keys())
        s_tot = set(d_tot.keys())

        self._check_systematics(s_pas, s_tot)

        s_int = s_pas.intersection(s_tot)

        d_eff = {}
        for sys in s_int:
            arr_pas = d_pas[sys]
            arr_tot = d_tot[sys]

            d_eff[sys] = efficiency(arr_pas, arg_tot=arr_tot, cut=sys, lab=sys) 

        d_unq_pas = { sys : val for sys, val in d_pas.items() if sys not in s_int}

        arr_tot_nom = d_tot['nom']

        for sys, arr_pas in d_unq_pas.items():
            d_eff[sys] = efficiency(arr_pas,     arg_tot=arr_tot_nom, cut = sys, lab=sys)

        return d_eff
    #------------------------------------
    def _get_sys_eff_dif(self, d_pas=None, d_tot=None):
        '''
        Takes {sys -> {var : dyield, ...}...} dictionary with systematic and dictionary of variable name and differential yield
        Returns {[sys, var] : defficiency} container with the same structure but a differential efficiency instead 
        '''
        s_pas = set(d_pas.keys())
        s_tot = set(d_tot.keys())
        self._check_systematics(s_pas, s_tot)

        s_int = s_pas.intersection(s_tot)

        d_deff = ndict()
        #Same systematic (including nominal) in numerator and denominator
        for sys in s_int:
            d_dyl_pas_sys = d_pas[sys]
            arr_tot_sys   = d_tot[sys]

            for var, dyl_pas_sys in d_dyl_pas_sys.items():
                d_deff[sys, var] = dyl_pas_sys / arr_tot_sys

        #Get systematics from only numerator and denominator
        d_unq_pas = { sys : d_dy  for sys, d_dy in d_pas.items() if sys not in s_int}
        d_unq_tot = { sys : arr   for sys, arr  in d_tot.items() if sys not in s_int}

        d_dyl_pas_nom = d_pas['nom']
        arr_tot_nom   = d_tot['nom']

        #Nominal denominator, systematic numerator
        for sys, d_dyl_pas_sys in d_unq_pas.items():
            for var, dyl_pas_sys in d_dyl_pas_sys.items():
                d_deff[sys, var] = dyl_pas_sys / arr_tot_nom

        #Nominal numerator, systematic denominator 
        for sys, arr_tot_sys in d_unq_tot.items():
            for var, dyl_pas_nom in d_dyl_pas_nom.items():
                d_deff[sys, var] = dyl_pas_nom / arr_tot_sys

        d_deff.check()

        return d_deff
    #------------------------------------
    def _check_systematics(self, s_pas, s_tot):
        '''
        Check that systematics from total and passed yields satisfy:
        1. Every systematic in total must be in passed.
        2. Pased and total contain the nominal
        '''

        if 'nom' not in s_pas:
            self.log.error(f'Nominal not found among passed sample systematics:')
            self.log.error(s_pas)
            raise

        if 'nom' not in s_tot:
            self.log.error(f'Nominal not found among total sample systematics:')
            self.log.error(s_tot)
            raise

        if not s_tot.issubset(s_pas):
            self.log.error(f'Total sample statistics are not part of passed sample:')
            self.log.error(s_tot)
            self.log.error(s_pas)
            raise
    #------------------------------------
    def get_geo(self):
        self._initialize()

        self.log.visible('--------------------------------')
        self.log.visible('Calculating geometric efficiency')

        eff, err = get_geo_eff(self._sample, self._year)

        df_gen = self._dfg.get_df('gen')
        npas   = df_gen.Count().GetValue()
        ntot   = math.floor(npas / eff)

        eff = efficiency(npas, arg_tot=ntot, cut='geo', lab='nom') 

        cf = cutflow()
        cf['geo acceptance'] = eff 

        self._save_cutflow('geo', cf, 'notrg')

        return {'nom' : eff}
    #------------------------------------
    def get_rec(self, weight_manager=None):
        self._initialize()

        self.log.visible('-------------------------------------')
        self.log.visible('Calculating reconstruction efficiency')

        df_gen=self._dfg.get_df('gen')
        df_rec=self._dfg.get_df('rec')

        d_gwt = self._get_arr_df(df_gen, 'gen', weight_manager)
        d_rwt = self._get_arr_df(df_rec, 'rec', weight_manager)

        self._save_cutflow('rec', df_rec.cf, 'notrg')

        if   isinstance(d_gwt,          int) and isinstance(d_rwt,          int):
            d_eff = {'nom' :   efficiency(d_rwt, arg_tot=d_gwt, lab='nom') }
        elif isinstance(d_gwt,         dict) and isinstance(d_rwt,         dict):
            d_eff = self._get_sys_eff_int(d_pas=d_rwt, d_tot=d_gwt)
        else:
            log.error(f'Yield objects are neither int nor Dataframes')
            log.info(type(df_gwt))
            log.info(type(df_rwt))
            raise

        return d_eff
    #------------------------------------
    def get_sel(self, weight_manager=None, selection=None, trigger=None, truth_corr_type=None, d_bin=None): 
        '''
        Will return {sys -> eff} dictionary, where sys is a systematic and eff an efficiency instance
        In case a binning was specified, will return {sys, var -> deff} 2D map with variable and differential efficiency
        '''
        self._initialize()

        self.log.visible('--------------------------------')
        self.log.visible('Calculating selection efficiency')

        utnr.check_none(selection)
        utnr.check_none(trigger)
        utnr.check_none(truth_corr_type)
        using_wmgr = weight_manager is not None

        df_raw = self._dfg.get_df('rec')
        df_sel = self._dfg.get_df('sel', trigger, selection, truth_corr_type, using_wmgr)

        df_raw.trigger = trigger
        df_sel.trigger = trigger

        d_wwt = self._get_arr_df(df_raw, 'raw', weight_manager)
        d_swt = self._get_arr_df(df_sel, 'sel', weight_manager)

        self._save_cutflow('raw', df_raw.cf, 'notrg')
        self._save_cutflow('sel', df_sel.cf, trigger)

        if   isinstance(d_wwt, dict) and isinstance(d_swt, dict) and self._binning is     None:
            d_eff = self._get_sys_eff_int(d_pas=d_swt, d_tot=d_wwt)
        elif isinstance(d_wwt, dict) and isinstance(d_swt, dict) and self._binning is not None:
            d_eff = self._get_sys_eff_dif(d_pas=d_swt, d_tot=d_wwt)
        elif isinstance(d_wwt,  int) and isinstance(d_swt,  int) and self._binning is     None:
            d_eff = { 'nom' : efficiency(d_swt, arg_tot=d_wwt, lab='nom', cut='offline selection') }
        else:
            self.log.error(f'Yield objects are neither int nor Dataframes')
            self.log.info(type(d_wwt))
            self.log.info(type(d_swt))
            raise

        return d_eff 
    #------------------------------------
    def _get_arr_df(self, rdf, kind, weight_manager=None):
        '''
        Takes RDF and returns {sys -> arr_wgt} dictionary, where the key signals the systematic
        and the value is an array of weights. The size of the array will agree with the rdf 

        If self._binning is not none, it will instead return a {sys -> dyield} dictionary.

        If weight_manager is None, truth matching correction won't be used.
        '''
        nevt = rdf.Count().GetValue()
        if   weight_manager is     None and self._binning is     None:
            self.log.warning(f'Not using any weights and integrating for yield of kind "{kind}"')

            return nevt
        elif weight_manager is     None and self._binning is not None:
            self.log.warning(f'Not using any weights for yield of kind "{kind}"')
            d_arr_wgt = {'nom' : numpy.ones(nevt)}
        elif weight_manager is not None:
            reader    = weight_manager.get_reader(kind, rdf)
            d_arr_wgt = reader.get_weights()
        else:
            self.log.error(f'Weight manager/Binning settings are invalid: {weight_manager}/{self._binning}')
            raise

        if kind == 'sel' and weight_manager is not None:
            arr_corr_wgt  = rdf.AsNumpy(['weight'])['weight']
            d_arr_wgt_cor = {key : arr_wgt * arr_corr_wgt for key, arr_wgt in d_arr_wgt.items()}
        else:
            d_arr_wgt_cor = d_arr_wgt

        if self._binning is None or kind != 'sel':
            return d_arr_wgt_cor

        d_d_dy = {}
        for sys, arr_wgt_cor in d_arr_wgt_cor.items():
            obj  = dyc(rdf, arr_wgt_cor, self._binning, label=sys)
            d_dy = {var : obj.get_yields(var=var) for var in self._binning.vars}

            d_d_dy[sys] = d_dy

        return d_d_dy
#-----------------------------------------

