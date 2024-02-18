from rk.eff_yld_loader import eff_yld_loader as eyl

import utils_noroot as utnr
import os
import logging
import re 
import numpy 

class model_const:
    '''
    Used to retrieve mean and width of multidimensional Gaussian that constrains
    c_K in final fit.
    '''
    log=utnr.getLogger(__name__)
    def __init__(self, eff=None, yld=None):
        self._eff = eff
        self._yld = yld
        self._wgt = 'p01_t01_g01_l01_h01_r01_q01'

        self._eff_dir = '/publicfs/lhcb/user/campoverde/checks/Efficiencies/output/efficiencies'
        self._yld_dir = '/publicfs/lhcb/user/campoverde/Data/model/fits'

        self._rare = 'psi2'

        self._initialized = False
    #--------------------------
    def _initialize(self):
        if self._initialized:
            return

        eyl.log.setLevel(logging.WARNING)

        self._check_ver(self._eff_dir, self._eff)
        self._check_ver(self._yld_dir, self._yld)

        if self._rare != 'sign':
            self.log.warning(f'Not using signal as rare mode, but {self._rare}')

        self._initialized = True 
    #--------------------------
    def _get_ver(self, dir_path):
        dir_name = os.path.basename(dir_path)
        ver_num  = dir_name.replace('v', '')

        return int(ver_num)
    #--------------------------
    def _check_ver(self, dir_path, version):
        regex = 'v(\d+)$'
        mtch  = re.match(regex, version)
        if not mtch:
            self.log.error('Cannot match {regex} to {version}')
            raise

        version    = int(mtch.group(1))
        l_dir_path = utnr.glob_regex(dir_path, regex) 
        l_version  = [ self._get_ver(dir_path) for dir_path in l_dir_path]
        l_version.sort()

        if version not in l_version:
            self.log.error(f'Directory v{version} not found in {dir_path}')
            raise

        if version != l_version[-1]:
            self.log.warning(f'Using v{version}, not picking up the latest version among:')
            print(l_version)
    #--------------------------
    def _get_mu_year(self, year):
        o_ctrl_mtos = eyl(         'ctrl_mm', 'MTOS', year, self._wgt)
        o_ctrl_etos = eyl(         'ctrl_ee', 'ETOS', year, self._wgt)
        o_ctrl_gtis = eyl(         'ctrl_ee', 'GTIS', year, self._wgt)

        o_rare_mtos = eyl(f'{self._rare}_mm', 'MTOS', year, self._wgt)
        o_rare_etos = eyl(f'{self._rare}_ee', 'ETOS', year, self._wgt)
        o_rare_gtis = eyl(f'{self._rare}_ee', 'GTIS', year, self._wgt)

        (ctrl_mtos_yld, _), (ctrl_mtos_eff, _, _) = o_ctrl_mtos.get_values(eff_version=self._eff, yld_version=self._yld)
        (ctrl_etos_yld, _), (ctrl_etos_eff, _, _) = o_ctrl_etos.get_values(eff_version=self._eff, yld_version=self._yld)
        (ctrl_gtis_yld, _), (ctrl_gtis_eff, _, _) = o_ctrl_gtis.get_values(eff_version=self._eff, yld_version=self._yld)

        (_            , _), (rare_mtos_eff, _, _) = o_rare_mtos.get_values(eff_version=self._eff, yld_version=self._yld)
        (_            , _), (rare_etos_eff, _, _) = o_rare_etos.get_values(eff_version=self._eff, yld_version=self._yld)
        (_            , _), (rare_gtis_eff, _, _) = o_rare_gtis.get_values(eff_version=self._eff, yld_version=self._yld)

        #From: https://gitlab.cern.ch/-/ide/project/r_k/diagrams/edit/master/-/equations/mass_model.md#likelihood
        mu_tos = (ctrl_mtos_eff / ctrl_etos_eff) * (rare_etos_eff / rare_mtos_eff)  * (ctrl_etos_yld / ctrl_mtos_yld)
        mu_tis = (ctrl_mtos_eff / ctrl_gtis_eff) * (rare_gtis_eff / rare_mtos_eff)  * (ctrl_gtis_yld / ctrl_mtos_yld)

        return (mu_tos, mu_tis)
    #--------------------------
    def _get_mean(self):
        mu_r1_tos, mu_r1_tis = self._get_mu_year('r1')
        mu_16_tos, mu_16_tis = self._get_mu_year('2016')
        mu_17_tos, mu_17_tis = self._get_mu_year('2017')
        mu_18_tos, mu_18_tis = self._get_mu_year('2018')

        return numpy.array([mu_r1_tos, mu_r1_tis, mu_16_tos, mu_16_tis, mu_17_tos, mu_17_tis, mu_18_tos, mu_18_tis])
    #--------------------------
    def get_pars(self):
        self._initialize()

        mu = self._get_mean()

        return (mu, None)
#-----------------------------------------------

