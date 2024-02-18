import zfit
import utils_noroot as utnr

from rk.mcstudy      import mcstudy
from rk.const_getter import const_getter as cget

import logging
import math 

log=utnr.getLogger(__name__)
#---------------------------------------------------
class data:
    out_dir = utnr.make_dir_path('tests/mcstudy')
    nevt    = 100000
#---------------------------------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#---------------------------------------------------
def get_model():
    obs   = zfit.Space('x', limits=(-10, 10))
    mu    = zfit.Parameter("mu", 2.4, -1, 5)
    sg    = zfit.Parameter("sg", 1.3,  0, 5)
    gaus  = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)
    nevt  = zfit.Parameter("nevt", data.nevt,  0, 2 * data.nevt)
    pdf   = gaus.create_extended(nevt, 'Gaussian')
                    
    return pdf 
#---------------------------------------------------
def test(ndatasets=None):
    d_opt = {}
    d_opt['initial_spread_factor'] = 4 

    pdf = get_model()

    d_set                          = {}
    d_set['nbins']                 = 300 
    d_set['binning_threshold']     = 30000 
    d_set['initial_spread_factor'] = 1 

    mcst = mcstudy(pdf, d_opt = d_set)
    mcst.plot_dir = f'tests/mcstudy/fits_{ndatasets:06}'
    mcst.run(ndatasets=ndatasets)
    
    d_fit_res = mcst.results()
    utnr.dump_json(d_fit_res, f'{data.out_dir}/nev_{ndatasets:05}/results.json')

    delete_all_pars()
#---------------------------------------------------
def main():
    data.nevt=100
    mcstudy.log.setLevel(logging.DEBUG)
    test(ndatasets=1000)

    return
    mcstudy.log.setLevel(logging.DEBUG)
    data.nevt=10000
    test(ndatasets= 10)

    data.nevt=1000
    mcstudy.log.setLevel(logging.INFO)
    test(ndatasets=100)

#---------------------------------------------------
if __name__ == '__main__':
    main()

