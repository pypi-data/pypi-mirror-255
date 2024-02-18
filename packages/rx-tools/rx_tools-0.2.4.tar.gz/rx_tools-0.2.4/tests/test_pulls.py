import utils_noroot as utnr

from rk.pulls import pulls  as rkpul
from logzero  import logger as log

import zfit 

#--------------------------------------------
def delete_all_pars():
    d_par = zfit.Parameter._existing_params
    l_key = list(d_par.keys())

    for key in l_key:
        del(d_par[key])
#--------------------------------------------
def get_model():
    obs   = zfit.Space('x', limits=(-10, 10))
    mu    = zfit.Parameter("mu", 2.4, -1, 5)
    sg    = zfit.Parameter("sg", 1.3,  0, 5)
    gauss = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)
    nev   = zfit.Parameter("nev", 200,  0, 100000)
    pdf   = gauss.create_extended(nev)
    
    return pdf 
#--------------------------------------------
def test_simple():
    pdf    = get_model()
    spread = 0.01
    seed   = 0
    sp_suf = f'{spread:.3f}'.replace('.', 'p')
    sd_suf = f'{seed:03.0f}' if seed is not None else 'none'

    plot_dir = utnr.make_dir_path(f'tests/pulls/{sp_suf}_{sd_suf}')
    
    d_set = {}
    d_set['ntoy']    = 1000
    d_set['spread' ] = spread 

    pl=rkpul(pdf, d_set)
    pl.plot_dir = f'{plot_dir}/fits'
    d_res = pl.run()

    plot_path = f'{plot_dir}/pars.json'

    log.visible(f'Saving to: {plot_path}')
    utnr.dump_json(d_res, plot_path)

    delete_all_pars()
#--------------------------------------------
def main():
    test_simple()
#--------------------------------------------
if __name__ == '__main__':
    main()
