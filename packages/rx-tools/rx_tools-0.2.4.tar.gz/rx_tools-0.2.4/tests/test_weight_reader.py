import ROOT
import logging
import os
import re
import matplotlib.pyplot as plt

from atr_mgr          import mgr        as amgr
from rk.pidreader     import reader     as pid_reader
from rk.trgreader     import reader     as trg_reader
from rk.trackreader   import reader     as tra_reader
from rk.oscillator    import oscillator as osc
from rk.q2smear       import q2smear
from rk.weight_reader import weight_reader

import utils_noroot  as utnr
import utils

import style

log=utnr.getLogger(__name__)
#----------------------------
osc.ntest = 0
#----------------------------
class wr_vars:
    ee_sel_version = None
    mm_sel_version = None

    nentries       = 10000

    ee_rec_version = 'v10.11tf' 
    mm_rec_version = 'v10.11tf' 

    ee_gen_version = 'v0' 
    mm_gen_version = 'v0' 

    ee_sel_version = 'v10.11tf.a0v1.3.0.1.0.0_v3'
    mm_sel_version = 'v10.11tf.a0v1.1.1.1.0.0_v3'
#----------------------------
#----------------------------
def set_log_level():
    q2smear.log.setLevel(logging.VISIBLE)
    utils.log.setLevel(logging.VISIBLE)
    weight_reader.log.setLevel(logging.DEBUG)
    osc.log.setLevel(logging.VISIBLE)
    amgr.log.setLevel(logging.VISIBLE)
    pid_reader.log.setLevel(logging.VISIBLE)
    trg_reader.log.setLevel(logging.VISIBLE)
    tra_reader.log.setLevel(logging.VISIBLE)
#----------------------------
def get_paths(proc, trigger, year, kind):
    dat_dir = os.environ['DATDIR']

    if   kind == 'sel' and trigger in ['ETOS', 'GTIS']:
        filepath=f'{dat_dir}/{proc}_ee/{wr_vars.ee_sel_version}/{year}.root'
        treepath=trigger
    elif kind == 'sel' and trigger == 'MTOS': 
        filepath=f'{dat_dir}/{proc}_mm/{wr_vars.mm_sel_version}/{year}.root'
        treepath=trigger
    elif kind == 'gen' and trigger == 'KMM': 
        filepath=f'{dat_dir}/gen_{proc}_mm/{wr_vars.mm_gen_version}/{year}.root'
        treepath='gen/truth'
    elif kind == 'gen' and trigger == 'KEE':
        filepath=f'{dat_dir}/gen_{proc}_ee/{wr_vars.ee_gen_version}/{year}.root'
        treepath='gen/truth'
    elif kind == 'rec' and trigger == 'KMM': 
        treepath=trigger
        filepath=f'{dat_dir}/{proc}_mm/{wr_vars.mm_rec_version}/{year}_truth.root'
    elif kind == 'rec' and trigger == 'KEE':
        filepath=f'{dat_dir}/{proc}_ee/{wr_vars.ee_rec_version}/{year}_truth.root'
        treepath=trigger
    else:
        log.error(f'Incorrect trigger/kind: {trigger}/{kind}')
        raise

    return (filepath, treepath) 
#----------------------------
def do_test_osc(df, setting, kind):
    plotsdir='tests/weight_reader/osc'

    wgt           = weight_reader(df, kind)
    wgt           = config(wgt, setting)
    wgt.valdir    = f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}'
    d_arr_wgt     = wgt.get_weights()

    total_yields = d_arr_wgt['nom'].sum()
    return total_yields
#----------------------------
def get_df(proc, trigger, year, kind):
    filepath, treepath = get_paths(proc, trigger, year, kind)

    df=ROOT.RDataFrame(treepath, filepath)
    if wr_vars.nentries > 0:
        df = df.Range(wr_vars.nentries)

    df.treename = 'truth' if treepath == 'gen/truth' else treepath
    df.year     = year
    df.filepath = filepath
    df.trigger  = trigger
    df.proc     = proc

    if df.treename == 'gen/truth':
        df = add_truth(df, filepath)
        df = add_pteta(df)

    return df 
#----------------------------
def add_pteta(df):
    df=df.Define('eventNumber',       "evt")
    df=df.Define('B_TRUEPT'   , "B_plus_PT")
    df=df.Define('B_TRUEETA'  , "TVector3 v(B_plus_PX, B_plus_PY, B_plus_PZ); return v.Eta();")

    return df
#----------------------------
def add_truth(df, filepath):
    rgx_sample = '.*gen_(ctrl|psi2)_(ee|mm).*'
    mtch = re.match(rgx_sample, filepath)

    if not mtch:
        log.error('Cannot match {} from:'.format(rgx_sample))
        log.error('{0:<20}{1:<100}'.format('Filepath', filepath))
        log.error('{0:<20}{1:<100}'.format('Tree'    , treepath))
        raise

    proc = mtch.group(1)
    if   proc == 'ctrl':
        pdg_id =    '443'
    elif proc == 'psi2':
        pdg_id = '100443'
    else:
        log.error('Invalid process: ' + proc)
        raise

    df = df.Define('Jpsi_TRUEID', pdg_id)

    return df
#----------------------------
#----------------------------
def get_tag_dc():
    
    return d_trg_tag
#----------------------------
def get_dst_dc():
    d_dst        = {}
    d_dst['year']=['2011', '2012', '2015', '2016', '2017', '2018']
    d_dst['trig']=['MTOS', 'ETOS', 'GTIS']
    d_dst['proc']=['psi2', 'ctrl']

    return d_dst
#----------------------------
#No q2 for 
#----------------------------
def do_test_q2(df, proc, turn_on=None):
    utnr.check_none(turn_on)

    d_ver        = get_ver_dc()
    pver         = d_ver['PVER']

    wgt          = weight_reader(df)
    wgt.valdir   = f'tests/weight_reader/q2/{proc}_{df.treename}_{df.year}'
    wgt['pid']   = (pver,  '0') 

    d_ver        = get_ver_dc()
    qver         = d_ver['QVER'] 

    if turn_on:
        wgt['qsq']  = (qver, '1') 
    else:
        wgt['qsq']  = (qver, '0') 

    arr_wgt  = wgt.get_weights(return_type='product')

    return arr_wgt
#----------------------------
def test_q2(year):
    plotsdir='tests/weight_reader/q2'

    d_dst = get_dst_dc()
    for trigger in d_dst['trig']: 
        for proc in d_dst['proc']: 
            df=get_data(proc, trigger, year, 'sel')

            d_hist         = {}
            d_hist['h_of'] = do_test_q2(df, proc, turn_on=False) 

            if trigger != 'MTOS':
                d_hist['h_on'] = do_test_q2(df, proc, turn_on= True) 
    
            plotpath=f'{plotsdir}/{proc}_{trigger}_{year}/weights.png'

            utils.plot_arrays(d_hist, plotpath, 30, min_x = 0, max_x = 1, d_opt={'draw_all' : True})
#----------------------------
#FULL TEST, return product
#----------------------------
def get_versions():
    d_ver         = {}
    d_ver['gen']  = 'v26'
    d_ver['rec']  = 'v28'
    d_ver['lzr']  = 'v20'
    d_ver['hlt']  = 'v20'
    d_ver['pid']  =  'v3'
    d_ver['qsq']  =  'v7'
    d_ver['trk']  =  'v1'
    d_ver['bts']  =  '10'

    return d_ver
#----------------------------
def get_kin_syst(setting):
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
def get_pid_syst(setting):
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
def get_bts_syst(setting):
    if   setting in ['nom', 'all']:
        value = 'nom'
    elif setting == 'bts':
        value = 'all'
    else:
        log.error(f'Ivalid setting {setting}')
        raise

    return {'bts' : value} 
#----------------------------
def get_systematics(df, setting):
    d_syst = {}

    d_syst.update(get_kin_syst(setting))
    d_syst.update(get_trg_syst(df, setting))
    d_syst.update(get_pid_syst(setting))
    d_syst.update(get_qsq_syst(df, setting))
    d_syst.update(get_bts_syst(setting))

    d_syst['trk'] = 'nom'

    return d_syst
#----------------------------
def config(wgt, setting):
    d_ver = get_versions()
    d_sys = get_systematics(wgt.df, setting)
    for kind in ['gen', 'rec', 'lzr', 'hlt', 'pid', 'qsq', 'trk', 'bts']:
        ver = d_ver[kind]
        sys = d_sys[kind]

        log.info(f'{kind:<20}{ver:<20}{sys:<20}')

        wgt[kind] = (ver, sys)

    return wgt
#----------------------------
def test_no_corr():
    setting = 'nom'
    plotsdir='tests/weight_reader/no_corr'

    df            = get_df('ctrl', 'ETOS', '2018', 'sel')
    wgt           = weight_reader(df, 'sel')
    wgt           = config(wgt, setting)
    wgt.no_corr   = True
    wgt.valdir    = f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}'
    d_arr_wgt     = wgt.get_weights()

    plotpath=f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}/total_weight.png'
    log.visible(f'Saving to: {plotpath}')

    plt.close('all')
    for sys, arr_wgt in d_arr_wgt.items():
        plt.hist(arr_wgt, range=(0, 2), bins=100, label=sys, histtype='step')

    plt.legend()
    plt.savefig(plotpath)
    plt.close('all')
#----------------------------
def do_test_all(df, setting, kind):
    plotsdir='tests/weight_reader/all'

    wgt           = weight_reader(df, kind)
    wgt           = config(wgt, setting)
    wgt.valdir    = f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}'
    d_arr_wgt     = wgt.get_weights()

    plotpath=f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}/total_weight.png'
    log.visible(f'Saving to: {plotpath}')

    plt.close('all')
    for sys, arr_wgt in d_arr_wgt.items():
        plt.hist(arr_wgt, range=(0, 2), bins=100, label=sys, histtype='step')

    plt.legend()
    plt.savefig(plotpath)
    plt.close('all')
#----------------------------
def test_all(year):
    kind='sel'
    #for setting in ['nom', 'all', 'bts']:
    for setting in ['nom']:
        for proc in ['ctrl', 'psi2']: 
            for trig in ['MTOS', 'ETOS', 'GTIS']: 
                df=get_df(proc, trig, year, kind)
                do_test_all(df, setting, kind) 
#----------------------------
def test_all_osc(year):
    osc.ntest = 0
    kind='sel'
    plotsdir='tests/weight_reader/osc'
    for trig in ['ETOS', 'MTOS', 'GTIS']: 
        for proc in ['ctrl']: 
            df=get_df(proc, trig, year, kind)
            for setting in ['nom']:
                total_yields = []
                for n_osc in range(201):
                    osc.ntest = n_osc
                    total_yields.append(do_test_osc(df, setting, kind))
                    log.visible(f'Oscillating the {n_osc} times.')
                plotpath=f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}/osced_yields.png'
                log.visible(f'Saving to: {plotpath}')
                plt.hist(total_yields[1:], bins=10, alpha=0.9)
                plt.axvline(total_yields[0], color = 'green', alpha=0.9)
                plt.savefig(plotpath)
                plt.close('all')
#----------------------------
def test_wgt_fac(proc='ctrl', trig='ETOS', year='2018'):
    kind       ='sel'
    df         =get_df(proc, trig, year, kind=kind)
    plotsdir   ='tests/weight_reader/fac'
    setting    ='nom'

    wgt        = weight_reader(df, kind)
    wgt        = config(wgt, setting)
    wgt.valdir = f'{plotsdir}/{df.proc}_{df.treename}_{df.year}/{setting}'
    
    d_wgt_fac  = wgt.get_wgt_fac()

    l_wgt_lab  = list(d_wgt_fac.keys())
    utnr.pretty_print(l_wgt_lab)
#----------------------------
#Test one weight at a time 
#with nominal map
#----------------------------
def do_test_one(df, kind):
    d_ver = get_ver_dc()
    gver  = d_ver['GVER'] 
    rver  = d_ver['RVER'] 
    tver  = d_ver['TVER'] 
    tver  = d_ver['TVER'] 
    pver  = d_ver['PVER'] 
    qver  = d_ver['QVER'] 

    wgt          = weight_reader(df)
    wgt.valdir   = 'tests/weight_reader/one/{}_{}/{}'.format(df.treename, df.year, kind)
    wgt['pid']   = (None, '0') 
    wgt['qsq']   = (qver, '0') 

    if   kind == 'rec':
        wgt['rec']  = (rver, '1') 
    elif kind == 'gen':
        wgt['gen']  = (gver, '1') 
    elif kind == 'lzr':
        wgt['lzr']  = (tver, '1')
    elif kind == 'pid':
        wgt['pid']  = (pver, '1') 
    elif kind == 'qsq' and df.treename == 'MTOS':
        wgt['qsq']  = (qver, '1') 
    elif kind == 'none':
        pass
    else:
        log.error('Unrecognized ' + kind)
        raise

    arr_wgt  = wgt.get_weights(return_type='product')
#----------------------------
def test_one(year, nentries=1000):
    plotsdir='tests/weight_reader/one'
    for trigger in ['MTOS', 'ETOS', 'GTIS']: 
        for proc in ['ctrl', 'psi2']: 
            df=get_data(proc, trigger, year, 'sel')
            do_test_one(df,  'gen')
            do_test_one(df,  'rec')
            do_test_one(df,  'lzr')
            do_test_one(df, 'none')
#----------------------------
#Testing all weights and adding
#polarity column
#----------------------------
def do_test_pol(df, proc):
    plotsdir='tests/weight_reader/pol'

    d_ver = get_ver_dc()
    gver  = d_ver['GVER'] 
    rver  = d_ver['RVER'] 
    tver  = d_ver['TVER'] 
    pver  = d_ver['PVER'] 
    qver  = d_ver['QVER'] 
    ever  = d_ver['EVER'] 

    wgt          = weight_reader(df)
    wgt.valdir   = '{}/{}_{}_{}'.format(plotsdir, proc, df.treename, df.year)

    wgt['gen']   = (gver, '1')
    wgt['rec']   = (rver, '1')
    wgt['lzr']   = (tver, '1')
    wgt['pid']   = (pver, '1')
    wgt['trk']   = (ever, '1')
    if df.treename != 'MTOS':
        wgt['qsq']  = (qver, '1')
    else: 
        wgt['qsq']  = (qver, '0')

    arr_wgt  = wgt.get_weights(return_type='product', l_ext_col=['Polarity'])

    return arr_wgt
#----------------------------
def test_pol(year):
    plotsdir='tests/weight_reader/pol'
    for trigger in ['MTOS', 'ETOS', 'GTIS']: 
        for proc in ['ctrl', 'psi2']: 
            df=get_data(proc, trigger, year, 'sel')
            arr_wgt = do_test_pol(df, proc) 
            mat_wgt = arr_wgt.T
            arr_wgt = mat_wgt[0]
            arr_pol = mat_wgt[1]

            plotpath=f'{plotsdir}/{trigger}_{year}/weights_{proc}.png'
            plt.hist(arr_wgt, bins=30, range=(0, 3))
            plt.savefit(plotpath)
            plt.close('all')

            plotpath=f'{plotsdir}/{trigger}_{year}/polarity_{proc}.png'
            plt.hist(arr_pol, bins=4, range=(-2, 2))
            plt.savefit(plotpath)
            plt.close('all')
#----------------------------
def test_atr():
    plotsdir='tests/weight_reader/sys'

    trigger = 'MTOS' 
    year    = '2011'
    proc    = 'ctrl' 

    df=get_data(proc, trigger, year, 'sel')
    df.atr  = 'some attribute'
    arr_wgt = do_test_pol(df, proc) 
    try:
        log.visible(df.atr)
    except:
        log.error('Atribute was dropped')
        raise
#----------------------------
#Test all weights as norminal, but one,
#which is systematic fluctuation
#----------------------------
def do_test_sys(df, sys):
    plotsdir='tests/weight_reader/sys'

    wgt          = weight_reader(df)
    wgt.valdir   = f'{plotsdir}/ctrl_{df.treename}_{df.year}'

    d_ver = get_ver_dc()
    gver  = d_ver['GVER'] 
    rver  = d_ver['RVER'] 
    tver  = d_ver['TVER'] 
    pver  = d_ver['PVER'] 
    qver  = d_ver['QVER'] 

    wgt['qsq']   = (qver, '1')
    wgt['pid']   = (pver, '1')

    kind, val = sys
    if kind == 'gen':
        wgt['gen']   = (gver , val)
    else:
        wgt['gen']   = (gver , '1')

    if kind == 'rec':
        wgt['rec']   = (rver , val)
    else:
        wgt['rec']   = (rver , '1')

    if kind == 'lzr':
        wgt['lzr']   = (tver , val)
    else:
        wgt['lzr']   = (tver , '1')

    if kind == 'pid':
        wgt['pid']   = (pver , val)
    else:
        wgt['pid']   = (pver , '1')

    if   kind == 'qsq' and df.treename == 'MTOS':
        wgt['qsq']   = (qver, '0')
    elif kind == 'qsq' and df.treename != 'MTOS':
        wgt['qsq']   = (qver, val)

    arr_wgt  = wgt.get_weights(return_type='product')

    return arr_wgt
#----------------------------
def test_sys(trigger):
    plotsdir='tests/weight_reader/sys'

    year    = '2011'
    proc    = 'ctrl' 

    #l_pid_val = ['1', '2e', '2h', '2m', '3gtis', '3chi2']
    l_kin_val = ['1'] 
    l_trg_val = ['1', '3mtis', '3mmuo', '3mhad', '3ehad']
    l_pid_val = ['1'] 
    l_qsq_val = ['1']

    df=get_data(proc, trigger, year, 'sel', nentries = nentries)

    for val in l_kin_val: 
        for kind in ['gen', 'rec']:
            arr_wgt = do_test_sys(df, ('gen', val) ) 
            plotpath=f'{plotsdir}/{trigger}_{year}/weights_{kind}_{val}.png'
            plt.hist(arr_wgt, bins=30, range=(0, 2))
            plt.savefig(plotpath)
            plt.close('all')

    for val in l_trg_val: 
        arr_wgt = do_test_sys(df, ('lzr', val) ) 
        plotpath='{}/{}_{}/weights_{}_{}.png'.format(plotsdir, trigger, year, 'lzr', val)
        utils.plot_arrays({'Wgt' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 2)

    for val in l_pid_val:
        arr_wgt = do_test_sys(df, ('pid', val) ) 
        plotpath='{}/{}_{}/weights_{}_{}.png'.format(plotsdir, trigger, year, 'pid', val)
        utils.plot_arrays({'Wgt' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 1.1)

    for val in l_qsq_val:
        arr_wgt = do_test_sys(df, ('qsq', val) ) 
        plotpath='{}/{}_{}/weights_{}_{}.png'.format(plotsdir, trigger, year, 'qsq', val)
        utils.plot_arrays({'Wgt' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 1)
#----------------------------
#Test only trigger with factorization map
#----------------------------
def do_test_fact(df, proc):
    plotsdir='tests/weight_reader/fact'

    wgt          = weight_reader(df)
    wgt.valdir   = '{}/{}_{}_{}'.format(plotsdir, proc, df.treename, df.year)

    d_ver        = get_ver_dc()
    tver         = d_ver['TVER'] 
    qver         = d_ver['QVER'] 
    pver         = d_ver['PVER'] 

    wgt['lzr']   = (tver, '5fact') 
    wgt['qsq']   = (qver,     '0') 
    wgt['pid']   = (pver,     '0') 

    arr_wgt  = wgt.get_weights()

    return arr_wgt
#----------------------------
def test_fact(nentries=1000):
    plotsdir='tests/weight_reader/fact'

    proc    = 'ctrl'
    trigger = 'ETOS'
    year    = '2016'

    df=get_data(proc, trigger, year, 'sel', nentries=nentries)
    arr_wgt = do_test_fact(df, proc) 
    
    plotpath='{}/{}_{}_{}/weights.png'.format(plotsdir, proc, trigger, year)
    utils.plot_arrays({'h' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 3, d_opt={'draw_all' : True})
#----------------------------
#Test HLT only
#----------------------------
def do_test_hlt(df, proc):
    plotsdir     = 'tests/weight_reader/hlt'

    d_ver        = get_ver_dc()
    tver         = d_ver['TVER'] 
    qver         = d_ver['QVER'] 

    wgt          = weight_reader(df)
    wgt.valdir   = '{}/{}_{}_{}'.format(plotsdir, proc, df.treename, df.year)
    wgt['pid']   = (None, '0') 
    wgt['qsq']   = (None, '0') 
    wgt['hlt']   = (tver, '1') 
    arr_wgt      = wgt.get_weights(return_type='product')

    return arr_wgt
#----------------------------
def test_hlt(nentries=4000):
    plotsdir='tests/weight_reader/hlt'

    d_dst  = get_dst_dc()
    l_year = d_dst['year']
    l_proc = d_dst['proc']
    l_trig = d_dst['trig']

    d_opt={}
    d_opt['draw_all'] = True
    d_opt['logy']     = False 
    d_opt['sty' ]     = ['text E0'] 
    for proc in l_proc:
        for trigger in l_trig:
            for year in l_year:
                df=get_data(proc, trigger, year, 'sel', nentries=nentries) 
                arr_wgt = do_test_hlt(df, proc) 

                plotpath='{}/{}_{}_{}/weights.png'.format(plotsdir, proc, trigger, year)
                utils.plot_arrays({'h' : arr_wgt}, plotpath, 300, min_x = 0.9, max_x = 1.1, d_opt = d_opt)
#----------------------------
#Test HLT only turned off
#----------------------------
def do_test_hlt_off(df, proc):
    plotsdir='tests/weight_reader/hlt_off'

    d_ver = get_ver_dc()
    gver  = d_ver['GVER'] 
    rver  = d_ver['RVER'] 
    tver  = d_ver['TVER'] 
    tver  = d_ver['TVER'] 
    pver  = d_ver['PVER'] 
    qver  = d_ver['QVER'] 

    wgt          = weight_reader(df)
    wgt.valdir   = '{}/{}_{}_{}'.format(plotsdir, proc, df.treename, df.year)

    wgt['gen']   = (gver, '1')
    wgt['rec']   = (rver, '1')
    wgt['lzr']   = (tver, '1')
    wgt['hlt']   = (tver, '0')
    wgt['pid']   = (pver, '1')

    if df.treename != 'MTOS':
        wgt['qsq']  = (qver, '1')
    else:
        wgt['qsq']  = (qver, '0')

    arr_wgt  = wgt.get_weights(return_type='product')

    return arr_wgt
#----------------------------
def test_hlt_off(nentries = 4000):
    plotsdir='tests/weight_reader/hlt_off'

    d_dst = get_dst_dc()

    for trigger in d_dst['trig']: 
        for year in d_dst['year']:
            for proc in d_dst['proc']: 
                df=get_data(proc, trigger, year, 'sel', nentries=nentries)
                arr_wgt = do_test_hlt_off(df, proc) 
    
                plotpath='{}/{}_{}_{}/weights.png'.format(plotsdir, proc, trigger, year)
                utils.plot_arrays({'h' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 1, d_opt={'draw_all' : True})
#----------------------------
#----------------------------
def do_test_rec_all(df, proc, kind):
    plotsdir= 'tests/weight_reader/{}_all'.format(kind)
    d_ver   = get_ver_dc()
    gver    = d_ver['GVER'] 

    wgt        = weight_reader(df)
    wgt.valdir = '{}/{}_{}_{}'.format(plotsdir, proc, df.treename, df.year)

    wgt['gen'] = (gver, '1')
    arr_wgt    = wgt.get_weights(return_type='product')

    return arr_wgt
#----------------------------
def test_rec_all(kind, year, nentries = 1000):
    plotsdir=f'tests/weight_reader/{kind}_all'
    for trigger in ['KEE', 'KMM']: 
        for proc in ['ctrl', 'psi2']: 
            df=get_data(proc, trigger, year, kind)
            arr_wgt = do_test_rec_all(df, proc, kind) 
    
            plotpath=f'{plotsdir}/{proc}_{trigger}_{year}/weights.png'
            utils.plot_arrays({'h' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 1, d_opt={'draw_all' : True})
#----------------------------
def do_test_raw_all(df, proc):
    plotsdir= 'tests/weight_reader/raw_all'
    d_ver   = get_ver_dc()
    gver    = d_ver['GVER'] 
    rver    = d_ver['RVER'] 

    wgt        = weight_reader(df)
    wgt.valdir = '{}/{}_{}_{}'.format(plotsdir, proc, df.treename, df.year)

    wgt['gen'] = (gver, '1')
    wgt['rec'] = (rver, '1')

    arr_wgt    = wgt.get_weights(return_type='product')

    return arr_wgt
#----------------------------
def test_raw_all(year, nentries = 1000):
    plotsdir='tests/weight_reader/raw_all'
    for trigger in ['KEE', 'KMM']: 
        for proc in ['ctrl', 'psi2']: 
            df=get_data(proc, trigger, year, 'rec')
            arr_wgt = do_test_raw_all(df, proc) 
    
            plotpath=f'{plotsdir}/{proc}_{trigger}_{year}/weights.png'
            utils.plot_arrays({'h' : arr_wgt}, plotpath, 30, min_x = 0, max_x = 1, d_opt={'draw_all' : True})
#----------------------------
def main():
    set_log_level()

    weight_reader.replica = 0
    return
    test_no_corr()
    test_all('2018')

    #test_wgt_fac(trig='MTOS')
    #test_all('2017')
    #test_raw_all('2017')
    #test_all_osc('2017')

    #reconstruction
    test_rec_all('gen', '2017')
    test_rec_all('rec', '2017')

    #selection
    test_all('2017')
    test_one('2017')
    test_pol('2017')
    test_q2('2017')
    test_atr()
    test_sys('ETOS')
    test_fact()
    test_hlt()
    test_hlt_off()
#----------------------------
if __name__ == '__main__':
    main()
