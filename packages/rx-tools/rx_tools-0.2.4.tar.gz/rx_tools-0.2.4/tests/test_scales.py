import math
import utils_noroot as utnr

from rk.scales import fraction as fscale
from rk.scales import plotter  as pscale
from rk.scales import mass     as mscale

from rk.scales import dump_scales as dscale
from rk.scales import load_scales as lscale

import zfit
#---------------------------------------------------------
class data:
    dmu =-1
    ssg = 2 
    frz = 2/3.
    fro = 4/3.

    plot_dir = 'tests/scales'
#---------------------------------------------------------
def get_m(mc=None, dt=None, dmu=None, ssg=None):
    dmu = data.dmu if dmu is None else dmu
    ssg = data.ssg if ssg is None else ssg

    d_par_dt = {'mu' : (11 + dmu, 1) , 'sg' : (1.0 * ssg, 0.1), 'yld_sig' : (dt, 10)}
    d_par_mc = {'mu' : (11      , 1) , 'sg' : (1.0      , 0.1), 'yld_sig' : (mc, 10)}
    
    ms = mscale(dt=d_par_dt, mc=d_par_mc)

    return ms
#---------------------------------------------------------
def test_scale():
    ms     = get_m(mc=1000, dt=1000)
    sv, se = ms.scale
    rv, re = ms.resolution 

    assert(sv == data.dmu)
    assert(rv == data.ssg)

    assert(math.isclose(se**2 , 2    ))
    assert(math.isclose(re**2 , 5/100))
#---------------------------------------------------------
def test_combine():
    ms   = get_m(mc=1000, dt=1000, dmu=+0, ssg=1.00)
    ms_1 = get_m(mc=1000, dt=1000, dmu=+1, ssg=1.05)
    ms_2 = get_m(mc=1000, dt=1000, dmu=-1, ssg=0.95)

    d_data = ms.combine([ms_1, ms_2])

    rv, _, _ = d_data['resolution']
    sv, _, _ = d_data['scale']

    assert(math.isclose(rv, 1, rel_tol=0.01))
    assert(math.isclose(sv, 0, abs_tol=10e-7))
#---------------------------------------------------------
def test_fraction():
    msz  = get_m(mc=1000, dt=1000)
    mso  = get_m(mc=1000, dt=2000)

    fr   = fscale({'z' : msz, 'o' : mso})
    d_fr = fr.scales

    val_z, err_z = d_fr['z']
    val_o, err_o = d_fr['o']

    assert( math.isclose(val_z, data.frz) )
    assert( math.isclose(val_o, data.fro) )

    err_z_cal = 0.006849340453819655
    err_o_cal = 0.010657385747189912

    assert( math.isclose(err_z, err_z_cal, rel_tol=1e-5) )
    assert( math.isclose(err_o, err_o_cal, rel_tol=1e-5) )
#---------------------------------------------------------
def test_plotter():
    msz  = get_m(mc=1000, dt=1000)
    mso  = get_m(mc=1000, dt=2000)

    psc  = pscale(dmu=data.dmu, ssg=data.ssg, dfr={'z' : data.frz, 'o' : data.fro})
    psc.scales = {'z' : msz, 'o' : mso} 
    psc.save_to(f'{data.plot_dir}/plotter')
#---------------------------------------------------------
def test_dumper():
    msz  = get_m(mc=1000, dt=1000)
    mso  = get_m(mc=1000, dt=2000)

    dscale({'z' : msz, 'o' : mso}, f'{data.plot_dir}/dumper/test.json')
#---------------------------------------------------------
def test_loader():
    msz  = get_m(mc=1000, dt=1000)
    mso  = get_m(mc=1000, dt=2000)
    mst  = get_m(mc=1000, dt=3000)

    dscale({'z' : msz, 'o' : mso, 't' : mst}, f'{data.plot_dir}/loader/2018_ETOS.json')

    dmu = zfit.param.Parameter('dmu', 0, -20, 20)
    ssg = zfit.param.Parameter('ssg', 1,   0,  2)
    brf = zfit.param.Parameter('brf', 1,   0,  2)

    lsc               = lscale(trig='ETOS', dset='2018', brem='z') 
    lsc.scale_dir     = f'{data.plot_dir}/loader'
    lsc['scale']      = dmu
    lsc['resolution'] = ssg
    lsc['brem_frac']  = brf

    d_const = lsc.get_constraints()

    check_const(d_const['scl'], mu=-1.0, sg=1.4142135623730947)
    check_const(d_const['res'], mu=+2.0, sg=0.2236067977499791)
    check_const(d_const['frc'], mu=+0.5, sg=0.0059511903571189)
#---------------------------------------------------------
def check_const(const, mu, sg):
    val = const.observation[0]
    cov = const.covariance.numpy()[0][0]
    err = math.sqrt(cov)

    pass_mu = math.isclose(val, mu, rel_tol=1e-5)
    pass_sg = math.isclose(err, sg, rel_tol=1e-5)

    assert(pass_mu)
    assert(pass_sg)
#---------------------------------------------------------
def main():
    test_combine()
    return
    test_loader()
    test_dumper()
    test_scale()
    test_plotter()
    test_fraction()
#---------------------------------------------------------
if __name__ == '__main__':
    main()

