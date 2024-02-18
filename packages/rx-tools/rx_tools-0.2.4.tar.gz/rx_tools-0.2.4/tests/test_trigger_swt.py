import sys
import os 
import pickle

import ROOT
import math

from rk.trigger_swt import trigger_swt as trigger 

import utils_noroot as utnr
import style

log=utnr.getLogger(__name__)
#-----------------------
class data:
    year = 2011
#-----------------------
def test_real(year, tag):
    binning_dir = '/publicfs/ucas/user/campoverde/Weights/Trigger/results/binning/v1'
    
    dat_path='/publicfs/ucas/user/campoverde/Data/RK/data_ee/v10.11tf.3.0.x.x.0_v1/{}_dt_trigger_weights_sweighted.root'.format(year)
    sim_path='/publicfs/ucas/user/campoverde/Data/RK/ctrl_ee/v10.11tf.3.0.x.x.0_v1/{}_mc_trigger_weights_sweighted.root'.format(year)
    
    df_dat = ROOT.RDataFrame('KEE', dat_path)
    df_dat = df_dat.Define('weight', 'pid_eff * sw_ETOS')
    
    df_sim = ROOT.RDataFrame('KEE', sim_path)
    df_sim = df_sim.Define('weight', 'pid_eff * sw_ETOS')

    df_dat = df_dat.Range(1000)
    df_sim = df_sim.Range(1000)
    
    trg = trigger(tag, year, binning_dir, df_dat, df_sim)
    rwt = trg.get_reweighter(tag)
#-----------------------
def declare_pdf():
    ROOT.gInterpreter.ProcessLine('''
    TF1 fun("fun", "[2]/2. * (1 + TMath::Erf((x - [0]) / (sqrt(2) * [1]))) + [3]", 0, 100000);
    
    TRandom3 r_1(1);
    TRandom3 r_2(2);
    ''')
#-----------------------
def initialize_pars():
    ROOT.gInterpreter.ProcessLine('''
    fun.SetParameter(0, 2000);
    fun.SetParameter(1,  300);
    fun.SetParameter(2, 0.90);
    fun.SetParameter(3, 0.01);
    ''')
#-----------------------
def set_pars(tag, kind):
    kind = kind.split('_')[0]

    if   tag == 'L0TIS_EM' and kind == 'dat':
        ROOT.fun.SetParameter(0, 2000)
        ROOT.fun.SetParameter(1, 5000)
        ROOT.fun.SetParameter(2, 0.10)
        ROOT.fun.SetParameter(3, 0.20)

        return
    elif tag == 'L0TIS_EM' and kind == 'sim':
        ROOT.fun.SetParameter(0, 2000)
        ROOT.fun.SetParameter(1, 5000)
        ROOT.fun.SetParameter(2, 0.15)
        ROOT.fun.SetParameter(3, 0.20)

        return
    elif tag == 'L0TIS_MH' and kind == 'dat':
        ROOT.fun.SetParameter(0, 5000)
        ROOT.fun.SetParameter(1, 5000)
        ROOT.fun.SetParameter(2, 0.35)
        ROOT.fun.SetParameter(3, 0.10)

        return
    elif tag == 'L0TIS_MH' and kind == 'sim':
        ROOT.fun.SetParameter(0, 5000)
        ROOT.fun.SetParameter(1, 5000)
        ROOT.fun.SetParameter(2, 0.25)
        ROOT.fun.SetParameter(3, 0.10)

        return
    elif tag.startswith('HLT_') and kind == 'sim':
        ROOT.fun.SetParameter(0, 10000)
        ROOT.fun.SetParameter(1,  2000)
        ROOT.fun.SetParameter(2,  0.25)
        ROOT.fun.SetParameter(3,  0.10)

        return
    elif tag.startswith('HLT_') and kind == 'dat':
        ROOT.fun.SetParameter(0, 12000)
        ROOT.fun.SetParameter(1,  2000)
        ROOT.fun.SetParameter(2,  0.25)
        ROOT.fun.SetParameter(3,  0.10)

        return
    elif tag in ['L0ElectronTIS', 'L0MuonALL1']:
        pass
    else:
        log.error('Invalid tag: ' + tag)
        raise

    d_thr = {}
    if True:
        d_thr[('L0ElectronTIS', 'dat')] = 2500
        d_thr[('L0ElectronTIS', 'sim')] = 2000
        d_thr[('L0MuonALL1'   , 'dat')] = 1600 
        d_thr[('L0MuonALL1'   , 'sim')] = 2000 

    d_sig = {}
    if True:
        d_sig[('L0ElectronTIS', 'dat')] =  400 
        d_sig[('L0ElectronTIS', 'sim')] =  200 
        d_sig[('L0MuonALL1'   , 'dat')] =  400 
        d_sig[('L0MuonALL1'   , 'sim')] =  200 

    thr = d_thr[(tag, kind)]
    sig = d_sig[(tag, kind)]
    ROOT.gInterpreter.ProcessLine('''
    fun.FixParameter(0, {});
    fun.FixParameter(1, {});
    '''.format(thr, sig))
#-----------------------
def make_data(param, treename, filepath, nentries):
    if os.path.isfile(filepath):
        return

    filedir = os.path.dirname(filepath)
    os.makedirs(filedir, exist_ok = True)

    df = ROOT.RDataFrame(nentries)
    if   param == 'L0ElectronFAC':
        df = df.Define('L1_L0Calo_ECAL_xProjection', 'return r_1.Uniform(10000);')
        df = df.Define('L1_L0Calo_ECAL_yProjection', 'return r_1.Uniform(10000);')
        df = df.Define('L1_L0Calo_ECAL_realET'     , 'return r_1.Exp(4000);')
        
        df = df.Define('L2_L0Calo_ECAL_xProjection', 'return r_2.Uniform(10000);')
        df = df.Define('L2_L0Calo_ECAL_yProjection', 'return r_2.Uniform(10000);')
        df = df.Define('L2_L0Calo_ECAL_realET'     , 'return r_2.Exp(4000);')

        df = df.Define('L1_L0ElectronDecision_TOS' , '0')
        df = df.Define('L2_L0ElectronDecision_TOS' , 'auto eff = fun.Eval( TMath::Max(L1_L0Calo_ECAL_realET, L2_L0Calo_ECAL_realET) ); auto val = r_1.Binomial(1, eff); return val;')
    elif param == 'L0ElectronTIS':
        df = df.Define('L1_L0Calo_ECAL_realET'     , 'return r_1.Exp(3000);')
        df = df.Define('L1_L0ElectronDecision_TOS' , 'auto eff = fun.Eval(L1_L0Calo_ECAL_realET); auto val = r_1.Binomial(1, eff); return val;')
        df = df.Define('L1_L0Calo_ECAL_region'     , 'return r_1.Integer(3);')
        
        df = df.Define('L2_L0Calo_ECAL_realET'     , 'return r_2.Exp(3000);')
        df = df.Define('L2_L0ElectronDecision_TOS' , 'auto eff = fun.Eval(L2_L0Calo_ECAL_realET); auto val = r_2.Binomial(1, eff); return val;')
        df = df.Define('L2_L0Calo_ECAL_region'     , 'return r_2.Integer(3);')
    elif param == 'L0MuonALL1':
        df = df.Define('L2_PT'                    , 'return r_1.Exp(4000);')
        df = df.Define('L2_L0MuonDecision_TOS'    , 'auto eff = fun.Eval(L2_PT); auto val = r_2.Binomial(1, eff); return val;')
        df = df.Define('L2_ETA'                   , 'return r_1.Uniform(0.0, 5.0);')
    elif param == 'L0TIS_EM':
        df = df.Define('B_PT'                    , 'return r_1.Exp(8000);')
        df = df.Define('B_ETA'                   , 'return r_1.Uniform(0.0, 5.0);')

        df = df.Define('B_L0MuonDecision_TIS'  , '0')
        df = df.Define('B_L0HadronDecision_TIS', 'auto eff = fun.Eval(B_PT); auto val = r_1.Binomial(1, eff); return val;')
    elif param == 'L0TIS_MH':
        df = df.Define('L1_PT'     , 'return r_1.Exp(15000);')
        df = df.Define('L2_PT'     , 'return r_2.Exp(15000);')

        df = df.Define('L1_ETA'    , 'return r_1.Uniform(0, 5);')
        df = df.Define('L2_ETA'    , 'return r_2.Uniform(0, 5);')

        df = df.Define('B_L0ElectronDecision_TIS', '0')
        df = df.Define('B_L0PhotonDecision_TIS'  , 'auto eff = fun.Eval(TMath::Max(L1_PT, L2_PT)); auto val = r_1.Binomial(1, eff); return val;')
    elif param.startswith('HLT_'):
        df = df.Define('L1_Hlt1TrackAllL0Decision_TOS' , '1')
        df = df.Define('L1_Hlt1TrackMVADecision_TOS', '1')
        df = df.Define('L1_IPCHI2_OWNPV', '1e10')
        df = df.Define('L1_PT', '2000')
        
        df = df.Define('L2_Hlt1TrackAllL0Decision_TOS', '1')
        df = df.Define('L2_Hlt1TrackMVADecision_TOS', '1')
        df = df.Define('L2_IPCHI2_OWNPV', '1e10')
        df = df.Define('L2_PT', '2000')
        
        df = df.Define('H_Hlt1TrackAllL0Decision_TOS', '1')
        df = df.Define('H_Hlt1TrackMVADecision_TOS', '1')
        df = df.Define('H_IPCHI2_OWNPV', '1e10')
        df = df.Define('H_PT', '2000')
        
        df = df.Define('threshold_b', '0')
        
        df = df.Define('B_Hlt2Topo3BodyBBDTDecision_TOS', '0')
        
        df = df.Define('B_Hlt2Topo2BodyDecision_TOS', '0')
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
        
        df = df.Define('B_Hlt2Topo2BodyBBDTDecision_TOS', 'auto eff = fun.Eval(B_PT); auto val = r_1.Binomial(1, eff); return val;')
    else:
        log.error('Unsupported param: ' + param)
        raise

    if param == 'L0ElectronFAC':
        tag = 'L0ElectronTIS'
    else:
        tag = param
    
    df = df.Define(f'sw_{tag}'   , '1')
    df = df.Define('pid_eff'     , '1')
    df = df.Define('eventNumber' , 'rdfentry_')


    df.Snapshot(treename, filepath)
#-------------------------------
def df_define(df, name, definition):
    v_col = df.GetColumnNames()
    l_col = [ col.c_str() for col in v_col ]

    if name in l_col:
        return df

    df = df.Define(name, definition)

    return df
#-------------------------------
def get_compatibility(h_eff, tag, kind, index):
    nbins = h_eff.GetNbinsX()

    name  = 'h_cmp_{}_{}_{}'.format(tag, kind, index)
    h_cmp = h_eff.Clone(name)
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
            log.warning('{0:<20}{1:<20}'.format(  'Tag',   tag))
            log.warning('{0:<20}{1:<20}'.format( 'Kind',  kind))
            log.warning('{0:<20}{1:<20}'.format(  'Bin', i_bin))
            log.warning('{0:<20}{1:<20}'.format('Index', index))

        h_cmp.SetBinContent(i_bin, 100 * tolv)
        h_cmp.SetBinError(i_bin, 100 * tole)

    max_val = h_cmp.GetMaximum()
    h_cmp.SetMaximum(100)
    h_cmp.SetMinimum(0.01)
    h_cmp.SetFillColor(ROOT.kBlue)
    h_cmp.SetFillStyle(3002)

    return h_cmp
#-------------------------------
def plot_eff(over_dir, l_h_eff, tag, kind, param = None):
    set_pars(tag, kind)
    os.makedirs(over_dir, exist_ok=True)

    for i_h_eff, h_eff in enumerate(l_h_eff):
        h_eff.SetLineColor(1)
        h_eff.SetMarkerColor(1)
        h_cmp = get_compatibility(h_eff, tag, kind, i_h_eff)

        c = ROOT.TCanvas('c_{}'.format(i_h_eff), '', 2000, 600)
        c.Divide(2, 1)

        c.cd(1)
        h_eff.Draw()
        ROOT.fun.Draw('same')

        pad=c.cd(2)
        pad.SetLogy()
        h_cmp.Draw('E2')

        if param is None:
            plotpath = '{}/eff_{}_{}_{}.png'.format(over_dir, kind,   tag, i_h_eff)
        else:
            plotpath = '{}/eff_{}_{}_{}.png'.format(over_dir, kind, param, i_h_eff)

        log.visible('Saving to ' + plotpath)
        c.SaveAs(plotpath)
#-------------------------------
def test_toy(nentries, tag, param=None):
    initialize_pars()

    if tag in ['L0MuonALL1', 'HLT_MTOS']:
        treename = 'KMM'
    else:
        treename = 'KEE'

    if param is None:
        lab = tag
    else:
        lab = param

    set_pars(tag, 'dat')
    dat_path=f'tests/trigger_swt/input/dat_{lab}.root'
    make_data(lab, treename, dat_path, nentries)

    set_pars(tag, 'sim')
    sim_path=f'tests/trigger_swt/input/sim_{lab}.root'
    make_data(lab, treename, sim_path, nentries)
    
    df_dat = ROOT.RDataFrame(treename, dat_path)
    df_dat = df_dat.Define('weight', f'pid_eff * sw_{tag}')
    
    df_sim = ROOT.RDataFrame(treename, sim_path)
    df_sim = df_sim.Define('weight' , f'pid_eff * sw_{tag}')
    df_sim = df_sim.Define('wgt_cal', '1')
    
    trg = trigger(tag, data.year, df_dat, df_sim, version='v00')
    rwt = trg.get_reweighter(lab, no_replicas=True)

    hist_dir = f'tests/trigger_swt/plots/sweight/toy_test/hist_{tag}_{param}'

    rwt.save_maps()
    l_h_dat, l_h_sim, l_h_dir = rwt.plot_maps(hist_dir, replica = 0, extension = 'png', d_opt={'sty' : ['colz L', 'colz L', 'colz L']})

    over_dir = f'tests/trigger_swt/plots/sweight/toy_test/over_{tag}_{param}'
    plot_eff(over_dir, l_h_dat, tag, 'dat_peff', param = param)
    plot_eff(over_dir, l_h_sim, tag, 'sim_peff', param = param)
    plot_eff(over_dir, l_h_dir, tag, 'sim_teff', param = param)
#-------------------------------
def main():
    declare_pdf()

    test_toy(500000, 'L0ElectronTIS', 'L0ElectronFAC')

    return
    test_toy(500000, 'L0ElectronTIS')
    test_toy(500000, 'L0MuonALL1')
    test_toy(500000, 'L0TIS_EM')
    test_toy(500000, 'L0TIS_MH')

    test_toy(500000, 'HLT_MTOS')
    test_toy(500000, 'HLT_ETOS')
    test_toy(500000, 'HLT_HTOS')
    test_toy(500000, 'HLT_GTIS')
#-------------------------------
if __name__ == '__main__':
    main()

