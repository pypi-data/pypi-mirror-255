import sys
import os
import ROOT
import numpy
import logging 

from   hist import Hist
import hist

import utils
import utils_noroot as utnr
import rk.pidreader as pidrd
from rk.collector import collector

import matplotlib.pyplot as plt

log=utnr.getLogger(__name__)
#-----------------------------
class data:
    l_year  = [2011, 2012, 2015, 2016, 2017, 2018]
    l_rel   = ['v3/nom', 'v3/el_bin1', 'v3/el_bin2', 'v3/kp_el_bin1', 'v3/kp_el_bin2', 'v3/kp_mu_bin1', 'v3/kp_mu_bin2', 'v3/mu_bin1', 'v3/mu_bin2']
    dat_dir = os.environ['DATDIR']
    cal_dir = os.environ['CALDIR']
    tabledir= utnr.make_dir_path('tests/pidreader/test_1/tables')
    replica = 0
    toy_ver = 'v0/nom'
    rel_ver = 'v3/nom'
#-----------------------------
def plot_unphysical(rd, key, df):
    l_eff   =rd.storage.get(key)
    nentries=df.Count().GetValue()

    if l_eff is None:
        return []

    plotsdir =utnr.make_dir_path(f'tests/pidreader/test_real/{df.year}')
    plot_path=f'{plotsdir}/pid_unphysical_{key}.png'
    neff     =len(l_eff)

    plt.hist(l_eff, bins=100)
    plt.savefig(plot_path)
    plt.close('all')

    line=f'{df.year:<10}{key:<40}{neff:<15}{float(neff)/nentries:<10.3e}'

    return [line]
#-----------------------------
def make_data(nentries=10000):
    df = ROOT.RDataFrame(nentries)
    df = df.Define('yearLabbel'     , '2011')
    df = df.Define('H_P'            , 'TRandom3 ran(0); return ran.Uniform(0, 10);')
    df = df.Define('H_ETA'          , 'TRandom3 ran(0); return ran.Uniform(0, 10);')
    df = df.Define('L1_P'           , 'TRandom3 ran(0); return ran.Uniform(0, 10);')
    df = df.Define('L1_ETA'         , 'TRandom3 ran(0); return ran.Uniform(0, 10);')
    df = df.Define('L2_P'           , 'TRandom3 ran(0); return ran.Uniform(0, 10);')
    df = df.Define('L2_ETA'         , 'TRandom3 ran(0); return ran.Uniform(0, 10);')
    df = df.Define('L1_HasBremAdded', 'TRandom3 ran(0); return ran.Integer(1);')
    df = df.Define('L2_HasBremAdded', 'TRandom3 ran(0); return ran.Integer(1);')
    df = df.Define('Polarity'       , 'TRandom3 ran(0); int pol = ran.Integer(1) == 1 ? 1 : -1; return pol;')

    return df
#-----------------------------
def check_eff(arr_eff, mu=None, sg=None):
    mu_cal = numpy.mean(arr_eff)
    sg_cal = numpy.std(arr_eff)

    tol_mu = 2 * abs(mu - mu_cal) / (mu + mu_cal)
    tol_sg = 2 * abs(sg - sg_cal) / (sg + sg_cal)

    if tol_mu > 0.02:
        log.error(f'Efficiency has the wrong value, exp/cal/tol: {mu}/{mu_cal:.3f}/{tol_mu:.3f}')
        raise

    if tol_sg > 0.02:
        log.error(f'Efficiency has the wrong stdev, exp/cal/tol: {sg}/{sg_cal:.3f}/{tol_sg:.3f}')
        raise
#-----------------------------
def do_test_toy(df):
    rdr = pidrd.reader()
    rdr.setMapPath(f'{data.cal_dir}/PID/{data.toy_ver}')
    arr_l1, arr_l2, arr_kp = rdr.predict_weights(df)

    log.info('Extracted toy weights')

    check_eff(arr_l1, mu=0.7, sg=0.05)
    check_eff(arr_l2, mu=0.7, sg=0.05)
    check_eff(arr_kp, mu=0.9, sg=0.02)

    log.info('Checked efficiencies')

    plt.hist(arr_l1, bins=80, range=(-0.1, 1.1), label='L1', alpha=0.75)
    plt.hist(arr_l2, bins=80, range=(-0.1, 1.1), label='L2', alpha=0.75)
    plt.hist(arr_kp, bins=80, range=(-0.1, 1.1), label='KP', alpha=0.75)

    plt.legend()

    plot_dir=utnr.make_dir_path('tests/pidreader/toy')
    plotpath=f'{plot_dir}/{df.treename}.png'
    log.visible(f'Saving to {plotpath}')
    plt.savefig(plotpath)
    plt.close('all')
#-----------------------------
def test_toy():
    df = make_data(nentries=40000)

    df.treename = 'ETOS'
    do_test_toy(df)

    df.treename = 'MTOS'
    do_test_toy(df)

    log.visible(f'Passed toy test')
#-----------------------------
def get_data(channel, year, entries=10000):
    if channel == 'ee':
        file_path = f'{data.dat_dir}/ctrl_ee/v10.11tf.3.0.x.x.0_v1/sweights_v0/{year}_mc_trigger_weights_sweighted.root'
        tree_path = 'KEE'
    elif channel == 'mm':
        file_path = f'{data.dat_dir}/ctrl_mm/v10.11tf.1.1.x.x.0_v1/sweights_v0/{year}_mc_trigger_weights_sweighted.root'
        tree_path = 'KMM'
    else:
        log.error(f'Invalid channel: {channel}')
        raise

    utnr.check_file(file_path)

    df=ROOT.RDataFrame(tree_path, file_path)
    df=df.Range(entries)
    df.treename= tree_path 
    df.year    = year

    return df
#-----------------------------
def test_pid_real(rd, df):
    arr_pid_l1, arr_pid_l2, arr_pid_kp=rd.predict_weights(df, replica=data.replica)

    plt.hist(arr_pid_l1, bins=100, range=(0, 1), label='L1', alpha=0.75)
    plt.hist(arr_pid_l2, bins=100, range=(0, 1), label='L2', alpha=0.75)
    plt.hist(arr_pid_kp, bins=100, range=(0, 1), label='K+', alpha=0.75)

    plotsdir=utnr.make_dir_path(f'tests/pidreader/test_1/{df.year}')
    plotpath= f'{plotsdir}/pid_{df.treename}.png'

    plt.legend()
    plt.savefig(plotpath)
    plt.close('all')

    arr_pid_rdr = arr_pid_l1 * arr_pid_l2 * arr_pid_kp
    arr_pid_sto = df.AsNumpy(['pid_eff'])['pid_eff']

    hobj = hist.axis.Regular(50, 0, 1, name="Eff", label="eff", underflow=False, overflow=False)

    h_rd = hist.Hist(hobj).fill(arr_pid_rdr)
    h_st = hist.Hist(hobj).fill(arr_pid_sto)
    
    fig = plt.figure(figsize=(10, 8))
    main_ax_artists, sublot_ax_arists = h_rd.plot_ratio(h_st,
        rp_ylabel=r"Ratio",
        rp_num_label="hist1",
        rp_denom_label="hist2",
        rp_uncert_draw_type="bar",  # line or bar
    )

    plotpath=f'{plotsdir}/pid_comparison_{df.treename}.png'
    plt.savefig(plotpath)
    plt.close('all')
#-----------------------------
def do_test_real(year):
    df_ee = get_data('ee', year)
    df_mm = get_data('mm', year)

    map_dir = f'{data.cal_dir}/PID/{data.rel_ver}/'
    rd=pidrd.reader()
    rd.setMapPath(map_dir)
    
    test_pid_real(rd, df_ee)
    test_pid_real(rd, df_mm)

    header=f'{"Year":<10}{"Key":<40}{"Unphysical":<15}{"Fraction":<10}'
    l_line=[header]
    
    l_line+=plot_unphysical(rd, 'eff_lep_above_KEE', df_ee)
    l_line+=plot_unphysical(rd, 'eff_lep_below_KEE', df_ee)
    l_line+=plot_unphysical(rd, 'eff_had_above_KEE', df_ee)
    l_line+=plot_unphysical(rd, 'eff_had_below_KEE', df_ee)
   
    l_line+=plot_unphysical(rd, 'eff_lep_above_KMM', df_mm)
    l_line+=plot_unphysical(rd, 'eff_lep_below_KMM', df_mm)
    l_line+=plot_unphysical(rd, 'eff_had_above_KMM', df_mm)
    l_line+=plot_unphysical(rd, 'eff_had_below_KMM', df_mm)

    tablepath=f'{data.tabledir}/unphysical_{year}.txt'
    otable=open(tablepath, 'w')
    for line in l_line:
        otable.write('{line}\n')
    otable.close()
#-----------------------------
def test_simple(year=2018, rel_ver='v3/nom'):
    df_ee = get_data('ee', year)
    df_mm = get_data('mm', year)

    rd=pidrd.reader()
    rd.setMapPath(f'{data.cal_dir}/PID/{rel_ver}')
    arr_l1, arr_l2, arr_hd = rd.predict_weights(df_ee)
    plot_eff(arr_l1, arr_l2, arr_hd, year, rel_ver, 'ee')

    arr_l1, arr_l2, arr_hd = rd.predict_weights(df_mm)
    plot_eff(arr_l1, arr_l2, arr_hd, year, rel_ver, 'mm')
#-----------------------------
def plot_eff(arr_l1, arr_l2, arr_had, year, rel_ver, chan):
    arr_eff = arr_l1 * arr_l2 * arr_had
    arr_lep = arr_l1 * arr_l2

    dir_path=f'tests/pidreader/simple/{year}/{rel_ver}'
    os.makedirs(dir_path, exist_ok=True)

    plt.hist(arr_eff, range=(0, 1), bins=50)
    plt.savefig(f'{dir_path}/eff_{chan}.png')
    plt.close('all')

    plt.hist(arr_lep, range=(0, 1) if chan == 'ee' else (0.9, 1), bins=50 if chan == 'ee' else 100)
    plt.savefig(f'{dir_path}/lep_{chan}.png')
    plt.close('all')

    plt.hist(arr_had, range=(0, 1), bins=50)
    plt.savefig(f'{dir_path}/had_{chan}.png')
    plt.close('all')
#-----------------------------
def test_real():
    for year in data.l_year:
        do_test_real(year)
        log.visible(f'Passed real test for year {year}')
#-----------------------------
def set_log():
    #pidrd.reader.log.setLevel(logging.WARNING)
    #pidrd.reader.log.setLevel(logging.DEBUG)
    utils.log.setLevel(logging.WARNING)
#-----------------------------
if __name__ == '__main__':
    set_log()

    for year in data.l_year:
        for rel in data.l_rel:
            test_simple(year, rel)

