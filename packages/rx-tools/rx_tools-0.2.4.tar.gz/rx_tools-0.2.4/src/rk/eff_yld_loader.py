import utils_noroot as utnr
import rk.utilities as rkut
import os
import re 
import tqdm

from rk.cutflow import cutflow
from ndict      import ndict

#------------------------------------------
class eff_yld_loader:
    log=utnr.getLogger('eff_yld_loader')
    #-------------------------------
    def __init__(self, sample=None, trigger=None, year=None, weights=None):
        self._sample  = sample
        self._trigger = trigger 
        self._year    = year 
        self._weights = weights 

        self._fit_dir = None
        self._eff_var = None
        self._eff_dir = os.environ['EFFDIR'] 

        self._l_sample = ['test_ee', 'ctrl_ee', 'ctrl_mm', 'psi2_ee', 'psi2_mm', 'sign_ee', 'sign_mm']
        self._l_trigger= ['test', 'MTOS', 'ETOS', 'GTIS']
        self._l_year   = ['test', 'r1', 'r2p1', '2017', '2018']
        self._l_weights= ['test'] + self._get_weights('<e15') + self._get_weights('>=e15') + self._get_weights('>=e17') + self._get_weights('>=e18') + self._get_weights('>=e53')

        self._initialzed = False
    #-------------------------------
    @property
    def eff_var(self):
        return self._eff_var

    @eff_var.setter
    def eff_var(self, value):
        self._eff_var = value
    #-------------------------------
    def _get_weights(self, kind):
        l_corr = []

        if   kind == '<e15':
            l_kind = ['p', 'g', 'l', 'h', 'r', 'q']
        elif kind in ['>=e15', '>=e17']:
            l_kind = ['p', 't', 'g', 'l', 'h', 'r', 'q']
        elif kind in ['>=e18']:
            l_kind = ['p', 't', 'g', 'l', 'h', 'r', 'q', 'b']
        elif kind in ['>=e53']:
            l_kind = ['p', 't', 'g', 'l', 'h', 'r', 'q', 'b', 's']
        else:
            self.log.error(f'Unrecognized weights of kind: {kind}')
            raise

        nwgt = len(l_kind)
        if kind in ['>=e17', '>=e18', '>=e53']:
            for i_corr in range(nwgt + 1): 
                l_flag_1 = ['all'] * i_corr + ['000'] * (nwgt - i_corr)
                l_flag_2 = ['nom'] * i_corr + ['000'] * (nwgt - i_corr)

                for l_flag in [l_flag_1, l_flag_2]:
                    l_set = [ f'{kind}{flg}' for kind, flg in zip(l_kind, l_flag) ]
                    corr  = '_'.join(l_set)
                    l_corr.append(corr)

            if kind in ['>=e53']:
                l_corr.append('pnom_tnom_gnom_lnom_hnom_rnom_qnom_bnom_sall')
                l_corr.append('pall_tall_gall_lall_hall_rall_qall_bnom_snom')
            else:
                l_corr.append('pnom_tnom_gnom_lnom_hnom_rnom_qnom_ball')
                l_corr.append('pall_tall_gall_lall_hall_rall_qall_bnom')
        else:
            for i_corr in range(nwgt + 1): 
                l_flag= ['1'.rjust(2, '0')] * i_corr + ['0'.rjust(2, '0')] * (nwgt - i_corr)
                l_set = [ f'{kind}{flg}' for kind, flg in zip(l_kind, l_flag) ]
                corr  = '_'.join(l_set)
                l_corr.append(corr)

        l_corr_fix = [ corr.replace('_s000', '_snom') for corr in l_corr ]

        return l_corr_fix
    #-------------------------------
    def _check_input(self, value, container):
        if value not in container:
            self.log.error(f'Invalid {value} not found in:')
            utnr.pretty_print(container)
            raise
    #-------------------------------
    def _initialize(self):
        if self._initialzed:
            return

        self._check_input(self._sample , self._l_sample )
        self._check_input(self._trigger, self._l_trigger)
        self._check_input(self._year   , self._l_year   )
        self._check_input(self._weights, self._l_weights)

        self._fit_dir = os.environ['FITDIR']

        self._initialized = True
    #-------------------------------
    def _check_version(self, version):
        if not isinstance(version, str):
            self.log.error(f'Version {version}, is not a string')
            raise

        if not re.match('v\d+', version):
            self.log.error(f'Version {version} is not valid.')
            raise
    #-------------------------------
    def get_values(self, yld_version=None, eff_version=None):
        self._check_version(yld_version)
        self._check_version(eff_version)
        self._initialize()


        (yld_val, yld_err) = self._get_yld(yld_version)
        eff_obj            = self._get_eff(eff_version)

        return ((yld_val, yld_err), eff_obj)
    #-------------------------------
    def _get_yld(self, version):
        if self._sample in ['sign_ee', 'sign_mm']:
            self.log.warning(f'Using a yield of 1 for sample {self._sample}')
            return [1, 0]

        proc      = utnr.get_regex_group(self._sample, '(test|ctrl|psi2)(_(ee|mm))?', i_group=1)
        json_path = utnr.get_path_from_wc(f'{self._fit_dir}/{version}/data/*/{proc}/{self._year}/pars_{self._trigger}.json')
    
        utnr.check_file(json_path)
        self.log.info(f'Extracting yields from {json_path}')
    
        d_data     = utnr.load_json(json_path)

        if   'nsig'    in d_data:
            [val, err] = utnr.get_from_dic(d_data, 'nsig'   )
        elif 'nsig_dt' in d_data:
            [val, err] = utnr.get_from_dic(d_data, 'nsig_dt')
        else:
            self.log.error(f'Cannot find signal yield among: {d_data.keys()}')
            raise
    
        return [val, err]
    #------------------------------------------
    def _check_keys(self, l_d_cfl):
        '''
        Check that the keys of all the dictionaries in list are the same
        '''
        l_key = l_d_cfl[0].keys() 
        for d_cfl in l_d_cfl:
            if l_key == d_cfl.keys():
                continue

            self.log.error(f'Efficiency object keys differ:')
            print(l_key)
            print(d_cfl.keys())
            raise
    #------------------------------------------
    def _get_cfl_from_wc(self, cf_wc):
        '''
        From wildcard string associated to pickle files containing cfl | {sys -> cfl} | {(sys, var) -> cfl}
        0.  If cutflow, add them all and return
        1a. Check that all keys are the same 
        1b. Add cutflow and put them in a new dictionary 
        '''
        l_cf_path = utnr.glob_wc(cf_wc)
        l_eff_obj = [ utnr.load_pickle(eff_obj_path) for eff_obj_path in l_cf_path ]

        if   isinstance(l_eff_obj[0], cutflow):
            eff_obj = sum(l_eff_obj[1:], l_eff_obj[0])
        elif isinstance(l_eff_obj[0], (dict, ndict)):
            self._check_keys(l_eff_obj)
            eff_obj = {} if isinstance(l_eff_obj[0], dict) else ndict()
            for d_cfl in l_eff_obj:
                for key, cfl in d_cfl.items():
                    if self._eff_var is not None and key[1] != self._eff_var:
                        continue

                    if key not in eff_obj:
                        eff_obj[key] = cfl
                    else:
                        try:
                            eff_obj[key]+= cfl
                        except:
                            cfl_1=eff_obj[key]
                            cfl_2=cfl

                            self.log.error(f'For {self._weights} cannot add cutflows:')
                            self.log.error(cfl_1)
                            self.log.error(cfl_2)
                            raise
        else:
            self.log.error(f'Object is of invalid type: {type(l_eff_obj[0])}')
            raise TypeError

        return eff_obj
    #------------------------------------------
    def _get_eff(self, version):
        cf_path_wc = f'{self._eff_dir}/{version}/*_{self._weights}/cf_tot_{self._sample}_{self._year}_{self._trigger}.pickle'
    
        self.log.info(f'Extracting efficiencies from {cf_path_wc}')
    
        eff_obj = self._get_cfl_from_wc(cf_path_wc)

        return eff_obj 
#------------------------------------------

