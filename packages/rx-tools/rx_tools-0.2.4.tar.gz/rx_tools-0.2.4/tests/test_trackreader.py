import ROOT
import sys
import os
import numpy
import utils
import matplotlib.pyplot as plt
import utils_noroot      as utnr

from rk.efficiency  import df_getter as dfg
from rk.trackreader import reader    as trareader 

log=utnr.getLogger(__name__)
#-------------------------------------------------
class data:
    cal_dir = os.environ['CALDIR']
    version = 'v1.nom'
#-------------------------------------------------
def get_simple_df(trig):
    file_dir  = utnr.make_dir_path('tests/trackreader')
    file_path = f'{file_dir}/simple_test_{trig}.root'
    if os.path.isfile(file_path):
        df = ROOT.RDataFrame(trig, file_path)
        df.treename = trig
        return df

    proc = 'ctrl_mm' if trig == 'MTOS' else 'ctrl_ee'

    obj = dfg(proc, '2016', 'v10.14', (0, 500))
    df  = obj.get_df('sel', trigger=trig, selection='all_gorder', truth_corr_type='none', using_wmgr=False)
    df.Snapshot(trig, file_path) 
    df.treename = trig

    return df
#-------------------------------------------------
def make_maps(df):
    if   df.treename == 'ETOS':
        kind = 'etra'
        name = 'heffratio'
        mod  = get_binning(kind)

        h_dt = df.Histo3D(mod, 'L1_Phi', 'L1_ETA', 'L1_PT')
        h_mc = df.Histo3D(mod, 'L1_Phi', 'L1_ETA', 'L1_PT', 'weight')
    elif df.treename == 'MTOS':
        kind = 'mtra'
        name = 'Ratio'
        mod  = get_binning(kind)

        h_dt = df.Histo2D(mod, 'L1_P', 'L1_ETA')
        h_mc = df.Histo2D(mod, 'L1_P', 'L1_ETA', 'weight')
    else:
        log.error(f'Invalid treename {df.treename}')
        raise

    h_dt = h_dt.GetValue()
    h_mc = h_mc.GetValue()

    h_dt.Scale(1./h_dt.Integral())
    h_mc.Scale(1./h_mc.Integral())

    h_wt = h_dt.Clone(name)
    h_wt.Divide(h_dt, h_mc)

    cwd     = os.getcwd()
    map_dir = utnr.make_dir_path(f'{cwd}/tests/trackreader/toys')
    map_pat = f'{map_dir}/{kind}_0.root'

    ofile = ROOT.TFile(map_pat, 'recreate')
    h_wt.Write()
    ofile.Close()

    return map_dir
#-------------------------------------------------
def test(df, kind, map_path):
    rdr1 = trareader()
    rdr1.setMapPath(map_path)
    wgt_l1o, wgt_l2o = rdr1.getWeight(df)
    wgt_o = wgt_l1o * wgt_l2o

    plt.hist(wgt_l1o, bins=100, range=(-1, 2), label='L1', alpha=0.75)
    plt.hist(wgt_l2o, bins=100, range=(-1, 2), label='L2', alpha=0.75)
    plt.legend()

    cwd = os.getcwd()
    plot_dir=utnr.make_dir_path(f'{cwd}/tests/trackreader/{kind}')
    plot_path=f'{plot_dir}/{df.treename}.png'
    log.visible(f'Saving to: {plot_path}')

    plt.savefig(plot_path)
    plt.close('all')

    wgt_i = df.AsNumpy(['weight'])['weight']

    plt.scatter(wgt_i, 1/wgt_o)

    plt.xlabel("Input")
    plt.ylabel("Output")
    plt.savefig(f'{plot_dir}/weights.png')

    return wgt_i
#-------------------------------------------------
def test_real():
    map_path = f'{data.cal_dir}/TRK/{data.version}'

    df_mc = get_simple_df('ETOS')
    test(df_mc, map_path)

    df = get_simple_df('MTOS')
    test(df_mc, map_path)
#-------------------------------------------------
#-------------------------------------------------
def make_data(nentries=10000):
    ROOT.gInterpreter.ProcessLine('TRandom3 ran(1);')

    df = ROOT.RDataFrame(nentries)
    df = df.Define('yearLabbel' , '0')
    df = df.Define('L1_PT'      , 'ran.Uniform(0,    10000)')
    df = df.Define('L1_P'       , 'ran.Uniform(0,    10000)')
    df = df.Define('L1_ETA'     , 'ran.Uniform(0,        5)')
    df = df.Define('L1_Phi'     , 'ran.Uniform(-3.14, 3.14)')

    df = df.Define('L2_PT'      , 'ran.Uniform(0,    10000)')
    df = df.Define('L2_P'       , 'ran.Uniform(0,    10000)')
    df = df.Define('L2_ETA'     , 'ran.Uniform(0,        5)')
    df = df.Define('L2_Phi'     , 'ran.Uniform(-3.14, 3.14)')

    return df
#-------------------------------------------------
def get_binning(kind):
    if   kind == 'mtra':
        mod     = ROOT.RDF.TH2DModel('h', '', 10, 0, 10000, 5, 0, 5) 
    elif kind == 'etra':
        mod     = ROOT.RDF.TH3DModel('h', '', 10, -3.14, +3.14, 10, 0, 3, 10, 0, 15000)
    else:
        log.error(f'Wrong kind: {kind}')
        raise

    return mod
#-------------------------------------------------
def get_binned_weight_hist(df, mod, LP):
    wgt = f'1 + {LP}_P/100000. - {LP}_ETA/50.'
    df  = df.Define('wgt', wgt)

    h_w = df.Histo2D(mod, f'{LP}_P', f'{LP}_ETA', 'wgt')
    h_n = df.Histo2D(mod, f'{LP}_P', f'{LP}_ETA')

    h_w = h_w.GetValue()
    h_n = h_n.GetValue()

    h_r = h_w.Clone('h_r')
    h_r.Divide(h_w, h_n)

    return h_r
#-------------------------------------------------
def make_sim(df, mod, LP):
    h_wgt = get_binned_weight_hist(df, mod, LP)

    d_dat = df.AsNumpy([f'{LP}_P', f'{LP}_ETA'])

    arr_x = d_dat[f'{LP}_P'  ]
    arr_y = d_dat[f'{LP}_ETA']

    l_wgt = []
    for x, y in zip(arr_x, arr_y):
        i_bin = h_wgt.FindBin(x, y)
        wgt   = h_wgt.GetBinContent(i_bin)

        l_wgt.append(wgt)

    arr_wgt = numpy.array(l_wgt)

    df = utils.add_df_column(df, arr_wgt, 'weight')

    return df
#-------------------------------------------------
def test_toy():
    #----------------
    df_dt          = make_data()
    df_dt.treename = 'MTOS'

    mod            = get_binning('mtra')

    df_mc          = make_sim(df_dt, mod, 'L1')
    df_mc.treename = 'MTOS'

    map_path       = make_maps(df_mc)
    #----------------
    arr_wgt_corr   = test(df_mc, 'toys', map_path)
    #----------------
    arr_wgt_bias   = df_mc.AsNumpy(['weight'])['weight']

    nfail    = numpy.count_nonzero(arr_wgt_corr == 1. / arr_wgt_bias)

    print(arr_wgt_corr)
    print(arr_wgt_bias)
    if nfail == 0:
        log.visible(f'Toy test passed')
    else:
        log.error(f'Toy test failed, nfail = {nfail}')
        raise
#-------------------------------------------------
def main():
    test_toy()

    return
    test_real()
#-------------------------------------------------
if __name__ == '__main__':
    main()

