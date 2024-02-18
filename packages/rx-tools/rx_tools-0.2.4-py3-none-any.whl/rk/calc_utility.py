import os
import json
import glob
import math
import array
import numpy
import ROOT

import utils_noroot as utnr
import utils

from atr_mgr import mgr

log=utnr.getLogger(__name__)
#------------------------------
class data:
    d_name_evt={}
    d_name_evt["ctrl_electron"]=12153001
    d_name_evt["ctrl_ee"]      =12153001
    d_name_evt["psi2_electron"]=12153012
    d_name_evt["psi2_ee"]      =12153012
    d_name_evt["rare_electron"]=12123003
    d_name_evt["sign_ee"]      =12123003

    d_name_evt["ctrl_muon"]    =12143001
    d_name_evt["ctrl_mm"]      =12143001
    d_name_evt["psi2_muon"]    =12143020
    d_name_evt["psi2_mm"]      =12143020
    d_name_evt["rare_muon"]    =12113002
    d_name_evt["sign_mm"]      =12113002

    d_name_evt["bpks_ee" ]     =12123445
    d_name_evt["bdks_ee" ]     =11124002
    d_name_evt["bpkp_ee" ]     =12123003
    d_name_evt["bsph_ee"]      =13124006
    d_name_evt["bpk1_ee"]      =12425000
    d_name_evt["bpk2_ee"]      =12425011

    l_var_kind = ['all', 'cmb_bdt', 'prc_bdt', 'dif_fit']
#------------------------------
def getProdID(evt, polarity, year):
    find_dir =os.environ['FINDIR']
    json_path=f'{find_dir}/json/prodID.json'
    d_key_id=utnr.load_json(json_path)

    key=f'{evt}_{polarity}_{year}'

    #Subtracting 1 due to merging step between Generator Statistics page and Dirac
    ID = utnr.get_from_dic(d_key_id, key) - 1

    return ID
#------------------------------
def calcGeomEff(name, polarity, year, perc=False):
    #This way can use either trigger or channel as key
    if True:
        name = name.replace('MTOS',     'muon')
        name = name.replace('ETOS', 'electron')
        name = name.replace('HTOS', 'electron')
        name = name.replace('GTIS', 'electron')

    evt=utnr.get_from_dic(data.d_name_evt, name)
    json_path = get_json_table(year, polarity, evt)
    if json_path is None:
        return None

    obj=utnr.load_json(json_path)
    l_data=obj["Signal Counters"]

    d_part=l_data[0]
    d_anti=l_data[1]

    eff_part = 100 * d_part["value"] 
    err_part = 100 * d_part["error"] 

    eff_anti = 100 * d_anti["value"] 
    err_anti = 100 * d_anti["error"] 

    eff, err = utils.value_and_covariance('(p + a) / 2.', p = (eff_part, err_part), a = (eff_anti, err_anti) )

    if not perc:
        eff = eff / 100.
        err = err / 100.

    return (eff, err) 
#------------------------------
def get_json_table(year, polarity, evt):
    #wont break if year is int
    year=str(year)

    if   year == "2011":
        dirname=f'Sim09-Beam3500GeV-{year}-{polarity}-Nu2-Pythia8'
    elif year == "2012":
        dirname=f'Sim09-Beam4000GeV-{year}-{polarity}-Nu2.5-Pythia8'
    elif year in ["2015", "2016", "2017", "2018"]:
        dirname=f'Sim09-Beam6500GeV-{year}-{polarity}-Nu1.6-25ns-Pythia8'
    else:
        log.error(f'Year {year} is not supported')
        raise

    prodID=getProdID(evt, polarity, year)

    json_path=get_geo_acc_json(dirname, evt, prodID)
    if not os.path.isfile(json_path):
        return None

    return json_path
#------------------------------
def get_geo_acc_json(dirname, evt, prodID, allow_other=False):
    dbb_dir  =os.environ['DBBDIR']
    json_path=f'{dbb_dir}/gen_info/{dirname}/Evt{evt}-P{prodID}.json'
    if os.path.isfile(json_path):
        return json_path

    if allow_other:
        log.warning('-' * 20)
        log.warning(f'File not found: {json_path}')
        log.warning('Using other prodID')
        json_path = get_any_geo_acc_json(dirname, evt, prodID)
        log.warning('-' * 20)

        return json_path
    else:
        log.error(f'File not found: {json_path}')
        raise
#------------------------------
def get_any_geo_acc_json(dirname, evt):
    dbb_dir    = os.environ['DBBDIR']
    path_wc    = f'{dbb_dir}/gen_info/{dirname}/Evt{evt}-P*.json'
    l_json_path= glob.glob(path_wc)
    njsn       = len(l_json_path) 
    if njsn == 1:
        json_path_backup = l_json_path[0]
        log.warning(f'Found instead  {os.path.basename(json_path_backup)}')
        return json_path_backup
    else:
        log.error(f'Did not find one and only one JSON files: {l_json_path}')
        [ log.info(f'    {path}') for path in l_json_path ]
        raise
#------------------------------
def getGeomEff(name, dset, perc=False):
    if dset in ['2011', '2012', '2015', '2016', '2017', '2018']:
        eff_1 = calcGeomEff(name,   "MagUp", dset, perc)
        eff_2 = calcGeomEff(name, "MagDown", dset, perc)
        names = [f'{dset} MU', f'{dset} MD']
    elif dset == 'r1':
        eff_1 = getGeomEff(name, '2011', perc) 
        eff_2 = getGeomEff(name, '2012', perc) 
        names = ['2011', '2012']
    elif dset == 'r2p1':
        eff_1 = getGeomEff(name, '2015', perc) 
        eff_2 = getGeomEff(name, '2016', perc) 
        names = ['2015', '2016']
    elif dset == 'r2p2':
        eff_1 = getGeomEff(name, '2017', perc) 
        eff_2 = getGeomEff(name, '2018', perc) 
        names = ['2017', '2018']
    else:
        log.error('Efficiencies not implemented yet for ' + dset)
        raise

    eff = average_eff(eff_1, eff_2, names)

    return eff
#------------------------------
def average_eff(eff_1, eff_2, names):
    if   eff_1 is None and eff_2 is None:
        log.warning(f'Cannot average {names}, returning 0, 0')
        return 0, 0
    elif eff_1 is None:
        log.warning(f'Taking only {names[1]}, dropping {names[0]}')
        return eff_2
    elif eff_2 is None:
        log.warning(f'Taking only {names[0]}, dropping {names[1]}')
        return eff_1
    else:
        eff_1, err_1 = eff_1
        eff_2, err_2 = eff_2

        eff = (eff_1 + eff_2) / 2.
        err = 0.5 * math.sqrt(err_1 ** 2 + err_2 ** 2)

        return (eff, err)
#------------------------------
def get_binning(min_x, max_x, nbins=10):
    return numpy.linspace(min_x, max_x, nbins + 1)
#------------------------------
def get_var_binning(var_name):
    if   var_name == 'B_ETA':
        arr_bin = array.array('f', [1.9, 2.6, 2.9, 3.1, 3.2, 3.45, 3.65, 4, 5] )
    elif var_name == 'bdt_cmb':
        arr_bin = array.array('f', [ 0.0,  0.1,  0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9, 1.0]) 
    elif var_name == 'bdt_prc':
        arr_bin = array.array('f', [0.25, 0.3 , 0.35, 0.4 , 0.45, 0.5 , 0.55, 0.6 , 0.65, 0.7 , 0.75, 0.8 , 0.85])
    elif var_name == 'B_PT':
        arr_bin = array.array('f', [0, 4250, 5750, 7000, 8259, 9500, 11500, 14500, 18500 ] ) 
    elif var_name == 'MinLPT':
        arr_bin = array.array('f', [300, 750, 1100, 1400, 1750, 2200, 2800, 3700, 5000] )
    elif var_name == 'MaxLPT':
        arr_bin = array.array('f', [900, 2500, 3100, 3650, 4200, 4900, 5750, 7300, 10000] )
    elif var_name == 'H_PT':
        arr_bin = array.array('f', [400, 1100, 1600, 2100, 2700, 3400, 4400, 6000, 8500 ] ) 
    elif var_name == 'H_calo_ET':
        arr_bin = array.array('f', [400, 1100, 1600, 2100, 2700, 3400, 4400, 6000, 8500, 12000 ] ) 
    elif var_name == 'L_calo_ET':
        arr_bin = array.array('f', [400, 1100, 1600, 2100, 2700, 3400, 4400, 6000, 8500, 12000 ] ) 
    elif var_name == 'MinLETA':
        arr_bin = array.array('f', [1.5, 2.2, 2.4, 2.6, 2.7, 2.9, 3.1, 3.4, 5 ] ) 
    elif var_name == 'MaxLETA':
        arr_bin = array.array('f', [1.5, 2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.9, 5.1] )
    elif var_name == 'H_ETA':
        arr_bin = array.array('f', [1.5, 2.4, 2.6, 2.9, 3.1, 3.3, 3.6, 3.9, 5.2] )
    elif var_name == 'nSPDHits':
        arr_bin = array.array('f', [0, 168, 224, 272, 317, 366, 422, 491, 600] )
    elif var_name == 'nTracks':
        arr_bin = get_binning(0, 400, 20) 
    elif var_name == 'nPVs':
        arr_bin = get_binning(0, 10, 10) 
    elif var_name == 'LogIPCHI2':
        arr_bin = array.array('f', [-5, -0.84, -0.05, 0.46, 0.88, 1.3, 1.7, 2.2, 3] )
    elif var_name == 'vtxchi2':
        arr_bin = array.array('f', [-3, -0.38, 0.21, 0.6, 0.92, 1.2, 1.5, 1.9, 3.3] )
    elif var_name == 'llangle':
        arr_bin = array.array('f', [0.0, 0.063, 0.086, 0.11, 0.13, 0.16, 0.2, 0.25, 0.5] )
    elif var_name == 'klangle':
        arr_bin = array.array('f', [0, 0.05, 0.07, 0.09, 0.12, 0.14, 0.18, 0.23, 0.5] )
    elif var_name == 'cos_L':
        arr_bin = array.array('f', [-1., -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 1] )
    elif var_name == 'et_reg':
        arr_bin = array.array('f', [-0.001, 0.999, 1.999, 3])
    elif var_name == 'fdchi2':
        arr_bin = get_binning(+1.651e+00, 1.405e+01)
    elif var_name == 'h_ipchi2':
        arr_bin = get_binning(ROOT.TMath.Log(4), 1.2e+01)
    elif var_name == 'max_lipchi2':
        arr_bin = get_binning(-1, 12)
    elif var_name == 'min_lipchi2':
        arr_bin = get_binning(-1, 10)
    elif var_name == 'cos_dira':
        arr_bin = get_binning(0, 5e-02)
    elif var_name == 'jpsi_pt':
        arr_bin = get_binning(+1.296e+02, 3.639e+04)
    elif var_name == 'jpsi_ip_chi2':
        arr_bin = get_binning(-1, 8)
    elif var_name == 'B_T_L1_CONEPTASYM':
        arr_bin = get_binning(-1, +1, nbins=20) 
    elif var_name == 'log_B_VTXISODCHI2ONETRACK_p10':
        arr_bin = get_binning( 2, 10, nbins=8)
    elif var_name == 'log_B_VTXISODCHI2TWOTRACK_p10':
        arr_bin = get_binning( 2, 10, nbins=8) 
    elif var_name == 'B_const_mass_M':
        arr_bin = get_binning( 5070, 5700)
    elif var_name == 'B_VTXISODCHI2MASSONETRACK':
        arr_bin = get_binning(4e3, 11e3)
    elif var_name == 'Jpsi_FDCHI2_OWNPV':
        arr_bin = get_binning(0, 300)
    elif var_name == 'cos_dira_jpsi':
        arr_bin = get_binning(0, 5e-2)
    elif var_name == 'min_lp_cc_spt':
        arr_bin = get_binning(0, 5e+03)
    elif var_name == 'max_lp_cc_spt':
        arr_bin = get_binning(0, 7e+03)
    elif var_name == 'min_lp_cc_it':
        arr_bin = get_binning(0, 1.2)
    elif var_name == 'max_lp_cc_mul':
        arr_bin = get_binning(0, 11) 
    elif var_name == 'xbrem':
        arr_bin = get_binning(0, 3, nbins=3) 
    else:
        log.error(f'Invalid variable: {var_name}')
        raise

    return arr_bin
#------------------------------
def getDiffHist(trigger='BOTH', l_ext=[]):
    if trigger not in ['ETOS', 'HTOS', 'GTIS', 'MTOS', 'BOTH', 'test']:
        log.error(f'Using unsuported trigger: {trigger}')
        raise

    log.info(f'Using trigger: {trigger}')

    d_hist={}
    if True:
        add_hist('B_T_L1_CONEPTASYM'            , d_hist) 
        add_hist('log_B_VTXISODCHI2ONETRACK_p10', d_hist) 
        add_hist('log_B_VTXISODCHI2TWOTRACK_p10', d_hist) 
        add_hist('B_PT'                         , d_hist)
        add_hist('B_ETA'                        , d_hist)
        add_hist('MinLPT'                       , d_hist)
        add_hist('MaxLPT'                       , d_hist)
        add_hist('MinLETA'                      , d_hist)
        add_hist('MaxLETA'                      , d_hist)
        add_hist('H_PT'                         , d_hist)
        add_hist('H_ETA'                        , d_hist)
        add_hist('nSPDHits'                     , d_hist)
        add_hist('nTracks'                      , d_hist)
        add_hist('nPVs'                         , d_hist)
        add_hist('LogIPCHI2'                    , d_hist)
        add_hist('vtxchi2'                      , d_hist)
        add_hist('llangle'                      , d_hist)
        add_hist('klangle'                      , d_hist)
        add_hist('cos_L'                        , d_hist)
        add_hist('fdchi2'                       , d_hist)
        add_hist('h_ipchi2'                     , d_hist)
        add_hist('max_lipchi2'                  , d_hist)
        add_hist('min_lipchi2'                  , d_hist)
        add_hist('cos_dira'                     , d_hist)
        add_hist('jpsi_pt'                      , d_hist)
        add_hist('jpsi_ip_chi2'                 , d_hist)
        add_hist('B_VTXISODCHI2MASSONETRACK'    , d_hist)
        add_hist('Jpsi_FDCHI2_OWNPV'            , d_hist)
        add_hist('cos_dira_jpsi'                , d_hist)
        add_hist('min_lp_cc_spt'                , d_hist)
        add_hist('max_lp_cc_spt'                , d_hist)
        add_hist('min_lp_cc_it'                 , d_hist)
        add_hist('max_lp_cc_mul'                , d_hist)

    if   trigger in ["ETOS", 'GTIS']:
        add_hist('xbrem'                        , d_hist)

    #if   trigger in ["ETOS", 'GTIS']:
    #    add_hist("et_reg"   , d_hist)
    #    add_hist("et_rec"   , d_hist)
    #    add_hist("L_calo_ET", d_hist)
    #elif trigger in ['HTOS', 'GTIS']:
    #    add_hist("H_calo_ET", d_hist)

    if 'bmass' in l_ext:
        add_hist("B_const_mass_M", d_hist)

    return d_hist
#------------------------------
def add_hist(varname, d_hist):
    arr_bound       = get_var_binning(varname)

    d_hist[varname] = ROOT.TH1D(f'h_{varname}', '', len(arr_bound) - 1, arr_bound)
#------------------------------
def addDiffVars(rdf, kind='all', trigger=None):
    if kind not in data.l_var_kind:
        log.error(f'Invalid variables kind: {kind}')
        log.error(f'Choose among: {data.l_var_kind}')
        raise

    if kind == 'all' or kind == 'cmb_bdt':
        man = mgr(rdf)
        rdf = define_cmb_bdt_vars(rdf)
        man.add_atr(rdf) 

    if kind == 'all' or kind == 'prc_bdt':
        man = mgr(rdf)
        rdf = define_prc_bdt_vars(rdf)
        man.add_atr(rdf) 

    if kind == 'all' or kind == 'dif_fit':
        man = mgr(rdf)
        rdf = define_dif_fit_vars(rdf)
        man.add_atr(rdf) 

    if kind == 'all' or kind == 'ext_vars':
        man = mgr(rdf)
        rdf = define_ext_vars(rdf, trigger)
        man.add_atr(rdf) 

    return rdf
#------------------------------
def define_cmb_bdt_vars(rdf):
    rdf=rdf.Define("PT"       , "B_PT")
    rdf=rdf.Define("ETA"      , "B_ETA" )
    rdf=rdf.Define("MinLPT"   , "TMath::Min(L1_PT , L2_PT)")
    rdf=rdf.Define("MaxLPT"   , "TMath::Max(L1_PT , L2_PT)")
    rdf=rdf.Define("MinLETA"  , "TMath::Min(L1_ETA, L2_ETA)")
    rdf=rdf.Define("MaxLETA"  , "TMath::Max(L1_ETA, L2_ETA)")
    rdf=rdf.Define("LogIPCHI2", "TMath::Log(B_IPCHI2_OWNPV)")
    rdf=rdf.Define("vtxchi2"  , "TMath::Log(B_ENDVERTEX_CHI2)")
    rdf=rdf.Define("llangle"  , "TVector3 v_l1(L1_PX, L1_PY, L1_PZ); TVector3 v_l2(L2_PX, L2_PY, L2_PZ); return v_l1.Angle(v_l2);")
    rdf=rdf.Define("klangle"  , "TVector3 v_k(H_PX, H_PY, H_PZ)    ; TVector3 v_l1(L1_PX, L1_PY, L1_PZ); return v_k.Angle(v_l1);")
    rdf=rdf.Define("cos_L"    , """TLorentzVector v_l1(L1_PX, L1_PY, L1_PZ, L1_PE); 
                                 TLorentzVector v_l2(L2_PX, L2_PY, L2_PZ, L2_PE);
                                 auto v_ll = v_l1 + v_l2; 
                                 auto v_boost = -1 * v_ll.BoostVector(); 
                                 v_l1.Boost(v_boost); 
                                 auto v1 = v_l1.Vect();
                                 auto v2 = v_ll.Vect();
                                 auto u1 = v1.Unit();
                                 auto u2 = v2.Unit();
                                 return u1.Dot(u2);""")

    rdf=rdf.Define('fdchi2'      , 'TMath::Log(B_FDCHI2_OWNPV)                                           ')
    rdf=rdf.Define('h_ipchi2'    , 'TMath::Log(H_IPCHI2_OWNPV)                                           ')
    rdf=rdf.Define('max_lipchi2' , 'TMath::Max(TMath::Log(L1_IPCHI2_OWNPV),TMath::Log(L2_IPCHI2_OWNPV))  ')
    rdf=rdf.Define('min_lipchi2' , 'TMath::Min(TMath::Log(L1_IPCHI2_OWNPV),TMath::Log(L2_IPCHI2_OWNPV))  ')
    rdf=rdf.Define('cos_dira'    , 'TMath::ACos(B_DIRA_OWNPV)                                            ')
    rdf=rdf.Define('jpsi_pt'     , 'Jpsi_PT                                                              ')
    rdf=rdf.Define('jpsi_ip_chi2', 'TMath::Log(Jpsi_IPCHI2_OWNPV)                                        ')
    rdf=rdf.Define('log_B_VTXISODCHI2ONETRACK_p10', 'TMath::Log(B_VTXISODCHI2ONETRACK + 10)')
    rdf=rdf.Define('log_B_VTXISODCHI2TWOTRACK_p10', 'TMath::Log(B_VTXISODCHI2TWOTRACK + 10)')

    return rdf
#------------------------------
def define_prc_bdt_vars(rdf):
    rdf = rdf.Define('cos_dira_jpsi', 'TMath::ACos(Jpsi_DIRA_OWNPV)')
    rdf = rdf.Define('min_lp_cc_spt', 'TMath::Min(B_L1_CC_SPT, B_L2_CC_SPT)')
    rdf = rdf.Define('max_lp_cc_spt', 'TMath::Max(B_L1_CC_SPT, B_L2_CC_SPT)')
    rdf = rdf.Define('min_lp_cc_it' , 'TMath::Min(B_L1_CC_IT, B_L2_CC_IT)')
    rdf = rdf.Define('max_lp_cc_mul', 'TMath::Max(B_L1_CC_MULT, B_L2_CC_MULT)')

    return rdf
#------------------------------
def define_ext_vars(rdf, trigger):
    if trigger in ['ETOS', 'GTIS']:
        rdf = rdf.Define('xbrem', 'L1_BremMultiplicity + L2_BremMultiplicity')

    return rdf
#------------------------------
def define_dif_fit_vars(rdf):
    log.info(f'Adding variables that are required by differential checks.')
    q2   = rdf.q2
    trig = rdf.trig

    if   q2 == 'jpsi':
        rdf=rdf.Define('mass', 'B_const_mass_M[0]')
    elif q2 == 'psi2':
        rdf=rdf.Define('mass', 'B_const_mass_psi2S_M[0]')
    else:
        log.warning(f'q2 category {rdf.q2} is not jpsi or psi2s, use mass without any constrain.')
        rdf=rdf.Define('mass', 'B_M')

    rdf=rdf.Define('ll_max_P'            , 'TMath::Max( L1_P  , L2_P )'  )
    rdf=rdf.Define('ll_min_P'            , 'TMath::Min( L1_P  , L2_P )'  )
    rdf=rdf.Define('ll_max_PT'           , 'TMath::Max( L1_PT , L2_PT )' )
    rdf=rdf.Define('ll_min_PT'           , 'TMath::Min( L1_PT , L2_PT )' )
    rdf=rdf.Define('ll_max_ETA'          , 'TMath::Max( L1_ETA, L2_ETA )')
    rdf=rdf.Define('ll_min_ETA'          , 'TMath::Min( L1_ETA, L2_ETA )')

    rdf=rdf.Define('ll_angle'            , """TVector3 v_l1(L1_PX, L1_PY, L1_PZ); 
                                              TVector3 v_l2(L2_PX, L2_PY, L2_PZ); 
                                              return v_l1.Angle(v_l2);""")

    rdf=rdf.Define('Kl1_angle'           , """TVector3 v_k(H_PX, H_PY, H_PZ);
                                              TVector3 v_l1(L1_PX, L1_PY, L1_PZ); 
                                              return v_k.Angle(v_l1);""")

    rdf=rdf.Define('Kl2_angle'           , """TVector3 v_k(H_PX, H_PY, H_PZ);
                                              TVector3 v_l2(L2_PX, L2_PY, L2_PZ); 
                                              return v_k.Angle(v_l2);""")

    rdf=rdf.Define('cos_theta_L'         , """TLorentzVector v_l1(L1_PX, L1_PY, L1_PZ, L1_PE); 
                                              TLorentzVector v_l2(L2_PX, L2_PY, L2_PZ, L2_PE);
                                              auto v_ll = v_l1 + v_l2; 
                                              auto v_boost = -1 * v_ll.BoostVector(); 
                                              v_l1.Boost(v_boost); 
                                              auto v1 = v_l1.Vect();
                                              auto v2 = v_ll.Vect();
                                              auto u1 = v1.Unit();
                                              auto u2 = v2.Unit();
                                              return u1.Dot(u2);""")


    rdf=rdf.Define('B_ENDVTX_Z'          , 'B_ENDVERTEX_Z')

    rdf=rdf.Define('log_B_IPCHI2_PV'    , 'TMath::Log(B_IPCHI2_OWNPV)')
    rdf=rdf.Define('log_B_VTXCHI2'      , 'TMath::Log(B_ENDVERTEX_CHI2)')

    rdf=rdf.Define('K_P'                 , 'TMath::Sqrt(H_PX*H_PX+H_PY*H_PY+H_PZ*H_PZ)')
    rdf=rdf.Define('K_PT'                , 'H_PT')
    rdf=rdf.Define('K_ETA'               , 'H_ETA')

    rdf=rdf.Define('l1_PT'               , 'L1_PT')
    rdf=rdf.Define('l2_PT'               , 'L2_PT')
    rdf=rdf.Define('l1_ETA'              , 'L1_ETA')
    rdf=rdf.Define('l2_ETA'              , 'L2_ETA')

    return rdf 
#------------------------------

