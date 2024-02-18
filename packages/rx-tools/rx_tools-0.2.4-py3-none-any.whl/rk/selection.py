import read_selection as rs
import utils_noroot   as utnr

log=utnr.getLogger(__name__)

#-----------------------
class data:
    l_ee_trig   = ['ETOS', 'HTOS', 'GTIS']
    l_mm_trig   = ['MTOS']
    l_data_type = ['data_ee', 'data_mm', 'cmb_ss', 'cmb_em']
    l_year      = ['2011', '2012', '2015', '2016', '2017', '2018']
    d_mtis_trig = {'MTIS_ee' : 'ETOS', 'MTIS_mm' : 'MTOS'}

    d_proc_q2bin = {'high_hhh' : 'high', 'ctrl_ee' : 'jpsi' , 'psi2_ee' : 'psi2', 'ctrl_mm' : 'jpsi', 'psi2_mm' : 'psi2'}
#-----------------------
def get_wide_mass(d_cut, min_mass, max_mass):
    cut  = utnr.get_from_dic(d_cut, 'mass')
    regex='\(B_[\w_\[\]]+\s+>\s(\d+)\)\s+&&\s+\(B_[\w_\[\]]+\s+<\s(\d+)\)'

    cut_min_mass = utnr.get_regex_group(cut, regex, i_group=1)
    cut_max_mass = utnr.get_regex_group(cut, regex, i_group=2)

    cut=cut.replace(cut_min_mass, min_mass)
    cut=cut.replace(cut_max_mass, max_mass)

    return cut
#-----------------------
def selection(kind, trigger, year, proc, q2bin='none'):
    utnr.check_included(year, data.l_year)

    #If q2bin is not specified guess it from the proc variable.
    #Same for 'all' cuts, given that it wil be used directly
    #Otherwise, q2bin SHOULD be decided in ifs anyway.

    pick_q2 = (q2bin == 'none') or (kind == 'all')
    if pick_q2 and '_noq2_' not in kind:
        q2bin = utnr.get_from_dic(data.d_proc_q2bin, proc)

    log.visible(f'Using q2bin {q2bin} for cut type {kind}, process {proc}, trigger {trigger} and year {year}')

    d_cut = {}

    if ('data_' not in proc) and ('cmb_' not in proc): 
        d_cut['truth'] = rs.get_truth(proc)
    #--------------------------------
    if   kind == 'loose_000':
        d_cut[trigger]      = rs.get(trigger.lower(), trigger, 'none', 'none')
        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
    elif kind == 'loose_001':
        d_cut[trigger]      = 'B_L0MuonDecision_TIS'
        trigger             = utnr.get_from_dic(data.d_mtis_trig, trigger)

        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
    elif kind == 'loose_002':
        d_cut[trigger]      = 'B_L0MuonDecision_TIS'
        trigger             = utnr.get_from_dic(data.d_mtis_trig, trigger)

        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
        d_cut[  'q2']       = rs.get(  'q2'         , trigger,  q2bin,   year)
        d_cut['mass']       = rs.get(  'mass'       , trigger,  q2bin,   year)
    elif kind == 'loose_004':
        d_cut[trigger]      = rs.get(trigger.lower(), trigger, 'none', 'none')
        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
        d_cut[  'q2']       = rs.get(  'q2'         , trigger,  q2bin,   year)
        d_cut['mass']       = rs.get(  'mass'       , trigger,  q2bin,   year)
    #--------------------------------
    elif kind == 'all_gorder_no_truth_mass_bdt':
        d_cut               = selection('all_gorder', trigger, year, proc, q2bin='none')
        d_cut['truth']      = '(1)'
        d_cut['bdt'  ]      = '(1)'
        d_cut['mass']       = '(1)'
    elif kind == 'all_gorder_no_bdt':
        d_cut        = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['bdt'] = '(1)'
    elif kind == 'all_gorder_no_cmb_bdt':
        d_cut        = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['bdt'] = rs.get('bdt_prc'      , trigger, 'none',   year)
    elif kind == 'all_gorder_no_prc_bdt':
        d_cut        = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['bdt'] = rs.get('bdt_cmb'      , trigger, 'none',   year)
    elif kind == 'calibration':
        d_cut         = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['pid']  = '(1)'
        d_cut[trigger]= '(1)'
        d_cut['hlt1'] = '(1)'
        d_cut['hlt2'] = '(1)'
        d_cut['bdt']  = '(1)'
    elif kind == 'all_gorder_no_bdt_nojpsimisid':
        d_cut        = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['bdt'] = '(1)'
        if 'jpsi_misid' in d_cut:
            d_cut['jpsi_misid'] = '(1)'
    elif kind == 'all_gorder_no_bdt_wide':
        d_cut               = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['mass']       = get_wide_mass(d_cut, '4900', '5700')
        d_cut['bdt']        = '(1)'
    elif kind == 'all_gorder_no_q2_mass' and trigger in data.l_ee_trig:
        d_cut               = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        d_cut['qsq']        = '(1)'
        d_cut['mass']       = '(1)' 
    #--------------------------------
    elif kind == 'all'        and trigger in data.l_ee_trig:
        d_cut['nspd']       = rs.get('nspd'         , trigger, 'none', 'none')
        d_cut['calo_rich']  = rs.get('calo_rich'    , trigger, 'none', 'none')
        d_cut['cascade']    = rs.get('cascade'      , trigger, 'none', 'none')
        d_cut['ghost']      = rs.get('ghost'        , trigger, 'none', 'none')
        d_cut['kinematics'] = rs.get('kinematics'   , trigger, 'none', 'none')
        d_cut['xyecal']     = rs.get('xyecal'       , trigger, 'none', 'none')
        d_cut['q2' ]        = rs.get('q2'           , trigger,  q2bin, 'none')
        d_cut['pid']        = rs.get('pid'          , trigger, 'none', 'none')
        d_cut[trigger]      = rs.get(trigger.lower(), trigger, 'none', 'none')
        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
        d_cut['bdt']        = rs.get('bdt'          , trigger, 'none',   year)
        d_cut['mass']       = rs.get('mass'         , trigger,  q2bin,   year)
    elif kind == 'all'        and trigger in data.l_mm_trig:
        d_cut['nspd']       = rs.get('nspd'         , trigger, 'none', 'none')
        d_cut['rich']       = rs.get('rich'         , trigger, 'none', 'none')
        d_cut['cascade']    = rs.get('cascade'      , trigger, 'none', 'none')
        d_cut['ghost']      = rs.get('ghost'        , trigger, 'none', 'none')
        d_cut['kinematics'] = rs.get('kinematics'   , trigger, 'none', 'none')
        d_cut['acceptance'] = rs.get('acceptance'   , trigger, 'none', 'none')
        d_cut['jpsi_misid'] = rs.get('jpsi_misid'   , trigger, 'none', 'none')
        d_cut['q2' ]        = rs.get('q2'           , trigger,  q2bin, 'none')
        d_cut['pid']        = rs.get('pid'          , trigger, 'none', 'none')
        d_cut[trigger]      = rs.get(trigger.lower(), trigger, 'none', 'none')
        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
        d_cut['bdt']        = rs.get('bdt'          , trigger, 'none',   year)
        d_cut['mass']       = rs.get('mass'         , trigger,  q2bin,   year)
    elif kind == 'all_gorder' and trigger in data.l_ee_trig:
        d_cut['nspd']       = rs.get('nspd'         , trigger, 'none', 'none')
        d_cut[trigger]      = rs.get(trigger.lower(), trigger, 'none', 'none')
        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
        d_cut['q2' ]        = rs.get('q2'           , trigger,  q2bin, 'none')
        d_cut['kinematics'] = rs.get('kinematics'   , trigger, 'none', 'none')
        d_cut['cascade']    = rs.get('cascade'      , trigger, 'none', 'none')
        d_cut['ghost']      = rs.get('ghost'        , trigger, 'none', 'none')
        d_cut['calo_rich']  = rs.get('calo_rich'    , trigger, 'none', 'none')
        d_cut['pid']        = rs.get('pid'          , trigger, 'none', 'none')
        d_cut['xyecal']     = rs.get('xyecal'       , trigger, 'none', 'none')
        d_cut['bdt']        = rs.get('bdt'          , trigger, 'none',   year)
        d_cut['mass']       = rs.get('mass'         , trigger,  q2bin,   year)
    elif kind == 'all_gorder' and trigger in data.l_mm_trig:
        d_cut['nspd']       = rs.get('nspd'         , trigger, 'none', 'none')
        d_cut[trigger]      = rs.get(trigger.lower(), trigger, 'none', 'none')
        d_cut['hlt1']       = rs.get('hlt1'         , trigger, 'none',   year)
        d_cut['hlt2']       = rs.get('hlt2'         , trigger, 'none',   year)
        d_cut['q2' ]        = rs.get('q2'           , trigger,  q2bin, 'none')
        d_cut['kinematics'] = rs.get('kinematics'   , trigger, 'none', 'none')
        d_cut['cascade']    = rs.get('cascade'      , trigger, 'none', 'none')
        d_cut['ghost']      = rs.get('ghost'        , trigger, 'none', 'none')
        d_cut['rich']       = rs.get('rich'         , trigger, 'none', 'none')
        d_cut['acceptance'] = rs.get('acceptance'   , trigger, 'none', 'none')
        d_cut['jpsi_misid'] = rs.get('jpsi_misid'   , trigger, 'none', 'none')
        d_cut['pid']        = rs.get('pid'          , trigger, 'none', 'none')
        d_cut['bdt']        = rs.get('bdt'          , trigger, 'none',   year)
        d_cut['mass']       = rs.get('mass'         , trigger,  q2bin,   year)
    #--------------------------------
    elif kind == 'cr_common'  and trigger in data.l_ee_trig:
        d_cut        = selection('all_gorder', trigger, year, proc, q2bin= q2bin)
        del(d_cut['mass'])
        del(d_cut[ 'bdt'])
        del(d_cut[  'q2'])
    else:
        log.error(f'Wrong kind "{kind}" and/or trigger "{trigger}"')
        raise

    return d_cut
#-----------------------

