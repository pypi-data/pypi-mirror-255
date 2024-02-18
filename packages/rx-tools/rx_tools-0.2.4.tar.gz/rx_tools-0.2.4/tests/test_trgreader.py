import ROOT
import numpy

import os

import rk.trgreader as trgrd
import utils_noroot as utnr
import utils
import trgwgt
import pickle 
import matplotlib.pyplot as plt

from rk.collector import collector

log=utnr.getLogger(__name__)
#------------------------------
class data:
    year   ='2017'
    bin_dir='/publicfs/ucas/user/campoverde/Weights/Trigger/results/binning/v0'
    bin_ver='v0'
    trg_ver='v15.1'
    dat_dir=os.environ['DATDIR']
    cal_dir=os.environ['CALDIR']

    ee_filepath=f'{dat_dir}/sign_ee/v10.10tf.a0v2ss.3.0.1.0.0/2017.root'
    mm_filepath=f'{dat_dir}/sign_mm/v10.10tf.a0v2ss.1.1.1.0.0/2017.root'
#------------------------------
def initialize():
    ROOT.gInterpreter.ProcessLine('''
    TF1 fun("fun", "x * [1] + [0]", 0, 100000);
    
    fun.SetParameter(0, 0.5);
    fun.SetParameter(1, 1./50000);
    ''')
#------------------------------
def set_pars(kind, tag):
    if   kind == 'sim':
        ROOT.fun.FixParameter(1, 0)
    elif kind == 'dat' and tag == 'L0TIS_MH':
        ROOT.fun.FixParameter(1, 1./60000)
    elif kind == 'dat' and tag == 'L0TIS_EM':
        ROOT.fun.FixParameter(1, 1./200000)
    elif kind == 'dat' and tag in ['L0ElectronTIS', 'L0ElectronFAC', 'L0HadronElEL', 'L0MuonALL1']:
        ROOT.fun.FixParameter(1, 1./50000)
    else:
        log.error('Wrong kind ' + kind)
        raise
#------------------------------
def make_toy_data(tag, df=None, nentries = 1000000):
    ROOT.gInterpreter.ProcessLine('''
    TRandom3 r_1(1);
    TRandom3 r_2(2);
    ''')

    if df is None:
        df = ROOT.RDataFrame(nentries)

    if   tag in ['L0ElectronTIS', 'L0ElectronHAD']:
        df = df.Define('L1_L0Calo_ECAL_realET'     , 'return r_1.Uniform(10000);')
        df = df.Define('L2_L0Calo_ECAL_realET'     , 'return r_2.Uniform(10000);')

        df = df.Define('L1_L0Calo_ECAL_region'     , 'return r_1.Integer(3);')
        df = df.Define('L2_L0Calo_ECAL_region'     , 'return r_2.Integer(3);')

        df = df.Define('L1_L0ElectronDecision_TOS' , 'auto eff = fun.Eval(L1_L0Calo_ECAL_realET); auto val = r_1.Binomial(1, eff); return val;')
        df = df.Define('L2_L0ElectronDecision_TOS' , 'auto eff = fun.Eval(L2_L0Calo_ECAL_realET); auto val = r_2.Binomial(1, eff); return val;')
    elif tag == 'L0ElectronFAC':
        df = df.Define('max_e'     , 'return r_1.Uniform(10000);')
        df = df.Define('min_e'     , 'return r_2.Uniform(max_e);')

        df = df.Define('max_l1'    , 'return r_1.Binomial(1, 0.5);')

        df = df.Define('L1_L0Calo_ECAL_realET', 'max_l1 == 1 ? max_e : min_e;')
        df = df.Define('L2_L0Calo_ECAL_realET', 'max_l1 == 0 ? max_e : min_e;')

        df = df.Define('L1_L0ElectronDecision_TOS' , '0')
        df = df.Define('L2_L0ElectronDecision_TOS' , 'auto eff = fun.Eval(max_e); auto val = r_2.Binomial(1, eff); return val;')

        df = df.Define('r_epem'                     , 'return r_1.Uniform(0, 10000)')

        df = df.Define('L1_L0Calo_ECAL_xProjection' , 'return r_1.Uniform(0, 10000)')
        df = df.Define('L2_L0Calo_ECAL_xProjection' , 'auto dst = (r_epem + L1_L0Calo_ECAL_xProjection) < 10000 ? r_epem + L1_L0Calo_ECAL_xProjection : L1_L0Calo_ECAL_xProjection - r_epem; return dst;')

        df = df.Define('L1_L0Calo_ECAL_yProjection' , '0')
        df = df.Define('L2_L0Calo_ECAL_yProjection' , '0')
    elif tag.startswith('L0Hadron'):
        df = df.Define('H_L0Calo_HCAL_realET'      , 'return r_1.Uniform(10000);')
        df = df.Define('H_L0Calo_HCAL_region'      , 'return r_1.Integer(3);')

        df = df.Define('H_L0HadronDecision_TOS'    , 'auto eff = fun.Eval(H_L0Calo_HCAL_realET); auto val = r_1.Binomial(1, eff); return val;')
    elif tag == 'L0TIS_EM':
        df = df.Define('B_PT' , 'return r_1.Uniform(100000);')
        df = df.Define('B_ETA', 'return r_1.Uniform(0, 5);')

        df = df.Define('B_L0HadronDecision_TIS', '0')
        df = df.Define('B_L0MuonDecision_TIS'  , 'auto eff = fun.Eval(B_PT); auto val = r_1.Binomial(1, eff); return val;')
    elif tag == 'L0TIS_MH':
        df = df.Define('L1_PT' , 'return r_1.Uniform(30000);')
        df = df.Define('L2_PT' , 'return r_2.Uniform(30000);')

        df = df.Define('L1_ETA', 'return r_1.Uniform(0,5);')
        df = df.Define('L2_ETA', 'return r_2.Uniform(0,5);')

        df = df.Define('max_ll_pt', 'TMath::Max(L1_PT, L2_PT);')

        df = df.Define('B_L0PhotonDecision_TIS'  , '0')
        df = df.Define('B_L0ElectronDecision_TIS', 'auto eff = fun.Eval(max_ll_pt); auto val = r_1.Binomial(1, eff); return val;')
    elif tag.startswith('L0Muon'):
        df = df.Define('L1_PT'                 , 'return r_1.Uniform(20000);')
        df = df.Define('L2_PT'                 , 'return r_1.Uniform(20000);')

        df = df.Define('L1_ETA'                , 'return r_1.Uniform(1.5, 5);')
        df = df.Define('L2_ETA'                , 'return r_1.Uniform(1.5, 5);')

        df = df.Define('L1_L0MuonDecision_TOS' , 'auto eff = fun.Eval(L1_PT); auto val = r_1.Binomial(1, eff); return val;')
        df = df.Define('L2_L0MuonDecision_TOS' , 'auto eff = fun.Eval(L2_PT); auto val = r_1.Binomial(1, eff); return val;')
    else:
        log.error('Invalid tag ' + tag)
        raise

    if 'eventNumber' not in df.GetColumnNames():
        df = df.Define('eventNumber', 'rdfentry_')

    return df
#------------------------------
def get_tag_exp(tag):
    if tag == 'L0ElectronFAC':
        exp = 'L1_L0ElectronDecision_TOS || L2_L0ElectronDecision_TOS'
        xvr = 'max_e'
        yvr = 'r_epem'
    elif tag.startswith('L0Electron'):
        exp = 'L1_L0ElectronDecision_TOS'
        xvr = 'L1_L0Calo_ECAL_realET'
        yvr = 'L1_L0Calo_ECAL_region'
    elif tag.startswith('L0Hadron'):
        exp = 'H_L0HadronDecision_TOS'
        xvr = 'H_L0Calo_HCAL_realET'
        yvr = 'H_L0Calo_HCAL_region'
    elif tag.startswith('L0Muon'):
        exp = 'L2_L0MuonDecision_TOS'
        xvr = 'L2_PT'
        yvr = 'L2_ETA'
    elif tag == 'L0TIS_EM':
        exp = 'B_L0HadronDecision_TIS || B_L0MuonDecision_TIS'
        xvr = 'B_PT'
        yvr = 'B_ETA'
    elif tag == 'L0TIS_MH':
        exp = 'B_L0PhotonDecision_TIS || B_L0ElectronDecision_TIS'
        xvr = 'max_ll_pt'
        yvr = 'L1_ETA'
    else:
        log.error('Invalid tag ' + tag)
        raise

    return (exp, xvr, yvr)
#------------------------------
def get_tup(pars, tag, fail=False):
    set_pars(pars, tag)
    df = make_toy_data(tag)

    cut, xvr, yvr = get_tag_exp(tag)
    if fail:
        df = df.Filter(cut + ' == 0')
    else:
        df = df.Filter(cut + ' == 1')

    df.Snapshot('tree', 'tests/trgreader/toys/{}_{}_{}.root'.format(pars, tag, fail))

    d_dat  = df.AsNumpy([xvr, yvr, 'eventNumber'])
    arr_x  = d_dat[xvr]
    arr_y  = d_dat[yvr]
    arr_xy = numpy.array([arr_x, arr_y]).T
    arr_w  = numpy.ones(arr_x.size)
    arr_e  = d_dat['eventNumber']

    return (arr_xy, arr_w, arr_e)
#------------------------------
def get_arr_wgt(treename, inef=False, nentries=10000):
    a = 0.5
    if   treename == 'MTOS':
        b = 0.9
    elif treename in ['ETOS', 'HTOS']:
        b = 0.7
    elif treename == 'GTIS':
        b = 1.0
    elif treename == 'ETOS_fac':
        return numpy.random.uniform(0.5, 0.7, size=nentries) / 0.5
    elif treename == 'GTIS_ex':
        arr_z = get_arr_wgt('GTIS') * get_arr_wgt('ETOS', inef=True) * get_arr_wgt('HTOS', inef=True)
        return arr_z
    else:
        log.error('Unsupported treename ' + treename)
        raise

    arr_x = numpy.random.uniform(a, b, size=nentries)
    arr_y = numpy.random.uniform(a, b, size=nentries)

    if   treename == 'HTOS' and     inef:
        arr_z = (1 - arr_x) / 0.5
    elif treename == 'HTOS' and not inef:
        arr_z = (    arr_x) / 0.5
    elif treename in ['MTOS', 'ETOS', 'GTIS'] and     inef:
        arr_z = (    (1 - arr_x) * (1 - arr_y) ) /      0.25
    elif treename in ['MTOS', 'ETOS', 'GTIS'] and not inef:
        arr_z = (1 - (1 - arr_x) * (1 - arr_y) ) / (1 - 0.25)
    else:
        log.error('Unsupported treename ' +  treename)
        raise

    return arr_z
#------------------------------
def make_toy_maps(tag, year, pickledir, plotdir):
    if tag == 'L0TIS':
        make_toy_maps('L0TIS_EM', year, pickledir, plotdir)
        make_toy_maps('L0TIS_MH', year, pickledir, plotdir)
        return 

    tp_dat_p = get_tup('dat', tag, fail=False)
    tp_dat_f = get_tup('dat', tag, fail= True)

    tp_sim_p = get_tup('sim', tag, fail=False)
    tp_sim_f = get_tup('sim', tag, fail= True)
    
    obj = trgwgt.rwt(tag, year, data.bin_dir, version=data.bin_ver)
    obj.set_array(tp_dat_p, 'data_passed')
    obj.set_array(tp_dat_f, 'data_failed')
    obj.set_array(tp_sim_p,  'sim_passed')
    obj.set_array(tp_sim_f,  'sim_failed')
    obj.set_array(tp_sim_p,  'dir_passed')
    obj.set_array(tp_sim_f,  'dir_failed')

    d_opt={'sty' : 'colz', 'ovr_yrange' : (0, 1), 'ovr_yminr' : 0.8, 'ovr_ymaxr' : 2, 'zrange' : (0.4, 1.0) }
    obj.save_map(plotdir, 0, extension='png', d_opt = d_opt)
    pickle.dump(obj, open('{}/{}_{}.pickle'.format(pickledir, tag, year), 'wb'))
#------------------------------
def do_test_tag(tp_tag, df, plot_path):
    rd=trgrd.reader(data.year)
    rd.storage = collector() 
    rd.setMapPath(f'{data.cal_dir}/TRG/{data.trg_ver}')
    arr_wgt = rd.predict_weights(tp_tag, df) 

    plt.hist(arr_wgt, range=(0, 2), bins=30, label='Total', alpha=0.5)

    if   df.treename == 'HTOS':
        arr_had_wgt = rd.d_wgt['had']
        arr_lep_wgt = rd.d_wgt['lep']

        plt.hist(arr_had_wgt, range=(0, 2), bins=30, label='Hadron', alpha=0.5)
        plt.hist(arr_lep_wgt, range=(0, 2), bins=30, label='Lepton', alpha=0.5)
    elif df.treename == 'GTIS':
        arr_tis_wgt = rd.d_wgt['tis']
        arr_had_wgt = rd.d_wgt['had']
        arr_lep_wgt = rd.d_wgt['lep']

        plt.hist(arr_tis_wgt, range=(0, 2), bins=30, label='TIS'   , alpha=0.5)
        plt.hist(arr_had_wgt, range=(0, 2), bins=30, label='Hadron', alpha=0.5)
        plt.hist(arr_lep_wgt, range=(0, 2), bins=30, label='Lepton', alpha=0.5)

    plt.legend()
    plt.savefig(plot_path)
    plt.close('all')
#------------------------------
def test_real(treename, tp_tag):
    tag_pref = '_'.join(tp_tag)
    plot_dir = utnr.make_dir_path(f'tests/trgreader')
    plot_path= f'{plot_dir}/{tag_pref}.png'

    if treename == 'MTOS':
        filepath = data.mm_filepath
    else:
        filepath = data.ee_filepath

    df=ROOT.RDataFrame(treename, filepath)
    df.treename = treename 
    
    do_test_tag(tp_tag, df, plot_path)
#------------------------------
def test_toy(treename, tp_tag):
    initialize()
    str_tag   = '_'.join(tp_tag)

    pickledir = utnr.make_dir_path('tests/trgreader/toys/{}/maps'.format(str_tag))
    plotdir   = utnr.make_dir_path('tests/trgreader/toys/{}/plots'.format(str_tag))
    year      = '2011'

    df_sim    = None
    for tag in tp_tag:
        if tag == 'L0TIS':
            make_toy_maps('L0TIS_MH', year, pickledir, plotdir)
            make_toy_maps('L0TIS_EM', year, pickledir, plotdir)

            set_pars('sim', 'L0TIS_MH')
            df_sim = make_toy_data('L0TIS_MH', df = df_sim)

            set_pars('sim', 'L0TIS_EM')
            df_sim = make_toy_data('L0TIS_EM', df = df_sim)
        else:
            make_toy_maps(tag, year, pickledir, plotdir)
            set_pars('sim', tag)
            df_sim = make_toy_data(tag, df = df_sim)

    df_sim.treename = treename 

    rd=trgrd.reader(year)
    rd.storage = collector() 
    rd.setMapPath(pickledir)

    arr_wgt = rd.predict_weights(tp_tag, df_sim) 

    if treename == 'GTIS':
        arr_ana = get_arr_wgt('GTIS_ex')
    elif tp_tag == ('L0ElectronFAC',):
        arr_ana = get_arr_wgt('ETOS_fac')
    else:
        arr_ana = get_arr_wgt(treename)

    wgt_avg = numpy.mean(arr_wgt)
    wgt_std = numpy.std(arr_wgt)

    ana_avg = numpy.mean(arr_ana)
    ana_std = numpy.std(arr_ana)

    utnr.check_close(wgt_avg, ana_avg, 0.02, fail=False)
    utnr.check_close(wgt_std, ana_std, 0.03, fail=False)

    arr_dat = numpy.concatenate((arr_wgt, arr_ana))

    mx = numpy.amax(arr_dat)
    mn = numpy.amin(arr_dat)

    plt.hist(arr_ana, 100, density=True, range=(mn, mx), alpha=0.5, label='Calculated') 
    plt.hist(arr_wgt, 100, density=True, range=(mn, mx), alpha=0.5, label='Code') 
    plt.legend(loc='upper left')
    plt.savefig(plotdir + '/wgt.png')
    plt.clf()
#--------------------------------
def main(): 
    test_real('ETOS', ('L0ElectronTIS',) )
    #test_real('ETOS', ('L0ElectronFAC',) )
    #test_real('MTOS', ('L0MuonALL1',) )

    #test_real('GTIS', ('L0TIS_EMMH','L0HadronElEL', 'L0ElectronTIS') )
    #test_real('GTIS', ('L0TIS_MMMH','L0HadronElEL', 'L0ElectronTIS') )

    #test_toy('ETOS', ('L0ElectronFAC',) )
    #test_toy('MTOS', ('L0MuonALL1',) )
    #test_toy('ETOS', ('L0ElectronTIS',) )

    #test_toy('GTIS', ('L0TIS_EMMH','L0HadronElEL', 'L0ElectronTIS') )
    #test_toy('GTIS', ('L0TIS_MMMH','L0HadronElEL', 'L0ElectronTIS') )
#--------------------------------
if __name__ == '__main__':
    main()
#--------------------------------

