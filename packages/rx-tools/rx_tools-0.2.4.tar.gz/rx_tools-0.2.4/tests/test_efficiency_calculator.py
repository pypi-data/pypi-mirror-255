from rk.calculator            import calculator      as eff_cal
from rk.efficiency            import efficiency      as eff
from rk.wgt_mgr               import wgt_mgr         as wmg
from rk.cutflow               import cutflow_manager as ctfm

from rk.trackreader           import reader          as trk
from rk.trgreader             import reader          as pid
from rk.pidreader             import reader          as trg
from rk.weight_reader         import weight_reader   as wrd 
from rk.q2smear               import q2smear         as qsq 
from rk.mva                   import mva_man         as mva

from atr_mgr                  import mgr             as amg
from pprint                   import pprint

import utils_noroot      as utnr
import matplotlib.pyplot as plt
import pandas            as pnd
import utils
import math 
import logging
import logzero
import numpy
import os

#---------------------------------------
class data:
    log             = utnr.getLogger(__name__)
    version         = 'v10.18is'
    selection       = 'all_gorder'
    trigger         = 'ETOS'
    channel         = 'electron'
    truth_corr      = 'final_no_truth_mass_bdt'
    year            = '2018'
    proc            = 'ctrl_ee'

    test_partition  = 1, 10000
    small_partition = 1,  1000
    plot_dir        = utnr.make_dir_path('tests/efficiency/calculator_diff/plots')
#---------------------------------------
def set_logger(level):
    trg.log.setLevel(level)
    wrd.log.setLevel(level)
    pid.log.setLevel(level)
    qsq.log.setLevel(level)
    amg.log.setLevel(level)
    mva.log.setLevel(level)
    eff.log.setLevel(level)
    ctfm.log.setLevel(level)

    utils.log.setLevel(level)
#---------------------------------------
def get_wgt_opt(val_dir, syst='nom'):
    d_set = {}

    d_set['val_dir'] = val_dir 
    d_set['channel'] = data.channel 
    d_set['replica'] = 0 

    d_set['gen_sys'] = syst 
    d_set['rec_sys'] = syst 
    d_set['lzr_sys'] = syst 
    d_set['hlt_sys'] = syst 
    d_set['pid_sys'] = syst 
    d_set['trk_sys'] = syst 
    d_set['bts_sys'] = syst 
    d_set['bts_ver'] = 200 
    d_set['bdt_sys'] = syst 

    if data.channel != 'muon':
        d_set['qsq_sys'] = syst
    else:
        d_set['qsq_sys'] ='0'

    return d_set 
#---------------------------------------
@utnr.timeit
def test_geo_rec(wman):
    obj   = eff_cal(data.proc, data.year, version=data.version, partition=data.small_partition)
    eff_g = obj.get_geo()
    eff_r = obj.get_rec(weight_manager=wman)

    eff = eff_g * eff_r

    eff_g.show()
    eff_r.show()
    
    eff.show()
#---------------------------------------
@utnr.timeit
def test_all(wman, partition=None):
    suffix = 'nowgt' if wman is None else 'wgt'

    out_dir=utnr.make_dir_path(f'tests/efficiency/calculator_{suffix}')

    obj   = eff_cal(data.proc, data.year, version=data.version, partition=partition)
    obj.out_dir = out_dir

    d_eff_g = obj.get_geo()
    d_eff_r = obj.get_rec(weight_manager=wman)
    d_eff_s = obj.get_sel(weight_manager=wman, truth_corr_type=data.truth_corr, selection=data.selection, trigger=data.trigger)

    mg        = ctfm()
    mg['gen'] = d_eff_g
    mg['rec'] = d_eff_r
    mg['sel'] = d_eff_s
    d_cf      = mg.get_cf()
#---------------------------------------
@utnr.timeit
def test_dif(wman, partition=None):
    out_dir  = utnr.make_dir_path(f'tests/efficiency/calculator_diff')
    out_path = f'{out_dir}/diff_cuflow_wgt.pkl' if wman is not None else f'{out_dir}/diff_cuflow_nowgt.pkl'
    eff_path = f'{out_dir}/defficiency_wgt.tex' if wman is not None else f'{out_dir}/defficiency_nowgt.tex'
    if os.path.isfile(out_path):
        d_cf = utnr.load_pickle(out_path)
        data.log.visible(f'Loading cached cutflow: {out_path}')
        plot_dcf(d_cf, partition)

        df = get_df_from_cf(d_cf)
        utnr.df_to_tex(df.T, eff_path)

        return d_cf

    obj         = eff_cal(data.proc, data.year, version=data.version, partition=partition)
    obj.out_dir = out_dir
    obj.add_var('BDT'              , numpy.linspace(   0,   1.1, 10))
    obj.add_var('B_PT'             , numpy.linspace(   0, 25000, 10))
    obj.add_var('B_ETA'            , numpy.linspace(   0,     5, 10))
    obj.add_var('B_const_mass_M[0]', numpy.linspace(5200,  6000, 10))
    
    d_eff_g = obj.get_geo()
    d_eff_r = obj.get_rec(weight_manager=wman)
    d_eff_s = obj.get_sel(weight_manager=wman, truth_corr_type=data.truth_corr, selection=data.selection, trigger=data.trigger)

    mg        = ctfm()
    mg['gen'] = d_eff_g
    mg['rec'] = d_eff_r
    mg['sel'] = d_eff_s
    d_cf      = mg.get_cf()

    utnr.dump_pickle(d_cf, out_path)
    plot_dcf(d_cf, partition)

    df = get_df_from_cf(d_cf)
    utnr.df_to_tex(df.T, eff_path) 

    return d_cf
#---------------------------------------
def get_df_from_cf(d_cf):
    df = pnd.DataFrame(columns=list(d_cf.x_axis), index=list(d_cf.y_axis))
    for sys in d_cf.x_axis:
        l_val     = check_deff(d_cf, sys)
        l_val_str = [ f'{val:.3e}' for val in l_val]
        df[sys]   = l_val_str

    return df
#---------------------------------------
@utnr.timeit
def test_int_dif(wman, partition=None, d_cf_dif=None):
    out_dir  =utnr.make_dir_path(f'tests/efficiency/calculator_diff')
    out_path = f'{out_dir}/int_cuflow_wgt.pkl' if wman is not None else f'{out_dir}/int_cuflow_nowgt.pkl'
    if os.path.isfile(out_path):
        d_cf_int = utnr.load_pickle(out_path)
        data.log.visible(f'Loading cached cutflow: {out_path}')
        check_eq_cf(d_cf_dif, d_cf_int)

        return

    obj         = eff_cal(data.proc, data.year, version=data.version, partition=partition)
    obj.out_dir = out_dir
    
    d_eff_g = obj.get_geo()
    d_eff_r = obj.get_rec(weight_manager=wman)
    d_eff_s = obj.get_sel(weight_manager=wman, truth_corr_type=data.truth_corr, selection=data.selection, trigger=data.trigger)

    mg        = ctfm()
    mg['gen'] = d_eff_g
    mg['rec'] = d_eff_r
    mg['sel'] = d_eff_s
    d_cf_int  = mg.get_cf()

    utnr.dump_pickle(d_cf_int, out_path)
    check_eq_cf(d_cf_dif, d_cf_int)
#---------------------------------------
def check_eq_cf(d_cf_dif, d_cf_int):
    l_sys = d_cf_dif.x_axis
    l_var = d_cf_dif.y_axis

    success=True
    for var in sorted(l_var):
        for sys in sorted(l_sys):
            cf_dif = d_cf_dif[sys, var]
            cf_int = d_cf_int[sys]

            eff_int      = cf_int.efficiency
            ieff_vl, _, _= eff_int.val

            eff_dif      = cf_dif.efficiency.efficiency()
            deff_vl, _, _= eff_dif.val

            try:
                assert(math.isclose(deff_vl, ieff_vl, abs_tol=1e-6))
                data.log.visible(f'Pass: ({sys}, {var})')
            except AssertionError:
                data.log.error(f'{sys:<20}{var:<20}{deff_vl:<20.6e}{ieff_vl:<20.6e}')
                print(cf_dif)
                print(cf_int)
                success=False

    assert(success)
#---------------------------------------
def plot_dcf(d_cf, partition):
    l_syst_allowed = ['nom', 'gen_npv', 'rec_GTIS_ee', 'lzr_L0ElectronHAD']
    l_sty          = ['-', '-.', ':', '--']
    l_syst         = [ syst for syst in d_cf.x_axis if syst in l_syst_allowed]

    for var in sorted(d_cf.y_axis):
        print(var)
        eff_max = 0
        for ls, sys in zip(l_sty, l_syst):
            print(f'{"":<4}{sys:<20}')
            cf = d_cf[sys, var]
            eff= cf.efficiency

            eff.plot(linestyle=ls)
            if eff.max > eff_max:
                eff_max = eff.max

        plot_path = f'{data.plot_dir}/{var}.png'
        plt.gca().set_ylim(0, 1.05 * eff_max)
        plt.title(f'{data.proc}, {data.year}, {str(partition)}')
        plt.tight_layout()
        plt.legend()
        plt.savefig(plot_path)
        plt.close('all')
#---------------------------------------
def check_deff(d_cf, sys):
    l_val = []
    for var in d_cf.y_axis:
        cf   = d_cf[sys, var]
        deff = cf.efficiency
        teff = deff.efficiency()
        val, _, _ = teff.val
        l_val.append(val)

    for val in l_val:
        assert( math.isclose(l_val[0], val, abs_tol=1e-10) )

    return l_val
#---------------------------------------
@utnr.timeit
def test_geo():
    obj = eff_cal('ctrl_ee', data.year, version=data.version, partition=data.small_partition)
    eff = obj.get_geo()

    eff.show()
#---------------------------------------
@utnr.timeit
def test_rec():
    obj = eff_cal('ctrl_ee', data.year, version=data.version, partition=data.small_partition)
    eff = obj.get_rec()

    eff.show()
#---------------------------------------
@utnr.timeit
def test_no_bdt():
    out_dir = 'tests/efficiency/calculator_diff/wmgr_no_bdt'
    d_opt=get_wgt_opt(out_dir)
    wman =wmg(d_opt)

    obj = eff_cal('ctrl_ee', data.year, version=data.version, partition=data.small_partition)
    obj.add_var('BDT_prc', numpy.linspace(0, 1.1, 10))
    obj.add_var('BDT_cmb', numpy.linspace(0, 1.1, 10))
    obj.out_dir = out_dir

    d_eff = obj.get_sel(weight_manager=wman, selection='all_gorder_no_bdt', trigger='ETOS', truth_corr_type=data.truth_corr)

    deff_prc = d_eff['nom', 'BDT_prc']
    deff_cmb = d_eff['nom', 'BDT_cmb']

    print(deff_prc)
    print(deff_cmb)
#---------------------------------------
@utnr.timeit
def test_boost():
    out_dir = 'tests/efficiency/calculator_diff/boost'
    d_opt=get_wgt_opt(out_dir)

    d_opt['bts_ver'] = 30 
    d_opt['bts_sys'] = 'all'
    wman =wmg(d_opt)

    obj = eff_cal('ctrl_ee', data.year, version=data.version, partition=data.test_partition)
    obj.add_var('BDT_prc', numpy.linspace(0, 1.1, 10))
    obj.add_var('BDT_cmb', numpy.linspace(0, 1.1, 10))
    obj.out_dir = out_dir

    d_eff_g = obj.get_geo()
    d_eff_r = obj.get_rec(weight_manager=wman)
    d_eff_s = obj.get_sel(weight_manager=wman, selection='all_gorder_no_bdt', trigger='ETOS', truth_corr_type=data.truth_corr)

    deff_prc = d_eff_s['nom', 'BDT_prc']
    deff_cmb = d_eff_s['nom', 'BDT_cmb']

    print(deff_prc)
    print(deff_cmb)
#---------------------------------------
@utnr.timeit
def test_no_cmb_bdt():
    out_dir = 'tests/efficiency/calculator_diff/wmgr_no_cmb_bdt'
    d_opt=get_wgt_opt(out_dir)
    wman =wmg(d_opt)

    obj = eff_cal('ctrl_ee', data.year, version=data.version, partition=data.small_partition)
    obj.add_var('BDT_prc', numpy.linspace(0, 1.1, 10))
    obj.out_dir = out_dir

    d_eff = obj.get_sel(weight_manager=wman, selection='all_gorder_no_cmb_bdt', trigger='ETOS', truth_corr_type=data.truth_corr)

    deff_prc = d_eff['nom', 'BDT_prc']
    print(deff_prc)
#---------------------------------------
@utnr.timeit
def test_no_prc_bdt():
    out_dir = 'tests/efficiency/calculator_diff/wmgr_no_prc_bdt'
    d_opt=get_wgt_opt(out_dir)
    wman =wmg(d_opt)

    obj = eff_cal('ctrl_ee', data.year, version=data.version, partition=data.small_partition)
    obj.add_var('BDT_cmb', numpy.linspace(0, 1.1, 10))
    obj.out_dir = out_dir

    d_eff = obj.get_sel(weight_manager=wman, selection='all_gorder_no_prc_bdt', trigger='ETOS', truth_corr_type=data.truth_corr)

    deff_prc = d_eff['nom', 'BDT_cmb']
    print(deff_prc)
#---------------------------------------
def main():
    utnr.timer_on = True

    test_boost()

    return
    test_no_bdt()
    test_no_cmb_bdt()
    test_no_prc_bdt()

    data.plot_dir = utnr.make_dir_path('tests/efficiency/calculator_diff/plots/int_dif_wgt')

    wman=get_wgt_mgr('tests/efficiency/calculator_diff/wdif')
    d_cf_dif = test_dif(wman, (0, 50))


    wman=get_wgt_mgr('tests/efficiency/calculator_diff/wint')
    test_int_dif(wman, (0, 50), d_cf_dif)

    data.plot_dir = utnr.make_dir_path('tests/efficiency/calculator_diff/plots/int_dif_nowgt')
    wman=None
    d_cf_dif = test_dif(wman, (0, 50))
    
    wman=None
    test_int_dif(wman, (0, 50), d_cf_dif)


    eff_cal.log.level = logging.DEBUG
    set_logger(logging.WARNING)

    wman=get_wgt_mgr()
    test_all(wman, (0, 500))

    wman=get_wgt_mgr()
    cf_0=test_all(wman, (0, 2))

    wman=get_wgt_mgr()
    cf_1=test_all(wman, (1, 2))

    wman=get_wgt_mgr()
    cf_2=test_all(wman,   None)

    if cf_2 == cf_0 + cf_1:
        data.log.visible('Splitting passed')
    else:
        data.log.error('Splitting failed')
        print(cf_0.df_eff)
        print(cf_1.df_eff)
        print(cf_2.df_eff)
        raise

    wman=get_wgt_mgr()
    test_geo_rec(wman)

    test_geo()
    test_rec()
    test_loose_000(smear= True)
    test_loose_000(smear=False)

    test_loose_001(smear= True)
    test_loose_001(smear=False)

    utnr.timer_on = False
#---------------------------------------
def set_log_level():
    utils.log.setLevel(logging.WARNING)

    qsq.log.setLevel(logging.WARNING)
    wrd.log.setLevel(logging.VISIBLE)
    pid.log.setLevel(logging.WARNING)
    trg.log.setLevel(logging.WARNING)
    trk.log.setLevel(logging.WARNING)
    mva.log.setLevel(logging.WARNING)

    from atr_mgr      import mgr         as amgr 
    from hep_cl       import hist_reader as hrd
    from rk.df_getter import df_getter   as dfg

    import read_selection    as rsl

    amgr.log.setLevel(logging.WARNING)
    hrd.log.setLevel(logging.WARNING)
    dfg.log.setLevel(logging.INFO)
    rsl.log.setLevel(logzero.WARNING)
#----------------------------
if __name__ == '__main__':
    set_log_level()
    main()

