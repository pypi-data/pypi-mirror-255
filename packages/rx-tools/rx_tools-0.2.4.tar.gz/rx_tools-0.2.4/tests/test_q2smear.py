import ROOT

import utils
import numpy
import os

from rk.q2smear import q2smear as q2

import utils_noroot      as utnr
import read_selection    as rs
import matplotlib.pyplot as plt

log=utnr.getLogger(__name__)
#------------------------------
class data:
    plot_dir = os.getcwd()
    replica  = 0
    log      = utnr.getLogger(__name__)

    ROOT.gInterpreter.ProcessLine('TRandom3 ran(1);')
#------------------------------
def get_mu_sg(is_sim, trig, d_par):
    mu_MC = d_par[f'{trig} mu_MC 0 gamma']
    sg_MC = d_par[f'{trig} sg_MC 0 gamma']

    if is_sim:
        return mu_MC, sg_MC

    dl_mu = d_par[f'{trig} delta_m 0 gamma']
    rt_sg = d_par[f'{trig} s_sigma 0 gamma']

    mu_DT = mu_MC + dl_mu
    sg_DT = sg_MC * rt_sg 

    return mu_DT, sg_DT
#------------------------------
def make_rdf(d_par, trig, is_sim, nentries=300000, year='2000'):
    mu, sg = get_mu_sg(is_sim, trig, d_par)

    df = ROOT.RDataFrame(nentries)
    df = df.Define('Jpsi_M'    , f'TRandom3 ran(0); return ran.Gaus({mu}, {sg});') 
    df = df.Define('yearLabbel', year) 
    df = df.Define('L1_P', 'ran.Uniform(0, 120000);') 
    df = df.Define('L2_P', 'ran.Uniform(0, 120000);') 
    df = df.Define('L1_BremMultiplicity', 'ran.Integer(2);') 
    df = df.Define('L2_BremMultiplicity', 'ran.Integer(2);') 

    df.treename = trig

    return df
#------------------------------
def do_test_real(year, treename, plot_dir):
    filepath=f'/publicfs/ucas/user/campoverde/Data/RK/ctrl_ee/v10.11tf.a0v1x7y4z4.3.0.1.0.0_v1/{year}_reso.root'

    df=ROOT.RDataFrame(treename, filepath)
    df.treename = treename 

    q2dir ='/publicfs/ucas/user/campoverde/calibration/qsq/v2.nom'
    q2_sel=rs.get('q2', treename, q2bin='jpsi', year=year)

    obj=q2(df, q2dir)
    arr_wgt = obj.get_weights(q2_sel, data.replica)
    arr_psm = obj.get_q2_smear(data.replica)

    num     = numpy.sum(arr_wgt) 
    den     = float(arr_wgt.size)
    q2_eff  = numpy.sum(arr_wgt) / float(arr_wgt.size)
    if q2_eff < 0.01:
        log.warning('Efficiency: {:.3e}/{:.3e}={:.3e}'.format(num, den, q2_eff))
        log.warning('{0:<20}{1:40}'.format('Selection' , q2_sel))
    else:
        log.visible(f'q2 efficiency: {q2_eff:.3e}')

    nentries = df.Count().GetValue()
    if nentries <= 0:
        log.error('Found {} entries for year {} and tree {}'.format(nentries, year, treename))
        raise
    else:
        log.debug('Found {} entries for year {} and tree {}'.format(nentries, year, treename))

    arr_org = df.AsNumpy(['Jpsi_M'])['Jpsi_M']

    d_opt={}
    d_opt['legend'] = 1
    d_opt['text']   = ('year:{}, tree:{}'.format(year, treename), 1)

    plotpath='{}/mass/smr_{}_{}.png'.format(plot_dir, year, treename)
    log.info('Sending plot to ' + plotpath)
    utils.plot_arrays({'Original' : arr_org, 'PSmeared' : arr_psm}, plotpath, 30, d_opt=d_opt)

    d_opt={}
    d_opt['text']   = ('year:{}, tree:{}'.format(year, treename), 1)

    plotpath='{}/weights/wgt_{}_{}.png'.format(plot_dir, year, treename)
    log.info('Sending plot to ' + plotpath)
    utils.plot_arrays({'weights' : arr_wgt}, plotpath, 30, d_opt=d_opt)
#------------------------------
def test_remote():
    plot_dir=f'{data.plot_dir}/tests/q2smear/remote'
    os.makedirs(plot_dir, exist_ok=True)
    filepath='root://x509up_u12477@ccxrootdlhcb.in2p3.fr//pnfs/in2p3.fr/data/lhcb/LHCb_USER/lhcb/user/a/acampove/GangaFiles_20.02_Saturday_30_October_2021/2018_psi_skimmed.root'
    treename='ETOS'

    df=ROOT.RDataFrame(treename, filepath)
    df.treename = treename 
    q2dir='/publicfs/ucas/user/campoverde/calibration/qsq/v2.nom'
    q2_sel=rs.get('q2', treename, q2bin='jpsi', year='2016')
    
    obj=q2(df, q2dir)
    arr_mass_smr=obj.get_q2_smear(data.replica)
    arr_weights =obj.get_weights(q2_sel, data.replica)
#------------------------------
def test_real():
    plot_dir=utnr.make_dir_path(f'{data.plot_dir}/tests/q2smear/real')

    l_year=['2011', '2012', '2015', '2016', '2017', '2018']
    l_tree=['ETOS', 'GTIS']

    for year in l_year: 
        for tree in l_tree:
            do_test_real(year, tree, plot_dir)
#------------------------------
def get_pars():
    return {
    "ETOS delta_m 0 gamma": 10, 
    "ETOS delta_m 1 gamma": 10, 
    "ETOS delta_m 2 gamma": 10, 
    "ETOS mu_MC 0 gamma"  : 3096.9,
    "ETOS mu_MC 1 gamma"  : 3096.9,
    "ETOS mu_MC 2 gamma"  : 3096.9,
    #-----------------------------
    "ETOS s_sigma 0 gamma": 1.0,
    "ETOS s_sigma 1 gamma": 1.0,
    "ETOS s_sigma 2 gamma": 1.0,
    "ETOS sg_MC 0 gamma": 30,
    "ETOS sg_MC 1 gamma": 30,
    "ETOS sg_MC 2 gamma": 30,
    #-----------------------------
    #-----------------------------
    "HTOS delta_m 0 gamma": 0,
    "HTOS delta_m 1 gamma": 0,
    "HTOS delta_m 2 gamma": 0,
    "HTOS mu_MC 0 gamma"  : 3106.9,
    "HTOS mu_MC 1 gamma"  : 3106.9,
    "HTOS mu_MC 2 gamma"  : 3106.9,
    #-----------------------------
    "HTOS s_sigma 0 gamma": 0.5,
    "HTOS s_sigma 1 gamma": 0.5,
    "HTOS s_sigma 2 gamma": 0.5,
    "HTOS sg_MC 0 gamma": 50,
    "HTOS sg_MC 1 gamma": 50,
    "HTOS sg_MC 2 gamma": 50,
    #-----------------------------
    #-----------------------------
    "GTIS delta_m 0 gamma": 0.0,
    "GTIS delta_m 1 gamma": 0.0,
    "GTIS delta_m 2 gamma": 0.0,
    "GTIS mu_MC 0 gamma"  : 3096.9,
    "GTIS mu_MC 1 gamma"  : 3096.9,
    "GTIS mu_MC 2 gamma"  : 3096.9,
    #-----------------------------
    "GTIS s_sigma 0 gamma": 1.1,
    "GTIS s_sigma 1 gamma": 1.1,
    "GTIS s_sigma 2 gamma": 1.1,
    "GTIS sg_MC 0 gamma": 80,
    "GTIS sg_MC 1 gamma": 80,
    "GTIS sg_MC 2 gamma": 80 
    }
#------------------------------
def fill_hist(hist, trig=None, brem=None, par=None):
    axis_x = hist.GetXaxis()
    axis_y = hist.GetYaxis()

    nbins_x = axis_x.GetNbins()
    nbins_y = axis_y.GetNbins()

    d_par = get_pars()
    var   = {'rsg' : 's_sigma', 'dmu' : 'delta_m', 'mMC' : 'mu_MC'}[par]
    key   = f'{trig} {var} {brem} gamma'
    val   = d_par[key]

    for x_bin in range(1, nbins_x + 1):
        for y_bin in range(1, nbins_y + 1):
            hist.SetBinContent(x_bin, y_bin, val)
#------------------------------
def save_pars(d_par, q2dir):
    d_par_json = { name : val for name, val in d_par.items() if 'sg_MC' not in name}

    path = f'{q2dir}/2000.json'

    utnr.dump_json(d_par_json, path)
#------------------------------
def test_toy():
    q2dir   = '/publicfs/ucas/user/campoverde/calibration/QSQ/v0.nom'
    d_par = get_pars()
    save_pars(d_par, q2dir)

    plot_dir=utnr.make_dir_path(f'{data.plot_dir}/tests/q2smear/toys')

    for trigger in ['ETOS', 'HTOS', 'GTIS']:
        rdf_sim          = make_rdf(d_par, trigger, True)
        rdf_dat          = make_rdf(d_par, trigger, False)
        rdf_sim.treename = trigger 

        qsq = q2(rdf_sim, q2dir)
        arr_smr_q2 = qsq.get_q2_smear(data.replica)
        arr_org_q2 = rdf_sim.AsNumpy(['Jpsi_M'])['Jpsi_M']
        arr_dat_q2 = rdf_dat.AsNumpy(['Jpsi_M'])['Jpsi_M']

        plot_arr(arr_smr_q2, arr_org_q2, arr_dat_q2, trigger, plot_dir)
#------------------------------
def create_mom_map(dir_name, year, trigger):
    map_path = f'{dir_name}/{year}_{trigger}.root'

    data.log.info(f'Sending toy maps to: {map_path}')
    ofile = ROOT.TFile(map_path, 'recreate')

    h_map = ROOT.TH2F('hist', '', 10, 0, 100000, 10, 0, 100000)
    for par in ['rsg', 'dmu', 'mMC']:
        for brem in [0, 1, 2]:
            h_map = h_map.Clone(f'h_{par}_brem_{brem}')
            fill_hist(h_map, trig=trigger, brem=brem, par=par)
            h_map.Write()

    ofile.Close()
#------------------------------
def create_mom_maps(dir_name):
    create_mom_map(dir_name, '2000', 'ETOS')
    create_mom_map(dir_name, '2000', 'HTOS')
    create_mom_map(dir_name, '2000', 'GTIS')

    return dir_name
#------------------------------
def test_sys():
    plot_dir=utnr.make_dir_path(f'{data.plot_dir}/tests/q2smear/syst')
    q2dir   = create_mom_maps('/publicfs/ucas/user/campoverde/calibration/QSQ/v0.mom')
    d_par   = get_pars()

    for trigger in ['ETOS', 'HTOS', 'GTIS']:
        rdf_dt       = make_rdf(d_par, trigger, False)
        rdf_mc       = make_rdf(d_par, trigger, True)

        qsq        = q2(rdf_mc, q2dir)
        qsq.out_dir= f'{plot_dir}/pars_{trigger}'
        arr_smr_q2 = qsq.get_q2_smear(data.replica)
        arr_org_q2 = rdf_mc.AsNumpy(['Jpsi_M'])['Jpsi_M']
        arr_dat_q2 = rdf_dt.AsNumpy(['Jpsi_M'])['Jpsi_M']

        plot_arr(arr_smr_q2, arr_org_q2, arr_dat_q2, trigger, plot_dir)
#------------------------------
def test_sys_real():
    plot_dir= utnr.make_dir_path(f'{data.plot_dir}/tests/q2smear/syst_real')
    q2dir   = '/publicfs/ucas/user/campoverde/calibration/QSQ/v13.mom'
    d_par   = get_pars()

    for trigger in ['ETOS', 'GTIS']:
        rdf_dt       = make_rdf(d_par, trigger, False, year='2018')
        rdf_mc       = make_rdf(d_par, trigger, True , year='2018')

        qsq        = q2(rdf_mc, q2dir)
        qsq.out_dir= f'{plot_dir}/pars_{trigger}'
        arr_smr_q2 = qsq.get_q2_smear(data.replica)
        arr_org_q2 = rdf_mc.AsNumpy(['Jpsi_M'])['Jpsi_M']
        arr_dat_q2 = rdf_dt.AsNumpy(['Jpsi_M'])['Jpsi_M']

        plot_arr(arr_smr_q2, arr_org_q2, arr_dat_q2, trigger, plot_dir)
#------------------------------
def plot_arr(arr_smr, arr_org, arr_dat, trigger, plot_dir):
    mu_org = numpy.mean(arr_org)
    sg_org = numpy.std(arr_org)

    mu_smr = numpy.mean(arr_smr)
    sg_smr = numpy.std(arr_smr)

    if   trigger == 'ETOS':
        utnr.check_close(sg_org, sg_smr, epsilon=0.01, verbose=True)
        utnr.check_close(mu_org, mu_smr, epsilon=0.01, verbose=True)
    elif trigger == 'HTOS':
        utnr.check_close(sg_org, 2 * sg_smr, epsilon=0.01, verbose=True)
        utnr.check_close(mu_org, mu_smr - 5, epsilon=0.01, verbose=True)
    elif trigger == 'GTIS':
        utnr.check_close(1.1 * sg_org, sg_smr, epsilon=0.01, verbose=True)
        utnr.check_close(mu_org      , mu_smr, epsilon=0.01, verbose=True)
    else:
        log.error('Unsupported branch name ' + trigger)
        raise

    plot_path=f'{plot_dir}/{trigger}.png'

    plt.hist(arr_org, bins=30, range=[3000, 3200], histtype='step', label='MC')
    plt.hist(arr_smr, bins=30, range=[3000, 3200], histtype='step', label='MC smeared')
    plt.hist(arr_dat, bins=30, range=[3000, 3200], histtype='step', label='Data')
    plt.legend()
    plt.xlabel('$q^{2}$')
    plt.savefig(plot_path)
    plt.close('all')
#------------------------------
def main():
    test_sys_real()
    return
    test_sys()
    test_toy()
    #test_real()
#------------------------------
if __name__ == '__main__':
    main()

