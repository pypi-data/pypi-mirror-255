from rk.cutflow                 import cutflow_manager as ctfm
from rk.efficiency              import efficiency      as eff 
from rk.differential_efficiency import defficiency     as deff
from ndict                      import ndict

import numpy
import utils_noroot as utnr

#--------------------------------------------------
def get_eff(tot=None, pas=None, mu=None, lab=None):
    arr_tot = numpy.random.normal(mu, 0.1, tot * 100)
    arr_pas = numpy.random.choice(arr_tot, pas * 100)

    return eff(arr_pas, arg_tot=arr_tot, cut='na', lab=lab)
#--------------------------------------------------
def get_deff(tot=None, pas=None, lab=None):
    tot    = 100 * tot
    pas    = 100 * pas 

    obj    = deff(lab=lab)
    obj[1] = eff(pas - 30, arg_tot=tot, cut='0 < a < 1', lab='c1')
    obj[2] = eff(      20, arg_tot=tot, cut='1 < a < 2', lab='c2')
    obj[3] = eff(      10, arg_tot=tot, cut='2 < a < 3', lab='c2')

    return obj
#--------------------------------------------------
def get_deff_mat():
    mat               = ndict()
    mat['nom', 'var'] = get_deff(tot= 20, pas=10, lab='nom') 
    mat['al1', 'var'] = get_deff(tot= 20, pas=11, lab='al1') 
    mat['al3', 'var'] = get_deff(tot= 20, pas=12, lab='al3')

    return mat
#--------------------------------------------------
def test_simple():
    mg = ctfm()
    mg['eff_0'] = {'nom' : get_eff(tot=100, pas=50, mu=1.0, lab='nom') }
    mg['eff_1'] = {'nom' : get_eff(tot= 50, pas=30, mu=1.0, lab='nom'), 'al1' : get_eff(tot=50, pas=30, mu=0.9, lab='al1')}
    mg['eff_2'] = {'nom' : get_eff(tot= 30, pas=20, mu=1.0, lab='nom'), 'al1' : get_eff(tot=30, pas=20, mu=0.9, lab='al1'), 'al2' : get_eff(tot=30, pas=20, mu=1.1, lab='al2')}
    mg['eff_3'] = {'nom' : get_eff(tot= 20, pas=10, mu=1.0, lab='nom'), 'al1' : get_eff(tot=20, pas=10, mu=0.9, lab='al1'), 'al3' : get_eff(tot=20, pas=10, mu=0.8, lab='al3')}
    d_cf = mg.get_cf()

    validate(d_cf)
#--------------------------------------------------
def test_deff():
    mg          = ctfm()
    mg['eff_0'] = {'nom' : get_eff (tot=100, pas=50, mu=1.0, lab='nom') }
    mg['eff_1'] = {'nom' : get_eff (tot= 50, pas=30, mu=1.0, lab='nom'), 'al1' : get_eff (tot=50, pas=30, mu=0.9, lab='al1')}
    mg['eff_2'] = {'nom' : get_eff (tot= 30, pas=20, mu=1.0, lab='nom'), 'al1' : get_eff (tot=30, pas=20, mu=0.9, lab='al1'), 'al2' : get_eff (tot=30, pas=20, mu=1.1, lab='al2')}
    mg['eff_3'] = get_deff_mat()

    d_cf        = mg.get_cf()

    validate(d_cf)
#--------------------------------------------------
def validate(d_cf):
    for key, cf in d_cf.items():
        print('-----------------')
        print(key)
        print(cf)
        print('-----------------')
#--------------------------------------------------
def main():
    test_simple()
    test_deff()
#--------------------------------------------------
if __name__ == '__main__':
    main()

