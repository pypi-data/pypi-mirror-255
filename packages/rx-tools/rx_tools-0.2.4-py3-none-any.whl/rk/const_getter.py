import ROOT
import utils_noroot as utnr
import utils
import math 
import pandas       as pnd
import re
import os

#-----------------------------------------
class const_getter:
    log=utnr.getLogger(__name__)
    #-----------------------------------------
    def __init__(self, wks):
        self._d_data = {}
        self._l_line = []

        self._wks_ot    = ROOT.RooWorkspace('wks') 
        self._wks_in    = wks 
        self._l_pdf_con = ROOT.RooArgSet()
        self._l_par_con = ROOT.RooArgSet()

        self._d_var_const = {}

        self._initialized = False
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        utnr.check_type(self._wks_in,  ROOT.RooWorkspace)
        utils.check_wks_obj(self._wks_in, 'model', 'pdf')

        self._initialized = True
    #-----------------------------------------
    def constrain_var(self, var_name, scale=1):
        utnr.check_numeric(scale)

        self._d_var_const[var_name] = scale 
    #-----------------------------------------
    def _add_snapshot(self, wks, name):
        self._wks_in.loadSnapshot(name)

        s_par_in = self._wks_in.allVars()
        s_par    =          wks.allVars()
        s_par_ot = ROOT.RooArgSet(s_par_in)

        for par in s_par:
            if s_par_ot.find(par):
                continue

            s_par_ot.add(par)

        wks.saveSnapshot(name, s_par_ot, True)
    #-----------------------------------------
    def get_model(self):
        self._initialize()

        self._add_constraints()

        if self._l_pdf_con.getSize() == 0:
            self.log.error('No constraints added!')
            raise
        else:
            self._print_constraints()

        model = utils.check_wks_obj(self._wks_in, 'model', 'pdf', retrieve=True)
        model.SetName('org_model')

        l_pdf = ROOT.RooArgSet(model)
        l_pdf.add(self._l_pdf_con)

        const_model = ROOT.RooProdPdf('model', '', l_pdf)

        self._wks_ot.Import(const_model)

        model.SetName('model')

        self._add_snapshot(self._wks_ot, 'prefit')

        return self._wks_ot
    #-----------------------------------------
    def save_to(self, val_dir):
        if len(self._d_data) == 0:
            return

        utnr.make_dir_path(val_dir)

        df = pnd.DataFrame(self._d_data)

        ofile = open(f'{val_dir}/constraints.tex', 'w')

        df.to_latex(buf=ofile, index=False)
    #-----------------------------------------
    def _add_constraints(self):
        if len(self._d_var_const) == 0:
            return

        for var_name, scale in self._d_var_const.items():
            mean, width = self._add_constraint(var_name, scale)

            utnr.add_to_dic_lst(self._d_data, 'Variable', f'{var_name}')
            utnr.add_to_dic_lst(self._d_data, 'Mean'    , f'{mean:.3e}')
            utnr.add_to_dic_lst(self._d_data, 'Width'   , f'{width:.3e}')
    #-----------------------------------------
    def _add_constraint(self, var_name, scale):
        self._initialize()

        l_var = self._wks_in.allVars()
        var   = l_var.find(var_name)

        if not var:
            self.log.error(f'Variable {var_name} not found in workspace:')
            self._wks_in.Print()
            raise

        mean = var.getVal()
        if var.isConstant():
            self.log.warning(f'Variable {var_name} is constant in model, not constraining it')
            return (mean, 0)

        error= var.getError()

        if error <= 0:
            self.log.error(f'Parameter {var_name} has invalid error: {error}')
            raise

        width= scale * error 

        self._l_line.append(f'{var_name:<40}{mean:<20.3e}{width:<20.3e}')
        mu   = ROOT.RooRealVar(f'{var_name}_mu', '',   mean,   mean - 1,   mean + 1)
        sg   = ROOT.RooRealVar(f'{var_name}_sg', '',  width, width / 2., 2. * width)

        mu.setConstant()
        sg.setConstant()

        gaus = ROOT.RooGaussian(f'{var_name}_const', '', var, mu, sg)
        self._wks_ot.Import(gaus)
        self._l_par_con.add(var)

        pdf = self._wks_ot.pdf(f'{var_name}_const')
        self._l_pdf_con.add(pdf)

        return (mean, width)
    #-----------------------------------------
    def _print_constraints(self):
        self.log.info(f'------------------------------------------------')
        self.log.info(f'{"Parameter":<40}{"Mean":<20}{"Width":<20}')
        self.log.info(f'------------------------------------------------')
        for line in self._l_line:
            self.log.info(line)
#-----------------------------------------

