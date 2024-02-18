import ROOT
import utils
import sys 
import os 
import math
import pickle
import logging
import utils_noroot as utnr

import read_calibration as rc
import read_selection   as rs

from importlib.resources import files
from rk.trigger_tnp      import trigger_tnp as tnp

from fit_manager         import fit_manager as fm
from version_management  import get_last_version

log = utnr.getLogger(__name__)
#-----------------------
def initialize(kind):
    ROOT.gInterpreter.ProcessLine('''
    TF1 fun("fun", "[2]/2. * (1 + TMath::Erf((x - [0]) / (sqrt(2) * [1]))) + [3]", 0, 100000);
    
    fun.SetParameter(0, 2000);
    fun.SetParameter(1,  300);
    fun.SetParameter(2, 0.90);
    fun.SetParameter(3, 0.01);
    
    TRandom3 r_1(1);
    TRandom3 r_2(2);
    ''')

    ROOT.gInterpreter.ProcessLine('''
    RooRealVar x("B_const_mass_M", "", 4980, 5680);
    RooRealVar m("m", "", 5280, 4980, 5680);
    RooRealVar s("s", "", 10, 10, 200);
    RooRealVar c("c", "", -3e-2, 0.);
    RooRealVar ns("ns", "", 1000, 0., 1000000);
    RooRealVar nb("nb", "", 1000, 0., 1000000);
    
    RooGaussian gs("gs", "", x, m, s);
    RooExponential ex("exp", "", x, c);
    
    RooAddPdf pdf("model", "", RooArgSet(gs, ex), RooArgSet(ns, nb));

    RooWorkspace wks("wks");
    wks.import(pdf);
    wks.writeToFile("tests/trigger_tnp/{}/input/model.root");
    
    auto dat = pdf.generate(RooArgSet(x), 100000);
    auto t_dat = dat->GetClonedTree();

    auto sim =  gs.generate(RooArgSet(x), 100000);
    auto t_sim = sim->GetClonedTree();
    
    auto df_dat = ROOT::RDataFrame(*t_dat);
    auto df_sim = ROOT::RDataFrame(*t_sim);
    
    auto ptr_dat = df_dat.Take<double>("B_const_mass_M");
    auto ptr_sim = df_sim.Take<double>("B_const_mass_M");

    auto v_dat_mass = ptr_dat.GetValue();
    auto v_sim_mass = ptr_sim.GetValue();
    '''.format(kind))
#-----------------------
def set_pars(is_data):
    if   is_data == 1: 
        ROOT.fun.SetParameter(0, 10000)
        ROOT.fun.SetParameter(1,  2000)
        ROOT.fun.SetParameter(2,  0.25)
        ROOT.fun.SetParameter(3,  0.10)
    elif is_data == 0:
        ROOT.fun.SetParameter(0, 12000)
        ROOT.fun.SetParameter(1,  2000)
        ROOT.fun.SetParameter(2,  0.25)
        ROOT.fun.SetParameter(3,  0.11)
    else:
        ROOT.fun.SetParameter(0, 12000)
        ROOT.fun.SetParameter(1,  2000)
        ROOT.fun.SetParameter(2,  0.25)
        ROOT.fun.SetParameter(3,  0.10)

    return
#----------------------------------
def do_get_toy_data(data, nentries=100000):
    df = ROOT.RDataFrame(nentries)

    df = df.Define('pid_eff', '1')
    if data:
        df = df.Define('B_const_mass_M', 'v_dat_mass.at(rdfentry_)')
    else:
        df = df.Define('B_const_mass_M', 'v_sim_mass.at(rdfentry_)')

    df = df.Define('L1_PT', '10000')
    df = df.Define('L2_PT', '10000')
    df = df.Define('H_PT' , '10000')
    df = df.Define('L0Data_Muon1_Pt', '1000')

    df = df.Define('L1_IPCHI2_OWNPV', '1e10')
    df = df.Define('L2_IPCHI2_OWNPV', '1e10')
    df = df.Define('H_IPCHI2_OWNPV' , '1e10')

    df = df.Define('L1_Hlt1TrackAllL0Decision_TOS' , '1')
    df = df.Define('L1_Hlt1TrackMVADecision_TOS', '1')
    df = df.Define('L2_Hlt1TrackAllL0Decision_TOS' , '1')
    df = df.Define('L2_Hlt1TrackMVADecision_TOS', '1')
    df = df.Define('H_Hlt1TrackAllL0Decision_TOS' , '1')
    df = df.Define('H_Hlt1TrackMVADecision_TOS', '1')

    df = df.Define('B_Hlt1Phys_TIS', '1')
    df = df.Define('B_Hlt2Phys_TIS', '1')

    df = df.Define('L1_L0MuonDecision_TOS', '1')
    df = df.Define('L2_L0MuonDecision_TOS', '1')

    df = df.Define('L1_L0ElectronDecision_TOS', '1')
    df = df.Define('L1_L0Calo_ECAL_realET'   , '1')
    df = df.Define('L2_L0ElectronDecision_TOS', '1')
    df = df.Define('L2_L0Calo_ECAL_realET'   , '1')

    df = df.Define('threshold_m' , '0')
    df = df.Define('threshold_el', '0')
    df = df.Define('threshold_kp', '0')
    df = df.Define('threshold_b' , '0')

    df = df.Define('H_L0HadronDecision_TOS', '1')
    df = df.Define('H_L0Calo_HCAL_realET', '1')

    df = df.Define('B_L0PhotonDecision_TIS', '1')
    df = df.Define('B_L0ElectronDecision_TIS', '1')
    df = df.Define('B_L0HadronDecision_TIS', '1')
    df = df.Define('B_L0MuonDecision_TIS', '1')

    df = df.Define('B_Hlt2Topo3BodyBBDTDecision_TOS', '0')
    df = df.Define('B_Hlt2Topo3BodyDecision_TOS', '0')
    
    df = df.Define('B_Hlt2TopoE2BodyBBDTDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoE3BodyBBDTDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoMu2BodyBBDTDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoMu3BodyBBDTDecision_TOS', '0')
    
    df = df.Define('B_Hlt2TopoE2BodyDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoE3BodyDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoEE2BodyDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoEE3BodyDecision_TOS', '0')
    
    df = df.Define('B_Hlt2TopoMu2BodyDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoMu3BodyDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoMuMu2BodyDecision_TOS', '0')
    df = df.Define('B_Hlt2TopoMuMu3BodyDecision_TOS', '0')
    
    df = df.Define('B_ETA', 'return r_1.Uniform(0, 5);')
    df = df.Define('B_PT' , 'return r_2.Exp(8000);')

    set_pars(data)

    df = df.Define('B_Hlt2Topo2BodyBBDTDecision_TOS', 'auto eff = fun.Eval(B_PT); auto val = r_1.Binomial(1, eff); return val;')
    df = df.Define('B_Hlt2Topo2BodyDecision_TOS', 'auto eff = fun.Eval(B_PT); auto val = r_1.Binomial(1, eff); return val;')

    return df
#----------------------------------
def get_toy_data(data, kind, nentries=100000):
    datadir  = utnr.make_dir_path('tests/trigger_tnp/{}/input'.format(kind))
    datapath = '{}/data_{}_{}.root'.format(datadir, data, nentries)
    if os.path.isfile(datapath):
        log.info('Reusing dataset')
        df = ROOT.RDataFrame('tree', datapath)
        return df

    log.info('Creating dataset')
    df = do_get_toy_data(data, nentries)
    df.Snapshot('tree', datapath)

    df = ROOT.RDataFrame('tree', datapath)

    return df
#----------------------------------
def prepare_dataset(df, prb_cut, tag_cut):
    ant_cut = f'({prb_cut}) == 0'

    df_tag = df.Filter(tag_cut)
    df_tag = df.Define('weight', '1')

    df_prb = df_tag.Filter(prb_cut)
    df_ant = df_tag.Filter(ant_cut)

    df_prb = ROOT.RDF.AsRNode(df_prb)
    df_ant = ROOT.RDF.AsRNode(df_ant)

    return df_prb, df_ant
#----------------------------------
def get_bin_hist():
     bin_dir  = files('tools_data').joinpath('trigger')
     bin_path = get_last_version(bin_dir, version_only=False)
     bin_path = f'{bin_path}/HLTElectron_NA_2015.root'

     return bin_path
#----------------------------------
def save_maps_noconst(trigger_name):
    df_dat = get_toy_data(1, 'noconst') 
    df_sim = get_toy_data(0, 'noconst') 
    
    outdir     = 'tests/trigger_tnp/noconst/output'
    picklepath = f'{outdir}/{trigger_name}.root'
    binpath    = get_bin_hist()
    
    d_opt = {}
    d_opt['modelpath'] = 'tests/trigger_tnp/noconst/input/model.root' 
    d_opt['tag']       = trigger_name 
    d_opt['outdir']    = 'tests/trigger_tnp/noconst/output'
    d_opt['plotdir']   = 'tests/trigger_tnp/noconst/plots'
    d_opt['version']   = 'v0' 
    d_opt['sigvar']    = 'ns'
    d_opt['slicing']   = (binpath, 'B_PT', 'B_ETA')
    d_opt['nbins']     = 100 
    d_opt['fix_pass']  = None 
    d_opt['fix_fail']  = None 
    d_opt['fix_list']  = None 

    tag = rc.get( trigger_name, year=2016)
    prb = rc.get('HLTElectron', year=2016)

    tp_dat = prepare_dataset(df_dat, prb, tag)
    tp_sim = prepare_dataset(df_sim, prb, tag)
    
    obj = tnp(tp_dat, tp_sim, d_opt)
    obj.save_map(picklepath)
#----------------------------------
def save_maps_const(trigger_name, constpath, constlist):
    df_dat = get_toy_data(1, 'const') 
    df_sim = get_toy_data(0, 'const') 
    
    outdir     = 'tests/trigger_tnp/const/output'
    picklepath = f'{outdir}/{trigger_name}.root'
    binpath    = get_bin_hist()

    d_opt = {}
    d_opt['modelpath'] = 'tests/trigger_tnp/const/input/model.root' 
    d_opt['tag']       = trigger_name 
    d_opt['outdir']    = 'tests/trigger_tnp/const/output'
    d_opt['plotdir']   = 'tests/trigger_tnp/const/plots'
    d_opt['version']   = 'v0' 
    d_opt['sigvar']    = 'ns'
    d_opt['slicing']   = (binpath, 'B_PT', 'B_ETA')
    d_opt['nbins']     = 100 
    d_opt['fix_pass']  = constpath
    d_opt['fix_fail']  = constpath
    d_opt['fix_list']  = constlist

    tag = rc.get( trigger_name, year=2016)
    prb = rc.get('HLTElectron', year=2016)

    tp_dat = prepare_dataset(df_dat, prb, tag)
    tp_sim = prepare_dataset(df_sim, prb, tag)
    
    obj = tnp(tp_dat, tp_sim, d_opt_fit = d_opt, d_opt_plt = {'legend' : True})
    obj.save_map(picklepath)
#----------------------------------
def get_compatibility(h_eff):
    nbins = h_eff.GetNbinsX()

    hname  = 'h_cmp_' + h_eff.GetName()
    h_cmp = h_eff.Clone(hname)

    h_cmp.GetYaxis().SetTitle('Bias[%]')

    for i_bin in range(1, nbins + 1):
        xmin = h_eff.GetBinLowEdge(i_bin + 0)
        xmax = h_eff.GetBinLowEdge(i_bin + 1)

        intv = ROOT.fun.Integral(xmin, xmax)
        inte = 0#ROOT.fun.IntegralError(xmin, xmax)

        avgv = intv / (xmax - xmin)
        avge = inte / (xmax - xmin)

        binc = h_eff.GetBinContent(i_bin)
        bine = h_eff.GetBinError(i_bin)

        tole = 3 * math.sqrt(avge ** 2 + bine ** 2)

        tolv, is_close = utnr.get_closeness(avgv, binc, epsilon = tole)
        if not is_close:
            log.warning('{0:<20}{1:<20}'.format(  'Bin', i_bin))

        h_cmp.SetBinContent(i_bin, 100 * tolv)
        h_cmp.SetBinError(i_bin, 100 * tole)

    max_val = h_cmp.GetMaximum()
    h_cmp.SetMaximum(100)
    h_cmp.SetMinimum(0.01)
    h_cmp.SetFillColor(ROOT.kBlue)
    h_cmp.SetFillStyle(3002)

    return h_cmp
#----------------------------------
def check_map(outdir, h_eff, data = None):
    if data not in [0, 1]:
        log.error('data argument not specified')
        raise

    can = ROOT.TCanvas('c_eff_{}'.format(data), '', 1200, 600)
    can.Divide(2, 1)

    set_pars(data)

    pad_ovr = can.cd(1)
    h_eff.GetYaxis().SetRangeUser(0, 1)
    h_eff.Draw()
    ROOT.fun.Draw('same')

    pad_cmp = can.cd(2)
    h_cmp = get_compatibility(h_eff)
    pad_cmp.SetLogy()
    h_cmp.Draw('E2')

    outpath = '{}/cmp_{}.png'.format(outdir, data)
    can.SaveAs(outpath)
#----------------------------------
def constrain_fit(constdir):
    data = ROOT.ex.generate(ROOT.RooArgSet(ROOT.x), 10000)
    tree = data.GetClonedTree()
    df   = ROOT.RDataFrame(tree)
    df   = df.Define('B_PT'  , 'TRandom3 r(0); return r.Uniform(0, 40000);')
    df   = df.Define('B_ETA' , 'TRandom3 r(0); return r.Uniform(0,     5);')
    df   = df.Define('weight', '1')
    df   = ROOT.RDF.AsRNode(df)

    binpath    = get_bin_hist()

    d_opt                   = {}
    d_opt['slicing']        = (binpath, 'B_PT', 'B_ETA')
    d_opt['nbins']          = 300 
    d_opt['outdir']         = constdir 
    d_opt['weight']         = 'weight' 
    d_opt['max_attempts']   = 5 
    d_opt['bin_threshold']  = 20000
    d_opt['pval_threshold'] = 20000
    d_opt['fix_par']        = None 

    tree, _ = utils.df_to_tree(df)
    obj     = fm(ROOT.ex, tree, d_opt)
    obj.fit()

    constpar = f'{constdir}/pars.txt'
    ofile= open(constpar, 'w')
    ofile.write('c')
    ofile.close()

    constpath = f'{constdir}/fit_results.root'

    return constpath, constpar
#----------------------------------
def test_noconst():
    utnr.make_dir_path('tests/trigger_tnp/noconst/input')
    outdir = utnr.make_dir_path('tests/trigger_tnp/noconst/plots')
    
    initialize('noconst')
    
    save_maps_noconst('HLT_ETOS')

    return
    df  = get_toy_data(0, 'noconst') 
    
    arr_wgt = obj.predict_weights(df)
    h_eff_dat, h_eff_sim = obj.get_eff_maps()

    l_h_eff_dat = utils.poly2D_to_1D(h_eff_dat)
    l_h_eff_sim = utils.poly2D_to_1D(h_eff_sim)
    
    check_map(outdir, l_h_eff_dat[0], data = 1)
    check_map(outdir, l_h_eff_sim[0], data = 0)
#----------------------------------
def test_const():
    constdir = utnr.make_dir_path('tests/trigger_tnp/const/const')
    utnr.make_dir_path('tests/trigger_tnp/const/input')
    outdir = utnr.make_dir_path('tests/trigger_tnp/const/plots')

    initialize('const')
    constpath, constlist = constrain_fit(constdir)
    
    save_maps_const('HLT_ETOS', constpath, constlist)

    return
    df  = get_toy_data(0, 'const') 
    
    arr_wgt = obj.predict_weights(df)
    h_eff_dat, h_eff_sim = obj.get_eff_maps()

    l_h_eff_dat = utils.poly2D_to_1D(h_eff_dat)
    l_h_eff_sim = utils.poly2D_to_1D(h_eff_sim)
    
    check_map(outdir, l_h_eff_dat[0], data = 1)
    check_map(outdir, l_h_eff_sim[0], data = 0)
#----------------------------------
def main():
    test_noconst()
    test_const()
#----------------------------------
if __name__ == '__main__':
    main()

