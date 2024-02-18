import utils_noroot      as utnr
import os
import ROOT
import math
import re

import utils 
import read_selection  as rs
import rk.selection    as rksl
import rk.calc_utility as rkcu


from rk.truth_eff          import get_eff           as get_truth_eff
from atr_mgr               import mgr               as amgr
from rk.mva                import mva_man
from rk.cutflow            import cutflow
from rk.efficiency         import efficiency
#-----------------------------------------
class df_getter:
    log=utnr.getLogger('df_getter')
    #------------------------------------
    def __init__(self, sample, year, version, partition):
        self._sample    = sample
        self._year_file = year
        self._vers      = version
        self._part      = partition

        self._l_sample  = ['sign_ee', 'ctrl_ee', 'psi2_ee', 'sign_mm', 'ctrl_mm', 'psi2_mm']
        self._l_year    = ['2011', '2012', '2015', '2016', '2017', '2018']
        self._l_version = ['v10.11tf', 'v10.12', 'v10.13', 'v10.14', 'v10.15', 'v10.18is', 'v10.21p2']

        self._d_sam_tre = {'sign_ee' : 'KEE' , 'ctrl_ee' : 'KEE' , 'psi2_ee' : 'KEE' , 'sign_mm' : 'KMM' , 'psi2_mm' : 'KMM' , 'ctrl_mm' : 'KMM' }
        self._d_sam_qsq = {'sign_ee' : 'high', 'ctrl_ee' : 'jpsi', 'psi2_ee' : 'psi2', 'sign_mm' : 'high', 'ctrl_mm' : 'jpsi', 'psi2_mm' : 'psi2'}

        self._bdt_dir_cmb= f'{os.environ["MVADIR"]}/electron/bdt_v10.11tf.a0v2ss'
        self._bdt_dir_prc= f'{os.environ["MVADIR"]}/electron/bdt_v10.18is.prec'

        self._h_ipchi2   = 'H_IPCHI2_OWNPV > 4'

        #Fake trigger needed to get nspd hits cut, tool needs a trigger
        #but cut does not depend on trigger
        self._dummy_trigger = 'ETOS'

        self._df_gen = None
        self._df_rec = None
        self._df_sel = None

        self._d_var_arr = {} 

        self._initialized = False
    #------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        #To find files xxxx_test will work, for everything else, only xxxx works
        self._year= self._year_file.replace('_test', '')

        utnr.check_included(self._sample , self._l_sample )
        utnr.check_included(self._year   , self._l_year   )
        utnr.check_included(self._vers   , self._l_version)

        try:
            if self._part is not None:
                i_part, n_part = self._part
        except:
            self.log.error(f'Could not extract partitioning scheme from: {self._part}')
            raise

        self._initialized = True
    #------------------------------------
    @property
    def var_arr(self):
        """
        Return {kind -> [var1, var2, ...]}. 
        Kind is among ['sel', 'rec', 'gen']
        The variables are array columns like B_const_mass_M[0]

        If variable is found in the dataframe
        as a column, will be used to redefine the column, i.e:
        var -> var[3]
        """

        return self._d_var_arr
    #------------------------------------
    def _get_df(self, kind):
        dat_dir   = os.environ['DATDIR']
        file_path = f'{dat_dir}/{self._sample}/{self._vers}/{self._year_file}.root'
        #In case this is a testing dataset, use only the actual year, not xxxx_test
        if   kind == 'rec':
            tree_path = utnr.get_from_dic(self._d_sam_tre, self._sample)
        elif kind == 'gen': 
            tree_path = 'gen'
        else:
            self.log.error(f'Unrecognized dataframe kind {kind}')
            raise

        utnr.check_file(file_path)

        self.log.visible('------------------------------------')
        self.log.visible(f'Retrieving dataframe for:')
        self.log.visible(f'{"File path  ":<20}{file_path:<100}')
        self.log.visible(f'{"Tree path  ":<20}{tree_path:<100}')
        self.log.visible('------------------------------------')

        df = ROOT.RDataFrame(tree_path, file_path)
        df = self._skim_df(df)

        if kind == 'gen':
            df = self._add_truth(df)

        df.filepath = file_path
        df.treename = tree_path
        df.year     = self._year

        return df
    #------------------------------------
    def _split_var(self, var_arr):
        regex='(.*)\[(\d+)\]'
        mtch = re.match(regex, var_arr)

        if not mtch:
            self.log.error(f'Cannot match {var_arr} to {regex}')
            raise

        name = mtch.group(1)
        posi = mtch.group(2)

        return (name, posi)
    #------------------------------------
    def _redefine_cols(self, df, l_var_arr):
        """
        l_Var_arr contains elements of the form var[i]. Function redefines df column as

        var[i] -> var

        if var not found in df, will raise exception
        """
        l_var_df   = df.GetColumnNames()
        l_pyvar_df = [ str(var_df.c_str()) for var_df in l_var_df]

        self.log.visible('Redefining variables')
        for var_arr in l_var_arr:
            var_name, var_pos = self._split_var(var_arr)
            if var_name not in l_pyvar_df:
                self.log.error(f'Variable {var_name} not found in RDF, skipping redefinition')
                print(sorted(l_pyvar_df))
                raise RuntimeError

            self.log.visible(f'{"":<10}{var_arr:<20}{"->":<10}{var_name:<20}')
            df = df.Redefine(var_name, var_arr)

        return df
    #------------------------------------
    def _get_df_rec(self):
        df_rec = self._get_df('rec')
        dfmgr  = amgr(df_rec)

        self.log.info('Applying truth matching')
        cut    = rs.get_truth(self._sample)
        df_rec = df_rec.Filter(cut, 'truth')

        if self._df_gen is None:
            self._df_gen = self._get_df('gen')

        df_gen = self._df_gen
        ngen   = df_gen.Count().GetValue()

        cf = cutflow()
        #-------------------------
        nrec         = df_rec.Count().GetValue()
        cf['reco']   = efficiency(nrec, ngen - nrec, lab='nom')
        #-------------------------
        self.log.info(f'Applying IPChi2: {self._h_ipchi2}')
        df_rec       = df_rec.Filter(self._h_ipchi2, 'K IPChi2')
        nipc         = df_rec.Count().GetValue()
        cf['IPChi2'] = efficiency(nipc, nrec - nipc, lab='nom')
        #-------------------------
        cut        = rs.get('nspd', self._dummy_trigger, 'none', 'none')

        self.log.info(f'Applying nSPD cut: {cut}')
        df_rec     = df_rec.Filter(cut, 'nspd')
        nspd       = df_rec.Count().GetValue()
        cf['nSPD'] = efficiency(nspd, nipc - nspd, lab='nom')
        #-------------------------
        df_rec.cf = cf

        df_rec=dfmgr.add_atr(df_rec)

        return df_rec
    #------------------------------------
    def _get_df_sel(self, truth_corr_type, trigger, selection, using_wmgr):
        d_cut  = self._get_sel_cuts(selection, trigger, using_wmgr)
        #treename is KEE/KMM for reco df. After selection, this has to be the trigger
        if self._df_rec is None:
            self._df_rec = self.get_df('rec')

        df_rec = self._df_rec

        dfmgr = amgr(df_rec)

        cf = cutflow()
        tot=df_rec.Count().GetValue()
        for key, cut in d_cut.items():
            self.log.info(f'Applying: {key}')

            if key == 'bdt':
                df_rec = self._filter_bdt(df_rec, cut, trigger)
            else:
                df_rec = df_rec.Filter(cut, key)

            pas=df_rec.Count().GetValue()

            cf[key] = efficiency(pas, tot - pas, cut=cut)
            tot=pas

        wgt = self._get_corr_wgt(df_rec, trigger, truth_corr_type) 

        pas = math.floor(tot * wgt)
        cf['truth'] = efficiency(pas, arg_tot=tot, cut='truth_corr')

        if 'sel' in self._d_var_arr:
            l_var_arr = self._d_var_arr['sel']
            df_rec = self._redefine_cols(df_rec, l_var_arr)

        df_rec          = df_rec.Define('weight', str(wgt) )
        df_rec          = dfmgr.add_atr(df_rec)
        df_rec.treename = trigger
        df_rec.trig     = trigger
        df_rec.q2       = utnr.get_from_dic(self._d_sam_qsq, self._sample)
        df_rec.cf       = cf

        df_rec          = rkcu.addDiffVars(df_rec, kind='all')

        return df_rec
    #------------------------------------
    def _get_corr_wgt(self, df, trigger, truth_corr_type):
        if truth_corr_type == 'none':
            self.log.warning('Not using truth matching correction')
            return 1 

        self.log.info(f'Using truth matching correction of type {truth_corr_type}')

        proc = self._sample.replace('_ee', '').replace('_mm', '')
        eff  = get_truth_eff(proc, self._year, trigger, self._vers, truth_corr_type)

        return 1 / eff 
    #------------------------------------
    def _add_truth(self, df):
        df  = df.Define( 'B_PT', 'TVector3 v(B_TRUEP_X, B_TRUEP_Y, B_TRUEP_Z); return v.Perp();')
        df  = df.Define('B_ETA', 'TVector3 v(B_TRUEP_X, B_TRUEP_Y, B_TRUEP_Z); return v.Eta();')

        return df
    #------------------------------------
    def _get_sel_cuts(self, selection, trigger, using_wmgr):
        q2bin = utnr.get_from_dic(self._d_sam_qsq, self._sample)
        d_cut = rksl.selection(selection, trigger, self._year, self._sample, q2bin=q2bin)

        if 'truth' in d_cut:
            del(d_cut['truth'])

        if using_wmgr:
            self.log.info('Using weights => dropping [pid, q2] from selection')
            del(d_cut['pid'])
            del(d_cut[ 'q2'])

        return d_cut
    #------------------------------------
    def _filter_bdt(self, df, cut, trigger):
        man_cmb =mva_man(df, self._bdt_dir_cmb, trigger)
        df      = man_cmb.add_scores('BDT_cmb')

        man_prc =mva_man(df, self._bdt_dir_prc, trigger)
        df      = man_prc.add_scores('BDT_prc')

        df = df.Filter(cut, 'bdt')

        return df
    #------------------------------------
    def _skim_df(self, df):
        if self._part is None:
            return df

        islice, nslice = self._part

        df = utils.get_df_range(df, islice, nslice)

        return df
    #------------------------------------
    def get_df(self, kind, trigger=None, selection=None, truth_corr_type=None, using_wmgr=None):
        self._initialize()

        try:
            df = getattr(self, f'_df_{kind}')
        except:
            self.log.error(f'Invalid dataframe of type: {kind}')
            raise

        if   df is not None:
            return df
        elif kind == 'gen': 
            self._df_gen = self._get_df('gen')
            df           = self._df_gen
        elif kind == 'rec':
            self._df_rec = self._get_df_rec()
            df           = self._df_rec
        elif kind == 'sel':
            utnr.check_included(using_wmgr, [True, False])
            self._df_sel = self._get_df_sel(truth_corr_type, trigger, selection, using_wmgr)
            df           = self._df_sel

        return df
#-----------------------------------------

