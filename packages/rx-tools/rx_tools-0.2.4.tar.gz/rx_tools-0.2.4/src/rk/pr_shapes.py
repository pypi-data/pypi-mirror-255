import utils_noroot     as utnr
import read_calibration as rcal
import pandas           as pnd
import read_selection   as rs
import matplotlib.pyplot as plt

from rk.cutflow      import cutflow
from rk.efficiency   import efficiency 
from rk.selection    import selection  as rksl
from rk.inclusive    import corrector  as icor
from atr_mgr         import mgr        as amgr
from version_management import get_last_version 

import os
import re 
import ROOT
import utils
import zfit
import numpy
import glob

#-----------------------------------------------------------
class pr_maker:
    log = utnr.getLogger('pr_maker')
    #-----------------------------------------------------------
    def __init__(self, proc, dset, trig, vers, q2bin):
        self._proc   = proc
        self._dset   = dset 
        self._trig   = trig 
        self._vers   = vers 
        self._q2bin  = q2bin

        self._bkg_cat_cut = 'B_BKGCAT < 60'

        self._l_truth_var = [
                'L1_TRUEID',
                'L2_TRUEID',
                'Jpsi_TRUEID',
                'H_TRUEID',
                'B_TRUEID',
                'Jpsi_MC_MOTHER_ID',
                'H_MC_MOTHER_ID',
                'H_MC_GD_MOTHER_ID',
                'Jpsi_MC_GD_MOTHER_ID',
                'L1_MC_GD_MOTHER_ID',
                'L2_MC_GD_MOTHER_ID',
                'L1_MC_GD_GD_MOTHER_ID',
                'L2_MC_GD_GD_MOTHER_ID']
        self._l_main_var  = ['mass_jpsi', 'mass_psi2', 'mass', 'nbrem', 'BDT_cmb', 'BDT_prc', 'wgt_br']
        self._l_trig_sel  = ['ETOS', 'GTIS']
        self._l_trig_cal  = ['gtis_inclusive', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0ElectronHAD', 'L0HadronElEL']
        self._l_trig      = self._l_trig_sel + self._l_trig_cal

        self._l_proc = ['bpXcHs_ee', 'bdXcHs_ee']
        self._l_dset = ['r1', 'r2p1', '2016', '2017', '2018']
        self._l_vers = ['v10.11tf', 'v10.18is']
        self._l_q2bin= ['jpsi', 'psi2', 'high']

        self._initialized   = False
    #-----------------------------------------------------------
    def  _initialize(self):
        if self._initialized:
            return

        if self._trig == 'GTIS_ee':
            self._trig = 'gtis_inclusive'

        utnr.check_included(self._proc , self._l_proc )
        utnr.check_included(self._vers , self._l_vers )
        utnr.check_included(self._dset , self._l_dset )
        utnr.check_included(self._trig , self._l_trig )
        utnr.check_included(self._q2bin, self._l_q2bin)

        self._initialized = True
    #-----------------------------------------------------------
    def _get_rdf(self, year):
        cas_dir = os.environ['CASDIR']
        file_wc = f'{cas_dir}/tools/apply_selection/prec_shape/{self._proc}/{self._vers}/{year}_{self._trig}/*.root'

        self.log.info(f'Data: {file_wc}')

        rdf = ROOT.RDataFrame(self._trig, file_wc)
        rdf = self._filter(rdf, year)
        mgr = amgr(rdf)
        rdf = self._add_columns(rdf)
        rdf = mgr.add_atr(rdf)

        return rdf
    #-----------------------------------------------------------
    def _filter(self, rdf, year):
        q2_cut = rs.get('q2'   , self._trig,  self._q2bin, year)
        ms_cut = rs.get('mass' , self._trig,  self._q2bin, year)

        if self._trig in self._l_trig_sel:
            trig = self._trig.lower()
            self.log.info(f'Using selection trigger: {trig}')
            lz_cut = rs.get(trig, self._trig,  self._q2bin, year)
        elif self._trig in self._l_trig_cal:
            self.log.info(f'Using calibration trigger: {self._trig}')
            lz_cut = rcal.get(self._trig, year)
        else:
            self.log.error(f'Cannot find appropiate trigger')
            raise

        d_cut         = {}
        d_cut[ 'bct'] = self._bkg_cat_cut
        d_cut[ 'lzr'] = lz_cut           
        d_cut[ 'qsq'] = q2_cut           

        for cut, val in d_cut.items():
            rdf = rdf.Filter(val, cut)

        rep               = rdf.Report()
        df_cfl            = utils.rdf_report_to_df(rep)
        df_cfl['cut_val'] = d_cut.values()

        rdf.df_cfl = df_cfl

        return rdf
    #-----------------------------------------------------------
    def _add_columns(self, rdf):
        true_mass = '''
        ROOT::Math::LorentzVector<ROOT::Math::XYZTVector> v_h( H_TRUEP_X,  H_TRUEP_Y,  H_TRUEP_Z,  H_TRUEP_E);
        ROOT::Math::LorentzVector<ROOT::Math::XYZTVector> v_1(L1_TRUEP_X, L1_TRUEP_Y, L1_TRUEP_Z, L1_TRUEP_E);
        ROOT::Math::LorentzVector<ROOT::Math::XYZTVector> v_2(L2_TRUEP_X, L2_TRUEP_Y, L2_TRUEP_Z, L2_TRUEP_E);

        auto v_b = v_h + v_1 + v_2;

        return v_b.M();
        '''

        rdf = rdf.Define('true_mass', true_mass)
        rdf = rdf.Define('mass'     , 'B_M')
        rdf = rdf.Define('mass_jpsi', 'B_const_mass_M[0]')
        rdf = rdf.Define('mass_psi2', 'B_const_mass_psi2S_M[0]')
        rdf = rdf.Define('nbrem'    , 'L1_BremMultiplicity + L2_BremMultiplicity')

        cor = icor(rdf)
        rdf = cor.add_weight(name='wgt_br')

        return rdf
    #-----------------------------------------------------------
    def _get_years(self):
        if   self._proc in ['bpXcHs_ee', 'bdXcHs_ee']   and self._dset in [  'r1', '2011']:
            l_year = []
        elif self._proc == 'bpXcHs_ee'                  and self._dset in ['r2p1', '2015', '2016']:
            l_year = []
        #-----------------------------
        elif self._proc == 'bdXcHs_ee'                  and self._dset == 'r2p1':
            l_year = ['2015', '2016']
        #-----------------------------
        elif                               self._dset in ['2011', '2012', '2015', '2016', '2017', '2018']:
            l_year = [self._dset]
        else:
            self.log.error(f'Cannot find list of year for process "{self._proc}" and dataset "{self._dset}"')
            raise

        self.log.info(f'Using years "{l_year}" for process "{self._proc}" and dataset "{self._dset}"')

        if l_year == []:
            self.log.warning(f'Cannot get model for dataset "{self._dset}", no corresponding files found, skipping')
            raise

        return l_year
    #-----------------------------------------------------------
    def _save_df(self, rdf, out_dir, add_vars):
        df_cfl = rdf.df_cfl
        d_data = rdf.AsNumpy(self._l_main_var + self._l_truth_var + add_vars)
        df_dat = pnd.DataFrame(d_data)

        dat_path = f'{out_dir}/data.json'
        cfl_path = f'{out_dir}/cutflow.json'

        self.log.visible(f'Saving to: {dat_path}')
        df_dat.to_json(dat_path, indent=4)

        self.log.visible(f'Saving to: {cfl_path}')
        df_cfl.to_json(cfl_path, indent=4)
    #-----------------------------------------------------------
    def save_data(self, version, add_vars=[]):
        self._initialize()

        l_year = self._get_years()
        for year in l_year:
            rdf = self._get_rdf(year)

            prc_dir = os.environ['PRCDIR']
            out_dir = f'{prc_dir}/{version}/{self._proc}_{self._trig}_{self._q2bin}_{year}'
            os.makedirs(out_dir, exist_ok=True)

            self._save_df(rdf, out_dir, add_vars)
#-----------------------------------------------------------
class pr_loader:
    log = utnr.getLogger('pr_loader')
    #-----------------------------------------------------------
    def __init__(self, proc=None, trig=None, q2bin=None, dset=None, vers=None):
        self._proc = proc
        self._trig = trig
        self._q2bin= q2bin
        self._dset = dset
        self._vers = vers

        self._l_proc = ['bdXcHs', 'bpXcHs', 'b*XcHs'] 
        self._l_trig = ['ETOS', 'GTIS'] 
        self._l_q2bin= ['jpsi', 'psi2', 'high'] 
        self._l_dset = ['r1', 'r2p1', '2011', '2012', '2015', '2016', '2017', '2018']

        self._val_dir = None
        self._prc_dir = None
        self._nbrem   = None
        self._chan    = None
        self._df      = None

        self._l_ee_trig = ['ETOS', 'GTIS']
        self._l_mm_trig = ['MTOS']
        self._d_match   = None

        self._initialized=False
    #-----------------------------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        try:
            self._prc_dir = os.environ['PRCDIR']
        except:
            log.error('PRCDIR variable not found in environment')
            raise

        self._check_valid(self._proc , self._l_proc,  'proc')
        self._check_valid(self._trig , self._l_trig,  'trig')
        self._check_valid(self._q2bin, self._l_q2bin, 'q2bin')
        self._check_valid(self._dset , self._l_dset,  'dset')

        self._vers    = self._get_version()
        self._d_match = self._get_match_str()
        self._chan    = self._get_channel()
        self._df      = self._get_df()

        self._initialized = True
    #-----------------------------------------------------------
    @property
    def val_dir(self):
        return self._val_dir

    @val_dir.setter
    def val_dir(self, value):
        try:
            os.makedirs(value, exist_ok=True)
        except:
            self.log.error(f'Cannot make {value}')
            raise

        self._val_dir = value
    #-----------------------------------------------------------
    @property
    def nbrem(self):
        return self._nbrem

    @nbrem.setter
    def nbrem(self, value):
        if value not in [0, 1, 2]:
            self.log.error(f'Invalid nbrem value of: {value}')
            raise ValueError

        self._nbrem = value
    #-----------------------------------------------------------
    def _check_valid(self, var, l_var, name):
        if var not in l_var:
            self.log.error(f'Value for {name}, {var}, is not valid')
            raise ValueError
    #-----------------------------------------------------------
    def _get_version(self):
        vers = get_last_version(self._prc_dir)

        if self._vers is None:
            return vers

        if self._vers != vers:
            self.log.warning(f'Not using last version {vers} but {self._vers}')

        return self._vers
    #-----------------------------------------------------------
    def _get_match_str(self):
        bp_psjp     = '(abs(Jpsi_MC_MOTHER_ID) == 100443) & (abs(Jpsi_MC_GD_MOTHER_ID) == 521) & (abs(H_MC_MOTHER_ID) == 521)'
        bd_psks     = '(abs(Jpsi_MC_MOTHER_ID) ==    511) & (abs(H_MC_MOTHER_ID) == 313) & (abs(H_MC_GD_MOTHER_ID) == 511) & (abs(Jpsi_TRUEID) == 100443)'
        bp_psks     = '(abs(Jpsi_MC_MOTHER_ID) ==    521) & (abs(H_MC_MOTHER_ID) == 323) & (abs(H_MC_GD_MOTHER_ID) == 521) & (abs(Jpsi_TRUEID) == 100443)'
        
        neg_bp_psjp = bp_psjp.replace('==', '!=').replace('&' , '|')
        neg_bd_psks = bd_psks.replace('==', '!=').replace('&' , '|')
        neg_bp_psks = bp_psks.replace('==', '!=').replace('&' , '|')
        
        bx_jpkp     = f' (abs(H_TRUEID) == 321) & (abs(Jpsi_TRUEID) == 443)  & ({neg_bp_psjp}) & ({neg_bd_psks}) & ({neg_bp_psks})'
        none        = f'((abs(H_TRUEID) != 321) | (abs(Jpsi_TRUEID) != 443)) & ({neg_bp_psjp}) & ({neg_bd_psks}) & ({neg_bp_psks})'
        
        d_cut            = {}
        d_cut['bp_psjp'] = bp_psjp
        d_cut['bd_psks'] = bd_psks
        d_cut['bp_psks'] = bp_psks
        
        d_cut['bx_jpkp'] = bx_jpkp
        d_cut['unmatched'] = none

        return d_cut
    #-----------------------------------------------------------
    def _get_channel(self):
        if   self._trig in self._l_ee_trig: 
            chan = 'ee' 
        elif self._trig in self._l_mm_trig: 
            chan = 'mm' 
        else:
            self.log.error(f'Invalid trigger: {self._trig}')
            raise

        return chan
    #-----------------------------------------------------------
    def _df_from_path(self, path):
        self.log.visible(f'Reading data from: {path}')

        return pnd.read_json(path)
    #-----------------------------------------------------------
    def _get_df(self):
        data_path = f'{self._prc_dir}/{self._vers}/{self._proc}_{self._chan}_{self._trig}_{self._q2bin}_{self._dset}/data.json'
        self.log.visible(f'Loading data from: {data_path}')

        try:
            l_df= [ self._df_from_path(data_path) for data_path in glob.glob(data_path) ]
            df  = pnd.concat(l_df, axis=0)
        except:
            self.log.error(f'Cannot read: {data_path}')
            raise

        if self._nbrem is not None:
            self.log.info(f'Applying nbrem = {self._nbrem} requirement')
            df = df[df.nbrem == self._nbrem] if self._nbrem < 2 else df[df.nbrem >= 2]
            df = df.reset_index(drop=True)

        return df
    #-----------------------------------------------------------
    def _print_wgt_stat(self, arr_wgt):
        l_wgt = arr_wgt.tolist()
        s_wgt = set(l_wgt)

        self.log.info('-' * 20)
        self.log.info(f'{"Frequency":<10}{"Weight":>10}')
        for wgt in s_wgt:
            nwgt = numpy.count_nonzero(wgt == arr_wgt)
            self.log.info(f'{nwgt:<10}{wgt:>10.3}')
    #-----------------------------------------------------------
    def _get_df_id(self, df):
        l_col = [
                'L1_TRUEID',
                'L2_TRUEID',
                'Jpsi_TRUEID',
                'Jpsi_MC_MOTHER_ID',
                'Jpsi_MC_GD_MOTHER_ID',
                'H_TRUEID',
                'H_MC_MOTHER_ID',
                'H_MC_GD_MOTHER_ID',
                'B_TRUEID'
                ]

        df = df[l_col]

        return df.reset_index(drop=True)
    #-----------------------------------------------------------
    def _filter_mass(self, df, mass, obs):
        ([[minx]], [[maxx]]) = obs.limits

        cut   = f'({minx} < {mass}) & ({mass} < {maxx})'
        self.log.debug(f'Applying: {cut}')
        df    = df.query(cut)

        return df
    #-----------------------------------------------------------
    def _filter_cut(self, cut):
        if cut is not None:
            self.log.info(f'Applying cut: {cut}')
            df = self._df.query(cut)
        else:
            df = self._df

        return df
    #-----------------------------------------------------------
    def _plot_data(self, arr_mass, arr_wgt, name=''):
        if self._val_dir is None:
            return

        plt.hist(arr_mass, weights=arr_wgt, bins=30, range=(4500, 6000), histtype='step')

        nbrem = 'all' if self._nbrem is None else self._nbrem

        plot_path = f'{self._val_dir}/distribution_{nbrem}_{name}.png'
        self.log.visible(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
    #-----------------------------------------------------------
    def get_pdf(self, mass=None, cut=None, use_weights=True, **kwargs):
        '''
        Will take the mass, with values in: 

        mass: Non constrained B mass
        mass_jpsi: Jpsi constrained B mass
        mass_psi2: Psi2S constrained B mass

        use_weights indicates wether to use the wgt_br branch (from the inclusive MC BR corrections) or not

        The observable.

        Optional arguments:
        Cut 

        **kwargs: These are all arguments for KDE1DimFFT

        and it will return a KDE1DimFFT PDF.
        '''
        self._initialize()

        df = self._filter_cut(cut)
        df = self._filter_mass(df, mass, kwargs['obs'])

        self.log.info(f'Using mass: {mass} for component {kwargs["name"]}')
        arr_mass = df[mass].to_numpy()
        if use_weights:
            arr_wgt = df['wgt_br'].to_numpy()
            self._print_wgt_stat(arr_wgt)
        else:
            self.log.warning('Not using BR weights')
            arr_wgt = numpy.ones_like(arr_mass)

        self._plot_data(arr_mass, arr_wgt, name = kwargs["name"])

        df_id        = self._get_df_id(df)

        pdf          = zfit.pdf.KDE1DimFFT(arr_mass, weights=arr_wgt, **kwargs) 
        pdf.arr_mass = arr_mass 
        pdf.arr_wgt  = arr_wgt 
        pdf.df_id    = df_id

        return pdf
    #-----------------------------------------------------------
    def get_components(self, mass=None, use_weights=True, **kwargs):
        '''Provides dictionary of PDFs making up PRec components

        Parameters:
        mass (str) : Defines which mass constrain to use, choose between "mass", "mass_jpsi", "mass_psi2"
        use_weights (bool): Should BR weights be used or not
        **kwargs: Arguments meant to be taken by zfit KDE1DimFFT

        Returns:
        {'str' : pdf} dictionary
        '''
        self._initialize()

        return { name : self.get_pdf(mass, cut, use_weights, name=name, **kwargs) for name, cut in self._d_match.items()}
    #-----------------------------------------------------------
    def get_sum(self, mass=None, use_weights=True, name='unnamed', **kwargs):
        '''Provides extended PDF that is the sum of multiple KDEs representing PRec background

        Parameters:
        mass (str) : Defines which mass constrain to use, choose between "mass", "mass_jpsi", "mass_psi2"
        use_weights (bool): Should BR weights be used or not
        name (str) : PDF name
        **kwargs: Arguments meant to be taken by zfit KDE1DimFFT

        Returns:
        zfit.pdf.SumPDF instance
        '''
        d_pdf     = self.get_components(mass=mass, use_weights=use_weights, **kwargs)
        l_pdf     = list(d_pdf.values())
        l_wgt_yld = [ sum(pdf.arr_wgt) for pdf in l_pdf ]
        l_yld     = [ zfit.param.Parameter(f'n_{pdf.name}', wgt_yld, 0, 10 * wgt_yld) for pdf, wgt_yld in zip(l_pdf, l_wgt_yld)]
        l_df_id   = [ pdf.df_id for pdf in l_pdf ]

        [pdf.set_yield(yld) for pdf, yld in zip(l_pdf, l_yld) ]

        pdf          = zfit.pdf.SumPDF(l_pdf, name=name)
        l_arr_mass   = [ pdf.arr_mass for pdf in l_pdf ] 
        l_arr_wgt    = [ pdf.arr_wgt  for pdf in l_pdf ] 

        pdf.arr_mass = numpy.concatenate(l_arr_mass)
        pdf.arr_wgt  = numpy.concatenate(l_arr_wgt )
        pdf.df_id    = pnd.concat(l_df_id, ignore_index=True)

        return pdf
#-----------------------------------------------------------

