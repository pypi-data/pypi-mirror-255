import ROOT
import selection.utilities as slut 

import re
import os 
import sys
import glob
import json
import pandas as pnd
import numpy
import utils
import utils_noroot        as utnr

from rk.settings   import settings as rkst
from pathfinder    import get_path as pf_get_path
from rk.cutflow    import cutflow
from ndict         import ndict

if sys.version_info < (3, 7):
    print("utilities.py:: Cannot run with python < 3.7")
    exit(0)

log=utnr.getLogger(__name__)

#------------------------------------------
def trim_val(val, skip=False):
    '''
    This function will take a float and make zeros all the numbers after the 4th decimal
    The trimmed float will be returned
    '''

    if skip:
        return val

    if   isinstance(val, str):
        return val
    elif isinstance(val, tuple):
        return trim_val(val[0]), trim_val(val[1])

    return numpy.format_float_positional(val, precision=4, unique=False, fractional=False, trim='k')
#------------------------------------------
def result_to_dict(res, trim=False):
    '''
    This function will take a Zfit result object, after calling hesse on it
    but before freezing it. It will store them in a dictionary and return it 
    '''
    if trim:
        log.warning('Trimming fit results')
    else:
        log.debug('Not trimming fit results')

    d_res = {}
    for par, d_val in res.params.items():
        val = d_val['value']
        try:
            err = d_val['hesse']['error'] 
        except:
            err = -999

        d_res[par.name] = val, err 

    d_res['converged'] = res.converged
    d_res['status']    = res.status
    d_res['valid']     = res.valid
    d_res['fmin']      = res.fmin
    d_res['edf']       = res.edm
    #----------------------
    d_res_trim         = {key : trim_val(val, skip= not trim) for key, val in d_res.items()}

    l_l_cov_trim = []
    l_par        = [par for par in res.params]
    l_l_cov      = res.covariance(params=l_par).tolist()
    for l_cov in l_l_cov:
        l_cov_trim = [ trim_val(val, skip=not trim) for val in l_cov ]
        l_l_cov_trim.append(l_cov_trim)

    d_res_trim['cov'] = l_l_cov_trim
    d_res_trim['par'] = [ par.name for par in l_par ] 

    return d_res_trim
#------------------------------------------
def reso_to_rare(d_res, kind=None):
    '''
    Will calculate rare mode yields from resonant ones, using branching fractions 

    Parameters
    ---------------------
    d_res (dict): Dictionary {dset : yield} with dset e.g. r2p1
    kind (str): Should they be transformed from Jpsi or from Psi2S yields

    Returns
    ---------------------
    d_rar (dict): Dictionary as in input but rare mode yields
    '''
    if kind not in ['jpsi', 'psi2']:
        log.error(f'Invalid kind: {kind}')
        raise ValueError

    ccbr     = 5.96e-2 if kind == 'jpsi' else 7.9e-3
    bbbr_res = 1.02e-3
    bbbr_rar = 4.37e-7

    d_rar = { dset : yld * bbbr_rar / (bbbr_res * ccbr) for dset, yld in d_res.items()}

    return d_rar
#------------------------------------------
def average_byields(d_byld, l_exclude=[]):
    '''
    Will calculate average yields of B candidates

    Parameters
    --------------------
    d_byld (dict): {ds : yld}, where ds e.g. r2p1_TIS_ee and yld is a float
    l_exclude (list): List of datasets, or channels to exclude from average

    Returns
    --------------------
    d_byld (dict): {ds : yld}, where ds e.g. r2p1
    '''

    d_avg = {}
    for dset in ['r1', 'r2p1', '2017', '2018']:
        nval = 0
        val  = 0
        for trig in ['TIS', 'TOS']:
            if trig in l_exclude:
                continue
    
            for chan in ['ee', 'mm']:
                if chan in l_exclude:
                    continue

                key  = f'{dset}_{trig}_{chan}'
                val += d_byld[key]
                nval+= 1.

        d_avg[dset] = val / nval 

    return d_avg
#------------------------------------------
def check_keys(l_d_cfl):
    '''
    Check that the keys of all the dictionaries in list are the same
    '''
    l_key = l_d_cfl[0].keys()
    for d_cfl in l_d_cfl:
        if l_key == d_cfl.keys():
            continue

        log.error(f'Efficiency object keys differ:')
        print(l_key)
        print(d_cfl.keys())
        raise
#------------------------------------------
def get_cfl_from_wc(cf_wc):
    '''
    From wildcard string associated to pickle files containing cfl | {sys -> cfl} | {(sys, var) -> cfl}
    0.  If cutflow, add them all and return
    1a. Check that all keys are the same
    1b. Add cutflow and put them in a new dictionary
    '''
    l_eff_obj = [ utnr.load_pickle(eff_obj_path) for eff_obj_path in utnr.glob_wc(cf_wc) ]

    if   isinstance(l_eff_obj[0], cutflow):
        eff_obj = sum(l_eff_obj[1:], l_eff_obj[0])
    elif isinstance(l_eff_obj[0], (dict, ndict)):
        check_keys(l_eff_obj)
        eff_obj = {} if isinstance(l_eff_obj[0], dict) else ndict()
        for d_cfl in l_eff_obj:
            for key, cfl in d_cfl.items():
                if key not in eff_obj:
                    eff_obj[key] = cfl
                else:
                    eff_obj[key]+= cfl
    else:
        log.error(f'Object is of invalid type: {type(l_eff_obj[0])}')
        raise TypeError

    return eff_obj
#------------------------------------------
def add_dict(d_old, d_new):
    if len(d_old) == 0:
        return d_new

    k_old = d_old.keys()
    k_new = d_new.keys()

    s_old = set(k_old)
    s_new = set(k_new)

    l_old = list(s_old)
    l_new = list(s_new)

    l_old.sort()
    l_new.sort()

    if s_old != s_new:
        log.error(f'Keys differ: {l_old}/{l_new}')
        raise

    d_full = {}
    for key in s_new:
        d_full[key] = d_old[key] + d_new[key]

    return d_full
#------------------------------------------
def getYears(dset):
    if   dset == 'r1':
        return ('2011', '2012')
    elif dset == 'r2p1':
        return ('2015', '2016')
    elif dset == '01':
        return ('0', '1')
    else:
        log.error('Invalid dataset ' + dset)
        raise
#------------------------------------------
def get_lumi(year, polarity = None):
    year = str(year)

    if year not in ['0', '1', '01'] + ['2011', '2012', '2015', '2016', '2017', '2018'] + ['r1', 'r2p1']:
        log.error('Unsupported year: ' + year)
        raise

    if polarity not in ['up', 'dn', 'both']:
        log.error('Unsupported polarity: ' + polarity)
        raise

    if polarity == 'both':
        return get_lumi(year, 'up') + get_lumi(year, 'dn')
    #-----------------
    #For tests
    #-----------------
    if   year == '0' and polarity == 'up':
        return 1
    elif year == '0' and polarity == 'dn':
        return 2 
    elif year == '1' and polarity == 'up':
        return 2
    elif year == '1' and polarity == 'dn':
        return 1 
    elif year == '01':
        return get_lumi('0', polarity) + get_lumi('1', polarity)
    elif year == 'r1':
        return get_lumi('2011', polarity) + get_lumi('2012', polarity)
    elif year == 'r2p1':
        return get_lumi('2015', polarity) + get_lumi('2016', polarity)
    #-----------------
    tckpath = os.environ['TCKDB']
    jsonpath = tckpath + '/luminosity.json'
    utnr.check_file(jsonpath)
    try:
        ifile=open(jsonpath)
    except:
        log.error('Cannot open ' + jsonpath)
        raise

    d_lumi = json.load(ifile)

    try:
        key = '{}_{}'.format(year, polarity)
        lumi = d_lumi[key]
    except:
        log.error('Cannot retrieve luminosity for year: {} and polarity: {} from:'.format(year, polarity))
        print(d_lumi)
        raise

    return lumi
#------------------------------
def reformat_mat(mat):
    arr_wgt = mat.T[0]
    arr_pol = mat.T[1]

    arr_wgt_pos = numpy.where(arr_pol == +1, arr_wgt, 0)
    arr_wgt_neg = numpy.where(arr_pol == -1, arr_wgt, 0)

    sum_wgt_pos = numpy.sum(arr_wgt_pos)
    sum_wgt_neg = numpy.sum(arr_wgt_neg)

    return numpy.array([[sum_wgt_pos, +1], [sum_wgt_neg, -1]])
#------------------------------
def get_gen_mat(process, channel, year, polarization=None, skimmed=False, reformat=False):
    mat = do_get_gen_mat(process, channel, year, polarization=polarization, skimmed=skimmed)
    if reformat == False:
        return mat
    else:
        mat = reformat_mat(mat)
        return mat
#------------------------------
def get_measurement(kind, year):
    d_meas = {}

    #CDS, from https://arxiv.org/pdf/hep-ex/9909011v1.pdf
    #d_meas['fu'] = (0.375, 0.023)

    #LHCb, inferred from https://arxiv.org/pdf/1111.2357.pdf
    d_meas['fu'] = (0.337, 0.022)

    #From PDG
    d_meas['br_Bp_Jpsi'] = (1.010e-3, 0.029e-3)
    d_meas['br_Bp_ctrl'] = d_meas['br_Bp_Jpsi'] 

    d_meas['br_Bp_Psi2'] = (6.210e-4, 0.230e-4) 
    d_meas['br_Bp_psi2'] = d_meas['br_Bp_Psi2'] 

    d_meas['br_Jpsi_ee'] = (5.971e-2, 0.032e-2)
    d_meas['br_ctrl_ee'] = d_meas['br_Jpsi_ee']

    d_meas['br_Jpsi_mm'] = (5.961e-2, 0.033e-2)
    d_meas['br_ctrl_mm'] = d_meas['br_Jpsi_mm']

    d_meas['br_Psi2_ee'] = (7.720e-3, 0.170e-3)
    d_meas['br_psi2_ee'] = d_meas['br_Psi2_ee']

    d_meas['br_Psi2_mm'] = (7.700e-3, 0.800e-3)
    d_meas['br_psi2_mm'] = d_meas['br_Psi2_mm']

    #From https://arxiv.org/pdf/1710.04921.pdf, in LHCb acceptance in picobarns
    if year in ['2011', '2012', 'r1']:
        #7TeV 0.2 (stat), 2.5 (syst), 1.7 (br)  
        d_meas['xsec_Bp'] = (43.0e6, 3.03e6)
    elif year in ['2015', '2016', '2017', '2018', 'r2p1']:
        #13TeV 0.5 (stat), 5.4 (syst), 3.4 (br)
        d_meas['xsec_Bp'] = (86.6e6, 6.40e6)
    else:
        log.error('Invalid Year/Dataset: {}'.format(year))
        raise

    #From arXiv:1612.05140v9, in LHCb acceptance in picobarns
    if year in ['2011', '2012', 'r1']:
        #7TeV, 0.3 (stat), 6.8 (syst)
        d_meas['xsec_bb'] = (72e6, 6.8e6)
    elif year in ['2015', '2016', '2017', '2018', 'r2p1']:
        #13TeV, 1 (stat), 21 (syst)
        d_meas['xsec_bb'] = (144e6, 21e6) 
    else:
        log.error('Invalid Year/Dataset: {}'.format(year))
        raise

    if kind not in d_meas:
        log.error('Quantity {} not found among:'.format(kind))
        print(d_meas.keys())
        raise

    return d_meas[kind]
#------------------------------
def do_get_gen_mat(process, channel, year, polarization=None, skimmed=False):
    #----------------------------------
    #years, tests
    #----------------------------------
    if   year == '0'  and polarization == 'up':
        return numpy.array([[2.0, +1]])
    elif year == '0'  and polarization == 'dn':
        return numpy.array([[1.0, -1]])
    elif year == '1'  and polarization == 'up':
        return numpy.array([[1.0, +1]])
    elif year == '1'  and polarization == 'dn':
        return numpy.array([[2.0, -1]])
    elif year in ['0', '1'] and polarization is None:
        mat_up = get_gen_mat(process, channel, year, polarization='up', skimmed=skimmed)
        mat_dn = get_gen_mat(process, channel, year, polarization='dn', skimmed=skimmed)

        return numpy.concatenate((mat_up, mat_dn))
    #----------------------------------
    #years, no tests
    #----------------------------------
    elif year in ['2011', '2012', '2015', '2016', '2017', '2018']:
        pass
    else:
        log.error('Wrong year/polarity: {}/{}'.format(year, polarization))
        raise
    #----------------------------------
    #----------------------------------
    if   polarization is None:
        mat_d = get_gen_mat(process, channel, year, 'dn')
        mat_u = get_gen_mat(process, channel, year, 'up')

        return numpy.concatenate((mat_d, mat_u))
    elif polarization == 'up':
        year = year + '_MagUp'
        pol  = +1
    elif polarization == 'dn':
        year = year + '_MagDown'
        pol  = -1
    else:
        log.error('Invalid polarization {}'.format(polarization))
        raise
    #----------------------------------
    if   channel in ['ee', 'mm']:
        pass
    elif channel in ['ETOS', 'GTIS']:
        channel = 'ee'
    elif channel == 'MTOS':
        channel = 'mm'
    else:
        log.error('Unsupported channel ' + channel)
        raise
    #----------------------------------
    filepath= '/publicfs/ucas/user/campoverde/Data/RK/gen_{}_{}/v0/{}.root'.format(process, channel, year)
    if skimmed:
        filepath=filepath.replace('.root', '_skimmed.root')

    filepath = pf_get_path(filepath)

    nentries = utils.get_tree_entries('gen/truth', filepath)
    mat      = numpy.array([[nentries, pol]])
    #----------------------------------

    return mat
#------------------------------
def getBYield(year, channel):
    lumi   = get_lumi(year)
    t_lumi = (lumi, 0)

    if   year in ['2011', '2012']:
        t_xsec = (72e9, 6.8e9) 
    elif year in ['2015', '2016', '2017', '2018']:
        t_xsec = (144e9, 21e9) 
    else:
        log.error('Wrong year ' + year)
        raise

    t_fu       = (40.5e-2, 0.500e-2)
    t_bplus_bf = (1.01e-3, 0.029e-3)

    if   channel == 'electron':
        t_jpsi_bf = (5.971e-2, 0.032e-2)
    elif channel == 'muon':
        t_jpsi_bf = (5.961e-2, 0.033e-2)
    else:
        log.error('Wrong channel ' + channel)
        raise

    nbplus, err = utils.value_and_covariance('lumi * xsec * f * B_Br * Jpsi_BR', lumi=t_lumi, xsec=t_xsec, f=t_fu, B_Br=t_bplus_bf, Jpsi_BR=t_jpsi_bf)

    return (nbplus, err)
#------------------------------------------
#------------------------------------------
def transform_bdt(working_point):
    return slut.transform_bdt(working_point)
#------------------------------------------
def check_thresholds(df, storage, trigger, prefix):
    if   trigger == 'ETOS':
        df=df.Define('var', 'L1_L0ElectronDecision_TOS == 1 ? L1_L0Calo_ECAL_realET : L2_L0Calo_ECAL_realET')
        df=df.Define('thr', 'threshold_el')
    elif trigger == 'MTOS':
        df=df.Define('var', 'L0Data_Muon1_Pt')
        df=df.Define('thr', 'threshold_mu')
    elif trigger == 'HTOS':
        df=df.Define('var', 'H_L0Calo_HCAL_realET')
        df=df.Define('thr', 'threshold_kp')
    elif trigger == 'GTIS':
        return
    else:
        log.error('Wrong trigger ' + trigger)
        raise

    d_data = df.AsNumpy(['thr', 'var', 'L0DUTCK'])

    arr_tck = d_data['L0DUTCK']
    arr_thr = d_data['thr']
    arr_var = d_data['var']

    arr_val = numpy.vstack((arr_tck, arr_thr, arr_var)).T

    storage.add('trg_thr_{}_{}'.format(prefix, trigger) , arr_val)
#----------------------
def getCuts(eventType, mode, preselection, trigger, pid, year, skip_truth=False):
    d_cut={}

    if "data_" in eventType:
        sb    = getMassSideBand(eventType)
        d_cut["SB"] = sb
    elif not skip_truth:
        truth = getTruthString(eventType)
        d_cut['truth'] = truth
    else:
        ROOT.Warning("getCuts", "Skipping truth matching")

    d_pres=getPreselection(mode, preselection, eventType)
    #Add NSPD hits cut after truth/sideband
    cut_nspd = d_pres["nspd"]
    d_cut['nspd'] = cut_nspd
    d_cut.update(d_pres)

    d_pid=getPID(pid, eventType)
    d_cut.update(d_pid)

    d_trig=getTrigger(trigger, year)
    d_cut.update(d_trig)

    bdt=getBDT(trigger)
    d_cut['BDT'] = bdt

    mass=getMass(mode, eventType)
    d_cut['Mass'] = mass

    return d_cut
#----------------------
def mapToDic(cpp_map):
    d_data={}
    for entry in cpp_map:
        key=entry[0]
        str_cut=renameVars(entry[1])

        d_data[key]=str_cut

    return d_data
#----------------------
def renameVars(expr):
    cpp_expr=ROOT.std.string(expr)
    str_expr=ROOT.utils.renameVarsRet(cpp_expr)

    return str_expr
#----------------------
def loadCPP():
    ROOT.gInterpreter.AddIncludePath(PRSDIR + "/include")
    ROOT.gInterpreter.AddIncludePath(TLSDIR + "/include")
    ROOT.gInterpreter.ProcessLine('#include "getPreselection.h"')
    ROOT.gInterpreter.ProcessLine('#include "utils.h"')
    ROOT.gInterpreter.ProcessLine('#include "cutflowreport.h"')
    ROOT.gSystem.Load(PRSDIR + '/lib/libpres.so')
    ROOT.gSystem.Load(TLSDIR + '/lib/libtools.so')
#----------------------
def getMass(mode, eventType):
    if   rkst.is_electron(eventType):
        str_mass=ROOT.getMassCutEE(mode)
    elif rkst.is_muon(eventType):
        str_mass=ROOT.getMassCutMM(mode)
    else:
        log.error('Unrecognized eventType: {}'.format(eventType))
        raise

    return renameVars(str_mass)
#----------------------
def getTriggerTag(tag, year):
    selection=ROOT.getTriggerTag(tag, year)

    return renameVars(selection)
#----------------------
def getTriggerProbe(tag, year):
    selection=ROOT.getTriggerProbe(tag, year)

    return renameVars(selection)
#----------------------
def getMassSideBand(eventType):
    if   rkst.is_electron(eventType):
        str_sb=ROOT.getMassSideBandEE()
    elif rkst.is_muon(eventType):
        str_sb=ROOT.getMassSideBandMM()
    else:
        log.error('Unrecognized eventType: {}'.format(eventType))
        raise

    return renameVars(str_sb)
#----------------------
def getBDT(trigger):
    str_bdt=ROOT.getBDTCut(trigger)

    return str_bdt
#----------------------
def getTrigger(trigger, year):
    loadCPP()
    d_trig={}
    if   trigger == ROOT.mTOS:
        str_l0=ROOT.getL0MuonTOS()
        str_l0=renameVars(str_l0)
        d_trig["L0"] = str_l0

        str_hlt1=ROOT.getHlt1(year)
        str_hlt1=renameVars(str_hlt1)
        d_trig["Hlt1"] = str_hlt1

        str_hlt2=ROOT.getHlt2MM(year)
        str_hlt2=renameVars(str_hlt2)
        d_trig["Hlt2"] = str_hlt2

        return d_trig
    elif trigger == ROOT.eTOS:
        str_l0=ROOT.getL0ElectronTOS()
        name="ETOS"
    elif trigger == ROOT.hTOS:
        str_l0=ROOT.getL0HadronTOSOnly()
        name="HTOS"
    elif trigger == ROOT.gTIS:
        str_l0=ROOT.getL0TISOnly()
        name="GTIS"
    else:
        ROOT.Error("getTrigger", "Undefined trigger " + trigger)
        exit(1)

    str_l0=renameVars(str_l0)
    d_trig["L0"] = str_l0

    str_hlt1=ROOT.getHlt1(year)
    str_hlt1=renameVars(str_hlt1)
    d_trig["Hlt1"] = str_hlt1

    str_hlt2=ROOT.getHlt2EE(year)
    str_hlt2=renameVars(str_hlt2)
    d_trig["Hlt2"] = str_hlt2

    return d_trig
#----------------------
def getPreselection(mode, presel, eventType):
    loadCPP()
    if   rkst.is_electron(eventType):
        cpp_map = ROOT.getPreselectionEE(mode, presel)
    elif rkst.is_muon(eventType):
        cpp_map = ROOT.getPreselectionMM(mode, presel)
    else:
        log.error('Unrecognized eventType: {}'.format(eventType))
        raise

    d_pres=mapToDic(cpp_map)

    return d_pres
#----------------------
def get_nspd_cut():
    loadCPP()
    cut = ROOT.get_nspd_cut()

    return cut 
#----------------------
def getPID(pid, eventType):
    loadCPP()
    if   rkst.is_electron(eventType):
        str_pid = ROOT.getPIDEE(pid)
    elif rkst.is_muon(eventType):
        str_pid = ROOT.getPIDMM(pid)
    else:
        log.error('Unrecognized eventType: {}'.format(eventType))
        raise

    str_pid=renameVars(str_pid)

    return {"pid" : str_pid} 
#----------------------
def getTruthString(evt_typ):
    loadCPP()
    str_truth = ROOT.getTruthID(int(evt_typ))
    cpp_truth = ROOT.std.string(str_truth)
    str_truth = ROOT.utils.renameVarsRet(cpp_truth)
    truth     = str_truth + " == 1"

    return truth
#----------------------
def getEventType(ntuplepath):
    regex=".*\/(\d{8})_\d{4}_(MagUp|MagDown)\.root"

    mtch=re.match(regex, ntuplepath)
    if not mtch:
        ROOT.Error("getEventType", "Cannot extract eventType from " + ntuplepath)
        exit(1)

    return mtch.group(1)
#----------------------
def extract_df_cutflow(rdf, l_cut = None):
    '''Will tranform cutflow report from ROOT Into pandas dataframe
    Parameters:
    ---------------
    rdf : ROOT dataframe
    l_cut : List of strings with the definitions of the cuts, optional

    Returns:
    ---------------
    Pandas dataframe with cutflow
    '''

    rep = rdf.Report()
    df  = utils.rdf_report_to_df(rep)

    df  = df.rename(columns={'All': 'Total', 'Passed' : 'Pased', 'Cummulative' : 'Cumulative'})
    df  = df.set_index('cut')


    if l_cut is None:
        return df

    if len(df.index) != len(l_cut):
        log.error(f'List of cuts and cuts in dataframe do not align')
        raise

    sr = pnd.Series(l_cut)

    df['cut_value'] = sr

    return df
#----------------------
def get_ctfl_df(file_wc, suffix=None):
    '''Will get pandas dataframe with cutflow corresponding to ROOT files wild card
    Parameters:
    -------------
    file_wc(str): Wildcard for root files. The cutflow files are JSON files with the same name but with json extention 
    suffix (str): String specifying how to rename the .root termination, e.g. '.root' -> '_cut.json'.

    Returns
    -------------
    Pandas dataframe with the cutflow
    '''

    l_root_wc = glob.glob(file_wc)

    if len(l_root_wc) == 0:
        log.error(f'No file found in: {file_wc})')
        raise

    if suffix is None:
        file_wc   = file_wc.replace('.root', '.json')
    else:
        file_wc   = file_wc.replace('.root',  suffix)

    l_json_wc = glob.glob(file_wc)

    if len(l_root_wc) != len(l_json_wc):
        log.error(f'Number of JSON and ROOT files differ: {len(l_json_wc)}/{len(l_root_wc)}')
        raise

    l_df = [ pnd.read_json(json_path) for json_path  in l_json_wc ]
    
    df_tot = l_df[0]
    l_df   = l_df[1:]

    for df in l_df:
        df_tot = df_tot.add(df)

    df_tot['Efficiency'] = df_tot.Pased / df_tot.Total
    df_tot['Cumulative'] = df.Efficiency.cumprod()

    return df_tot
#----------------------

