import numpy
import logging
import matplotlib.pyplot as plt

from rk.cutflow_merger    import merger as cfmrg
from rk.efficiency        import efficiency
from rk.efficiency        import cutflow 

import utils_noroot as utnr

#-------------------------------------
class data:
    out_dir = utnr.make_dir_path('tests/cutflow_merger')
#-------------------------------------
def get_input_cf(index, mc_stats):
    numpy.random.seed(index)

    arr_a = numpy.random.normal(1, 0.1, mc_stats)

    arr_b = numpy.random.choice(arr_a , int(mc_stats * 0.8 - index * 0.1 * mc_stats) ) 
    arr_c = numpy.random.choice(arr_b , int(mc_stats * 0.7 - index * 0.1 * mc_stats) )
    arr_d = numpy.random.choice(arr_c , int(mc_stats * 0.6 - index * 0.1 * mc_stats) )
    arr_e = numpy.random.choice(arr_d , int(mc_stats * 0.5 - index * 0.1 * mc_stats) )

    eff_1 = efficiency(arr_b, arg_tot=arr_a, cut='c1')
    eff_2 = efficiency(arr_c, arg_tot=arr_b, cut='c2')
    eff_3 = efficiency(arr_d, arg_tot=arr_c, cut='c3')
    eff_4 = efficiency(arr_e, arg_tot=arr_d, cut='c4')
    
    cfl      = cutflow()
    cfl['a'] = eff_1
    cfl['b'] = eff_2
    cfl['c'] = eff_3
    cfl['d'] = eff_4

    return cfl
#------------------------------------------
def plot_cutflows(file_name, cf_1, cf_2, cf_3):
    df_1 = cf_1.df_eff
    df_2 = cf_2.df_eff
    df_3 = cf_3.df_eff

    ax = df_1.plot(x='Cut', y='Cumulative', label='First')
    ax = df_2.plot(x='Cut', y='Cumulative', label='Second', ax=ax)
    ax = df_3.plot(x='Cut', y='Cumulative', label='Merged', ax=ax)

    plt.savefig(f'{data.out_dir}/{file_name}')
#------------------------------------------
def test_1(lumi_1, lumi_2):
    cf_1 = get_input_cf(1, 100000)
    cf_2 = get_input_cf(2, 200000)

    obj=cfmrg()
    obj.add_input(cf_1, lumi_1)
    obj.add_input(cf_2, lumi_2)
    cf_3=obj.get_cutflow(kind='weighted')

    plot_cutflows('test_1.png', cf_1, cf_2, cf_3)
#------------------------------------------
def test_2(lumi_1, lumi_2):
    cf_1 = get_input_cf(1, 100000)
    cf_2 = get_input_cf(2, 200000)

    obj=cfmrg()
    obj.add_input(cf_1, lumi_1, stats=100000)
    obj.add_input(cf_2, lumi_2, stats=200000)
    cf_3=obj.get_cutflow(kind='weighted')

    plot_cutflows('test_2.png', cf_1, cf_2, cf_3)
#------------------------------------------
if __name__ == '__main__':
    cfmrg.log.setLevel(logging.DEBUG)

    test_1(10.0, 2.0)
    test_2(10.0, 2.0)


