from rk.differential_yield      import dyield
from rk.efficiency              import efficiency
from rk.differential_efficiency import defficiency as deff

from ndict import ndict

import numpy

#-------------------------------------
def test_print():
    d_data = ndict()
    d_data[1, 2] = 2
    d_data[2, 3] = 4
    d_data[3, 4] = 5
    
    dy=dyield(d_data, varname='B_PT')
    
    print(dy)
#-------------------------------------
def test_div_by_arr():
    d_data = ndict()
    d_data[1, 2] = numpy.array([1] * 2) 
    d_data[2, 3] = numpy.array([1] * 3)
    d_data[3, 4] = numpy.array([1] * 4)
    
    dy_1=dyield(d_data, varname='B_PT')

    deff= dy_1 / numpy.array([1] * 12)

    eff_1, _, _ = deff[1, 2].val
    eff_2, _, _ = deff[2, 3].val
    eff_3, _, _ = deff[3, 4].val

    assert eff_1 == 2. / 12
    assert eff_2 == 3. / 12
    assert eff_3 == 4. / 12
#-------------------------------------
def test_div_by_deff():
    d_data = ndict()
    d_data[1, 2] = numpy.array([1] * 2) 
    d_data[2, 3] = numpy.array([1] * 3)
    d_data[3, 4] = numpy.array([1] * 4)
    dyl=dyield(d_data, varname='B_PT')

    eff= deff(lab='test', varname='B_PT')
    eff[1, 2] = efficiency(1, arg_tot=20, cut='0 < a < 1', lab='c1')
    eff[2, 3] = efficiency(1, arg_tot=20, cut='1 < a < 2', lab='c2')
    eff[3, 4] = efficiency(1, arg_tot=20, cut='2 < a < 3', lab='c2')

    dyl = dyl / eff

    assert dyl[1, 2] == 40
    assert dyl[2, 3] == 60
    assert dyl[3, 4] == 80
#-------------------------------------
def main():
    test_div_by_deff()
    test_div_by_arr()
    test_print()
#-------------------------------------
if __name__ == '__main__':
    main()

