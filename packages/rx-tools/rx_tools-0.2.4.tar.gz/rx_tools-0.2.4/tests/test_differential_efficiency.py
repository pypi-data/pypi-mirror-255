from rk.differential_efficiency import defficiency as deff
from rk.efficiency              import efficiency

import utils_noroot      as utnr
import matplotlib.pyplot as plt
import pprint

from math import inf

#-----------------------------------    
class data:
    plt_dir = utnr.make_dir_path(f'tests/differential_efficiency')
#-----------------------------------    
def test_copy():
    eff_0       = deff(lab='syst', varname='x')
    eff_0[0, 1] = efficiency(5, arg_tot=20, cut='0 < a < 1', lab='c1')
    eff_0[1, 2] = efficiency(3, arg_tot=20, cut='1 < a < 2', lab='c2')
    eff_0[2, 3] = efficiency(1, arg_tot=20, cut='2 < a < 3', lab='c2')

    eff_2       = deff(lab='syst', varname='y')
    eff_2[0, 1] = efficiency(5, arg_tot=20, cut='0 < a < 1', lab='c1')
    eff_2[1, 2] = efficiency(3, arg_tot=20, cut='1 < a < 2', lab='c2')
    eff_2[2, 3] = efficiency(1, arg_tot=20, cut='2 < a < 3', lab='c2')

    eff_3       = deff(lab='syst', varname='x')
    eff_3[0, 1] = efficiency(3, arg_tot=20, cut='0 < a < 1', lab='c1')
    eff_3[1, 2] = efficiency(3, arg_tot=20, cut='1 < a < 2', lab='c2')
    eff_3[2, 3] = efficiency(1, arg_tot=20, cut='2 < a < 3', lab='c2')

    eff_1     = eff_0.copy(label='copy')

    assert(eff_0 == eff_1)
    assert(eff_0 != eff_2)
    assert(eff_0 != eff_3)
#-----------------------------------    
def test_min_max():
    eff       = deff(varname='x')
    eff[0, 1] = efficiency(5, arg_tot=20, cut='0 < a < 1', lab='c1')
    eff[1, 2] = efficiency(3, arg_tot=20, cut='1 < a < 2', lab='c2')
    eff[2, 3] = efficiency(1, arg_tot=20, cut='2 < a < 3', lab='c2')

    assert(eff.max == 0.25)
    assert(eff.min == 0.05)
#-----------------------------------    
def test_initialize():
    obj    = deff(varname='x')
    obj[0, 1] = efficiency(5, 20, cut='0 < a < 1', lab='c1')
    obj[1, 2] = efficiency(5, 20, cut='1 < a < 2', lab='c2')
    obj[2, 3] = efficiency(5, 20, cut='2 < a < 3', lab='c2')

    print(obj)
    print(obj.efficiency())
#-----------------------------------    
def test_multiply():
    eff_sel       = deff(varname='x')
    eff_sel[0, 1] = efficiency(5, 20, cut='0 < a < 1', lab='c1')
    eff_sel[1, 2] = efficiency(5, 20, cut='1 < a < 2', lab='c2')
    eff_sel[2, 3] = efficiency(5, 20, cut='2 < a < 3', lab='c2')

    eff_reco = efficiency(25, 25, cut='reco == 1', lab='rec')

    eff_tot  = eff_reco * eff_sel

    print(eff_tot)
    print(eff_tot.efficiency())
#-----------------------------------    
def test_add():
    eff_sel_1       = deff(varname='x')
    eff_sel_1[0, 1] = efficiency( 5, 20, cut='0 < a < 1', lab='c1')
    eff_sel_1[1, 2] = efficiency( 5, 20, cut='1 < a < 2', lab='c2')
    eff_sel_1[2, 3] = efficiency( 5, 20, cut='2 < a < 3', lab='c2')

    eff_sel_2       = deff(varname='x')
    eff_sel_2[0, 1] = efficiency(15, 30, cut='0 < a < 1', lab='c1')
    eff_sel_2[1, 2] = efficiency(10, 35, cut='1 < a < 2', lab='c2')
    eff_sel_2[2, 3] = efficiency(15, 30, cut='2 < a < 3', lab='c2')

    eff_sel_3       = eff_sel_1 + eff_sel_2

    print(eff_sel_1)
    print(eff_sel_2)
    print(eff_sel_3)
#-----------------------------------    
def test_plot():
    eff_sel_1    = deff(lab='eff 1', varname='$p_T$')
    eff_sel_1[0, 1] = efficiency( 5, 20, cut='0 < a < 1', lab='c1')
    eff_sel_1[1, 2] = efficiency( 5, 20, cut='1 < a < 2', lab='c2')
    eff_sel_1[2, 3] = efficiency( 5, 20, cut='2 < a < 3', lab='c2')

    eff_sel_2    = deff(lab='eff 2', varname='$p_T$')
    eff_sel_2[0, 1] = efficiency(15, 30, cut='0 < a < 1', lab='c1')
    eff_sel_2[1, 2] = efficiency(10, 35, cut='1 < a < 2', lab='c2')
    eff_sel_2[2, 3] = efficiency(15, 30, cut='2 < a < 3', lab='c2')

    eff_sel_1.plot()
    eff_sel_2.plot()

    plt_path = f'{data.plt_dir}/plot.png'
    plt.legend()
    plt.gca().set_ylim(0, 1)
    plt.savefig(plt_path)
#-----------------------------------    
def test_dict():
    eff_sel       = deff(lab='deff', varname='$p_T$')
    eff_sel[ 4.4,+inf] = efficiency( 1, 24, cut='   4 < a < +inf', lab='c5')
    eff_sel[ 3.3, 4.4] = efficiency( 0, 25, cut='   3 < a <    4', lab='c4')
    eff_sel[ 1.1, 2.2] = efficiency( 3, 22, cut='   1 < a <    2', lab='c2')
    eff_sel[ 0.0, 1.1] = efficiency( 5, 20, cut='   0 < a <    1', lab='c1')
    eff_sel[ 2.2, 3.3] = efficiency( 1, 24, cut='   2 < a <    3', lab='c3')
    eff_sel[-inf, 0.0] = efficiency( 2, 23, cut='-inf < a <    0', lab='c0')

    d_data = eff_sel.to_dict()

    pprint.pprint(eff_sel.data, sort_dicts=False)
    print(eff_sel)
#-----------------------------------    
def test_avg():
    eff_1            = deff(lab='deff', varname='$p_T$')
    #eff_1[ 4.4,+inf] = efficiency( 1, 24, cut='   4 < a < +inf', lab='c5')
    eff_1[ 3.3, 4.4] = efficiency( 0, 25, cut='   3 < a <    4', lab='c4')
    eff_1[ 1.1, 2.2] = efficiency( 3, 22, cut='   1 < a <    2', lab='c2')
    eff_1[ 0.0, 1.1] = efficiency( 5, 20, cut='   0 < a <    1', lab='c1')
    eff_1[ 2.2, 3.3] = efficiency( 1, 24, cut='   2 < a <    3', lab='c3')
    eff_1[-inf, 0.0] = efficiency( 2, 23, cut='-inf < a <    0', lab='c0')

    eff_2            = deff(lab='deff', varname='$p_T$')
    eff_2[ 4.4,+inf] = efficiency( 1, 25, cut='   4 < a < +inf', lab='c5')
    eff_2[ 3.3, 4.4] = efficiency( 0, 26, cut='   3 < a <    4', lab='c4')
    eff_2[ 1.1, 2.2] = efficiency( 3, 23, cut='   1 < a <    2', lab='c2')
    eff_2[ 0.0, 1.1] = efficiency( 5, 21, cut='   0 < a <    1', lab='c1')
    eff_2[ 2.2, 3.3] = efficiency( 1, 25, cut='   2 < a <    3', lab='c3')
    #eff_2[-inf, 0.0] = efficiency( 2, 24, cut='-inf < a <    0', lab='c0')

    eff_3 = deff.average({eff_1 : 1.2, eff_2 : 1.3}) 
#-----------------------------------    
def test_add_missing():
    eff_sel_1       = deff(varname='x')
    #eff_sel_1[1] = efficiency( 5, 20, cut='0 < a < 1', lab='c1')
    eff_sel_1[1, 2] = efficiency( 5, 20, cut='1 < a < 2', lab='c2')
    eff_sel_1[2, 3] = efficiency( 5, 20, cut='2 < a < 3', lab='c2')

    eff_sel_2       = deff(varname='x')
    eff_sel_2[0, 1] = efficiency(15, 30, cut='0 < a < 1', lab='c1')
    eff_sel_2[1, 2] = efficiency(10, 35, cut='1 < a < 2', lab='c2')
    #eff_sel_2[3] = efficiency(15, 30, cut='2 < a < 3', lab='c2')

    eff_sel_3    = eff_sel_1 + eff_sel_2

    print(eff_sel_1)
    print(eff_sel_2)
    print(eff_sel_3)
#-----------------------------------    
def main():
    test_avg()
    test_dict()
    test_copy()
    test_min_max()
    test_plot()
    test_initialize()
    test_multiply()
    test_add()
    test_add_missing()
#-----------------------------------    
if __name__ == '__main__':
    main()

