from  rk.const_getter import const_getter as cget
from  fit_manager     import fit_manager  as fm

import ROOT
import re
import numpy 

import utils
import pandas            as pnd 
import matplotlib.pyplot as plt
import utils_noroot      as utnr
import plot_fit          as pf

log=utnr.getLogger(__name__)
#------------------------
class data:
    out_dir   = None 
    nevt      = None 
#------------------------
def get_tree(wks):
    model = wks.pdf('model')
    obs   = wks.var('x')

    datas = model.generate(ROOT.RooArgSet(obs), ROOT.RooFit.NumEvents(data.nevt) ) 
    
    ofile = ROOT.TFile(f'{data.out_dir}/data.root', 'recreate')
    otree = datas.GetClonedTree()
    otree.SetName('data')
    otree.Write()

    return (otree, ofile)
#------------------------
def make_full_model():
    wks = ROOT.RooWorkspace('wks')

    x   = ROOT.RooRealVar('x'       , '', 5300, 5080, 5600)
    #---------------------------
    mu  = ROOT.RooRealVar('mu_sig'  , '', 5300, 5250, 5350)

    sg1 = ROOT.RooRealVar('sg1_sig' , '', 10, 2,  40)
    sg2 = ROOT.RooRealVar('sg2_sig' , '', 15, 2,  40)
    sg3 = ROOT.RooRealVar('sg3_sig' , '', 12, 2,  40)

    gs1 = ROOT.RooGaussian('gs1' , 'Gaus', x, mu, sg1)
    gs2 = ROOT.RooGaussian('gs2' , 'Gaus', x, mu, sg2)
    gs3 = ROOT.RooGaussian('gs3' , 'Gaus', x, mu, sg3)

    frc_1 = ROOT.RooRealVar('frc_1' , '', 0.3, 0, 1)
    frc_2 = ROOT.RooRealVar('frc_2' , '', 0.3, 0, 1)

    frc_1.setConstant(True)
    frc_2.setConstant(True)

    sig   = ROOT.RooAddPdf('sig', 'sig', ROOT.RooArgList(gs1, gs2, gs3), ROOT.RooArgList(frc_1, frc_2))
    #---------------------------
    c   = ROOT.RooRealVar('c_cmb', '', -0.005,  -0.01, 0.0)
    c.setError(0.002)

    bkg = ROOT.RooExponential('cmb', 'Combinatorial', x, c)
    #---------------------------
    nbkg  = ROOT.RooRealVar('ncmb', '', data.nevt * 0.2, 0., 10000000)
    nsig  = ROOT.RooRealVar('nsig', '', data.nevt * 0.8, 0., 10000000)

    model = ROOT.RooAddPdf('model', '', ROOT.RooArgList(sig, bkg), ROOT.RooArgList(nsig, nbkg) )

    wks.Import(model)

    s_var = wks.allVars()
    wks.saveSnapshot('prefit', s_var, True)

    return wks
#------------------------
def fit(wks, fit_dir = 'fit'):
    tree, f     = get_tree(wks)
    fit_dir     = f'{data.out_dir}/{fit_dir}'
    
    d_opt                  = {}
    d_opt['weight']        = None 
    d_opt['fix_par']       = {} 
    d_opt['nbins']         = 500 
    d_opt['max_attempts']  = 20 
    d_opt['bin_threshold'] = 50000
    d_opt['pval_threshold']= 0.001
    d_opt['outdir']        = fit_dir

    wks.loadSnapshot('prefit')

    model = wks.pdf('model')
    obj=fm(model, tree, d_opt)
    obj.fit()

    pf.plot(fit_dir)
    
    d_par = obj.get_pars()

    return d_par
#------------------------
def run(wks, var_name):
    d_par=fit(wks)

    var  = wks.var(var_name)
    val  = var.getVal()
    err  = var.getError()

    return (d_par, val, err)
#------------------------
def test_c_exp():
    l_wdt = []
    l_val = []
    l_err = []

    wks= make_full_model()
    for scale in numpy.arange(0.05, 1.05, 0.05):
        cg=cget(wks)
        cg.val_dir = data.out_dir 
        cg.constrain_var('c_cmb', scale) 
        wks_cns = cg.get_model()

        d_par, c_val, c_err = run(wks_cns, 'c_cmb')

        utnr.dump_json(d_par, f'{data.out_dir}/pars_{scale:.2f}.json')

        [val, err] = d_par['c_cmb']

        l_wdt.append(scale)
        l_val.append(val)
        l_err.append(err)

    fig, (ax0, ax1) = plt.subplots(2, 1)
    ax0.errorbar(l_wdt, l_val, yerr=l_err, label='' , marker='o', linestyle='none')
    ax0.set_ylim(c_val - c_err/3, c_val + c_err/3)
    ax0.axhline(y=c_val)
    
    ax1.plot(l_wdt, l_err)
    plt.savefig(f'{data.out_dir}/var_evol.png')
#------------------------
if __name__ == '__main__':
    ROOT.RooRandom.randomGenerator().SetSeed(1)

    data.nevt    = 5000
    data.out_dir = utnr.make_dir_path('tests/const_getter/c_exp')
    test_c_exp()

