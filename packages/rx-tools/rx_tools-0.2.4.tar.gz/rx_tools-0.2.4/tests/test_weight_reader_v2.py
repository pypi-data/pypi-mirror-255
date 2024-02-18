import ROOT
import logging
import os
import glob
import re
import matplotlib.pyplot as plt

from rk.pidreader     import reader     as pid_reader
from rk.trgreader     import reader     as trg_reader
from rk.trackreader   import reader     as tra_reader
from rk.oscillator    import oscillator as osc
from rk.q2smear       import q2smear
from rk.weight_reader import weight_reader

import utils_noroot  as utnr
import pandas        as pnd
import utils

import style

#----------------------------
class wr_vars:
    log                   = utnr.getLogger(__name__)
    utnr.timer_on         = True
    weight_reader.replica = 0
    osc.ntest             = 0
    nentries              = 1000
#----------------------------
def set_log_level():
    weight_reader.log.setLevel(logging.VISIBLE)

    q2smear.log.setLevel(logging.WARNING)
    utils.log.setLevel(logging.WARNING)
    pid_reader.log.setLevel(logging.WARNING)
    trg_reader.log.setLevel(logging.WARNING)
    tra_reader.log.setLevel(logging.WARNING)

    from atr_mgr import mgr         as amgr 
    from hep_cl  import hist_reader as hrd

    amgr.log.setLevel(logging.WARNING)
    hrd.log.setLevel(logging.WARNING)
#----------------------------
def get_versions():
    d_ver         = {}
    d_ver['gen']  = 'v27'
    d_ver['rec']  = 'v31'
    d_ver['lzr']  = 'v22'
    d_ver['hlt']  = 'v22'
    d_ver['pid']  = 'v4'
    d_ver['qsq']  = 'v13'
    d_ver['trk']  = 'v1'
    d_ver['bts']  = '1'
    d_ver['bdt']  = 'v3'
    d_ver['dcm']  = 'v1.0'

    return d_ver
#----------------------------
def get_kin_syst(df, setting):
    nominal = True if setting in ['nom', 'bts'] else False
    d_syst = {}

    if nominal:
        d_syst['gen'] = 'nom'
        d_syst['rec'] = 'nom' 
    else:
        d_syst['gen'] = 'all'
        d_syst['rec'] = 'all'

    return d_syst
#----------------------------
def get_trg_syst(df, setting):
    nominal = True if setting in ['nom', 'bts'] else False
    d_syst = {}

    if   df.trigger == 'ETOS':
        d_syst['lzr'] = 'nom' if nominal else 'all'
    elif df.trigger == 'MTOS':
        d_syst['lzr'] = 'nom' if nominal else 'all' 
    elif df.trigger == 'GTIS':
        d_syst['lzr'] = 'nom' if nominal else 'all' 
    else:
        log.error(f'Invalid trigger: {df.trigger}')
        raise

    d_syst['hlt'] = 'nom'

    return d_syst
#----------------------------
def get_pid_syst(df, setting):
    nominal = True if setting in ['nom', 'bts'] else False
    d_syst = {}

    if nominal:
        d_syst['pid'] = 'nom' 
    else:
        d_syst['pid'] = 'all' 

    return d_syst
#----------------------------
def get_qsq_syst(df, setting):
    nominal = True if setting in ['nom', 'bts'] else False

    d_syst = {}

    if               df.trigger == 'MTOS':
        d_syst['qsq'] = '000'
    elif nominal and df.trigger != 'MTOS':
        d_syst['qsq'] = 'nom'
    else:
        d_syst['qsq'] = 'all'

    return d_syst
#----------------------------
def get_dcm_syst(df, setting):
    nominal = True if setting in ['nom', 'bts'] else False

    d_syst = {}

    if nominal:
        d_syst['dcm'] = 'nom' 
    else:
        d_syst['dcm'] = 'all' 

    return d_syst
#----------------------------
def get_bts_syst(df, setting):
    if   setting in ['nom', 'all']:
        value = 'nom'
    elif setting == 'bts':
        value = 'all'
    else:
        log.error(f'Invalid setting {setting}')
        raise

    return {'bts' : value} 
#----------------------------
def get_bdt_syst(df, setting):
    return {'bdt' : 'nom'} 
#----------------------------
def get_systematics(df, setting):
    d_syst = {}

    d_syst.update(get_kin_syst(df, setting))
    d_syst.update(get_trg_syst(df, setting))
    d_syst.update(get_pid_syst(df, setting))
    d_syst.update(get_qsq_syst(df, setting))
    d_syst.update(get_bts_syst(df, setting))
    d_syst.update(get_bdt_syst(df, setting))
    d_syst.update(get_dcm_syst(df, setting))

    d_syst['trk'] = 'nom'

    return d_syst
#----------------------------
def config(wgt, setting):
    d_ver = get_versions()
    d_sys = get_systematics(wgt.df, setting)
    for kind in ['gen', 'rec', 'lzr', 'hlt', 'pid', 'qsq', 'trk', 'bts', 'bdt', 'dcm']:
        ver = d_ver[kind]
        sys = d_sys[kind]

        wgt[kind] = ver, sys

    return wgt
#----------------------------
def get_paths(proc, trig, year, kind, vers):
    cas_dir = os.environ['CASDIR']
    file_wc = f'{cas_dir}/tools/apply_selection/data_mc/ctrl/v10.18is/{year}_{trig}/*.root'
    # file_wc = f'{cas_dir}/tools/apply_selection/data_mc/sign/v10.18is/{year}_{trig}/*.root' # Change to high q2 region when testing decay model weight.

    l_file  = glob.glob(file_wc)

    if len(l_file) == 0:
        wr_vars.log.error(f'No files found in: {file_wc}')
        raise FileNotFoundError

    return file_wc 
#----------------------------
def get_df(proc, trigger, year, kind, vers):
    filepath = get_paths(proc, trigger, year, kind, vers)

    wr_vars.log.visible(f'Using: {filepath}:{trigger}')

    df=ROOT.RDataFrame(trigger, filepath)
    if wr_vars.nentries > 0:
        df = df.Range(wr_vars.nentries)

    df.treename = trigger 
    df.year     = year
    df.filepath = filepath
    df.trigger  = trigger
    df.proc     = proc

    return df 
#----------------------------
@utnr.timeit
def test_selection():
    vers         = 'v10.18'
    proc         = 'sign'

    trig         = 'MTOS'
    year         = '2018'
    kind         = 'sel'
    syst         = 'nom'

    out_dir      = f'tests/weight_reader/selection/{proc}_{trig}_{year}_{kind}_{syst}'
    rdf          = get_df(proc, trig, year, kind, vers)

    wgt          = weight_reader(rdf, kind)
    wgt          = config(wgt, syst)
    wgt.valdir   = out_dir 
    d_arr_wgt    = wgt.get_weights()

    df_wgt       = pnd.DataFrame(d_arr_wgt)
    df_wgt.to_json(f'{out_dir}/weight.json')

    df_wgt.plot.hist(column=['nom'], bins=50, histtype='step')
    plt.legend([])
    plt.savefig(f'{out_dir}/weight.png')
    plt.close('all')
#----------------------------
@utnr.timeit
def test_no_bdt():
    vers         = 'v10.18'
    proc         = 'sign'

    trig         = 'MTOS'
    year         = '2018'
    kind         = 'sel'
    syst         = 'nom'

    out_dir      = f'tests/weight_reader/no_bdt/{proc}_{trig}_{year}_{kind}_{syst}'
    rdf          = get_df(proc, trig, year, kind, vers)

    wgt          = weight_reader(rdf, kind)
    wgt          = config(wgt, syst)
    wgt['bdt']   = 'v1', '000'
    wgt.valdir   = out_dir 
    d_arr_wgt    = wgt.get_weights()

    df_wgt       = pnd.DataFrame(d_arr_wgt)
    df_wgt.to_json(f'{out_dir}/weight.json')

    df_wgt.plot.hist(column=['nom'], bins=50, histtype='step')
    plt.legend([])
    plt.savefig(f'{out_dir}/weight.png')
    plt.close('all')
#----------------------------
@utnr.timeit
def test_boost():
    vers         = 'v10.18'
    proc         = 'sign'

    trig         = 'MTOS'
    year         = '2018'
    kind         = 'sel'
    syst         = 'nom'

    out_dir      = f'tests/weight_reader/boost/{proc}_{trig}_{year}_{kind}_{syst}'
    rdf          = get_df(proc, trig, year, kind, vers)

    wgt          = weight_reader(rdf, kind)
    wgt          = config(wgt, syst)
    wgt['bts']   = 3, 'all' 
    wgt.valdir   = out_dir 
    d_arr_wgt    = wgt.get_weights()

    df_wgt       = pnd.DataFrame(d_arr_wgt)
    df_wgt.to_json(f'{out_dir}/weight.json', indent=4)

    df_wgt.plot.hist(column=['nom'], bins=50, histtype='step')
    plt.legend([])
    plt.savefig(f'{out_dir}/weight.png')
    plt.close('all')
#----------------------------
@utnr.timeit
def test_syst():
    vers         = 'v10.18'
    proc         = 'sign'

    trig         = 'ETOS'
    year         = '2018'
    kind         = 'sel'
    syst         = 'nom'

    out_dir      = f'tests/weight_reader/syst/{proc}_{trig}_{year}_{kind}_{syst}'
    rdf          = get_df(proc, trig, year, kind, vers)

    wgt          = weight_reader(rdf, kind)
    wgt          = config(wgt, 'all')
    wgt['bts']   = 3, 'nom' 
    wgt.valdir   = out_dir 
    # wgt.no_corr  = True
    d_arr_wgt    = wgt.get_weights()

    df_wgt       = pnd.DataFrame(d_arr_wgt)
    df_wgt.to_json(f'{out_dir}/weight.json', indent=4)

    df_wgt.plot.hist(column=['nom'], bins=50, histtype='step')
    plt.legend([])
    plt.savefig(f'{out_dir}/weight.png')
    plt.close('all')
#----------------------------
def main():
    test_syst()
    return
    test_boost()
    test_selection()
    test_no_bdt()
#----------------------------
if __name__ == '__main__':
    set_log_level()
    main()


