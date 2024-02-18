from rk.weight_reader import weight_reader
from rk.oscillator    import oscillator   as osci
from rk.trackreader   import reader       as tkrd
from rk.pidreader     import reader       as pird
from rk.trgreader     import reader       as trrd
from rk.q2smear       import q2smear      as qsmr

import os
import utils
import numpy
import logging
import utils_noroot     as utnr
import read_selection   as rs

from version_management import get_last_version
from hep_cl             import hist_reader      as hrdr
from atr_mgr            import mgr              as amgr

#-------------------------------
class data_filter:
    log=utnr.getLogger('data_filter')
    #-------------------------------
    def __init__(self, df):
        self._am            = amgr(df)
        self._df            = df
        self._val_dir       = None
        self._d_dilepton_id = {'jpsi' : '443', 'psi2' : '100443'}
        self._cal_dir       = os.environ['CALDIR'] 

        weight_reader.replica = 0
        weight_reader.kin_dir = self._cal_dir

        self._initialized   = False
    #-------------------------------
    def _get_df_attr(self, name):
        try:
            attr = getattr(self._df, name)
        except:
            self.log.error(f'Cannot find {name} attached to dataframe')
            raise

        return attr
    #-------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._set_log()

        trig = self._get_df_attr('treename')
        proc = self._get_df_attr('proc')
        year = self._get_df_attr('year')

        q2_sel = rs.get('q2', trig, q2bin=proc, year = year)

        dilepton_id = utnr.get_from_dic(self._d_dilepton_id, proc)

        df = self._df
        df = self._define_df(df, 'B_TRUEP_X', 'B_PX')
        df = self._define_df(df, 'B_TRUEP_Y', 'B_PY')
        df = self._define_df(df, 'B_TRUEP_Z', 'B_PZ')
        df = self._define_df(df, 'B_TRUEPT' , 'B_PT')
        df = self._define_df(df, 'B_TRUEID' , '521' )
        df = self._define_df(df, 'Jpsi_TRUEID', dilepton_id)

        df = df.Filter(q2_sel)

        self._df = self._am.add_atr(df)

        self._initialized = True
    #----------------------------
    def _set_log(self):
        amgr.log.setLevel(logging.WARNING)
        osci.log.setLevel(logging.WARNING)
        hrdr.log.setLevel(logging.WARNING)
        trrd.log.setLevel(logging.WARNING)
        tkrd.log.setLevel(logging.WARNING)
        pird.log.setLevel(logging.WARNING)
        qsmr.log.setLevel(logging.WARNING)

        utils.log.setLevel(logging.WARNING)
        weight_reader.log.setLevel(logging.WARNING)
    #----------------------------
    def _define_df(self, df, org, trg):
        #In case we run over MC and therefore the variable already exists
        l_column = df.GetColumnNames()
        if org in l_column:
            return df

        df = df.Define(org, trg)

        return df
    #----------------------------
    @property
    def val_dir(self):
        return self._val_dir

    @val_dir.setter
    def val_dir(self, value):
        try:
            self._val_dir = utnr.make_dir_path(value)
        except:
            self.log.error(f'Cannot make directory: {value}')
            raise

        self.log.info(f'Sending plots to: {value}')
    #----------------------------
    def _get_ver_dc(self):
        d_ver         = {}
        d_ver['GVER'] = get_last_version(dir_path=f'{self._cal_dir}/GEN', version_only=True, main_only= True)
        d_ver['EVER'] = get_last_version(dir_path=f'{self._cal_dir}/TRK', version_only=True, main_only= True)
        d_ver['RVER'] = get_last_version(dir_path=f'{self._cal_dir}/REC', version_only=True, main_only= True)
        d_ver['TVER'] = get_last_version(dir_path=f'{self._cal_dir}/TRG', version_only=True, main_only= True)
        d_ver['PVER'] = get_last_version(dir_path=f'{self._cal_dir}/PID', version_only=True, main_only= True)
        d_ver['QVER'] = get_last_version(dir_path=f'{self._cal_dir}/QSQ', version_only=True, main_only= True)
    
        return d_ver
    #----------------------------
    def _get_flags(self):
        d_ver = self._get_ver_dc()
        gver  = d_ver['GVER'] 
        rver  = d_ver['RVER'] 
        tver  = d_ver['TVER'] 
        pver  = d_ver['PVER'] 
        ever  = d_ver['EVER'] 
        qver  = d_ver['QVER'] 
    
        wgt          = weight_reader(self._df, 'sel')
        wgt.valdir   = self._val_dir 
        wgt.no_corr  = True
        self.log.warning('Using nominal maps to remove data falling in holes')
        wgt['gen']   = (gver, 'nom')
        wgt['rec']   = (rver, 'nom')
        wgt['lzr']   = (tver, 'nom')
        wgt['hlt']   = (tver, 'nom')
        wgt['pid']   = (pver, 'nom')
        wgt['trk']   = (ever, 'nom')
        #Q2 does not depend on maps => calibration won't give zeros
        wgt['qsq']   = (qver, '000')
        wgt['bts']   = ('20', 'nom')
    
        d_wgt   = wgt.get_weights()
        arr_wgt = d_wgt['nom']
        d_zeros = wgt.zeros 

        arr_flg = arr_wgt != 0 
        nzero   = numpy.count_nonzero(arr_flg == 0) 

        self.log.debug(f'#zeros/#total = {nzero}/{arr_flg.size}')
    
        return arr_flg, d_zeros
    #----------------------------
    def filter(self):
        self._initialize()
    
        arr_wgt, d_zeros = self._get_flags() 
        size_df          = self._df.Count().GetValue()
        size_ar          = arr_wgt.size
    
        if size_df != size_ar:
            self.log.error(f'Dataframe and array of weights sizes differ: {size_df}/{size_ar}')
            raise
    
        self._df = utils.add_df_column(self._df, arr_wgt, 'wgt_filt', {'exclude_re' : 'tmva_.*'})
    
        self._df = self._df.Filter('wgt_filt > 0', 'Map filter')
    
        rp = self._df.Report()
        rp.Print()

        df = self._am.add_atr(self._df)

        df.d_zeros = d_zeros
    
        return df
#----------------------------
def filter_zeros(rdf, val_dir):
    obj         = data_filter(rdf)
    obj.val_dir = val_dir
    rdf         = obj.filter()

    return rdf
#----------------------------

