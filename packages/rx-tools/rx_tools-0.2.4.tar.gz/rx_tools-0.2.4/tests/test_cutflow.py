from rk.cutflow                 import     cutflow 
from rk.efficiency              import  efficiency 
from rk.differential_efficiency import defficiency

import utils_noroot as utnr 
import numpy
import os
import math

log=utnr.getLogger(__name__)
#-------------------------------------
def get_cfl_ywt(index = 1):
    numpy.random.seed(1)

    arr_a = numpy.random.normal(1, 0.1, 10000) + index * 1e-7
    arr_b = numpy.random.choice(arr_a ,  8000)
    arr_c = numpy.random.choice(arr_b ,  7000)
    arr_d = numpy.random.choice(arr_c ,  6000)
    arr_e = numpy.random.choice(arr_d ,  5000)

    eff_1 = efficiency(arr_b, arg_tot=arr_a, cut='c1', lab='nom')
    eff_2 = efficiency(arr_c, arg_tot=arr_b, cut='c2', lab='nom')
    eff_3 = efficiency(arr_d, arg_tot=arr_c, cut='c3', lab='nom')
    eff_4 = efficiency(arr_e, arg_tot=arr_c, cut='c3', lab='nom')
    
    cfl = cutflow()
    if   index == 1:
        cfl['a'] = eff_1
        cfl['b'] = eff_2
        cfl['c'] = eff_3
    elif index == 2:
        cfl['a'] = eff_1
        cfl['b'] = eff_2
    elif index == 3:
        cfl['a'] = eff_1
        cfl['b'] = eff_2
        cfl['c'] = eff_4
    else:
        log.error(f'Invalid index: {index}')
        raise

    return cfl
#-------------------------------------
def get_cfl_nwt(index = 1):
    eff_1 = efficiency(100000000 + index, arg_fal=100000000, cut='c1', lab='nom')
    eff_2 = efficiency( 50000000 + index, arg_fal= 50000000, cut='c2', lab='nom')
    eff_3 = efficiency( 30000000 + index, arg_fal= 20000000, cut='c3', lab='nom')
    eff_4 = efficiency( 40000000 + index, arg_fal= 10000000, cut='c3', lab='nom')
    
    cfl = cutflow()
    if   index == 1:
        cfl['a'] = eff_1
        cfl['b'] = eff_2
        cfl['c'] = eff_3
    elif index == 2:
        cfl['a'] = eff_1
        cfl['b'] = eff_2
    elif index == 3:
        cfl['a'] = eff_1
        cfl['b'] = eff_2
        cfl['c'] = eff_4
    else:
        log.error(f'Invalid index: {index}')
        raise

    return cfl
#-------------------------------------
def get_cfl_dif(index = 1, index_d=None):
    index_d = index if index_d is None else index_d 

    eff_1 = efficiency(100000000 + index_d, arg_fal=100000000, cut='c1', lab='nom')
    eff_2 = efficiency( 50000000 + index_d, arg_fal= 50000000, cut='c2', lab='nom')

    
    cfl = cutflow()
    if   index == 1:
       cfl['a'] = eff_1
       cfl['b'] = eff_2
       cfl['c'] = get_deff(index, index_d) 
    elif index == 2:
       cfl['a'] = eff_1
       cfl['b'] = eff_2
    elif index == 3:
       cfl['a'] = eff_1
       cfl['b'] = eff_2
       cfl['c'] = get_deff(index, index_d) 
    else:
       log.error(f'Invalid index: {index}')
       raise

    return cfl
#-------------------------------------
def get_deff(index, index_d):
    obj    = defficiency(lab='nom', varname='x')

    if   index_d == 1:
        #obj[0, 1] = efficiency(10000, 40000, cut='0 < a < 1', lab='bin1')
        obj[1, 2] = efficiency(15000000, arg_fal=35000000 + index_d, cut='1 < a < 2', lab='nom')
        obj[2, 3] = efficiency(15000000, arg_fal=35000000 + index_d, cut='2 < a < 3', lab='nom')
    elif index_d == 2:
        obj[1, 2] = efficiency(20000000, arg_fal=30000000 + index_d, cut='1 < a < 2', lab='nom')
        obj[2, 3] = efficiency(20000000, arg_fal=30000000 + index_d, cut='2 < a < 3', lab='nom')
    elif index_d == 3:
        obj[0, 1] = efficiency(20000000, arg_fal=30000000 + index_d, cut='0 < a < 1', lab='nom')
        obj[1, 2] = efficiency(20000000, arg_fal=30000000 + index_d, cut='1 < a < 2', lab='nom')
        #obj[2, 3] = efficiency(10000, 40000, cut='2 < a < 3', lab='bin3')

    return obj
#-------------------------------------
def test_simple():
    eff_1 = efficiency(500, arg_tot=1000, cut='c1', lab='nom')
    eff_2 = efficiency(300, arg_tot= 500, cut='c2', lab='nom')
    eff_3 = efficiency(100, arg_tot= 300, cut='c3', lab='nom')
    eff_4 = efficiency( 50, arg_tot= 100, cut='c4', lab='nom')
    
    cfl = cutflow()
    cfl['a'] = eff_1
    cfl['b'] = eff_2
    cfl['c'] = eff_3
    cfl['d'] = eff_4

    tst_dir = f'tests/cutflow/simple'
    os.makedirs(tst_dir, exist_ok=True)

    cfl.to_json(f'{tst_dir}/cutflow.json')
#-------------------------------------
def test_meta():
    eff_1 = efficiency(500, arg_tot=1000, cut='c1', lab='nom')
    eff_2 = efficiency(300, arg_tot= 500, cut='c2', lab='nom')
    eff_3 = efficiency(100, arg_tot= 300, cut='c3', lab='nom')
    eff_4 = efficiency( 50, arg_tot= 100, cut='c4', lab='nom')
    
    cfl = cutflow(d_meta={'paths' : ['a', 'b', 'c']})
    cfl['a'] = eff_1
    cfl['b'] = eff_2
    cfl['c'] = eff_3
    cfl['d'] = eff_4

    tst_dir = f'tests/cutflow/meta'
    os.makedirs(tst_dir, exist_ok=True)

    cfl.to_json(f'{tst_dir}/cutflow.json')
#-------------------------------------
def test_print(cfl):
    log.visible('Print')
    #print(cfl.df_eff)
    #print(cfl.df_cut)
    #print(cfl)
    print(cfl.efficiency)
#-------------------------------------
def test_equal(get_cfl):
    log.visible('Equal')
    cfl_0 = get_cfl(1)
    cfl_1 = get_cfl(1)
    cfl_2 = get_cfl(2)
    cfl_3 = get_cfl(3)

    check_equal(cfl_0, cfl_1,  True)
    check_equal(cfl_0, cfl_2, False)
    check_equal(cfl_0, cfl_3, False)
#-------------------------------------
def test_add(get_cfl):
    log.visible('Add')
    cfl_0 = get_cfl(1)
    cfl_1 = get_cfl(3)

    cfl_2 = cfl_0 + cfl_1

    print(cfl_0.df_eff)
    print(cfl_1.df_eff)
    print(cfl_2.df_eff)
#-------------------------------------
def test_sum(get_cfl):
    log.visible('Sum')
    l_cfl = [ get_cfl(i_cfl) for i_cfl in [1, 3] ] 

    cfl_1 = l_cfl[0] + l_cfl[1]
    cfl_2 = sum(l_cfl[1:], l_cfl[0])

    assert(cfl_1 == cfl_2)
#-------------------------------------
def check_equal(o1, o2, expected):
    result = o1 == o2

    if result != expected:
        log.error('Failed')
        print(o1.df_eff)
        print(o2.df_eff)
        print(f'Should be equal: {expected}')
        raise
    else:
        log.info('Passed')
#-------------------------------------
def test_hash():
    log.visible(f'Hash')

    d_cfl = { get_cfl_nwt(i_cfl) : i_cfl for i_cfl in [1, 3] }
#-------------------------------------
def test_avg(get_cfl, avg, l_ind=None):
    log.visible(f'Average')

    if l_ind is not None:
        cfl_1, cfl_2 = [ get_cfl(i_cfl, j_cfl) for i_cfl, j_cfl in zip([1, 3], l_ind) ] 
    else:
        cfl_1, cfl_2 = [ get_cfl(i_cfl)        for i_cfl        in [1, 3] ] 

    cfl_3        = cutflow.average({cfl_1 : 1, cfl_2 : 2})

    eff_1        = cfl_1.tot_eff
    eff_2        = cfl_2.tot_eff
    eff_3        = cfl_3.tot_eff

    is_close = math.isclose(eff_3, avg, rel_tol=1e-5)
    if not is_close:
        log.error(f'Test failed: {eff_3:.5e} != {avg:.5e} = <{eff_1:.5e}, {eff_2:.5e}>')

    assert is_close
#-------------------------------------
def test_pickle(cfl):
    log.visible('Pickle')

    pickle_path = f'efficiency/cutflow/cfl.pickle'
    utnr.dump_pickle(cfl, pickle_path)

    cfl = utnr.load_pickle(pickle_path)
#-------------------------------------
def test_to_json(get_cfl):
    log.visible('JSON')
    cfl = get_cfl(1)

    cfl.to_json('tests/cutflow/test_save/cutflow.json')
#-------------------------------------
def main():
    test_meta()
    test_simple()

    test_avg(get_cfl_dif, 0.1833333333333333, l_ind=[1, 3])
    test_avg(get_cfl_dif, 0.1833333333333333, l_ind=[1, 2])
    test_avg(get_cfl_nwt, 0.1833333333333333)
    test_avg(get_cfl_ywt, 0.5331288178982908)

    test_hash()

    cfl_1 = get_cfl_nwt()
    cfl_2 = get_cfl_ywt()
    cfl_3 = get_cfl_dif()

    test_print(cfl_1)
    test_print(cfl_2)
    test_print(cfl_3)

    test_pickle(cfl_1)
    test_pickle(cfl_2)
    test_pickle(cfl_3)
    #---------------------------
    test_equal(get_cfl_nwt)
    test_equal(get_cfl_ywt)
    test_equal(get_cfl_dif)

    test_add(get_cfl_nwt)
    test_add(get_cfl_ywt)
    test_add(get_cfl_dif)

    test_sum(get_cfl_nwt)
    test_sum(get_cfl_ywt)
    test_sum(get_cfl_dif)

    test_to_json(get_cfl_ywt)
#-------------------------------------
if __name__ == '__main__':
    main()

