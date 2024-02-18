import ROOT
import argparse
import utils_noroot      as utnr
import matplotlib.pyplot as plt

log=utnr.getLogger(__name__)
#--------------------------------
class data:
    nsample = 200
    nevt    = 20000 
    ncpu    = 1
    version = None
    l_par   = ['m', 's', 'c']
    root_dir= 'tests/randomize_pars'

    silence = ROOT.RooFit.Silence(True)
    binned  = ROOT.RooFit.Binned(True)
#--------------------------------
def get_fit_opts():
    mn = ROOT.RooFit.Minimizer('Minuit2', 'migrad')
    op = ROOT.RooFit.Optimize(True)
    of = ROOT.RooFit.Offset(True)
    st = ROOT.RooFit.Strategy(2)
    sv = ROOT.RooFit.Save(True)
    pf = ROOT.RooFit.PrefitDataFraction(0.1)

    fit_opt = ROOT.RooFit.FitOptions(mn, op, of, st, sv)

    return fit_opt
#--------------------------------
def get_wks():
    x = ROOT.RooRealVar('x', '', 0, 10)
    m = ROOT.RooRealVar('m', '', 5, 0, 10)
    s = ROOT.RooRealVar('s', '', 1, 0.1, 10)
    c = ROOT.RooRealVar('c', '', -0.05, -0.1, 0.0)

    sig = ROOT.RooGaussian('sig', '', x, m, s)
    bkg = ROOT.RooExponential('bkg', '', x, c)

    fsig = ROOT.RooRealVar('fsig', '', 0, 1)

    model = ROOT.RooAddPdf('pdf', '', ROOT.RooArgList(sig, bkg), ROOT.RooArgList(fsig), True)

    wks = ROOT.RooWorkspace('wks')
    wks.Import(model)

    return wks
#--------------------------------
def get_spread():
    d_spread         = {}
    d_spread['m']    = 1
    d_spread['s']    = 0.5
    #d_spread['c']    = 0.02
    d_spread['fsig'] = 0.2 

    return d_spread
#--------------------------------
def fit():
    wks = get_wks()
    obs = wks.var('x')
    pdf = wks.pdf('pdf')

    fit_opt = get_fit_opts()

    rnd = ROOT.randomize_pars()
    d_spread = get_spread()
    for par, sig in d_spread.items():
        rnd.add_var(par, sig)
    
    mcs = ROOT.RooMCStudy(pdf, ROOT.RooArgSet(obs), data.binned, data.silence, fit_opt)
    mcs.addModule(rnd)
    mcs.generateAndFit(data.nsample, data.nevt)

    plot(mcs, wks)
    check_pars(mcs)
#--------------------------------
def get_pars(mcs, index):
    result = mcs.fitResult(index)
    l_par  = result.floatParsInit()

    d_par = {}
    for par in l_par:
        name  = par.GetName()
        value = par.getVal()

        d_par[name] = value

    return d_par
#--------------------------------
def check_pars(mcs):
    d_par_val = {}
    for i_fit in range(data.nsample):
        d_ipar = get_pars(mcs, i_fit)

        for par_nam in data.l_par:
            par_val = utnr.get_from_dic(d_ipar, par_nam)

            utnr.add_to_dic_lst(d_par_val, par_nam, par_val)

    for par_nam, l_par_val in d_par_val.items():
        min_par = min(l_par_val)
        max_par = max(l_par_val)

        plt.hist(l_par_val, 100, range=(min_par, max_par), alpha=0.75)

        out_dir = utnr.make_dir_path(f'{data.root_dir}/{data.version}')
        plot_path = f'{out_dir}/{par_nam}.png'
        log.visible(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
#--------------------------------
def plot(mcs, wks):
    obs = wks.var('x')
    m   = wks.var('m')
    s   = wks.var('s')

    l_par = [m, s]
    for par in l_par:
        plot_pull(mcs, par)
#--------------------------------
def plot_pull(mcs, par):
    parname = par.GetName()

    can = ROOT.TCanvas(f'c_{parname}', '', 600, 600)
    plot = mcs.plotPull(par)
    plot.Draw()

    out_dir = utnr.make_dir_path(f'{data.root_dir}/{data.version}')
    can.SaveAs(f'{out_dir}/pull_{parname}.png')
#--------------------------------
def get_args():
    parser = argparse.ArgumentParser(description='Used to perform several operations on TCKs')
    parser.add_argument('version', type=str, help='Version')
    parser.set_defaults(feature=True)
    args = parser.parse_args()
    
    data.version  = args.version
#--------------------------------
if __name__ == '__main__':
    get_args()

    fit()

