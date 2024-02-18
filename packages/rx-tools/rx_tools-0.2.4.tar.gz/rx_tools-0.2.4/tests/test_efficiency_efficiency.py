from rk.efficiency import efficiency
from rk.efficiency import InconsistentEff 

import utils_noroot as utnr
import numpy
import math
import logging

#------------------------------------
class data:
    log=utnr.getLogger(__name__)

    efficiency.log.setLevel(logging.DEBUG)
#------------------------------------
def is_equal(val_1, val_2):
    return math.isclose(val_1, val_2, rel_tol=1e-5)
#------------------------------------
def test_copy():
    eff_1 = efficiency(10, arg_fal=10, cut='cut_1', lab='lab_1')
    eff_5 = efficiency(11, arg_fal=10, cut='cut_1', lab='lab_1')
    eff_6 = efficiency(10, arg_fal=11, cut='cut_1', lab='lab_1')

    eff_2 = eff_1.copy()
    eff_3 = eff_1.copy(label='lab_3')
    eff_4 = eff_1.copy(cut  ='cut_4')

    assert(eff_1 == eff_2)
    assert(eff_1 == eff_3)

    assert(eff_1 != eff_4)
    assert(eff_1 != eff_5)
    assert(eff_1 != eff_6)
#------------------------------------
def test_equal(eff_0, eff_1, eff_2, eff_3):
    assert(eff_0 == eff_1)
    assert(eff_1 != eff_2)
    assert(eff_1 != eff_3)
#------------------------------------
def test_mult(eff_1, eff_2, eff_3):
    eff_r = eff_1 * eff_2

    assert(eff_r == eff_3)
#------------------------------------
def test_mult_fail(eff_1, obj):
    try:
        val = eff_1 * obj 
    except TypeError:
        data.log.visible('Pass mult fail')
        return

    data.log.error(f'Product returned: {val}')
    raise
#------------------------------------
def test_add(eff_1, eff_2):
    eff_3 = eff_1 + eff_2

    data.log.visible('Pass add')
#------------------------------------
def test_average_1(eff):
    r_eff = eff.val[0]

    eff_3 = efficiency.average({eff : 1, eff : 1})
    i_eff, i_eup, i_edn = eff_3.val

    eff_3 = efficiency.average({eff : 2, eff : 3})
    f_eff, f_eup, f_edn = eff_3.val

    if not is_equal(r_eff, i_eff):
        log.error(f'Efficiencies differ: {r_eff:.3f} -> {i_eff:.3f}')
        raise

    if not is_equal(r_eff, f_eff):
        log.error(f'Efficiencies differ: {r_eff:.3f} -> {f_eff:.3f}')
        raise
#------------------------------------
def test_average_2(eff_1, eff_2):
    r_eff_1 = eff_1.val[0]
    r_eff_2 = eff_2.val[0]
    r_eff_a = 0.5 * (r_eff_1 + r_eff_2)

    eff_3 = efficiency.average({eff_1 : 1, eff_2 : 1})
    a_eff_a = eff_3.val[0]

    if not is_equal(r_eff_a, a_eff_a):
        data.log.error(f'Efficiencies differ: {r_eff_a:.3f} -> {a_eff_a:.3f}')
        raise
    else:
        data.log.info(f'Efficiencies are equal: {r_eff_a:.3f} -> {a_eff_a:.3f}')
#------------------------------------
def test_no_wgt():
    eff_u  = efficiency(12, arg_fal= 8, cut='cut_1')
    eff_0  = efficiency(10, arg_fal=10, cut='cut_1')
    eff_1  = efficiency(10, arg_fal=10, cut='cut_1')
    eff_2  = efficiency(10, arg_fal=10, cut='cut_2')
    eff_3  = efficiency( 5, arg_fal= 5, cut='cut_3')

    eff_12 = efficiency(10, arg_fal=20, cut='(cut_1) && (cut_2)')
    eff_23 = efficiency( 5, arg_fal=15, cut='(cut_2) && (cut_3)')

    test_mult(eff_2, eff_3, eff_23)
    test_mult_fail(eff_1,   0)
    test_mult_fail(eff_1, 'x')
    test_mult_fail(eff_1,  [])
    test_equal(eff_0, eff_1, eff_2, eff_3)
    test_add(eff_0, eff_1)
    test_average_1(eff_0)
    test_average_2(eff_0, eff_u)

    try:
        test_mult(eff_1, eff_2, eff_12)
    except InconsistentEff:
        data.log.visible('Pass inconsistency')
        return

    data.log.error('Inconsistent efficiencies were not caught')
    raise
#------------------------------------
def test_wgt():
    arr_h = numpy.array([1.4, 1.4, 1.4])
    arr_i = numpy.array([0.6, 0.6, 0.6])

    arr_p = numpy.array([1.1, 1.1, 1.1])
    arr_f = numpy.array([0.9, 0.9, 0.9])

    arr_r = numpy.array([1.1, 1.1])
    arr_t = numpy.array([1.1])

    eff_u  = efficiency(arr_h, arg_fal=arr_i, cut='cut_1')
    eff_0  = efficiency(arr_p, arg_fal=arr_f, cut='cut_1')
    eff_1  = efficiency(arr_p, arg_fal=arr_f, cut='cut_1')
    eff_2  = efficiency(arr_p, arg_fal=arr_f, cut='cut_2')
    eff_3  = efficiency(arr_r, arg_fal=arr_t, cut='cut_3')

    eff_12 = efficiency(arr_p, arg_fal=numpy.concatenate((arr_f , arr_f)), cut='(cut_1) && (cut_2)')
    eff_23 = efficiency(arr_r, arg_fal=numpy.concatenate((arr_f , arr_t)), cut='(cut_2) && (cut_3)')

    test_mult(eff_2, eff_3, eff_23)
    test_equal(eff_0, eff_1, eff_2, eff_3)
    test_add(eff_0, eff_1)
    test_average_1(eff_0)
    test_average_2(eff_0, eff_u)

    try:
        test_mult(eff_1, eff_2, eff_12)
    except InconsistentEff:
        data.log.visible('Pass inconsistency')
        return

    data.log.error('Inconsistent efficiencies were not caught')
    raise
#------------------------------------
def test_tup():
    arr_p = numpy.array([1.1, 1.1, 1.1])
    arr_f = numpy.array([0.9, 0.9, 0.9])

    arr_r = numpy.array([1.1, 1.1])
    arr_t = numpy.array([1.1])

    eff_u  = efficiency((4.3, 3), arg_fal=(1.7, 3), cut='cut_1')
    eff_0  = efficiency((3.3, 3), arg_fal=(2.7, 3), cut='cut_1')
    eff_1  = efficiency((3.3, 3), arg_fal=(2.7, 3), cut='cut_1')
    eff_2  = efficiency((3.3, 3), arg_fal=(2.7, 3), cut='cut_2')
    eff_3  = efficiency((2.2, 2), arg_fal=(1.1, 1), cut='cut_3')

    eff_12 = efficiency(arr_p, arg_fal=numpy.concatenate((arr_f , arr_f)), cut='(cut_1) && (cut_2)')
    eff_23 = efficiency(arr_r, arg_fal=numpy.concatenate((arr_f , arr_t)), cut='(cut_2) && (cut_3)')

    test_equal(eff_0, eff_1, eff_2, eff_3)
    test_mult(eff_2, eff_3, eff_23)
    test_add(eff_0, eff_1)
    test_average_1(eff_0)
    test_average_2(eff_0, eff_u)

    try:
        test_mult(eff_1, eff_2, eff_12)
    except InconsistentEff:
        data.log.visible('Pass inconsistency')
        return

    data.log.error('Inconsistent efficiencies were not caught')
    raise
#------------------------------------
def main():
    test_copy()
    test_no_wgt()
    test_wgt()
    test_tup()
#------------------------------------
if __name__ == '__main__':
    main()

