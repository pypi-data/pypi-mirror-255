import numpy
import logging
import math

import pandas            as pnd 
import utils_noroot      as utnr
import matplotlib.pyplot as plt

from rk.efficiency     import efficiency
from rk.eff_yld_loader import eff_yld_loader as eyl
from stats.covariance  import covariance

#------------------------------
class calculator:
    log=utnr.getLogger(__name__)
    #---------------
    def __init__(self, eff_version=None, yld_version=None, unc=None, mode=None, years=None, proc=None, turn_off=None):
        self._eff_version = eff_version 
        self._yld_version = yld_version 
        self._unc         = unc
        self._mode        = mode 
        self._l_year      = years
        self._l_proc      = proc
        self._l_turn_off  = turn_off

        self._tool_level  = logging.WARNING
        self._l_unc       = ['bts', 'sys', 'osc']
        self._l_mode      = ['cx', 'rx']
        self._l_good_year = ['r1', 'r2p1', '2017', '2018']
        self._l_good_proc = ['ctrl', 'psi2', 'sign']
        self._initialized = False

        self._nboost      = None 
        self._d_kind_quant= None 
        self._l_trig_year = None 
        self._weights     = None 

        self._arr_cx_nom  = None
        self._arr_px_nom  = None
        self._arr_rx_nom  = None
        self._arr_pc_nom  = None
        self._arr_rc_nom  = None

        self._plot_dir    = None
        self._l_column    = None
        self._d_d_cov     = None
        self._d_yld       = {} 
        self._d_d_eff     = {} 

        self._df_ce_ee    = None
        self._df_pe_ee    = None
        self._df_re_ee    = None

        self._df_ce_mm    = None
        self._df_pe_mm    = None
        self._df_re_mm    = None

        self._df_cx       = None
        self._df_px       = None
        self._df_rx       = None

        self._df_pc       = None
        self._df_rc       = None
    #---------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, plot_dir):
        self._plot_dir = utnr.make_dir_path(plot_dir)
    #---------------
    def _get_kind_quant(self):
        d_quant             = {}
        if   self._mode == 'rx':
            d_quant['r_jpsi'  ] = '$r_{J/\psi}$'
            d_quant['r_psi2'  ] = '$r_{\psi(2S)}$'
            d_quant['r_k'     ] = '$r_{eff}^{rare}=\\varepsilon(B \\to K ee)/\\varepsilon(B\\to K \mu\mu))$'
            d_quant['R_psi2'  ] = '$R_{\psi(2S)}$'
            d_quant['R_k'     ] = '$c_{k}$'
        elif self._mode == 'cx':
            d_quant['r_jpsi'  ] = '$r_{eff}^{J/\psi}=\\varepsilon(J/\psi \\to ee)/\\varepsilon(J/\psi \\to \mu\mu)$' 
            d_quant['r_psi2'  ] = '$r_{eff}^{\psi(2S)}=\\varepsilon(\psi(2S) \\to ee)/\\varepsilon(\psi(2S) \\to \mu\mu)$'
            d_quant['r_k'     ] = '$r_{eff}^{rare}=\\varepsilon(B \\to K ee)/\\varepsilon(B\\to K \mu\mu))$'
            d_quant['R_psi2'  ] = '$r_{eff}^{J\psi}/r_{eff}^{\psi(2S)}$'
            d_quant['R_k'     ] = '$r_{eff}^{J\psi}/r_{eff}^{rare}$'
        else:
            self.log.error(f'Invalid mode: {self._mode}')
            raise ValueError

        d_quant['c_eff_ee'] = '$\\varepsilon(J/\psi \\to ee)$'
        d_quant['p_eff_ee'] = '$\\varepsilon(\psi(2S) \\to ee)$'
        d_quant['r_eff_ee'] = '$\\varepsilon(B\\to K e e)$'

        d_quant['c_eff_mm'] = '$\\varepsilon(J/\psi \\to \mu\mu)$'
        d_quant['p_eff_mm'] = '$\\varepsilon(\psi(2S) \\to \mu\mu))$'
        d_quant['r_eff_mm'] = '$\\varepsilon(B\\to K\mu\mu))$'

        return d_quant
    #---------------
    def _initialize(self):
        if self._initialized:
            return

        utnr.check_included(self._unc , self._l_unc )
        utnr.check_included(self._mode, self._l_mode)

        self._check_proc()

        self._d_kind_quant = self._get_kind_quant()
        self._l_trig_year  = self._get_trig_year()

        if   self._unc == 'bts' and self._eff_version < 'v53':
            self._weights = 'pnom_tnom_gnom_lnom_hnom_rnom_qnom_ball'
        elif self._unc == 'bts' and self._eff_version >='v53':
            self._weights = 'pnom_tnom_gnom_lnom_hnom_rnom_qnom_bnom_sall'
        elif self._unc == 'sys' and self._eff_version < 'v53':
            self._weights = 'pall_tall_gall_lall_hall_rall_qall_bnom'
        elif self._unc == 'sys' and self._eff_version >='v53':
            self._weights = 'pall_tall_gall_lall_hall_rall_qall_bnom_snom'
        else:
            self.log.error(f'Not supported uncertainty {self._unc}')
            raise

        eyl.log.setLevel(self._tool_level)

        self._l_column    = [ f'{trig} {year}' for trig, year in self._l_trig_year]

        self._df_ce_ee    = pnd.DataFrame(columns=self._l_column)
        self._df_pe_ee    = pnd.DataFrame(columns=self._l_column)
        self._df_re_ee    = pnd.DataFrame(columns=self._l_column)

        self._df_ce_mm    = pnd.DataFrame(columns=self._l_column)
        self._df_pe_mm    = pnd.DataFrame(columns=self._l_column)
        self._df_re_mm    = pnd.DataFrame(columns=self._l_column)

        self._df_cx       = pnd.DataFrame(columns=self._l_column)
        self._df_px       = pnd.DataFrame(columns=self._l_column)
        self._df_rx       = pnd.DataFrame(columns=self._l_column)

        self._df_pc       = pnd.DataFrame(columns=self._l_column)
        self._df_rc       = pnd.DataFrame(columns=self._l_column)

        self._df_ce_ee.style.set_caption('Efficiency electron jpsi')
        self._df_pe_ee.style.set_caption('Efficiency electron psi2')
        self._df_re_ee.style.set_caption('Efficiency electron rare')

        self._df_ce_mm.style.set_caption('Efficiency muon jpsi')
        self._df_pe_mm.style.set_caption('Efficiency muon psi2')
        self._df_re_mm.style.set_caption('Efficiency muon rare')
                      
        self._df_cx.style.set_caption('r_jpsi')
        self._df_px.style.set_caption('r_psi2')
        self._df_rx.style.set_caption('r_rare')

        self._df_pc.style.set_caption('R_psi2')
        self._df_rc.style.set_caption('R_k')

        self._fill_df('nom', 'nom')

        self._arr_cx_nom  = self._df_cx.loc['nom'].to_numpy()
        self._arr_px_nom  = self._df_px.loc['nom'].to_numpy()
        self._arr_rx_nom  = self._df_rx.loc['nom'].to_numpy()

        self._arr_pc_nom  = self._df_pc.loc['nom'].to_numpy()
        self._arr_rc_nom  = self._df_rc.loc['nom'].to_numpy()

        self._nboost = self._get_nboost()
        self._s_syst = self._get_syst_flags()

        self._initialized = True
    #---------------
    def _check_proc(self):
        if self._l_proc is None:
            return

        for proc in self._l_proc:
            if proc not in self._l_good_proc:
                self.log.error(f'Invalid process: {proc}')
                self.log.error(f'Choose from: {self._l_good_proc}')
                raise
    #---------------
    def _get_nboost(self):
        obj      = eyl('psi2_ee', 'ETOS', self._l_year[-1], self._weights)
        _, d_eff = obj.get_values(eff_version = self._eff_version, yld_version=self._yld_version)
        obj.eff_var = 'B_PT'

        nboost = 1
        for sys, var in d_eff:
            if var != 'B_PT' or not sys.startswith('bts_'):
                continue

            nboost += 1

        return nboost
    #---------------
    def _get_syst_flags(self):
        obj_m    = eyl('psi2_mm', 'MTOS', self._l_year[-1], self._weights)
        obj_e    = eyl('psi2_ee', 'ETOS', self._l_year[-1], self._weights)
        obj_t    = eyl('psi2_ee', 'GTIS', self._l_year[-1], self._weights)

        obj_m.eff_var = 'B_PT'
        obj_e.eff_var = 'B_PT'
        obj_t.eff_var = 'B_PT'

        _, d_eff_m = obj_m.get_values(eff_version = self._eff_version, yld_version=self._yld_version)
        _, d_eff_e = obj_e.get_values(eff_version = self._eff_version, yld_version=self._yld_version)
        _, d_eff_t = obj_t.get_values(eff_version = self._eff_version, yld_version=self._yld_version)

        s_sys_m = { sys for sys, _ in d_eff_m.keys() }
        s_sys_e = { sys for sys, _ in d_eff_e.keys() }
        s_sys_t = { sys for sys, _ in d_eff_t.keys() }

        s_syst  = s_sys_e.union(s_sys_m, s_sys_t)

        l_syst = list(s_syst)
        l_syst.sort()
        if l_syst[0].startswith('bts_'):
            self.log.info(f'Number of bootstrapping sets found: {len(l_syst)}')
            return s_syst

        self.log.info('-'  * 30)
        self.log.info('Systematic flags found: ')
        self.log.info('-'  * 30)
        for syst in l_syst:
            self.log.info(syst)

        return s_syst
    #---------------
    def _get_trig_year(self):
        l_trig_year = []
        for year in self._l_good_year:
            l_trig_year += [('TOS', year), ('TIS', year)]

        return l_trig_year
    #---------------
    def _get_data(self, proc, trig, year, syst):
        key = f'{proc}_{trig}_{year}'

        proc_noch=proc[:4]
        skip_proc = (self._l_proc is not None) and (proc_noch not in self._l_proc)
        skip_year = (self._l_year is not None) and (year      not in self._l_year)

        if skip_proc or skip_year:
            self.log.warning(f'Allowed proceses, {self._l_proc}, this: {proc_noch}')
            self.log.warning(f'Allowed years, {self._l_year}, this: {year}')

            eff = efficiency(0, arg_fal=10, cut='cut_dummy', lab='lab_dummy')
            return [math.nan, math.nan], eff

        if key not in self._d_yld:
            self.log.info(f'Loading {key}')

            obj        = eyl(proc, trig, year, self._weights)
            obj.eff_var= 'B_PT'
            yld, d_eff = obj.get_values(eff_version = self._eff_version, yld_version=self._yld_version)

            if self._mode == 'cx' and proc != 'ctrl':
                yld = [1, 0]
                self.log.info(f'Setting yields for {proc} to {yld} for mode {self._mode}')

            self._d_yld[key]   = yld
            self._d_d_eff[key] = d_eff 

        d_eff = self._d_d_eff[key]
        yld   =   self._d_yld[key]

        #If systematic does not make sense (e.g. electron systematic applied to muon)
        #use nominal value
        if (syst, 'B_PT') not in d_eff:
            ctf = d_eff['nom', 'B_PT']
        else:
            ctf = d_eff[(syst, 'B_PT')]

        deff = ctf.efficiency
        oeff = deff.efficiency()

        return yld, oeff
    #---------------
    def _get_syst(self, syst, trig, year):
        trig = 'ETOS' if trig == 'TOS' else 'GTIS'

        c_yld_ee, c_eff_ee = self._get_data('ctrl_ee',   trig, year, syst)
        p_yld_ee, p_eff_ee = self._get_data('psi2_ee',   trig, year, syst)
        r_yld_ee, r_eff_ee = self._get_data('sign_ee',   trig, year, syst)

        c_yld_mm, c_eff_mm = self._get_data('ctrl_mm', 'MTOS', year, syst)
        p_yld_mm, p_eff_mm = self._get_data('psi2_mm', 'MTOS', year, syst)
        r_yld_mm, r_eff_mm = self._get_data('sign_mm', 'MTOS', year, syst)

        c_yld_rat          = c_yld_mm[0]     / c_yld_ee[0]
        p_yld_rat          = p_yld_mm[0]     / p_yld_ee[0]
        r_yld_rat          = r_yld_mm[0]     / r_yld_ee[0]

        c_eff_rat          = math.nan if c_eff_ee.val[0] == 0 else c_eff_mm.val[0] / c_eff_ee.val[0]
        p_eff_rat          = math.nan if p_eff_ee.val[0] == 0 else p_eff_mm.val[0] / p_eff_ee.val[0]
        r_eff_rat          = math.nan if r_eff_ee.val[0] == 0 else r_eff_mm.val[0] / r_eff_ee.val[0]

        r_jpsi             = c_yld_rat / c_eff_rat 
        r_psi2             = p_yld_rat / p_eff_rat 
        r_k                = r_yld_rat / r_eff_rat 

        R_p                = r_psi2    / r_jpsi
        R_k                = r_k       / r_jpsi

        d_data             = {}
        d_data['c_eff_ee'] =  c_eff_ee.val[0]
        d_data['p_eff_ee'] =  p_eff_ee.val[0]
        d_data['r_eff_ee'] =  r_eff_ee.val[0]

        d_data['c_eff_mm'] =  c_eff_mm.val[0]
        d_data['p_eff_mm'] =  p_eff_mm.val[0]
        d_data['r_eff_mm'] =  r_eff_mm.val[0]

        d_data['r_jpsi'  ] =  r_jpsi
        d_data['r_psi2'  ] =  r_psi2 
        d_data['r_k'     ] =  r_k

        d_data['R_psi2'  ] =  R_p 
        d_data['R_k'     ] =  R_k 

        return d_data 
    #---------------
    def _fill_df(self, syst, label):
        l_ce_ee = []
        l_re_ee = []
        l_pe_ee = []

        l_ce_mm = []
        l_re_mm = []
        l_pe_mm = []

        l_cx = []
        l_px = []
        l_rx = []

        l_pc = []
        l_rc = []

        for trig, year in self._l_trig_year:
            d_data = self._get_syst(syst, trig, year)

            ce_ee = d_data['c_eff_ee']
            pe_ee = d_data['p_eff_ee']
            re_ee = d_data['r_eff_ee']

            ce_mm = d_data['c_eff_mm']
            pe_mm = d_data['p_eff_mm']
            re_mm = d_data['r_eff_mm']

            cx    = d_data['r_jpsi'  ]
            px    = d_data['r_psi2'  ]
            rx    = d_data['r_k'     ]

            pc    = d_data['R_psi2'  ]
            rc    = d_data['R_k'     ]

            l_ce_ee.append(ce_ee)
            l_pe_ee.append(pe_ee)
            l_re_ee.append(re_ee)

            l_ce_mm.append(ce_mm)
            l_pe_mm.append(pe_mm)
            l_re_mm.append(re_mm)

            l_cx.append(cx)
            l_px.append(px)
            l_rx.append(rx)

            l_pc.append(pc)
            l_rc.append(rc)

        self._df_ce_ee = utnr.add_row_to_df(self._df_ce_ee, l_ce_ee, index=label)
        self._df_pe_ee = utnr.add_row_to_df(self._df_pe_ee, l_pe_ee, index=label)
        self._df_re_ee = utnr.add_row_to_df(self._df_re_ee, l_re_ee, index=label)

        self._df_ce_mm = utnr.add_row_to_df(self._df_ce_mm, l_ce_mm, index=label)
        self._df_pe_mm = utnr.add_row_to_df(self._df_pe_mm, l_pe_mm, index=label)
        self._df_re_mm = utnr.add_row_to_df(self._df_re_mm, l_re_mm, index=label)

        self._df_cx = utnr.add_row_to_df(self._df_cx, l_cx, index=label)
        self._df_px = utnr.add_row_to_df(self._df_px, l_px, index=label)
        self._df_rx = utnr.add_row_to_df(self._df_rx, l_rx, index=label)

        self._df_pc = utnr.add_row_to_df(self._df_pc, l_pc, index=label)
        self._df_rc = utnr.add_row_to_df(self._df_rc, l_rc, index=label)

        return label
    #---------------
    def _get_syst_label(self, label):
        if   'gen' in label:
            l_flag = [ flag for flag in self._s_syst if 'gen' in flag ]
        elif 'rec' in label:
            flag   = {'rec_to': 'rec_GTIS_ee', 'rec_ti': 'rec_ETOS_ee', 'rec_mu' : 'rec_GTIS_mm'}[label]
            l_flag = [flag]
        elif label == 'lzr_mu':
            l_flag = [ flag for flag in self._s_syst if 'lzr_L0Muon'     in flag ]
        elif label == 'lzr_el':
            l_flag = [ flag for flag in self._s_syst if 'lzr_L0Electron' in flag ]
        elif label == 'lzr_ts':
            l_flag = [ flag for flag in self._s_syst if 'lzr_L0TIS'      in flag ]
        elif 'pid_kp_el' in label:
            l_flag = [ flag for flag in self._s_syst if 'pid_kpel'       in flag ]
        elif 'pid_kp_mu' in label:
            l_flag = [ flag for flag in self._s_syst if 'pid_kpmu'       in flag ]
        elif 'pid_el'    in label:
            l_flag = [ flag for flag in self._s_syst if 'pid_el'         in flag ]
        elif 'pid_mu'    in label:
            l_flag = [ flag for flag in self._s_syst if 'pid_mu'         in flag ]
        elif 'qsq'       in label:
            l_flag = [ flag for flag in self._s_syst if 'qsq_'           in flag ]
        elif 'bts'       in label:
            l_flag = [ flag for flag in self._s_syst if 'bts_'           in flag ]
        else:
            self.log.error(f'Cannot find flags for label {label} among:')
            self.log.info(self._s_syst)
            raise ValueError

        if len(l_flag) == 0:
            self.log.error(f'No systematic labels found for {label} among:')
            self.log.info(self._s_syst)
            raise

        return l_flag
    #---------------
    def _get_zero_matrices(self, label):
        self.log.warning(f'Turning off: {label}')
        matrix_size = self._arr_cx_nom.size

        cov_nl = numpy.zeros((matrix_size, matrix_size))

        return {'cx' : cov_nl, 'px' : cov_nl, 'rx' : cov_nl, 'pc' : cov_nl, 'rc' : cov_nl}
    #---------------
    def _get_cov(self, label):
        l_syst        = self._get_syst_label(label)
        skip_syst     = self._l_turn_off is not None and label in self._l_turn_off

        l_arr_cx_syst = []
        l_arr_px_syst = []
        l_arr_rx_syst = []

        l_arr_pc_syst = []
        l_arr_rc_syst = []

        for syst in l_syst:
            label = syst.split('.')[0]
            if skip_syst:
                index   = self._fill_df('nom', label)
                continue
            else:
                index   = self._fill_df(syst, label)

            arr_cx_syst = self._df_cx.loc[index].to_numpy()
            arr_px_syst = self._df_px.loc[index].to_numpy()
            arr_rx_syst = self._df_rx.loc[index].to_numpy()

            arr_pc_syst = self._df_pc.loc[index].to_numpy()
            arr_rc_syst = self._df_rc.loc[index].to_numpy()

            l_arr_cx_syst.append(arr_cx_syst) 
            l_arr_px_syst.append(arr_px_syst) 
            l_arr_rx_syst.append(arr_rx_syst) 

            l_arr_pc_syst.append(arr_pc_syst) 
            l_arr_rc_syst.append(arr_rc_syst) 

        if skip_syst:
            return self._get_zero_matrices(label)

        mat_cx_syst = numpy.array(l_arr_cx_syst)
        mat_px_syst = numpy.array(l_arr_px_syst)
        mat_rx_syst = numpy.array(l_arr_rx_syst)
        mat_pc_syst = numpy.array(l_arr_pc_syst)
        mat_rc_syst = numpy.array(l_arr_rc_syst)

        obj_cx = covariance(mat_cx_syst.T, self._arr_cx_nom)
        cov_cx = obj_cx.get_cov()

        obj_px = covariance(mat_px_syst.T, self._arr_px_nom)
        cov_px = obj_px.get_cov()

        obj_rx = covariance(mat_rx_syst.T, self._arr_rx_nom)
        cov_rx = obj_rx.get_cov()

        obj_pc = covariance(mat_pc_syst.T, self._arr_pc_nom)
        cov_pc = obj_pc.get_cov()

        obj_rc = covariance(mat_rc_syst.T, self._arr_rc_nom)
        cov_rc = obj_rc.get_cov()

        return {'cx' : cov_cx, 'px' : cov_px, 'rx' : cov_rx, 'pc' : cov_pc, 'rc' : cov_rc}
    #---------------
    def _plot_df(self, df_org, column, kind):
        nom_val = df_org.iloc[0][column]
        df      = df_org.sort_index()
        if self._plot_dir is None:
            return

        nrm_col = f'{column} nrm'

        df[nrm_col]= 100 * (df[column] - nom_val) / nom_val

        df=df.drop('nom')

        fig, ax = plt.subplots(figsize=(10,4))

        arr_val = df[ column].values
        arr_nrm = df[nrm_col].values

        ax.axhline(y=nom_val, color='red')
        if self._unc == 'bts':
            ax.plot(arr_val, marker='o', linestyle='None')
            rms = numpy.sqrt(numpy.mean( (df[column] - nom_val) ** 2))
            ax.axhline(y=nom_val + rms , color='red', linestyle=':')
            ax.axhline(y=nom_val - rms , color='red', linestyle=':')
            ax.legend(['Nominal', 'Systematic', '$+1\sigma$', '$-1\sigma$'])
        else:
            ax.plot(arr_val) 
            ax.legend(['Nominal', 'Systematic'])

        l_loc, l_lab = utnr.get_axis(df, 'index')
        if self._unc != 'bts':
            plt.xticks(l_loc, l_lab, rotation=80)

        ex=ax.twinx()
        ex.plot(arr_nrm, alpha=0, color='red')

        ax.grid()
        plt.title(column)

        quant = self._d_kind_quant[kind]
        ax.set_ylabel(quant)
        ex.set_ylabel('Bias [%]')

        fig.tight_layout()

        syst_dir = utnr.make_dir_path(f'{self._plot_dir}/syst_{kind}')
        plot_name= column.replace(' ', '_') + '.png'
        plot_path= f'{syst_dir}/{plot_name}'

        self.log.visible(f'Saving to: {plot_path}')
        fig.savefig(plot_path)
        plt.close('all')
    #---------------
    def _get_all_cov(self):
        d_cov = {}

        if   self._unc == 'bts':
            d_cov['bts']       = self._get_cov('bts'   )
        elif self._unc == 'sys':
            d_cov['gen']       = self._get_cov('gen'   ) 

            d_cov['rec_to']    = self._get_cov('rec_to') 
            d_cov['rec_ti']    = self._get_cov('rec_ti') 
            d_cov['rec_mu']    = self._get_cov('rec_mu') 

            d_cov['lzr_mu']    = self._get_cov('lzr_mu') 
            d_cov['lzr_el']    = self._get_cov('lzr_el') 
            d_cov['lzr_ts']    = self._get_cov('lzr_ts') 

            d_cov['pid_kp_el'] = self._get_cov('pid_kp_el') 
            d_cov['pid_kp_mu'] = self._get_cov('pid_kp_mu')
            d_cov['pid_el'   ] = self._get_cov('pid_el')
            d_cov['pid_mu'   ] = self._get_cov('pid_mu')

            d_cov['qsq'   ]    = self._get_cov('qsq'   )
        else:
            self.log.error(f'Invalid uncertainty type: {self._unc}')
            raise

        return d_cov
     #---------------
    def _plot_all_df(self):
        for column in self._l_column:
            self._plot_df(self._df_ce_ee, column, 'c_eff_ee')
            self._plot_df(self._df_pe_ee, column, 'p_eff_ee')
            self._plot_df(self._df_re_ee, column, 'r_eff_ee')

            self._plot_df(self._df_ce_mm, column, 'c_eff_mm')
            self._plot_df(self._df_pe_mm, column, 'p_eff_mm')
            self._plot_df(self._df_re_mm, column, 'r_eff_mm')

            self._plot_df(self._df_cx   , column, 'r_jpsi'  )
            self._plot_df(self._df_px   , column, 'r_psi2'  )
            self._plot_df(self._df_rx   , column, 'r_k'     )

            self._plot_df(self._df_pc   , column, 'R_psi2'  )
            self._plot_df(self._df_rc   , column, 'R_k'     )
    #---------------
    def _get_rel_cov(self, d_cv_ij):
        cx_ij = numpy.outer(self._arr_cx_nom, self._arr_cx_nom)
        d_cv_ij['cx'] = d_cv_ij['cx'] / cx_ij

        px_ij = numpy.outer(self._arr_px_nom, self._arr_px_nom)
        d_cv_ij['px'] = d_cv_ij['px'] / px_ij

        rx_ij = numpy.outer(self._arr_rx_nom, self._arr_rx_nom)
        d_cv_ij['rx'] = d_cv_ij['rx'] / rx_ij

        pc_ij = numpy.outer(self._arr_pc_nom, self._arr_pc_nom)
        d_cv_ij['pc'] = d_cv_ij['pc'] / pc_ij

        rc_ij = numpy.outer(self._arr_rc_nom, self._arr_rc_nom)
        d_cv_ij['rc'] = d_cv_ij['rc'] / rc_ij

        return d_cv_ij 
    #---------------
    def _save_df(self):
        self._save_table(self._df_cx, 'r_jpsi')
        self._save_table(self._df_px, 'r_psi2')
        self._save_table(self._df_rx, 'r_k'   )

        self._save_table(self._df_pc, 'R_psi2')
        self._save_table(self._df_rc, 'R_k'   )
    #---------------
    def _save_table(self, df, label):
        if self._plot_dir is None:
            return

        table_dir  = utnr.make_dir_path(f'{self._plot_dir}/tables')
        table_path = f'{table_dir}/{label}.tex'

        df.index=df.index.map(lambda value: value.replace('_', '\_'))
        utnr.df_to_tex(df, table_path, hide_index=False)
    #---------------
    def _swap_keys(self, d_d_cov):
        d_d_knd = {}
        for sys, d_cov in d_d_cov.items():
            for knd, cov in d_cov.items():
                if knd in d_d_knd:
                    d_d_knd[knd][sys] = cov
                else:
                    d_d_knd[knd] = { sys : cov}

        return d_d_knd
    #---------------
    def cov(self, relative=False):
        self._initialize()

        if self._d_d_cov is None:
            self._d_d_cov = self._get_all_cov()
            self._plot_all_df()
            self._save_df()

        if relative:
            d_d_cov = {syst : self._get_rel_cov(d_cov) for syst, d_cov in self._d_d_cov.items() }
        else:
            d_d_cov = self._d_d_cov

        d_d_cov = self._swap_keys(d_d_cov)

        return d_d_cov
#------------------------------

