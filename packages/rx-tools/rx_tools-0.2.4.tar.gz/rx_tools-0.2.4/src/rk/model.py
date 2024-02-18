import ROOT
import math
import os
import logging

import utils
import zfit
import pandas         as pnd
import utils_noroot   as utnr
import read_selection as rsel

from rk.mva       import mva_man
from rk.pr_shapes import pr_loader   as prc_ldr
from zutils.pdf   import FermiDirac  as zpdf_fd
from fit_manager  import fit_manager as ftm

log=utnr.getLogger(__name__)
#-----------------------------------------
class zmodel:
    log=utnr.getLogger('zmodel')
    #-----------------------------------------
    def __init__(self, proc=None, trig=None, q2bin=None, year=None, obs=None, mass=None):
        self._proc        = proc
        self._trig        = trig 
        self._q2bin       = q2bin
        self._year        = year 
        self._obs         = obs
        self._mass        = mass

        self._l_proc_sig  = ['ctrl'   , 'psi2'   , 'ctrl_binned']
        self._l_proc_csp  = ['ctrl_pi', 'psi2_pi']
        self._l_proc      = self._l_proc_sig + self._l_proc_csp
        self._l_year      = ['r1', '2011', '2012', 'r2p1','2015','2016', '2017', '2018']
        self._l_q2bin     = ['jpsi', 'psi2', 'high']
        self._l_trig_ee   = ['ETOS', 'GTIS', 'GTIS_ee', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0ElectronHAD', 'L0HadronElEL']
        self._l_trig_mm   = ['MTOS', 'L0MuonALL1', 'L0MuonALL2', 'L0MuonTIS', 'L0MuonMU1', 'L0MuonMU2', 'L0MuonHAD', 'GTIS_mm']
        self._l_trig      = self._l_trig_ee + self._l_trig_mm 

        self._suffix      = None
        self._chan        = None
        self._use_br_wgt  = None
        self._nbrem       = None

        self._initialized = False
    #-----------------------------------------
    def _check_valid(self, choice, l_choice):
        if choice not in l_choice:
            self.log.error(f'Invalid value: {choice}, choose from:')
            print(l_choice)
            raise
    #-----------------------------------------
    def _check_valid_value(self, par, value=None, error=None):
        utnr.check_none(value)
        utnr.check_none(error)

        par_name = par.GetName()
        if error <= 0:
            self.log.error(f'Parameter {par_name} has invalid error: {par_error:.3e}')
            raise

        min_val = par.getMin()
        max_val = par.getMax()

        if (min_val < value < max_val) == False:
            self.log.error(f'Parameter {par_name} = {value:.3e} is not within bounds [{min_val:.3e}, {max_val:.3e}]')
            raise
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_valid(self._proc , self._l_proc)
        self._check_valid(self._trig , self._l_trig)
        self._check_valid(self._q2bin, self._l_q2bin)
        self._check_valid(self._year , self._l_year)

        self._chan = 'ee' if self._trig in self._l_trig_ee else 'mm'

        prc_ldr.log.setLevel(logging.WARNING)

        self._initialized = True
    #-----------------------------------------
    def _get_combinatorial(self, kind):
        if self._q2bin == 'jpsi':
            max_c_cmb = 0
        else:
            max_c_cmb = 0.01

        if   kind == 'expo':
            c   = zfit.param.Parameter(f'c_cmb_{self._suffix}', -0.005, -0.01, max_c_cmb) 
            pdf = zfit.pdf.Exponential(c, self._obs)
        elif kind == 'pol1':
            a   = zfit.param.Parameter(f'a_cmb_{self._suffix}', -0.005, -0.95, 0.00)
            pdf = zfit.pdf.Chebyshev(obs=self._obs, coeffs=[a])
        elif kind == 'pol2':
            a   = zfit.param.Parameter(f'a_cmb_{self._suffix}', -0.005, -0.95, 0.00)
            b   = zfit.param.Parameter(f'b_cmb_{self._suffix}',  0.000, -0.95, 0.95)
            pdf = zfit.pdf.Chebyshev(obs=self._obs, coeffs=[a, b])
        else:
            log.error(f'Invalid combinatirial of kind: {kind}')
            raise

        return pdf
    #-----------------------------------------
    def _get_fd_prec(self, suffix):
        self.log.warning('Using Fermi-Dirac for PR')
    
        mu  = zfit.param.Parameter(f'mu_prec_{suffix}', 5135, 5125, 5160)
        sg  = zfit.param.Parameter(f'sg_prec_{suffix}', 7   ,    2,   35)
        pdf = zpdf_fd(obs=self._obs, mu=mu, ap=sg)

        return pdf
    #-----------------------------------------
    def _get_ke_prec(self, merged=None):
        obj       = prc_ldr(proc='b*XcHs', trig=self._trig, q2bin=self._q2bin, dset=self._year)
        if self._nbrem is not None:
            obj.nbrem = int(self._nbrem)

        if   merged == True:
            pdf = obj.get_pdf(obs=self._obs, mass=self._mass, name='PRec'        , use_weights=self._use_br_wgt, bandwidth=10, padding=0.1)
        elif merged == False:
            pdf = obj.get_sum(obs=self._obs, mass=self._mass, name='PRec (split)', use_weights=self._use_br_wgt, bandwidth=10, padding=0.1)
        else:
            self.log.error(f'Invalid merged value: {merged}')
            raise

        return pdf
    #-----------------------------------------
    def _get_prec(self, suffix, kind=None):
        log.info(f'Using Prec: {kind}')

        if   kind == 'fd':
            pdf = self._get_fd_prec(suffix)
        elif kind == 'ke_merged':
            pdf = self._get_ke_prec(merged=True)
        elif kind ==  'ke_split':
            pdf = self._get_ke_prec(merged=False)
        else:
            self.log.error(f'Invalid PR type: {kind}')
            raise

        return pdf
    #-----------------------------------------
    def _get_2cb_signal(self, suffix=None):
        self.log.visible('Using 2CB signal')
        mu  = zfit.param.Parameter(f'mu{suffix}', 5300, 5250, 5350)
        
        sg1 = zfit.param.Parameter(f'sg1{suffix}' , 10, 2, 300)
        sg2 = zfit.param.Parameter(f'sg2{suffix}' , 15, 2, 300)
        
        ar  = zfit.param.Parameter(f'ar{suffix}' , -3., -1.)
        al  = zfit.param.Parameter(f'al{suffix}' , +1., +3.)
    
        nr  = zfit.param.Parameter(f'nr{suffix}' , 1, 0.5, 5) 
        nl  = zfit.param.Parameter(f'nl{suffix}' , 2, 0.5, 5) 
    
        cb1 = zfit.pdf.CrystalBall(mu, sg1, ar, nr, self._obs)
        cb2 = zfit.pdf.CrystalBall(mu, sg2, al, nl, self._obs)
    
        frc = zfit.param.Parameter(f'frc{suffix}', 0.5, 0, 1) 
        
        pdf = zfit.pdf.SumPDF([cb1, cb2], frc)
    
        return pdf 
    #-----------------------------------------
    def _get_3cbr_signal(self, suffix=None):
        self.log.visible('Using 3CB signal')

        min_mu = 5000 if self._mass == 'mass' else 5250
        mu  = zfit.param.Parameter(f'mu{suffix}', 5300, min_mu, 5350)

        max_sg =  200 if self._mass == 'mass' else 40
        sg1 = zfit.param.Parameter(f'sg1{suffix}',  10, 2.0, max_sg)
        
        r21 = zfit.param.Parameter(f'r21{suffix}', 1.0, 0.1, 20)
        r31 = zfit.param.Parameter(f'r31{suffix}', 1.0, 0.1, 20)

        sg2 = zfit.ComposedParameter(f'sg2{suffix}', lambda d_par : d_par['p1'] * d_par['p2'], {'p1' : r21, 'p2' : sg1} )
        sg3 = zfit.ComposedParameter(f'sg3{suffix}', lambda d_par : d_par['p1'] * d_par['p2'], {'p1' : r31, 'p2' : sg1} )
        
        ar  = zfit.param.Parameter(f'ar{suffix}', -2, -4., -1.)
        al  = zfit.param.Parameter(f'al{suffix}',  2,  1.,  4.)
        ac  = zfit.param.Parameter(f'ac{suffix}',  2,  1.,  4.)
    
        nr  = zfit.param.Parameter(f'nr{suffix}', 1, 0.5, 5) 
        nl  = zfit.param.Parameter(f'nl{suffix}', 2, 0.5, 5) 
        nc  = zfit.param.Parameter(f'nc{suffix}', 3, 0.5, 5) 
    
        cb1 = zfit.pdf.CrystalBall(mu, sg1, ar, nr, self._obs)
        cb2 = zfit.pdf.CrystalBall(mu, sg2, al, nl, self._obs)
        cb3 = zfit.pdf.CrystalBall(mu, sg3, ac, nc, self._obs)
    
        f_1 = zfit.param.Parameter(f'f_1{suffix}', 0.5, 0, 1) 
        f_2 = zfit.param.Parameter(f'f_2{suffix}', 0.5, 0, 1) 
        
        pdf = zfit.pdf.SumPDF([cb1, cb2, cb3], [f_1, f_2])
    
        return pdf 
    #-----------------------------------------
    def _get_dscb_signal(self, suffix):
        self.log.visible('Using DSCB signal')

        mu  = zfit.param.Parameter(f'mu_dscb{suffix}' , 5300, 5250, 5400)
        sg  = zfit.param.Parameter(f'sg_dscb{suffix}' ,   10,    2,   30)
        ar  = zfit.param.Parameter(f'ar_dscb{suffix}' ,    1,    0,    5)
        al  = zfit.param.Parameter(f'al_dscb{suffix}' ,    1,    0,    5)
        nr  = zfit.param.Parameter(f'nr_dscb{suffix}' ,    2,    1,    5)
        nl  = zfit.param.Parameter(f'nl_dscb{suffix}' ,    2,    0,    5)
    
        pdf = zfit.pdf.DoubleCB(mu, sg, al, nl, ar, nr, self._obs)
    
        return pdf 
    #-----------------------------------------
    def get_signal(self, suffix='none'):
        self._initialize()

        if self._suffix is None:
            suffix = f'_{suffix}_{self._proc}'
        else:
            suffix = f'_{self._suffix}_{suffix}_{self._proc}'

        if   self._proc in ['ctrl', 'ctrl_pi', 'psi2'] and self._chan == 'mm':
            pdf = self._get_dscb_signal(suffix)
        elif self._proc in ['ctrl', 'ctrl_pi', 'psi2'] and self._chan == 'ee':
            pdf = self._get_3cbr_signal(suffix)
        else:
            self.log.error(f'Invalid channel {self._chan} or process {self._proc}')
            raise

        return pdf 
    #-----------------------------------------
    def _extend_prc(self, pdf, suffix):
        if pdf.is_extended:
            return pdf

        nprc    = zfit.param.Parameter(f'nprc_{suffix}', 100., 0., 100000)

        if isinstance(pdf, zfit.pdf.KDE1DimFFT):
            pdf.set_yield(nprc)
        else:
            pdf=pdf.create_extended(nprc, 'PRec')

        return pdf
    #-----------------------------------------
    def get_model(self, suffix=None, skip_csp=False, skip_prc=False, use_br_wgt=True, com_kind='expo', prc_kind='ke_merged', brem=None):
        self._initialize()

        self._nbrem      = brem
        self._suffix     = suffix
        self._use_br_wgt = use_br_wgt

        self.log.visible('Getting model')
    
        pdf_sig = self.get_signal(suffix='kp')    

        self.log.visible(f'Returning full PDF')

        pdf_cmb = self._get_combinatorial(com_kind)
    
        ncmb = zfit.param.Parameter(f'ncmb_{suffix}', 1000., 0., 1000000)
        nsig = zfit.param.Parameter(f'nsig_{suffix}', 1000., 0., 1000000)

        pdf_cmb = pdf_cmb.create_extended(ncmb, name='Combinatorial')
        pdf_sig = pdf_sig.create_extended(nsig, name=r'$B^+\to J/\psi(\to \ell\ell)K^+$')
    
        if   self._chan == 'mm' and self._proc.startswith('psi2'):
            model = zfit.pdf.SumPDF([pdf_sig, pdf_cmb], name='Model')
        elif self._chan == 'mm' and self._proc.startswith('ctrl'):
            pdf_csp = self.get_signal(suffix='pi')
            ncsp    = zfit.param.Parameter(f'ncsp_{suffix}', 0., 0., 1000000)
            pdf_csp = pdf_csp.create_extended(ncsp, name=r'$B^+\to J/\psi(\to \ell\ell)\pi^+$')

            if skip_csp:
                model = zfit.pdf.SumPDF([pdf_sig, pdf_cmb], name='Model')
            else:
                model = zfit.pdf.SumPDF([pdf_sig, pdf_csp, pdf_cmb], name='Model')
        elif self._chan == 'ee' and self._proc.startswith('ctrl'):
            pdf_prc = self._get_prec(suffix, kind=prc_kind)
            pdf_prc = self._extend_prc(pdf_prc, suffix)

            if   skip_csp and not skip_prc:
                self.log.warning('Skipping Cabbibo suppressed component')
                model = zfit.pdf.SumPDF([pdf_sig, pdf_prc, pdf_cmb], name='Model') 
            elif skip_prc and not skip_csp:
                self.log.warning('Skipping PRec component')
                model = zfit.pdf.SumPDF([pdf_sig, pdf_csp, pdf_cmb], name='Model') 
            elif skip_prc and     skip_csp:
                self.log.warning('Skipping Cabbibo suppressed component and PRec')
                model = zfit.pdf.SumPDF([pdf_sig, pdf_cmb], name='Model') 
            else:
                pdf_csp = self.get_signal(suffix='pi')
                ncsp    = zfit.param.Parameter(f'ncsp_{suffix}', 0., 0., 1000000)
                pdf_csp = pdf_csp.create_extended(ncsp, name=r'$B^+\to J/\psi(\to \ell\ell)\pi^+$')

                model = zfit.pdf.SumPDF([pdf_sig, pdf_prc, pdf_csp, pdf_cmb], name='Model')
        elif self._chan == 'ee' and self._proc.startswith('psi2'): 
            pdf_prc = self._get_prec(suffix, kind=prc_kind)
            pdf_prc = self._extend_prc(pdf_prc, suffix)
    
            model = zfit.pdf.SumPDF([pdf_sig, pdf_prc, pdf_cmb], name='Model')
        else:
            self.log.error(f'Invalid process "{self._proc}" and trigger "{self._chan}"')
            raise

        return model
#-----------------------------------------
class model:
    log=utnr.getLogger('model')
    #-----------------------------------------
    def __init__(self, proc, trig, year):
        self._proc        = proc
        self._trig        = trig 
        self._year        = year 

        self._obsname     = 'mass' 
        self._initialized = False

        self._pr_type     = 'ke'
        self._yield       = None

        self._l_proc_sig  = ['ctrl'   , 'psi2'   , 'ctrl_binned']
        self._l_proc_csp  = ['ctrl_pi', 'psi2_pi']

        self._l_proc      = self._l_proc_sig + self._l_proc_csp
        self._l_trig_ee   = ['ETOS', 'GTIS', 'GTIS_ee', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0ElectronHAD', 'L0HadronElEL']
        self._l_trig_mm   = ['MTOS', 'L0MuonALL1', 'L0MuonALL2', 'L0MuonTIS', 'L0MuonMU1', 'L0MuonMU2', 'L0MuonHAD', 'GTIS_mm']
        self._l_trig      = self._l_trig_ee + self._l_trig_mm 

        self._l_year      = ['r1', '2011', '2012', 'r2p1','2015','2016', '2017', '2018']

        self._l_float_par = []
        self._mass        = None
        self._obsbranch   = None
        self._q2bin       = None

        self._val_dir     = None
    #-----------------------------------------
    def _check_valid(self, choice, l_choice):
        if choice not in l_choice:
            self.log.error(f'Invalid value: {choice}, choose from:')
            print(l_choice)
            raise
    #-----------------------------------------
    def _check_valid_value(self, par, value=None, error=None):
        utnr.check_none(value)
        utnr.check_none(error)

        par_name = par.GetName()
        if error <= 0:
            self.log.error(f'Parameter {par_name} has invalid error: {par_error:.3e}')
            raise

        min_val = par.getMin()
        max_val = par.getMax()

        if (min_val < value < max_val) == False:
            self.log.error(f'Parameter {par_name} = {value:.3e} is not within bounds [{min_val:.3e}, {max_val:.3e}]')
            raise
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_valid(self._proc, self._l_proc)
        self._check_valid(self._trig, self._l_trig)
        self._check_valid(self._year, self._l_year)

        self._chan = 'ee' if self._trig in self._l_trig_ee else 'mm'
        self._setup_obs()

        self._q2bin   = get_q2bin(self._proc)
        self._fit_dir = os.environ['FITDIR']
        self._prc_dir = os.environ['PRCDIR']

        self._initialized = True
    #-----------------------------------------
    def _setup_obs(self):
        self._obsbranch = get_mass_branch(self._proc)
        self._mass      = get_obs(self._proc, self._chan, name=self._obsname)
    #-----------------------------------------
    def _add_combinatorial(self, wks):
        self._l_float_par += ['c_cmb']

        c   = ROOT.RooRealVar('c_cmb', '', -0.01, 0.00)
        obs = wks.var(self._obsname)
        pdf = ROOT.RooExponential('cmb', 'Combinatorial', obs, c)
    
        wks.Import(pdf)
    #-----------------------------------------
    def _add_fd_prec(self, wks):
        self.log.warning('Using Fermi-Dirac for PR')
    
        mu  = ROOT.RooRealVar('mu_prec', '', 5100, 5200)
        sg  = ROOT.RooRealVar('sg_prec', '',    1,   30)
    
        obs = wks.var(self._obsname)
        pdf = ROOT.FermiDirac('prc', 'Prec-FD', obs, mu, sg)
    
        wks.Import(pdf)
    #-----------------------------------------
    def _get_ke_prec(self, kind):
        file_path = utnr.get_latest(f'{self._prc_dir}/VERSION/{kind}_{self._trig}_{self._q2bin}_{self._year}/workspace.root')
        self.log.visible(f'PR model: "{file_path}"')
        wks, _ = utils.get_from_file('wks', file_path)
    
        return wks
    #-----------------------------------------
    def _plot_prc(self, pdf, obs):
        if self._val_dir is None:
            return

        l_coef    = pdf.coefList()
        l_pdf_cmp = pdf.pdfList()
    
        self.log.info('---------------------------------')
        self.log.info(f'{"PR Fraction":<20}{"Value":<20}')
        self.log.info('---------------------------------')
        for coef in l_coef:
            name = coef.GetName()
            valu = coef.getVal()
            self.log.info(f'{name:<20}{valu:<20.3e}')
        self.log.info('---------------------------------')
    
        plot=obs.frame()
        pdf.plotOn(plot, ROOT.RooFit.Name('Prec'))
    
        d_label = {'Prec' : 'Prec'}
        for i_cmp, pdf_cmp in enumerate(l_pdf_cmp):
            name = pdf_cmp.GetName()
            title= pdf_cmp.GetTitle()
            pdf_cmp.plotOn(plot, ROOT.RooFit.Name(name), ROOT.RooFit.Components(name), ROOT.RooFit.LineColor(i_cmp + 1))
    
            d_label[name] = title
    
        utils.leg_xmax = utils.leg_xmax - 0.05
        utils.leg_xmax = 0.85
        label  = utils.getLegend(plot, d_label)
    
        can    = ROOT.TCanvas('can_pdf', '', 600, 400)
        plot.GetYaxis().SetRangeUser(1e-3, 10)
        plot.Draw()
        label.Draw()
        can.SetLogy()
        can.SaveAs(f'{self._val_dir}/pr_{self._trig}.png')
    #-----------------------------------------
    def _add_ke_prec(self, wks):
        self.log.visible('Using kernel estimate for PR')
        #----------------------
        wks_bp=self._get_ke_prec('bpXcHs_ee')
        pdf_bp=wks_bp.pdf('pdf')
        pdf_bp.SetName('bpx')
        pdf_bp.SetTitle('B^{+}#rightarrow cc X')
    
        wks_bd=self._get_ke_prec('bdXcHs_ee')
        pdf_bd=wks_bd.pdf('pdf')
        pdf_bd.SetName('bdx')
        pdf_bd.SetTitle('B_{d}#rightarrow cc X')
        #----------------------
        frac = ROOT.RooRealVar('bp_frac', '', 0., 1.)
        self._l_float_par += ['bp_frac']
    
        pdf  = ROOT.RooAddPdf('prc', 'Prec-KE', pdf_bp, pdf_bd, frac)
        obs  = wks.var(self._obsname)
    
        self._plot_prc(pdf, obs)
    
        wks.Import(pdf)
    #-----------------------------------------
    def _add_prec(self, wks):
        if   self._pr_type == 'fd':
            self._add_fd_prec(wks)
        elif self._pr_type == 'ke':
            self._add_ke_prec(wks)
        else:
            self.log.error(f'Invalid PR type "{self._pr_type}"')
            raise
    #-----------------------------------------
    def _add_2cb_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            self._l_float_par += ['mu_sig', 'sg1_sig', 'sg2_sig']
            suffix = ''
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        mu  = ROOT.RooRealVar(f'mu_sig{suffix}' , '', 5300, 5250, 5350)
        
        sg1 = ROOT.RooRealVar(f'sg1_sig{suffix}' , '', 10, 2, 300)
        sg2 = ROOT.RooRealVar(f'sg2_sig{suffix}' , '', 15, 2, 300)
        
        ar  = ROOT.RooRealVar(f'ar_sig{suffix}' , '', -3., -1.)
        al  = ROOT.RooRealVar(f'al_sig{suffix}' , '', +1., +3.)
    
        nr  = ROOT.RooRealVar(f'nr_sig{suffix}' , '', 1, 0.5, 5) 
        nl  = ROOT.RooRealVar(f'nl_sig{suffix}' , '', 2, 0.5, 5) 
    
        cb1 = ROOT.RooCBShape(f'cb1{suffix}' , 'CB1', self._mass, mu, sg1, ar, nr)
        cb2 = ROOT.RooCBShape(f'cb2{suffix}' , 'CB2', self._mass, mu, sg2, al, nl)
    
        frc = ROOT.RooRealVar(f'frc{suffix}' , '', 0, 1) 
        
        pdf = ROOT.RooAddPdf(f'sig{suffix}', '2CB', ROOT.RooArgList(cb1, cb2), ROOT.RooArgList(frc), True)
    
        wks.Import(pdf) 
    
        return f'sig{suffix}'
    #-----------------------------------------
    def _add_2cb_gaus_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            suffix = ''
            self._l_float_par += ['mu_sig', 'sg1_sig', 'sg2_sig', 'sg3_sig']
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        mu  = ROOT.RooRealVar(f'mu_sig{suffix}'  , '', 5300, 5250, 5350)
        
        sg1 = ROOT.RooRealVar(f'sg1_sig{suffix}' , '', 10, 2,  40)
        sg2 = ROOT.RooRealVar(f'sg2_sig{suffix}' , '', 15, 2,  40)
        sg3 = ROOT.RooRealVar(f'sg3_sig{suffix}' , '', 15, 2,  40)
        
        ar  = ROOT.RooRealVar(f'ar_sig{suffix}' , '', -4., 0.)
        al  = ROOT.RooRealVar(f'al_sig{suffix}' , '', 0.1, 6.)
    
        nr  = ROOT.RooRealVar(f'nr_sig{suffix}' , '', 1, 0.1, 7) 
        nl  = ROOT.RooRealVar(f'nl_sig{suffix}' , '', 2, 0.1, 7) 
    
        cb1 = ROOT.RooCBShape (f'cb1{suffix}' , 'CB1' , self._mass, mu, sg1, ar, nr)
        cb2 = ROOT.RooCBShape (f'cb2{suffix}' , 'CB2' , self._mass, mu, sg2, al, nl)
        gau = ROOT.RooGaussian(f'gau{suffix}' , 'Gaus', self._mass, mu, sg3)
    
        f_1 = ROOT.RooRealVar(f'f_1{suffix}' , '', 0, 1) 
        f_2 = ROOT.RooRealVar(f'f_2{suffix}' , '', 0, 1) 
        
        pdf = ROOT.RooAddPdf(f'sig{suffix}', '2CB + Gauss', ROOT.RooArgList(cb1, cb2, gau), ROOT.RooArgList(f_1, f_2), False)
    
        wks.Import(pdf)
    
        return f'sig{suffix}'
    #-----------------------------------------
    def _add_johnson_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            suffix = ''
            self._l_float_par += ['mu_sig', 'lb_sig']
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        mu  = ROOT.RooRealVar(f'mu_sig{suffix}', '', 5280, 5250, 5400)
        lb  = ROOT.RooRealVar(f'lb_sig{suffix}', '', 20, 2,  40)
        gm  = ROOT.RooRealVar(f'gm_sig{suffix}', '', -2, 5)
        dl  = ROOT.RooRealVar(f'dl_sig{suffix}', '', 0, 4)
    
        obs = wks.var(self._obsname)
        pdf = ROOT.RooJohnson(f'sig{suffix}', 'Johnson', obs, mu, lb, gm, dl)
    
        wks.Import(pdf)
    
        return f'sig{suffix}'
    #-----------------------------------------
    def _add_hypatia_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            self._l_float_par += ['mu_sig', 'sg_sig']
            suffix = ''
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        lb = ROOT.RooRealVar(f'lb_sig{suffix}', '', -3,   -6, -1e-6)
        zt = ROOT.RooRealVar(f'zt_sig{suffix}', '',  0,   0.,     1)
        fb = ROOT.RooRealVar(f'fb_sig{suffix}', '',  0, -0.1,   0.1)
        
        mu = ROOT.RooRealVar(f'mu_sig{suffix}', '', 5260,    5350)
        sg = ROOT.RooRealVar(f'sg_sig{suffix}', '',   10,   5, 50)
        
        a1 = ROOT.RooRealVar(f'a1_sig{suffix}', '', 1.5, 1.0, 3.5)
        a2 = ROOT.RooRealVar(f'a2_sig{suffix}', '', 1.5, 1.0, 3.5)
        
        n1 = ROOT.RooRealVar(f'n1_sig{suffix}', '', 1.0, 0.5, 5.0)
        n2 = ROOT.RooRealVar(f'n2_sig{suffix}', '', 2.0, 0.5, 5.0)
        
        obs= wks.var(self._obsname)
        pdf= ROOT.RooHypatia2(f'sig{suffix}', 'Hypatia', obs, lb, zt, fb, sg, mu, a1, n1, a2, n2)
    
        wks.Import(pdf) 
    
        return f'sig{suffix}' 
    #-----------------------------------------
    def _add_3cb_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            self._l_float_par += ['mu_sig', 'sg1_sig', 'sg2_sig', 'sg3_sig']
            suffix = ''
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        mu  = ROOT.RooRealVar(f'mu_sig{suffix}' , '', 5300, 5250, 5350)
        
        sg1 = ROOT.RooRealVar(f'sg1_sig{suffix}' , '', 10, 2, 500)
        sg2 = ROOT.RooRealVar(f'sg2_sig{suffix}' , '', 15, 2, 500)
        sg3 = ROOT.RooRealVar(f'sg3_sig{suffix}' , '', 15, 2, 500)
        
        ar  = ROOT.RooRealVar(f'ar_sig{suffix}' , '', -4., 1.)
        al  = ROOT.RooRealVar(f'al_sig{suffix}' , '',  1., 4.)
        ac  = ROOT.RooRealVar(f'ac_sig{suffix}' , '', -4., 1.)
    
        nr  = ROOT.RooRealVar(f'nr_sig{suffix}' , '', 1, 0.5, 5) 
        nl  = ROOT.RooRealVar(f'nl_sig{suffix}' , '', 2, 0.5, 5) 
        nc  = ROOT.RooRealVar(f'nc_sig{suffix}' , '', 3, 0.5, 5) 
    
        cb1 = ROOT.RooCBShape(f'cb1{suffix}' , 'CB1', self._mass, mu, sg1, ar, nr)
        cb2 = ROOT.RooCBShape(f'cb2{suffix}' , 'CB2', self._mass, mu, sg2, al, nl)
        cb3 = ROOT.RooCBShape(f'cb3{suffix}' , 'CB3', self._mass, mu, sg3, ac, nc)
    
        f_1 = ROOT.RooRealVar(f'f_1{suffix}' , '', 0, 1) 
        f_2 = ROOT.RooRealVar(f'f_2{suffix}' , '', 0, 1) 
        
        pdf = ROOT.RooAddPdf(f'sig{suffix}', '3CB', ROOT.RooArgList(cb1, cb2, cb3), ROOT.RooArgList(f_1, f_2), True)
    
        wks.Import(pdf) 
    
        return f'sig{suffix}'
    #-----------------------------------------
    def _add_3cbr_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            self._l_float_par += ['mu_sig', 'sg1_sig', 'r21_sig', 'r31_sig']
            suffix = ''
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        mu  = ROOT.RooRealVar(f'mu_sig{suffix}' , '', 5300, 5250, 5350)
        
        sg1 = ROOT.RooRealVar(f'sg1_sig{suffix}' , '',  10, 2.0, 50)
        r21 = ROOT.RooRealVar(f'r21_sig{suffix}' , '', 1.0, 0.1, 20)
        r31 = ROOT.RooRealVar(f'r31_sig{suffix}' , '', 1.0, 0.1, 20)

        sg2 = ROOT.RooFormulaVar(f'sg2_sig{suffix}', '@0 * @1', ROOT.RooArgList(r21, sg1)) 
        sg3 = ROOT.RooFormulaVar(f'sg3_sig{suffix}', '@0 * @1', ROOT.RooArgList(r31, sg1)) 
        
        ar  = ROOT.RooRealVar(f'ar_sig{suffix}' , '', -4., 1.)
        al  = ROOT.RooRealVar(f'al_sig{suffix}' , '',  1., 4.)
        ac  = ROOT.RooRealVar(f'ac_sig{suffix}' , '', -4., 1.)
    
        nr  = ROOT.RooRealVar(f'nr_sig{suffix}' , '', 1, 0.5, 5) 
        nl  = ROOT.RooRealVar(f'nl_sig{suffix}' , '', 2, 0.5, 5) 
        nc  = ROOT.RooRealVar(f'nc_sig{suffix}' , '', 3, 0.5, 5) 
    
        cb1 = ROOT.RooCBShape(f'cb1{suffix}' , 'CB1', self._mass, mu, sg1, ar, nr)
        cb2 = ROOT.RooCBShape(f'cb2{suffix}' , 'CB2', self._mass, mu, sg2, al, nl)
        cb3 = ROOT.RooCBShape(f'cb3{suffix}' , 'CB3', self._mass, mu, sg3, ac, nc)
    
        f_1 = ROOT.RooRealVar(f'f_1{suffix}' , '', 0, 1) 
        f_2 = ROOT.RooRealVar(f'f_2{suffix}' , '', 0, 1) 
        
        pdf = ROOT.RooAddPdf(f'sig{suffix}', '3CB', ROOT.RooArgList(cb1, cb2, cb3), ROOT.RooArgList(f_1, f_2), True)
    
        wks.Import(pdf) 
    
        return f'sig{suffix}'
    #-----------------------------------------
    def _add_dscb_signal(self, wks, suffix=None):
        if   suffix in self._l_proc_sig:
            suffix = ''
            self._l_float_par += ['mu_dscb', 'sg_dscb']
        elif suffix in self._l_proc_csp:
            suffix = f'_{suffix}'
            #self._l_float_par += [f'sg_dscb{suffix}']
        else:
            self.log.error(f'Invalid suffix "{suffix}"')
            raise
    
        mu  = ROOT.RooRealVar(f'mu_dscb{suffix}' , '', 5250, 5400)
        sg  = ROOT.RooRealVar(f'sg_dscb{suffix}' , '',    2,   30)
        ar  = ROOT.RooRealVar(f'ar_dscb{suffix}' , '',    0,    5)
        al  = ROOT.RooRealVar(f'al_dscb{suffix}' , '',    0,    5)
        nr  = ROOT.RooRealVar(f'nr_dscb{suffix}' , '',    1,    5)
        nl  = ROOT.RooRealVar(f'nl_dscb{suffix}' , '',    0,    5)
    
        obs = wks.var(self._obsname)
        pdf = ROOT.RooDoubleCrystalBall(f'sig{suffix}', 'DSCB', obs, mu, sg, al, nl, ar, nr)
    
        wks.Import(pdf)
    
        return f'sig{suffix}'
    #-----------------------------------------
    def _add_signal(self, wks, suffix=None):
        utnr.check_none(suffix)
        if   self._proc == 'ctrl_binned'               and self._chan == 'mm':
            sig_name = self._add_dscb_signal(wks, suffix=suffix)
        elif self._proc == 'ctrl_binned'               and self._chan == 'ee':
            sig_name = self._add_2cb_signal(wks, suffix=suffix)
        elif self._proc in ['ctrl', 'ctrl_pi', 'psi2'] and self._chan == 'ee':
            sig_name = self._add_3cbr_signal(wks, suffix=suffix)
        elif                                               self._chan == 'mm': 
            sig_name = self._add_hypatia_signal(wks, suffix=suffix)
        else:
            self.log.error(f'Invalid channel {self._chan} or process {self._proc}')
            raise
    
        self.log.info(f'Using signal "{sig_name}"')
    
        return sig_name
    #-----------------------------------------
    def _add_fit(self, cf, d_par, tree):
        [npas, _]  = utnr.get_from_dic(d_par, 'nsig')
        ntot       = tree.GetEntries()
        npas       = int(npas)
    
        self.log.info(f'{"Fit":<20}{ntot:<20}{"->":<10}{npas:<20}')
        cf['Fit']  = efficiency(npas, arg_tot=ntot, cut='Fit')
    
        return cf
    #-----------------------------------------
    def _get_model_pars(self, wks, d_par):
        if d_par is None:
            self.log.info('Not setting any parameter')
            return wks 

        s_par = ROOT.RooArgSet()

        self.log.visible('Setting parameter values')
        self.log.info('--------------------------------------------')
        self.log.info(f'{"Kind":<20}{"Parameter":<20}{"Value":<20}{"Error":<20}')
        self.log.info('--------------------------------------------')
        for par_name, [par_val, par_err] in d_par.items():
            par = wks.var(par_name)
            if not par:
                self.log.error(f'Parameter {par_name} not found in workspace:')
                wks.Print()
                raise

            self._check_valid_value(par, value=par_val, error=par_err)

            par.setVal(par_val)
            par.setError(par_err)

            if par_name in self._l_float_par:
                self.log.info(f'{"Variable":<20}{par_name:<20}{par_val:<20.3e}{par_err:<20.3e}')
            else:
                par.setConstant(True)
                self.log.info(f'{"Constant":<20}{par_name:<20}{par_val:<20.3e}{par_err:<20.3e}')

            s_par.add(par)

        s_par_wks = wks.allVars()
        for par_wks in s_par_wks:
            par_wks_name = par_wks.GetName()

            if par_wks_name == self._obsname:
                continue

            if par_wks_name not in d_par:
                self.log.error(f'Parameter {par_wks_name} not found among:')
                print(d_par.keys())
                raise

        return s_par
    #-----------------------------------------
    def get_float_par(self):
        return self._l_float_par
    #-----------------------------------------
    @property
    def val_dir(self):
        return self._val_dir
    #-----------------------------------------
    @val_dir.setter 
    def val_dir(self, value):
        self._val_dir = utnr.make_dir_path(value)
    #-----------------------------------------
    def get_sign_model(self, name='model'):
        self._initialize()

        wks = ROOT.RooWorkspace('wks')
        wks.Import(self._mass)
        org_name = self._add_signal(wks, suffix=self._proc)

        if name is not None:
            pdf=wks.pdf(org_name)
            pdf.SetName(name)

        return wks
    #-----------------------------------------
    def _save_snapshot(self, wks, s_par):
        s_par_wks = wks.allVars()

        for par_wks in s_par_wks:
            par_wks_name = par_wks.GetName()
            if par_wks_name == self._obsname:
                continue

            if not s_par.find(par_wks_name):
                self.log.warning(f'Unset/Unfixed: {par_name}')

        wks.saveSnapshot('prefit', s_par, True)
    #-----------------------------------------
    def get_yield(self):
        if self._yield is None:
            self.log.error('Yield has not been calculated, run get_full_model')
            raise

        return self._yield
    #-----------------------------------------
    def get_full_model(self, sim_fit_vers = None, skip_csp=False):
        self._initialize()

        self.log.visible('Getting model')
    
        wks = self.get_sign_model(name=None)    
        self._add_combinatorial(wks)
    
        pdf_cmb = wks.pdf('cmb')
        pdf_sig = wks.pdf('sig')
    
        self._l_float_par += ['ncmb', 'nsig']
        ncmb = ROOT.RooRealVar('ncmb', '', 0., 0., 10000000)
        nsig = ROOT.RooRealVar('nsig', '', 0., 0., 1000000)
    
        if   self._chan == 'mm' and self._proc.startswith('psi2'):
            model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(pdf_sig,          pdf_cmb), ROOT.RooArgList(nsig,       ncmb) )
        elif self._chan == 'mm' and self._proc.startswith('ctrl'):
            sig_name = self._add_signal(wks, suffix='ctrl_pi')
            pdf_csp  = wks.pdf(sig_name)

            self._l_float_par += ['ncsp']
            ncsp     = ROOT.RooRealVar('ncsp', '', 0., 0., 1000000)

            if skip_csp:
                model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(pdf_sig,          pdf_cmb), ROOT.RooArgList(nsig,       ncmb) )
            else:
                model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(pdf_sig, pdf_csp, pdf_cmb), ROOT.RooArgList(nsig, ncsp, ncmb) )
        elif self._chan == 'ee' and self._proc.startswith('ctrl'):
            self._add_prec(wks)
            pdf_prc = wks.pdf('prc')
            self._l_float_par += ['nprc']
            nprc    = ROOT.RooRealVar('nprc', '', 0., 0., 1000000)
    
            sig_name= self._add_signal(wks, suffix='ctrl_pi')
            pdf_csp = wks.pdf(sig_name)
            self._l_float_par += ['ncsp']
            ncsp    = ROOT.RooRealVar('ncsp', '', 0., 0., 1000000)

            if skip_csp:
                model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(pdf_sig, pdf_prc,          pdf_cmb), ROOT.RooArgList(nsig, nprc,       ncmb) )
            else:
                model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(pdf_sig, pdf_prc, pdf_csp, pdf_cmb), ROOT.RooArgList(nsig, nprc, ncsp, ncmb) )
        elif self._chan == 'ee' and self._proc.startswith('psi2'): 
            self._add_prec(wks)
            pdf_prc = wks.pdf('prc')
            self._l_float_par += ['nprc']
            nprc    = ROOT.RooRealVar('nprc', '', 0., 0., 1000000)
    
            model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(pdf_sig, pdf_prc, pdf_cmb), ROOT.RooArgList(nsig, nprc, ncmb) )
        else:
            self.log.error(f'Invalid process "{self._proc}" and trigger "{self._chan}"')
            raise
    
        wks.Import(model)

        if sim_fit_vers is None:
            self.log.warning('Not fixing any parameter for full model')
            self._yield = 0

            return wks

        pgt = pars_getter(self._proc, self._trig, self._year, sim_fit_vers)
        d_par, df = pgt.get_pars()

        self._yield = df.Yield.sum()
        s_par = self._get_model_pars(wks, d_par)

        self._save_snapshot(wks, s_par)

        return wks
#-----------------------------------------
class pars_getter():
    log=utnr.getLogger('pars_getter')
    #-----------------------------------------
    def __init__(self, proc, trig, year, sim_fit_vers):
        self._proc        = proc
        self._trig        = trig 
        self._year        = year 
        self._sim_fit_vers= sim_fit_vers

        self._l_proc      = ['ctrl', 'psi2']
        self._l_trig_ee   = ['ETOS', 'GTIS', 'GTIS_ee', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0ElectronHAD', 'L0HadronElEL']
        self._l_trig_mm   = ['MTOS', 'L0MuonALL1', 'L0MuonALL2', 'L0MuonTIS', 'L0MuonMU1', 'L0MuonMU2', 'L0MuonHAD', 'GTIS_mm']
        self._l_trig      = self._l_trig_ee + self._l_trig_mm
        self._l_year      = ['r1', '2011', '2012', 'r2p1', '2015', '2016', '2017', '2018']
        self._q2bin       = 'jpsi' if proc == 'ctrl' else 'psi2'

        self._val_dir     = None

        #From ntuple production tables
        self._gen_bp      = 20e6
        self._gen_bd      =  4e6 
        #From bf_calculator
        self._bp_bf       = 2 * 4.4e-4
        self._bd_bf       = 2 * 2.9e-4

        self._d_nsig      = {}
        for proc, frac in [('ctrl', 1), ('psi2', 0.3)]:
            self._d_nsig[f'{proc}_ETOS']          = frac * 155000
            self._d_nsig[f'{proc}_GTIS']          = frac * 37000
            self._d_nsig[f'{proc}_MTOS']          = frac * 525000

            self._d_nsig[f'{proc}_GTIS_mm']       = frac * 37000
            self._d_nsig[f'{proc}_L0MuonALL1']    = frac * 525000
            self._d_nsig[f'{proc}_L0MuonALL2']    = frac * 525000
            self._d_nsig[f'{proc}_L0MuonTIS']     = frac * 525000
            self._d_nsig[f'{proc}_L0MuonMU1']     = frac * 525000
            self._d_nsig[f'{proc}_L0MuonMU2']     = frac * 525000
            self._d_nsig[f'{proc}_L0MuonHAD']     = frac * 525000

            self._d_nsig[f'{proc}_GTIS_ee']       = frac * 37000
            self._d_nsig[f'{proc}_L0TIS_EM']      = frac * 37000
            self._d_nsig[f'{proc}_L0TIS_MH']      = frac * 37000
            self._d_nsig[f'{proc}_L0ElectronTIS'] = frac * 37000
            self._d_nsig[f'{proc}_L0ElectronHAD'] = frac * 37000
            self._d_nsig[f'{proc}_L0HadronElEL']  = frac * 37000

        self._d_ncsp      = self._scale_dict(self._d_nsig, 0.005) 
        self._d_ncmb      = self._scale_dict(self._d_nsig, 0.050) 
        self._d_nprc      = self._scale_dict(self._d_nsig, 0.200)

        self._initialized = False
    #-----------------------------------------
    def _get_sim_par(self):
        json_path_wc = f'{self._fit_dir}/{self._sim_fit_vers}/simulation/v10.11tf/{self._proc}*/{self._year}/pars_{self._trig}.json'
        l_json_path = utnr.glob_wc(json_path_wc)
    
        d_par = {}
        for json_path in l_json_path:
            d_data = utnr.load_json(json_path)
            d_par.update(d_data)
    
        return d_par
    #-----------------------------------------
    def _scale_dict(self, d_data, scale):
        return {key : scale * val for key, val in d_data.items()}  
    #-----------------------------------------
    def _check_valid(self, choice, l_choice):
        if choice not in l_choice:
            self.log.error(f'Invalid value: {choice}, choose from:')
            print(l_choice)
            raise
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_valid(self._proc, self._l_proc)
        self._check_valid(self._trig, self._l_trig)
        self._check_valid(self._year, self._l_year)

        self._fit_dir = os.environ['FITDIR']
        self._prc_dir = os.environ['PRCDIR']

        self._initialized = True
    #-----------------------------------------
    def _get_ke_prec_yield(self, kind):
        file_path = utnr.get_latest(f'{self._prc_dir}/VERSION/{kind}_{self._trig}_{self._q2bin}_{self._year}/events.json')
        self.log.visible(f'PR JSON:  "{file_path}"')
        d_evt  = utnr.load_json(file_path)
        nevt   = len(d_evt)
    
        return nevt 
    #-----------------------------------------
    def _get_bp_prec_fraction(self):
        yld_bp=self._get_ke_prec_yield('bpXcHs_ee')
        yld_bd=self._get_ke_prec_yield('bdXcHs_ee')
    
        eff_bp = yld_bp / self._gen_bp
        eff_bd = yld_bd / self._gen_bd
    
        bd_y = self._gen_bp * self._bd_bf * eff_bd 
        bp_y = self._gen_bd * self._bp_bf * eff_bp 
    
        tot_y = bp_y + bd_y
    
        frac_bp = bp_y/tot_y

        if self._val_dir:
            l_sam = ['$B^+$'    , '$B_d$'    ]
            l_sca = [bp_y       , bd_y       ]
            l_gen = [self._gen_bp, self._gen_bd]
            l_bf  = [self._bp_bf , self._bd_bf ]
            l_eff = [eff_bp     , eff_bd     ]
            l_frc = [frac_bp    , 1 - frac_bp]
    
            df = pnd.DataFrame({'Sample' : l_sam, 'Scale' : l_sca, 'Generator' : l_gen, 'BF' : l_bf, 'Efficiency' : l_eff , 'Fraction' : l_frc})
    
            out_path = f'{self._val_dir}/pr_frac_stats_{self._trig}.tex'
            self.log.info(f'Saving to: {out_path}')
            df.to_latex(buf=open(out_path, 'w'), index=False, escape=False)
    
        return frac_bp
    #-----------------------------------------
    def _get_normalizations(self):
        d_norm = {}

        key = f'{self._proc}_{self._trig}'

        d_norm['nsig'] = utnr.get_from_dic(self._d_nsig, key)
        d_norm['ncmb'] = utnr.get_from_dic(self._d_ncmb, key)

        if self._trig in self._l_trig_ee:
            d_norm['nprc'] = utnr.get_from_dic(self._d_nprc, key)

        if self._proc == 'ctrl':
            d_norm['ncsp'] = utnr.get_from_dic(self._d_ncsp, key)

        d_par = {}
        for var_name, value in d_norm.items():
            error = math.sqrt(value)
            value = int(value)
            error = int(error)
            d_par[var_name] = [value, error]

        return d_par
    #-----------------------------------------
    @property
    def val_dir(self):
        return self._val_dir
    #-----------------------------------------
    @val_dir.setter 
    def val_dir(self, value):
        self._val_dir = utnr.make_dir_path(value)
    #-----------------------------------------
    def _get_df(self, d_par):
        df = pnd.DataFrame(columns=['Yield', 'Error'])
        for var_name, [value, error] in d_par.items():
            df.loc[var_name] = [value, error]

        if self._val_dir is not None:
            l_form=[lambda x : f'{x:.3e}'] * 2
            df.to_latex(f'{self._val_dir}/{self._proc}_{self._trig}_{self._year}_{self._sim_fit_vers}.tex', formatters=l_form)

        return df
    #-----------------------------------------
    def get_pars(self):
        self._initialize()

        d_par = {}

        d_nrm = self._get_normalizations()
        d_par.update(d_nrm)

        d_sim=self._get_sim_par()
        d_par.update(d_sim)

        if self._trig in self._l_trig_ee:
            bp_frac = self._get_bp_prec_fraction()
            d_par['bp_frac'] = [bp_frac, 0.05]

        d_par['c_cmb'] = [-0.005, 0.001]

        df=self._get_df(d_par)

        return (d_par, df)
#-----------------------------------------
def get_obs(proc, chan, name='mass'):
    if   chan == 'mm' and proc.startswith('ctrl'):
        obs = ROOT.RooRealVar(name, '', 5180, 5600)
    elif chan == 'mm' and proc.startswith('psi2'):
        obs = ROOT.RooRealVar(name, '', 5180, 5600)
    elif chan == 'ee' and proc.startswith('ctrl'): 
        obs = ROOT.RooRealVar(name, '', 5080, 5680)
    elif chan == 'ee' and proc.startswith('psi2'): 
        obs = ROOT.RooRealVar(name, '', 5080, 5680)
    else:
        log.error(f'Cannot assign mass observable for channel {chan} and process {proc}')
        raise

    return obs
#-----------------------------------------
def get_q2bin(proc):
    if   proc.startswith('ctrl'): 
        q2bin = 'jpsi'
    elif proc.startswith('psi2'):
        q2bin = 'psi2'
    else:
        log.error(f'Invalid process: {proc}')
        raise

    return q2bin
#-----------------------------------------
def get_mass_branch(proc):
    if   proc.startswith('ctrl'):
        obs_branch = 'B_const_mass_M'
    elif proc.startswith('psi2'):
        obs_branch = 'B_const_mass_psi2S_M'
    else:
        log.error(f'Cannot find mass branch for process: {proc}')
        raise

    return obs_branch
#-----------------------------------------

