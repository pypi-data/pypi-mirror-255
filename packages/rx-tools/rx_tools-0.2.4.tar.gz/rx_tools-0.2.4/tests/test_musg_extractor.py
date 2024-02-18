import utils_noroot as utnr
import numpy
import zfit
import math

from logzero           import logger      as log
from rk.musg_extractor import extractor   as ext
from rk.scales         import fraction    as fscale
from rk.scales         import plotter     as pscale
from rk.scales         import dump_scales as dscale

#---------------------------------------
class data:
    zfit.settings.changed_warnings.all = False

    plot_dir  = 'tests/musg_extractor'

    mu_mc     = 50
    sg_mc     =  5

    obs       = zfit.Space('mass', limits=(0, 100))
    mu        = zfit.Parameter("mu", mu_mc, 40, 60)
    sg        = zfit.Parameter("sg", sg_mc, 2, 10)
    fr        = zfit.Parameter("fr", 0.5, 0, 1)
    az        = zfit.Parameter('az', 1, 0.1,  5.0)
    ao        = zfit.Parameter('ao', 2, 0.1,  5.0)
    nz        = zfit.Parameter('nz', 1, 0.1,  8.0)
    no        = zfit.Parameter('no', 2, 0.1,  5.0)

    nsig      = zfit.Parameter("yld_sig", 1000, 0, 1e5)
    nbkg      = zfit.Parameter("yld_bkg", 1000, 0, 1e5)

    dmu       = -10
    ssg       = 1.05

    dfz       = 0.6
    mfz       = 0.5

    d_pdf_sig = None
    d_pdf_bkg = None
    d_pdf_ful = None
#---------------------------------------
def get_signal(dmu=None, ssg=None):
    data.mu.set_value(data.mu_mc + dmu)
    data.sg.set_value(data.sg_mc * ssg)

    if data.d_pdf_sig is not None:
        return data.d_pdf_sig

    pdf_z = zfit.pdf.CrystalBall(obs=data.obs, mu=data.mu, sigma=data.sg, alpha=data.az, n=data.nz, name='Signal_z')
    pdf_o = zfit.pdf.CrystalBall(obs=data.obs, mu=data.mu, sigma=data.sg, alpha=data.ao, n=data.no, name='Signal_o')

    data.d_pdf_sig = {'z' : pdf_z, 'o' : pdf_o}

    return data.d_pdf_sig 
#---------------------------------------
def get_background():
    if data.d_pdf_bkg is not None:
        return data.d_pdf_bkg

    lamz= zfit.Parameter('lamz', -0.001, -0.1, 0.0)
    pdfz= zfit.pdf.Exponential(lam=lamz, obs=data.obs, name='Background_z')

    lamo= zfit.Parameter('lamo', -0.001, -0.1, 0.0)
    pdfo= zfit.pdf.Exponential(lam=lamo, obs=data.obs, name='Background_o')

    data.d_pdf_bkg = {'z' : pdfz, 'o' : pdfo}

    return data.d_pdf_bkg 
#---------------------------------------
def get_model(dmu=None, ssg=None):
    if data.d_pdf_ful is not None:
        return data.d_pdf_ful

    d_pdf_sig     = get_signal(dmu=dmu, ssg=ssg)
    pdf_sig_ext_z = d_pdf_sig['z'].create_extended(data.nsig)
    pdf_sig_ext_o = d_pdf_sig['o'].create_extended(data.nsig)

    d_pdf_bkg     = get_background()
    pdf_bkg_ext_z = d_pdf_bkg['z'].create_extended(data.nbkg)
    pdf_bkg_ext_o = d_pdf_bkg['o'].create_extended(data.nbkg)

    pdf_z         = zfit.pdf.SumPDF([pdf_sig_ext_z, pdf_bkg_ext_z])
    pdf_o         = zfit.pdf.SumPDF([pdf_sig_ext_o, pdf_bkg_ext_o])

    data.d_pdf_ful= {'z' : pdf_z, 'o' : pdf_o}

    return data.d_pdf_ful 
#---------------------------------------
def get_arrays(pdf_z, pdf_o, nentries, dfr):
    nentries_z = math.floor(dfr * nentries)
    nentries_o = nentries - nentries_z

    smp_z = pdf_z.create_sampler(n=nentries_z)
    smp_o = pdf_o.create_sampler(n=nentries_o)

    arr_sig_z = smp_z.numpy().flatten()
    arr_sig_o = smp_o.numpy().flatten()

    return arr_sig_z, arr_sig_o
#---------------------------------------
def get_data_arr(dmu=None, ssg=None, nentries=None, dfr=None, is_mc=None):
    d_sig_pdf = get_signal(dmu=dmu, ssg=ssg)
    arr_sig_z, arr_sig_o = get_arrays(d_sig_pdf['z'], d_sig_pdf['o'], nentries, dfr)

    if is_mc:
        return arr_sig_z, arr_sig_o

    d_bkg_pdf            = get_background()
    arr_bkg_z, arr_bkg_o = get_arrays(d_bkg_pdf['z'], d_bkg_pdf['o'], nentries, dfr)

    arr_z = numpy.concatenate([arr_sig_z, arr_bkg_z])
    arr_o = numpy.concatenate([arr_sig_o, arr_bkg_o])

    return arr_z, arr_o
#---------------------------------------
def get_data(nentries=100000):
    arr_mc_mass_z, arr_mc_mass_o = get_data_arr(dmu=       0, ssg=    1.00, dfr=data.mfz, nentries=nentries, is_mc=True )
    arr_dt_mass_z, arr_dt_mass_o = get_data_arr(dmu=data.dmu, ssg=data.ssg, dfr=data.dfz, nentries=nentries, is_mc=False)

    d_mc_mass = {}
    d_mc_mass['z'] = arr_mc_mass_z
    d_mc_mass['o'] = arr_mc_mass_o

    d_dt_mass = {}
    d_dt_mass['z'] = arr_dt_mass_z
    d_dt_mass['o'] = arr_dt_mass_o

    return d_mc_mass, d_dt_mass
#---------------------------------------
def test_simple():
    d_mc_mass, d_dt_mass = get_data()
    d_md_pdf             = get_model(dmu=0, ssg=1)

    d_scale = {}
    for cat in ['z', 'o']:
        arr_mc       = d_mc_mass[cat] 
        arr_dt       = d_dt_mass[cat] 

        obj          = ext(mc=arr_mc, dt=arr_dt)
        obj.plot_dir = f'{data.plot_dir}/simple/cat_{cat}'
        obj.model    = d_md_pdf[cat]
        scl          = obj.get_scales()
        sc_v, sc_e   = scl.scale
        rs_v, rs_e   = scl.resolution
        
        d_scale[cat] = scl

    fr   = fscale(d_scale)
    d_fr = fr.scales

    fz   = (    data.dfz) / (    data.mfz)
    fo   = (1 - data.dfz) / (1 - data.mfz)

    psc  = pscale(dmu=data.dmu, ssg=data.ssg, dfr={'z' : fz, 'o' : fo} )
    psc.scales = d_scale
    psc.save_to(f'{data.plot_dir}/simple')
#---------------------------------------
def test_json():
    d_mc_mass, d_dt_mass = get_data()
    d_md_pdf             = get_model(dmu=0, ssg=1)

    d_scale = {}
    for cat in ['z', 'o']:
        arr_mc       = d_mc_mass[cat] 
        arr_dt       = d_dt_mass[cat] 

        obj          = ext(mc=arr_mc, dt=arr_dt)
        obj.cache_dir= f'{data.plot_dir}/pars/cat_{cat}'
        obj.plot_dir = f'{data.plot_dir}/json/cat_{cat}'
        obj.model    = d_md_pdf[cat]
        d_scale[cat] = obj.get_scales()

    dscale(d_scale, f'{data.plot_dir}/json/scales.json')
#---------------------------------------
def main():
    test_json()
    test_simple()
#---------------------------------------
if __name__ == '__main__':
    main()

