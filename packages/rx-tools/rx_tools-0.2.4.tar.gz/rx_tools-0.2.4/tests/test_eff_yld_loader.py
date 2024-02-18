from rk.eff_yld_loader import eff_yld_loader as eyl
from rk.cutflow                 import cutflow
from rk.efficiency              import efficiency 
from rk.differential_efficiency import defficiency
from ndict                      import ndict

import utils_noroot as utnr 

import logging
import numpy 
import utils 
import math
import os 

log=utnr.getLogger(__name__)
#--------------------------------
def test_rare(chan, year, trig):
    obj=eyl(f'sign_{chan}', trig, year, 'pall_tall_gall_lall_hall_rall_qall_bnom_snom')
    ((yld_val, yld_err), d_eff) = obj.get_values(eff_version='v62', yld_version='v24')

    assert yld_val == 1
    assert yld_err == 0
#--------------------------------
def test_syst(proc, trig):
    obj=eyl(proc, trig, '2018', 'pall_tall_gall_lall_hall_rall_qall')
    ((yld_val, yld_err), d_eff) = obj.get_values(eff_version='v21', yld_version='v11')

    for key in sorted(d_eff.keys()):
        print(key)
#--------------------------------
def test_weights_int(weights):
    obj=eyl('ctrl_ee', 'ETOS', '2018', weights)
    ((yld_val, yld_err), eff_obj) = obj.get_values(eff_version='v28', yld_version='v11')

    cf  = eff_obj['nom']
    eff = cf.efficiency
    eff_val, eff_eup, eff_edn = eff.val

    return f'{weights:<40}{yld_val:<20.0f}{yld_err:<20.0f}{eff_val:<20.3e}{eff_eup:<20.3e}{eff_edn:<20.3e}'
#--------------------------------
def test_weights_dif(weights):
    obj=eyl('ctrl_ee', 'ETOS', '2018', weights)
    ((yld_val, yld_err), eff_obj) = obj.get_values(eff_version='v29', yld_version='v11')

    cf  = eff_obj['nom', 'BDT']
    eff = cf.efficiency.efficiency()
    eff_val, eff_eup, eff_edn = eff.val

    print(f'{weights:<40}{yld_val:<20.0f}{yld_err:<20.0f}{eff_val:<20.3e}{eff_eup:<20.3e}{eff_edn:<20.3e}')
#--------------------------------
def test_weights_stat(weights):
    obj=eyl('psi2_ee', 'ETOS', '2018', weights)
    ((yld_val, yld_err), eff_obj) = obj.get_values(eff_version='v53', yld_version='v23')

    for bts, var in sorted(eff_obj):
        if var != 'B_PT':
            continue
        print(bts)
#--------------------------------
def test_all_weights():
    l_out = [f'{"Weights":<40}{"Yields":<20}{"Error":<20}{"Eff":<20}{"Eff error up":<20}{"Eff error down":<20}']

    l_out.append(test_weights_int('p000_t000_g000_l000_h000_r000_q000_bnom'))
    l_out.append(test_weights_int('pnom_t000_g000_l000_h000_r000_q000_bnom'))
    l_out.append(test_weights_int('pnom_tnom_g000_l000_h000_r000_q000_bnom'))
    l_out.append(test_weights_int('pnom_tnom_gnom_l000_h000_r000_q000_bnom'))
    l_out.append(test_weights_int('pnom_tnom_gnom_lnom_h000_r000_q000_bnom'))
    l_out.append(test_weights_int('pnom_tnom_gnom_lnom_hnom_r000_q000_bnom'))
    l_out.append(test_weights_int('pnom_tnom_gnom_lnom_hnom_rnom_q000_bnom'))
    l_out.append(test_weights_int('pnom_tnom_gnom_lnom_hnom_rnom_qnom_bnom'))
    l_out.append(test_weights_int('pnom_tnom_gnom_lnom_hnom_rnom_qnom_bnom'))

    for line in l_out:
        print(line)
#--------------------------------
def make_efficiencies(version, weights, proc, year, trig, kind, part='p00'):
    eff_dir  = utnr.make_dir_path(f'/publicfs/lhcb/user/campoverde/checks/Efficiencies/output/efficiencies/{version}/{part}_{weights}')
    eff_path = f'{eff_dir}/cf_tot_{proc}_{year}_{trig}.pickle'

    if   kind ==   'cf':
        obj = get_cutflow(0.1, 'nom')
    elif kind ==  'dcf':
        l_eff_sys = [(0.1, 's1'), (0.2, 's2'), (0.3, 's3')]
        obj       = {syst : get_cutflow(eff_val, syst) for eff_val, syst in l_eff_sys }
    elif kind == 'ndcf':
        l_eff_sys = [(0.1, 's1'), (0.2, 's2'), (0.3, 's3')]
        l_var     = ['v1', 'v2', 'v3']
        obj       = ndict()

        for eff_val, sys in l_eff_sys:
            for var in l_var:
                obj[sys, var] = get_cutflow(eff_val, sys, var)
    else:
        data.log.error(f'Invalid kind: {kind}')
        raise

    utnr.dump_pickle(obj, eff_path)

    return obj
#--------------------------------
def print_cutflow(obj):
    if   isinstance(obj, dict):
        for sys, ctfl in obj.items():
            print(sys)
            print(ctfl)
    elif isinstance(obj, ndict):
        for (sys, var), obj in obj.items():
            print(sys, var)
            print(obj)
    else:
        print(obj)
#--------------------------------
def get_def(tot, syst, varname):
    v1 = numpy.random.uniform()
    v2 = numpy.random.uniform()
    v3 = numpy.random.uniform()

    y1 = v1 * tot / (v1 + v2 + v3)
    y2 = v2 * tot / (v1 + v2 + v3)
    y3 = v3 * tot / (v1 + v2 + v3)

    deff       = defficiency(lab=syst, varname=varname)
    deff[0, 1] = efficiency(math.floor(y1), arg_tot=tot, cut=f'0 < {varname} < 1', lab=syst)
    deff[1, 2] = efficiency(math.floor(y2), arg_tot=tot, cut=f'1 < {varname} < 2', lab=syst)
    deff[2, 3] = efficiency(math.floor(y3), arg_tot=tot, cut=f'2 < {varname} < 3', lab=syst)

    return deff
#--------------------------------
def get_cutflow(eff_val, syst, var=None):
    cf = cutflow()

    tot = 100000
    ini = tot
    for i_eff in range(3):
        fal = int((1 - eff_val) * tot)
        pas = tot - fal

        cf[f'cut {i_eff}'] = efficiency(pas, arg_fal = fal, cut=f'cut_{i_eff}', lab=syst)

        tot = pas

    deff = get_def(tot, syst, var if var is not None else 'no-var')

    cf['cut diff'] = deff if var is not None else deff.efficiency()

    return cf
#--------------------------------
def make_yields(version, proc, year, trig):
    fit_dir  = os.environ['FITDIR']
    yld_dir  = utnr.make_dir_path(f'{fit_dir}/{version}/data/v10.11tf/{proc}/{year}')
    yld_path = f'{yld_dir}/pars_{trig}.json'

    tp_yld = (10000, 100)
    utnr.dump_json({'nsig' : tp_yld}, yld_path)

    return tp_yld
#--------------------------------
def add_eff_obj(o1, o2):
    if isinstance(o1, cutflow) and isinstance(o2, cutflow):
        return o1 + o2

    if   isinstance(o1, dict)  and isinstance(o2,    dict):
        o3 = {}
    elif isinstance(o1,ndict)  and isinstance(o2,   ndict):
        o3 = ndict() 
    else:
        log.error(f'Invalid efficiency object types: {type(o1)}, {type(o2)}')
        raise

    for key, cfl_1 in o1.items():
        cfl_2 = o2[key]

        o3[key] = cfl_1 + cfl_2 

    return o3
#--------------------------------
def test_toy(kind):
    obj_0  = make_efficiencies('v0', 'test', 'test_ee', 'test', 'test', kind, part='p00')
    obj_1  = make_efficiencies('v0', 'test', 'test_ee', 'test', 'test', kind, part='p01')
    obj_in = add_eff_obj(obj_0, obj_1)

    yld_in = make_yields('v0', 'test', 'test', 'test')

    obj=eyl('test_ee', 'test', 'test', 'test')
    yld_ot, obj_ot = obj.get_values(eff_version='v0', yld_version='v0')

    if yld_in != yld_ot:
        log.error(f'Read yields differ from plugged yields: {yld_ot}/{yld_in}')
        raise AssertionError

    if obj_in != obj_ot:
        log.error(f'Efficiency object in and out differ')
        print_cutflow(obj_in)
        print_cutflow(obj_ot)
        raise AssertionError

    log.visible('Passed: test_toy')
#--------------------------------
def main():
    test_rare('ee', '2018', 'ETOS')
    test_rare('mm', '2018', 'MTOS')

    return
    test_weights_stat('pnom_tnom_gnom_lnom_hnom_rnom_qnom_bnom_sall')
    test_weights_dif('pall_tall_gall_lall_hall_rall_qall_bnom')
    test_toy(  'cf')
    test_toy( 'dcf')
    test_toy('ndcf')
    test_all_weights()
    #test_syst('ctrl_ee', 'ETOS')
    #test_syst('ctrl_ee', 'GTIS')
    #test_syst('ctrl_mm', 'MTOS')
#--------------------------------
if __name__ == '__main__':
    main()

