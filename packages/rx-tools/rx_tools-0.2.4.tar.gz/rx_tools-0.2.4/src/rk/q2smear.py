import ROOT

import os
import json
import math
import numpy
import numexpr

import utils
import utils_noroot      as utnr
import matplotlib.pyplot as plt

from rk.collector import collector
#-------------------------
class q2smear:
    log=utnr.getLogger(__name__)
    #-------------------------
    def __init__(self, df, q2dir):
        self._df          = df 
        self.q2dir        = q2dir
        self.storage      = collector() 
        self.jpsi_mass    = 'Jpsi_M'
        self.jpsi_pdg     = 3096.9
        self.arr_wgt      = None
        self.maxprint     = 0

        self._df_size     = None
        self._year        = None
        self._treename    = None
        self._out_dir     = None
        self._arr_wgt     = None

        self._initialized = False
        self._nprinted    = 0
        self._d_par_name  = {'rsg' : 's_sigma', 'dmu' : 'delta_m', 'mMC' : 'mu_MC'}

        self.__d_smear_par = {} 
        self.__d_smear_his = {} 
    #-------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except PermissionError:
            raise PermissionError(f'Cannot make: {value}')

        self._out_dir = value
    #-------------------------
    @property
    def weights(self):
        return self._arr_wgt

    @weights.setter
    def weights(self, value):
        self._arr_wgt = value
    #-------------------------
    def __initialize(self):
        if self._initialized:
            return

        self._check_df()

        self._treename = utnr.get_attr(self._df, 'treename')

        utnr.check_dir(self.q2dir)

        for var_name in ['yearLabbel', self.jpsi_mass, 'L1_P', 'L2_P']:
            self.__check_var(var_name)

        if 'nbrem' not in self._df.GetColumnNames():
            self.__check_var('L1_BremMultiplicity')
            self.__check_var('L2_BremMultiplicity')
            self._df = self._df.Define('nbrem', 'L1_BremMultiplicity + L2_BremMultiplicity >= 2 ? 2 : int(L1_BremMultiplicity + L2_BremMultiplicity)')

        arr_year =self._df.AsNumpy(['yearLabbel'])['yearLabbel']
        self._year=int(arr_year[0])

        if self.storage is None:
            self._initialized = True
            return

        self.storage.add('q2smr_treename', self._treename)

        self.__load_pars()

        self._initialized = True
    #-------------------------
    def _check_df(self):
        try:
            df_size = self._df.Count().GetValue()
        except:
            self.log.error('Cannot get size from dataframe')
            print(self._df)
            raise

        if df_size <= 0:
            self.log.error(f'Invalid dataframe size: {df_size}')
            raise

        self._df_size = df_size
    #-------------------------
    def __check_keys(self, filepath):
        for var in ['mu_MC', 'delta_m', 's_sigma']:
            for gamma in [0, 1, 2]:
                key=f'{self._treename} {var} {gamma} gamma'
                if key not in self.__d_smear_par:
                    self.log.error(f'key {key} not found in {filepath}')
                    raise
    #-------------------------
    def _check_size(self, obj, kind):
        if   isinstance(obj, numpy.ndarray):
            obj_size = len(obj)
        elif isinstance(obj, utils.get_df_types() ):
            obj_size = obj.Count().GetValue()
        else:
            self.log.error(f'Invalid object type')
            print(obj)
            raise

        if obj_size != self._df_size:
            self.log.error(f'Dataframe size {self._df_size} and object size {obj_size}, differ for {kind}')
            raise
    #-------------------------
    def _check_val(self, val, name):
        if not math.isnan(val) and not math.isinf(val):
            return

        self.log.error(f'Value of {name} found as {val}')
        raise
    #-------------------------
    def __check_var(self, var_name):
        l_var_name = self._df.GetColumnNames()
        if var_name not in l_var_name:
            self.log.error(f'Cannot retrieve {var_name} from dataframe')
            raise
    #-------------------------
    def _get_par_from_json(self, key, arr_ind):
        k0 = key.format(self._treename, 0)
        k1 = key.format(self._treename, 1)
        k2 = key.format(self._treename, 2)

        v0 = self.__d_smear_par[k0]
        v1 = self.__d_smear_par[k1]
        v2 = self.__d_smear_par[k2]

        arr_val = numpy.array([v0, v1, v2])

        arr_par = arr_val[arr_ind]

        if   arr_par.ndim == 1:
            arr_ret = arr_par
        elif arr_par.ndim == 2:
            arr_val = arr_par[:,0:1]
            arr_ret = arr_val.flatten()
        else:
            self.log.error(f'Array "{key}" has the wrong dimension:')
            print(arr_par)
            raise

        return arr_ret
    #-------------------------
    def _push_to_map(self, hist, val, axis):
        if val < 0:
            self.log.error(f'Found negative value of lepton momentum')
            raise

        if   axis == 'x':
            axe = hist.GetXaxis()
        elif axis == 'y': 
            axe = hist.GetYaxis()
        else:
            self.log.error(f'Invalid axis: {axis}')
            raise

        val_max = axe.GetXmax()
        
        if val < val_max:
            return val

        return val_max - 1
    #-------------------------
    def _get_par(self, par, arr_nbrem, arr_p1, arr_p2):
        '''
        Will read the smearing parameters in function of the electron momenta or the integrated one.

        Parameters:
        -----------------------
        par (str): String name of parameter
        arr_x (numpy array): array with location in brem and momentum of events

        Returns:
        -----------------------
        arr_val (numpy.ndarray) : Array q2 smearing parameters 
        '''
        if not self.q2dir.endswith('.mom'):
            old_par_name = self._d_par_name[par]
            arr_val = self._get_par_from_json(f'{{}} {old_par_name} {{}} gamma', arr_nbrem)

            return arr_val

        l_val = []
        for nbrem, p1, p2 in zip(arr_nbrem, arr_p1, arr_p2):
            key  = f'h_{par}_brem_{nbrem}'
            hist = self.__d_smear_his[key]

            p1   = self._push_to_map(hist, p1, 'x')
            p2   = self._push_to_map(hist, p2, 'y')

            pM   = max(p1, p2)
            pm   = min(p1, p2)

            ibin = hist.FindBin(pm, pM)
            val  = hist.GetBinContent(ibin)

            try:
                self._check_val(val, par)
            except:
                self.log.error(f'Cannot read map {key} at:')
                self.log.error(f'{"Brem":<20}{nbrem:<20}')
                self.log.error(f'{"MinP":<20}{pm:<20.0f}')
                self.log.error(f'{"MaxP":<20}{pM:<20.0f}')
                raise

            l_val.append(val)

        arr_val = numpy.array(l_val) 

        self._plot_qnt(par, [par], [arr_val])

        return arr_val
    #-------------------------
    def _plot_qnt(self, quantity, l_name, l_arr_val, rng=None):
        if self._out_dir is None:
            return

        for name, arr_val in zip(l_name, l_arr_val):
            a, b    = rng if rng is not None else (min(arr_val), max(arr_val))
            width   = (b - a) / 30.
            arr_bin = numpy.arange(a, b, width)
            if self._arr_wgt is None:
                self.log.warning(f'Weights not introduced, plotting unweighted data')
                name    = f'{name}: {arr_val.size}'
                clp_obj = numpy.clip(arr_val, arr_bin[0], arr_bin[-1])
                plt.hist(clp_obj, bins=arr_bin,                        label=name, histtype='step')
            else:
                mask    = self._arr_wgt != 0
                arr_wgt = self._arr_wgt[mask]
                arr_val = arr_val[mask]

                area    = numpy.sum(arr_wgt) 
                name    = f'{name}: {arr_val.size};{area:.0f}'
                clp_obj = numpy.clip(arr_val, arr_bin[0], arr_bin[-1])
                plt.hist(clp_obj, bins=arr_bin, weights=arr_wgt, label=name, histtype='step')

        plot_path = f'{self._out_dir}/{quantity}.png'
        plt.legend()
        self.log.visible(f'Saving to: {plot_path}')
        plt.xlabel('$q^2$[MeV]')
        plt.savefig(plot_path)
        plt.close('all')
    #-------------------------
    def __smear(self, arr_nbrem, arr_jpsi_m_reco, arr_p1, arr_p2):
        arr_s_sigma = self._get_par('rsg', arr_nbrem, arr_p1, arr_p2)
        arr_dmu     = self._get_par('dmu', arr_nbrem, arr_p1, arr_p2)
        arr_mu_MC   = self._get_par('mMC', arr_nbrem, arr_p1, arr_p2)
        
        jpsi_m_true = self.jpsi_pdg

        arr_jpsi_smear = jpsi_m_true + arr_s_sigma * (arr_jpsi_m_reco - jpsi_m_true) + arr_dmu + (1 - arr_s_sigma) * (arr_mu_MC - self.jpsi_pdg)

        if self._nprinted < self.maxprint:
            self._nprinted += 1
            self.log.info('{} = {} + {} * ({} - {}) + {} + (1 - {}) * ({} - {})'.format(jpsi_smear, jpsi_m_true, s_sigma, jpsi_m_reco, jpsi_m_true, dmu, s_sigma, mu_MC, self.jpsi_pdg) )

        return arr_jpsi_smear
    #-------------------------
    def __load_pars(self):
        if self.q2dir.endswith('.mom'):
            self._load_from_root()
        else:
            self._load_from_json()
    #-------------------------
    def _load_from_root(self):
        filepath = f'{self.q2dir}/{self._year}_{self._treename}.root'
        self.log.info(f'Loading smearing maps from: {filepath}')

        ifile = ROOT.TFile(filepath)

        for nbrem in [0, 1, 2]:
            for par in ['rsg', 'dmu', 'mMC']:
                key=f'h_{par}_brem_{nbrem}'
                his=getattr(ifile, key)
                his.SetDirectory(0)
                self.__d_smear_his[key] = his

        ifile.Close()
    #-------------------------
    def _load_from_json(self):
        filepath = f'{self.q2dir}/{self._year}.json'
        self.log.info(f'Loading smearing maps from: {filepath}')

        self.__d_smear_par = utnr.load_json(filepath)

        self.__check_keys(filepath)

        self.log.info('----------------------------')
        self.log.info('{0:<20}{1:<20}'.format('q2 file'  ,       filepath))
        self.log.info('{0:<20}{1:<20}'.format('Tree name', self._treename))
        self.log.info('----------------------------')
    #-------------------------
    def get_q2_smear(self, replica=None):
        utnr.check_numeric(replica, [int])
        self.__initialize()

        d_data    = self._df.AsNumpy(['nbrem', self.jpsi_mass, 'L1_P', 'L2_P'])
        arr_nbrem = d_data['nbrem'].astype(int)
        arr_p1    = d_data['L1_P']
        arr_p2    = d_data['L2_P']
        arr_jpsim = d_data[self.jpsi_mass]

        self._check_size( self._df, 'DataFrame')
        self._check_size(arr_nbrem, 'Original J/psi mass')
        self._check_size(arr_nbrem, 'NBrem')

        arr_smear = self.__smear(arr_nbrem, arr_jpsim, arr_p1, arr_p2)
        self._check_size(arr_smear, 'Smeared J/Psi mass')

        self._plot_qnt('q2_dist', ['Original', 'Smeared'], [arr_jpsim, arr_smear], rng=[2000, 4000])

        return arr_smear 
    #-------------------------
    def get_weights(self, q2_sel, replica):
        self.__initialize()
        if self.arr_wgt is not None:
            return self.arr_wgt

        q2_sel  = q2_sel.replace('&&', '&')
        arr_smr = self.get_q2_smear(replica)

        self.arr_wgt = numexpr.evaluate(q2_sel, {'Jpsi_M' : arr_smr})

        return self.arr_wgt
#-------------------------

