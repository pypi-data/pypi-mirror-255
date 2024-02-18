import ROOT

from rk.wgt_mgr import wgt_mgr
from atr_mgr    import mgr     as amgr

import read_selection as rs
import utils_noroot   as utnr 
import os
import logging 
import pprint

import utils
import calc_utility
import rk.selection as rksl

from rk.df_getter     import df_getter  as dfg
from rk.mva           import mva_man
from rk.q2smear       import q2smear
from rk.trgreader     import reader     as trg_reader 
from rk.weight_reader import weight_reader 
from rk.pidreader     import reader     as pid_reader 
from atr_mgr          import mgr        as amgr 

log=utnr.getLogger(__name__)
#--------------------------------
def set_log_level(level):
    utils.log.setLevel(level)
    calc_utility.log.setLevel(level)
    rksl.log.setLevel(level)
    dfg.log.setLevel(level)
    mva_man.log.setLevel(level)
    
    q2smear.log.setLevel(level)
    wgt_mgr.log.setLevel(level)
    pid_reader.log.setLevel(level)
    trg_reader.log.setLevel(level)
    amgr.log.setLevel(level)
#---------------------------------------
class data:
    dat_dir   = os.environ['DATDIR']
    year      = '2018'
    version   = 'v10.18is'
    partition = (1, 1000)
    selection = 'all_gorder'
    truth_corr= 'final_no_truth_mass_bdt'
    proc_ee   = 'ctrl_ee'
    proc_mm   = 'ctrl_mm'
    l_trigger = ['MTOS', 'ETOS', 'GTIS']
    cas_dir   = os.environ['CASDIR']
#---------------------------------------
def get_settings(index, trig, kind):
    d_set = {}

    d_set['val_dir'] = f'tests/wgt_mgr/{kind}/{trig}/test_{index:02d}'
    d_set['channel'] = 'electron'  if trig == 'MTOS' else 'muon'
    d_set['replica'] = 0 

    if index > 0:
        d_set['bts_sys'] ='nom'
        d_set['bts_ver'] = 200

    if index > 1:
        d_set['pid_sys'] ='nom'

    if index > 2:
        d_set['trk_sys'] ='nom'

    if index > 3:
        d_set['gen_sys'] ='nom'

    if index > 4:
        d_set['lzr_sys'] ='nom'

    if index > 5:
        d_set['hlt_sys'] ='nom'

    if index > 6:
        d_set['rec_sys'] ='nom'

    if index > 7:
        d_set['bdt_sys'] ='nom'

    if index > 8 and trig != 'MTOS':
        d_set['qsq_sys'] ='nom'

    for key, val in d_set.items():
        if not key.endswith('_sys'):
            continue

        if   kind == 'all' and key != 'bts_sys':
            d_set[key] = 'all' 
        elif kind == 'all' and key == 'bts_sys':
            d_set[key] = 'nom' 
        elif kind == 'off' and key != 'bts_sys':
            d_set[key] = '000' 
        elif kind == 'off' and key == 'bts_sys':
            d_set[key] = 'nom' 
        elif kind == 'nom':
            pass
        elif kind == 'bts' and key == 'bts_sys':
            d_set[key] = 'all' 
        elif kind == 'bts' and key != 'bts_sys':
            d_set[key] = 'nom' 
        else:
            log.error(f'Invalid kind {kind}')
            raise

    return d_set
#---------------------------------------
def get_data(vers, tree_name):
    proc = data.proc_mm if tree_name in ['MTOS', 'KMM'] else data.proc_ee

    file_path = f'{data.dat_dir}/{proc}/{vers}/{data.year}.root'
    utnr.check_file(file_path)

    df = ROOT.RDataFrame(tree_name, file_path)
    df = df.Range(data.max_evt)

    df.filepath = file_path
    df.treename = tree_name 
    df.year     = data.year

    return df
#---------------------------------------
def truth_match(df, trigger):
    proc = data.proc_mm if trigger == 'MTOS' else data.proc_ee

    cut  = rs.get_truth(proc)

    obj  = amgr(df)

    df   = df.Filter(cut, 'truth')

    df   = obj.add_atr(df)

    return df
#---------------------------------------
def add_extra(df):
    trigger = df.treename
    year    = df.year
    proc    = data.proc_mm if df.treename in ['MTOS', 'KMM'] else data.proc_ee

    d_sel   = rksl.selection('all', trigger, year, proc)
    pid_cut = d_sel['pid']

    obj     = amgr(df)
    df      = df.Define('pid_sim', f'bool pas = {pid_cut}; return int (pas);')
    df      = obj.add_atr(df)

    return df
#---------------------------------------
def add_truth(df):
    obj = amgr(df)

    df  = df.Define( 'B_PT', 'TVector3 v(B_TRUEP_X, B_TRUEP_Y, B_TRUEP_Z); return v.Perp();')
    df  = df.Define('B_ETA', 'TVector3 v(B_TRUEP_X, B_TRUEP_Y, B_TRUEP_Z); return v.Eta();')

    df  = obj.add_atr(df)

    return df
#---------------------------------------
def test_off(trig):
    proc  = data.proc_mm if trig == 'MTOS' else data.proc_ee
    gtr   = dfg(proc, data.year, data.version, data.partition)
    df_gn = gtr.get_df('gen')
    df_rc = gtr.get_df('rec')
    df_sl = gtr.get_df('sel', trigger=trig, selection=data.selection, truth_corr_type=data.truth_corr, using_wmgr=True)

    df_rc.trigger = trig
    df_sl.trigger = trig

    d_set = get_settings(100, trig, 'off')
    obj   = wgt_mgr(d_set)

    rdg = obj.get_reader('gen', df_gn)
    rdr = obj.get_reader('rec', df_rc)
    rdw = obj.get_reader('raw', df_rc)
    rsl = obj.get_reader('sel', df_sl)

    d_g = rdg.get_weights()
    d_r = rdr.get_weights()
    d_w = rdw.get_weights()
    d_s = rsl.get_weights()
#---------------------------------------
def test_nom(trig):
    proc  = data.proc_mm if trig == 'MTOS' else data.proc_ee
    gtr   = dfg(proc, data.year, data.version, data.partition)
    df_gn = gtr.get_df('gen')
    df_rc = gtr.get_df('rec')
    df_sl = gtr.get_df('sel', trigger=trig, selection=data.selection, truth_corr_type=data.truth_corr, using_wmgr=True)

    d_set = get_settings(100, trig, 'nom')
    obj   = wgt_mgr(d_set)

    df_rc.trigger = trig
    df_sl.trigger = trig

    rdg = obj.get_reader('gen', df_gn)
    rdr = obj.get_reader('rec', df_rc)
    rdw = obj.get_reader('raw', df_rc)
    rsl = obj.get_reader('sel', df_sl)

    d_g = rdg.get_weights()
    d_r = rdr.get_weights()
    d_w = rdw.get_weights()
    d_s = rsl.get_weights()
#---------------------------------------
def test_sel(trig):
    file_wc = f'{data.cas_dir}/tools/apply_selection/data_mc/ctrl/v10.18is/{data.year}_{trig}/*.root'
    df_sl=ROOT.RDataFrame(trig, file_wc)
    df_sl.trigger = trig
    df_sl.treename= trig
    df_sl.year    = data.year 
    df_sl.filepath= file_wc

    d_set = get_settings(9, trig, 'nom')

    log.visible('Running weight manager code')

    obj   = wgt_mgr(d_set)
    rsl   = obj.get_reader('sel', df_sl)

    arr_pid = rsl('pid', 'nom')
    arr_trk = rsl('trk', 'nom')
    arr_gen = rsl('gen', 'MTOS')
    arr_lzr = rsl('lzr', 'L0ElectronTIS')
    arr_hlt = rsl('hlt', 'ETOS')
    arr_rec = rsl('rec', 'ETOS')
    arr_qsq = rsl('qsq', 'nom')
    arr_bdt = rsl('bdt', 'nom')
#---------------------------------------
def test_print(trig):
    d_set = get_settings(100, trig, 'nom')
    obj   = wgt_mgr(d_set)

    log.info(obj)
#---------------------------------------
def test_all(trig):
    proc  = data.proc_mm if trig == 'MTOS' else data.proc_ee
    gtr   = dfg(proc, data.year, data.version, data.partition)
    df_gn = gtr.get_df('gen')
    df_rc = gtr.get_df('rec')
    df_sl = gtr.get_df('sel', trigger=trig, selection=data.selection, truth_corr_type=data.truth_corr, using_wmgr=True)

    d_set = get_settings(100, trig, 'all')
    obj   = wgt_mgr(d_set)

    rdg = obj.get_reader('gen', df_gn)
    rdr = obj.get_reader('rec', df_rc)
    rdw = obj.get_reader('raw', df_rc)
    rsl = obj.get_reader('sel', df_sl)

    d_wgt_g = rdg.get_weights()
    d_wgt_r = rdr.get_weights()
    d_wgt_w = rdw.get_weights()
    d_wgt_s = rsl.get_weights()
#---------------------------------------
def test_bts(trig):
    proc  = data.proc_mm if trig == 'MTOS' else data.proc_ee
    gtr   = dfg(proc, data.year, data.version, data.partition)
    df_gn = gtr.get_df('gen')
    df_rc = gtr.get_df('rec')
    df_sl = gtr.get_df('sel', trigger=trig, selection=data.selection, truth_corr_type=data.truth_corr, using_wmgr=True)

    d_set = get_settings(100, trig, 'bts')
    obj   = wgt_mgr(d_set)

    rdg = obj.get_reader('gen', df_gn)
    rdr = obj.get_reader('rec', df_rc)
    rdw = obj.get_reader('raw', df_rc)
    rsl = obj.get_reader('sel', df_sl)

    d_wgt_g = rdg.get_weights()
    d_wgt_r = rdr.get_weights()
    d_wgt_w = rdw.get_weights()
    d_wgt_s = rsl.get_weights()
#---------------------------------------
def main():
    test_sel('ETOS')
    return
    test_off('ETOS')
    test_nom('ETOS')
    test_print('ETOS')
    test_all('ETOS')
    test_bts('ETOS')

    for trigger in data.l_trigger:
        for index in range(0, 8):
            test_nom(index, trigger)
            log.visible(f'Passed {trigger}: {index}/7')

        break
#---------------------------------------
if __name__ == '__main__':
    set_log_level(logging.WARNING)

    main()

