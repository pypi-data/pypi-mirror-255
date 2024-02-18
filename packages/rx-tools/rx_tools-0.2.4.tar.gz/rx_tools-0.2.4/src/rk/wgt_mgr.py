import utils
import utils_noroot   as utnr
import os

from version_management import get_last_version 
from rk.weight_reader   import weight_reader
#----------------------------------------
class wgt_mgr:
    '''
    '''
    log=utnr.getLogger(__name__)
    #-----------------------------------
    def __init__(self, d_set):
        self._l_kind      = ['gen', 'rec', 'raw', 'sel']
        self._s_wgt       = {'gen', 'rec', 'lzr', 'hlt', 'pid', 'qsq', 'trk', 'bts', 'bdt', 'dcm'}
        self._d_set       = d_set

        self._d_wgt       = {} 
        self._val_dir     = None
        self._log_lvl     = None

        self._initialized = False
    #-----------------------------------
    @property
    def log_lvl(self):
        return self._log_lvl

    @log_lvl.setter
    def log_lvl(self, value):
        self._log_lvl = value
    #-----------------------------------
    def __str__(self):
        self._initialize()

        line = f'\n**********\n{"Kind":<10}{"Version":<10}{"Systematic":<10}\n**********\n'
        for kind, (vers, syst) in self._d_wgt.items():
            line += f'{kind:<10}{vers:<10}{syst:<10}\n'

        return line
    #-----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._set_log_lvl()
        self._set_kin_dir()
        self._update_versions()

        weight_reader.replica = utnr.get_from_dic(self._d_set, 'replica')
        val_dir               = utnr.get_from_dic(self._d_set, 'val_dir')

        self._val_dir = utnr.make_dir_path(val_dir)

        for wgt in self._s_wgt:
            try:
                ver = utnr.get_from_dic(self._d_set, f'{wgt}_ver', no_error=True)
                sys = utnr.get_from_dic(self._d_set, f'{wgt}_sys', no_error=True)
            except:
                continue

            self._d_wgt[wgt] = (ver, sys)

        #PID and q2 are always applied as cuts (weight = 0/1) or taken from maps
        if 'qsq' not in self._d_wgt:
            self._d_wgt['qsq'] = (None, '000')

        if 'pid' not in self._d_wgt:
            self._d_wgt['pid'] = (None, '000')

        self._initialized = True
    #-----------------------------------
    def _set_log_lvl(self):
        if self._log_lvl is None:
            return

        import utils
        import rk.calc_utility as cut
        import rk.selection    as rksl
        
        from rk.df_getter     import df_getter  as dfg
        from rk.mva           import mva_man    
        from rk.q2smear       import q2smear    
        from rk.trgreader     import reader     as trg_reader
        from rk.trackreader   import reader     as trk_reader
        from rk.weight_reader import weight_reader 
        from rk.pidreader     import reader     as pid_reader
        from rk.oscillator    import oscillator as osc
        from atr_mgr          import mgr        as amgr
        from stats            import correlations as corr
        from hep_cl           import hist_reader as hrdr

        self.log.setLevel(self._log_lvl)

        corr.corr.log.setLevel(self._log_lvl)
        hrdr.log.setLevel(self._log_lvl)
        utils.log.setLevel(self._log_lvl)
        osc.log.setLevel(self._log_lvl)
        cut.log.setLevel(self._log_lvl)
        rksl.log.setLevel(self._log_lvl)
        dfg.log.setLevel(self._log_lvl)
        mva_man.log.setLevel(self._log_lvl)
              
        q2smear.log.setLevel(self._log_lvl)
        wgt_mgr.log.setLevel(self._log_lvl)
        pid_reader.log.setLevel(self._log_lvl)
        trg_reader.log.setLevel(self._log_lvl)
        trk_reader.log.setLevel(self._log_lvl)
        amgr.log.setLevel(self._log_lvl)
        weight_reader.log.setLevel(self._log_lvl)
    #-----------------------------------
    def _update_versions(self):
        cal_dir = os.environ['CALDIR']

        d_set = {}
        for key, val in self._d_set.items():
            d_set[key] = val
            if not key.endswith('_sys') or key.startswith('bts_'):
                continue

            kind = key.replace('_sys', '')
            if kind in ['lzr', 'hlt']:
                dir_name = 'trg'
            else:
                dir_name = kind 

            wgt_dir = f'{cal_dir}/{dir_name}'

            try:
                ver = get_last_version(wgt_dir, version_only=True, main_only=True)
            except:
                self.log.error(f'Cannot find version for: {wgt_dir}')
                raise

            d_set[f'{kind}_ver'] = ver

        self._d_set = d_set
    #-----------------------------------
    def _set_kin_dir(self):
        try:
            cal_dir = os.environ['CALDIR']
        except:
            self.log.error('Cannot extract CALDIR variable from environment')
            raise

        utnr.check_dir(cal_dir)

        weight_reader.kin_dir = cal_dir
    #-----------------------------------
    def get_reader(self, kind, df):
        '''
        '''
        self._initialize()

        if kind in ['raw', 'sel'] and not hasattr(df, 'trigger'):
            self.log.error(f'Dataframe has no trigger attribute for reader of kind {kind}')
            raise

        if kind not in self._l_kind:
            self.log.error(f'Kind {kind} not valid, use:')
            utnr.pretty_print(self._l_kind)
            raise
        #----------------
        rdr           = weight_reader(df, kind)
        rdr.valdir    = f'{self._val_dir}/{kind}'
        #----------------
        s_wgt = set(self._s_wgt)

        rdr['bts'] = self._d_wgt['bts'] 
        s_wgt.remove('bts')

        if 'gen' in self._d_wgt:
            rdr['gen'] = self._d_wgt['gen'] 
            s_wgt.remove('gen')

        if kind in ['gen', 'rec']:
            return rdr 
        #----------------
        if 'rec' in self._d_wgt:
            rdr['rec'] = self._d_wgt['rec'] 
            s_wgt.remove('rec')

        if kind == 'raw':
            return rdr 
        #----------------
        for wgt in s_wgt:
            if wgt in self._d_wgt:
                rdr[wgt] = self._d_wgt[wgt] 
        #----------------
        return rdr
#----------------------------------------

