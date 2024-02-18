from rk.fitwgt import rwt as ftwt

import os
import zfit
import ROOT 
import math
import numpy 
import utils_noroot as utnr
import matplotlib.pyplot as plt

from hep_cl import hist_reader as hr

#-----------------------------------------------------------
class data:
    log     = utnr.getLogger(__name__)
    dat_dir = utnr.make_dir_path(f'{os.getcwd()}/tests/fitwgt/inputs/data')
    set_dir = utnr.make_dir_path(f'tests/fitwgt/inputs/share')

    nentries_s = 100000
    nentries_b1= 200000
    nentries_b2=  25000

    dat_ver = 'v0'

    os.environ['DATDIR'] = dat_dir
#-----------------------------------------------------------
def get_pdfs():
    obs = zfit.Space('m', limits=(0, 10))

    mu  = zfit.Parameter('mu', 5.3,  4.5, 5.5)
    sg  = zfit.Parameter('sg', 0.3,  0.2, 0.4)
    ap  = zfit.Parameter('ap', 1.0,  0.1, 5.0)
    pw  = zfit.Parameter('pw', 1.0,  0.1, 5.0)
    sig = zfit.pdf.CrystalBall(obs=obs, mu=mu, sigma=sg, alpha=ap, n=pw)

    mu_p= zfit.Parameter('mu_pr', 0.1,  -1, 1)
    sg_p= zfit.Parameter('sg_pr', 1.0,  0.2, 1.5)
    prc = zfit.pdf.Gauss(obs=obs, mu=mu_p, sigma=sg_p)
    
    lam = zfit.Parameter('lam', -1.2,  -2.3, -0.01)
    exp = zfit.pdf.Exponential(obs=obs, lam=lam)
    
    nsg = zfit.Parameter(f'nsg', 100, 0.1, 200000)
    nex = zfit.Parameter(f'nex', 100, 0.1, 200000)
    npr = zfit.Parameter(f'npr', 100, 0.1, 200000)
    
    sig = sig.create_extended(nsg)
    prc = prc.create_extended(npr)
    exp = exp.create_extended(nex)
    
    return [sig, prc, exp]
#-----------------------------------------------------------
def test_rec():
    pref='rec'
    trig='ETOS'
    year='2016'
    syst='trg'
    os.environ['CALDIR'] = f'tests/fitwgt/rec' 

    rdf_dt = get_data(pref, trig, year, 'data')
    rdf_mc = get_data(pref, trig, year, 'ctrl')

    rwt            = ftwt(dt=rdf_dt, mc=rdf_mc)
    rwt.model      = get_pdfs()
    rwt.wgt_ver    = 'v0.1'
    rwt.out_dir    = 'tests/fitwgt/rec'
    rwt.set_dir    = data.set_dir
    rwt.save_reweighter(name=f'{trig}_{year}_{pref}_{syst}')
#-----------------------------------------------------------
def test_bdt():
    pref='bdt'
    trig='ETOS'
    year='2016'
    syst='trg'
    os.environ['CALDIR'] = f'tests/fitwgt/bdt' 

    rdf_dt = get_data(pref, trig, year, 'data')
    rdf_mc = get_data(pref, trig, year, 'ctrl')

    rwt            = ftwt(dt=rdf_dt, mc=rdf_mc)
    rwt.model      = get_pdfs()
    rwt.wgt_ver    = 'v0.1'
    rwt.out_dir    = 'tests/fitwgt/bdt'
    rwt.set_dir    = data.set_dir
    rwt.save_reweighter(name=f'{trig}_{year}_{pref}_{syst}')
#-----------------------------------------------------------
def get_bdt(rdf):
    rdf   = rdf.Range(data.nentries_s)
    d_val = rdf.AsNumpy(['bdt_prc', 'bdt_cmb', 'B_DIRA_OWNPV'])
    l_arr_bdt = [ d_val['bdt_prc'], d_val['bdt_cmb'], d_val['B_DIRA_OWNPV'] ]

    arr_bdt = numpy.array(l_arr_bdt)

    return arr_bdt.T
#-----------------------------------------------------------
def check_weights(rdf_dt, rdf_mc, root_path):
    arr_dat = get_bdt(rdf_dt)
    arr_sim = get_bdt(rdf_mc)

    arr_mc_wgt = rdf_mc.AsNumpy(['weight'])['weight']

    ifile = ROOT.TFile(root_path)
    h_mc  = ifile.h_ctrl
    h_dt  = ifile.h_data

    rwt   = hr(dt=h_dt, mc=h_mc)

    arr_rw_wgt = rwt.predict_weights(arr_sim)

    plot_dist(arr_dat.T[0], arr_sim.T[0], arr_mc_wgt, arr_rw_wgt, 'prc')
    plot_dist(arr_dat.T[1], arr_sim.T[1], arr_mc_wgt, arr_rw_wgt, 'cmb')

    ifile.Close()
#-----------------------------------------------------------
def plot_dist(arr_dat, arr_sim, arr_mc_wgt, arr_rw_wgt, kind):
    plt.hist(arr_dat, range=(0, 1), bins=5, histtype='step', label='Data         ', density=True, weights=None                   )
    plt.hist(arr_sim, range=(0, 1), bins=5, histtype='step', label='MC           ', density=True, weights=arr_mc_wgt             )
    plt.hist(arr_sim, range=(0, 1), bins=5, histtype='step', label='MC reweighted', density=True, weights=arr_mc_wgt * arr_rw_wgt)

    plt.legend()
    plt.title(kind)
    plt.savefig(f'bdt_{kind}.png')
    plt.close()
#-----------------------------------------------------------
def test_1dm():
    pref='bdt'
    trig='ETOS'
    year='2016'
    syst='trg'
    os.environ['CALDIR'] = f'tests/fitwgt/1dm' 

    rdf_dt = get_data(pref, trig, year, 'data')
    rdf_mc = get_data(pref, trig, year, 'ctrl')

    root_path = '/home/angelc/Packages/RK/tools/tests/fitwgt/1dm/v0.1/ETOS_2016_bdt_trg.root'

    if True:
        rwt            = ftwt(dt=rdf_dt, mc=rdf_mc)
        rwt.model      = get_pdfs()
        rwt.wgt_ver    = 'v0.1'
        rwt.out_dir    = 'tests/fitwgt/1dm'
        rwt.set_dir    = data.set_dir
        rwt.one_dim    = True
        root_path      = rwt.save_reweighter(name=f'{trig}_{year}_{pref}_{syst}')

    check_weights(rdf_dt, rdf_mc, root_path)
#-----------------------------------------------------------
def get_data(pref, trig, year, kind):
    sample   = f'{kind}_mm' if trig == 'MTOS' else f'{kind}_ee'
    file_dir = utnr.make_dir_path(f'{data.dat_dir}/{sample}/{data.dat_ver}')
    file_path= f'{file_dir}/{year}.root'
    tree_name= 'KMM' if trig == 'MTOS' else 'KEE'

    if os.path.isfile(file_path):
        data.log.info(f'Using cached {file_path}')
        rdf = ROOT.RDataFrame(tree_name, file_path)
        return rdf
    else:
        data.log.info(f'Remaking {file_path}')

    if True:
        d_data                     = {}
        d_data['bdt_cmb']          = get_dist('bdt_cmb', kind)
        d_data['bdt_prc']          = get_dist('bdt_prc', kind)
        d_data['B_IPCHI2_OWNPV']   = get_dist('ipch', kind)
        d_data['B_ENDVERTEX_CHI2'] = get_dist('vtch', kind)
        d_data['B_DIRA_OWNPV']     = get_dist('dira', kind)
        d_data['mass']             = get_dist('mass', kind)
        d_data['H_ProbNNk']        = get_dist('hprb', kind)
        d_data['H_PIDe']           = get_dist('hpid', kind)
        d_data['L1_PIDe']          = get_dist('lpid', kind)
        d_data['L2_PIDe']          = get_dist('lpid', kind)
        d_data['nTracks']          = get_dist('ntrk', kind)
        d_data['L1_PX']            = get_dist('BPX', kind)
        d_data['L1_PY']            = get_dist('BPX', kind)
        d_data['L1_PZ']            = get_dist('BPX', kind)
        d_data['L2_PX']            = get_dist('BPX', kind)
        d_data['L2_PY']            = get_dist('BPX', kind)
        d_data['L2_PZ']            = get_dist('BPX', kind)
        d_data['H_PX']             = get_dist('BPX', kind)
        d_data['H_PY']             = get_dist('BPX', kind)
        d_data['H_PZ']             = get_dist('BPX', kind)
        d_data['H_P']              = get_dist('BPX', kind)

        d_data['B_PT']             = get_dist('BPX', kind)
        d_data['B_ETA']            = get_dist('ETA', kind)
        d_data['H_ETA']            = get_dist('ETA', kind)

        d_data['L1_P']             = get_dist('BPX', kind)
        d_data['L2_P']             = get_dist('BPX', kind)
        d_data['L1_PT']            = get_dist('BPX', kind)
        d_data['L2_PT']            = get_dist('BPX', kind)
        d_data['L1_ETA']           = get_dist('ETA', kind)
        d_data['L2_ETA']           = get_dist('ETA', kind)
        d_data['L1_Phi']           = get_dist('PHI', kind)
        d_data['L2_Phi']           = get_dist('PHI', kind)

        d_data['L1_HasBremAdded']  = get_dist('bool', kind)
        d_data['L2_HasBremAdded']  = get_dist('bool', kind)

        d_data['L1_L0Calo_ECAL_realET'] = get_dist('BPX', kind)
        d_data['L2_L0Calo_ECAL_realET'] = get_dist('BPX', kind)

        d_data['L1_L0Calo_ECAL_region'] = get_dist('reg', kind)
        d_data['L2_L0Calo_ECAL_region'] = get_dist('reg', kind)

        d_data['Jpsi_M']                = get_dist('Jpsi_M', kind)
        d_data['yearLabbel']            = get_dist('year', kind, value=year)
        d_data['Polarity']              = get_dist('pola', kind, value=year)
    #--------------------------------------------------
    if kind != 'data':
        d_data['Jpsi_TRUEID']  = numpy.array([443] * data.nentries_s) 
        d_data['B_TRUEP_X']    = numpy.random.uniform( 0, 10000, size=data.nentries_s)
        d_data['B_TRUEP_Y']    = numpy.random.uniform( 0, 10000, size=data.nentries_s)
        d_data['B_TRUEP_Z']    = numpy.random.uniform( 0, 10000, size=data.nentries_s)
        d_data['B_TRUEPT']     = numpy.random.uniform( 0, 30000, size=data.nentries_s)

    rdf = ROOT.RDF.FromNumpy(d_data) 

    if kind == 'data':
        rdf = rdf.Define('weight', '(1)')
    else:
        rdf = rdf.Define('weight', 'TMath::Sqrt((0.3 * TMath::Gaus(bdt_cmb, 0.5, 0.2) + 1) * ( 0.3 * TMath::Gaus(bdt_prc, 0.5, 0.2) + 1))')

    rdf.Snapshot(tree_name, file_path)

    return rdf
#-----------------------------------------------------------
def get_binning(pref, trig, year):
    d_bin = {}

    if pref == 'rec':
        d_bin['arr_x_1']  = [-2, 0.0, 3.0] 
        d_bin['arr_y_1']  = [-2, 0.0, 3.0] 
        d_bin['arr_z_1']  = [0.00, 10.00] 
        d_bin['rwt_vars'] = ['log(B_ENDVERTEX_CHI2)', 'log(B_IPCHI2_OWNPV)', 'TMath::ACos(B_DIRA_OWNPV)'] 
    elif pref == 'bdt':
        d_bin['arr_x_1']  = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0] 
        d_bin['arr_y_1']  = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0] 
        d_bin['arr_z_1']  = [0.00, 10.00] 
        d_bin['rwt_vars'] = ['bdt_cmb', 'bdt_prc', 'TMath::ACos(B_DIRA_OWNPV)']
    else:
        log.error(f'Invalid preffix: {pref}')
        raise

    return d_bin
#-----------------------------------------------------------
def make_settings(trig, year):
    d_set      = {}
    for pref in ['rec', 'bdt']:
        key        = f'{pref}_{trig}_{year}'
        d_set[key] = get_binning(pref, trig, year) 

    utnr.dump_json(d_set, f'{data.set_dir}/v1/kinematics_trg.json')
#-----------------------------------------------------------
def get_dist(var, kind, value=None):
    if   var in ['bdt_cmb', 'bdt_prc']: 
        if var == 'bdt_cmb':
            arr = numpy.random.normal(1.0, 0.3, size=data.nentries_s)
        else:
            arr = numpy.random.normal(0.7, 0.2, size=data.nentries_s)

        if kind == 'data':
            arr_b_1 = numpy.random.normal(0.0, 0.1, size=data.nentries_b1) 
            arr_b_2 = numpy.random.normal(0.1, 0.1, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var == 'mass': 
        arr = numpy.random.normal(5, 0.3, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.exponential(10, size=data.nentries_b1)
            arr_b_2 = numpy.random.normal(0, 0.6, size=data.nentries_b2)
            arr_b_2 = numpy.absolute(arr_b_2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var == 'dira':
        arr = numpy.random.exponential(0.01, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(0, 1.5, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(0, 1.5, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['ipch', 'vtch']:
        arr = numpy.random.chisquare(4, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(0, 100, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(0, 100, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['hpid', 'lpid']:
        arr = numpy.random.uniform(-5, 5, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(-5, 5, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(-5, 5, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['hprb']:
        arr = numpy.random.uniform( 0, 1, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(0, 1, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(0, 1, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['BPX']:
        arr = numpy.random.uniform( 0, 10000, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(0, 10000, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(0, 10000, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['ntrk']:
        arr = numpy.random.randint(0, 10, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.randint(0, 10, size=data.nentries_b1)
            arr_b_2 = numpy.random.randint(0, 10, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['reg']:
        arr = numpy.random.randint(-1, 3, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.randint(-1, 3, size=data.nentries_b1)
            arr_b_2 = numpy.random.randint(-1, 3, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['pola']:
        arr = numpy.random.randint(0, 2, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.randint(0, 2, size=data.nentries_b1)
            arr_b_2 = numpy.random.randint(0, 2, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))

        arr = arr * 2 - 1
    elif var in ['bool']:
        arr = numpy.random.randint(0, 2, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.randint(0, 2, size=data.nentries_b1)
            arr_b_2 = numpy.random.randint(0, 2, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['Jpsi_M']:
        arr = numpy.random.uniform(2000, 4000, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(2000, 4000, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(2000, 4000, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['year']:
        value = float(value)
        arr = numpy.array([value] * data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.array([value] * data.nentries_b1)
            arr_b_2 = numpy.array([value] * data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['ETA']:
        arr = numpy.random.uniform(1, 3, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(1, 3, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(1, 3, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['PHI']:
        arr = numpy.random.uniform(-math.pi, math.pi, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(-math.pi, math.pi, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(-math.pi, math.pi, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    else:
        data.log.error(f'Variable {var} not recognized')
        raise

    if var == 'dira':
        arr = numpy.cos(arr)

    return arr
#-----------------------------------------------------------
def main():
    make_settings('ETOS', '2016')

    test_1dm()

    return
    test_bdt()
    test_rec()
#-----------------------------------------------------------
if __name__ == '__main__':
    main()

