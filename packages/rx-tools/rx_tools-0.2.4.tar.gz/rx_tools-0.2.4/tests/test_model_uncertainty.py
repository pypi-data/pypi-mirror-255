import zfit
import math

import utils_noroot      as utnr
import matplotlib.pyplot as plt

from rk.model_uncertainty import calculator as ucal

#------------------------
class data:
    plot_dir = utnr.make_dir_path('tests/model_uncertainty')
    obs      = zfit.Space('mass', limits=(2450, 3600))

    zfit.settings.changed_warnings.all = False
#------------------------
def get_2cb():
    mu  = zfit.Parameter('mu', 3000,  2990, 3010)
    sg  = zfit.Parameter('sg',   40,    30,   50)

    al  = zfit.Parameter('al', 1, 0.1,  5.0)
    ar  = zfit.Parameter('ar',-1,-5.0, -0.1)

    nl  = zfit.Parameter('nl', 1, 0.1,  8.0)
    nr  = zfit.Parameter('nr', 1, 0.1, 10.0)

    fr  = zfit.Parameter('fr', 1, 0.0,  1.0)

    pdf_1 = zfit.pdf.CrystalBall(obs=data.obs, mu=mu, sigma=sg, alpha=al, n=nl)
    pdf_2 = zfit.pdf.CrystalBall(obs=data.obs, mu=mu, sigma=sg, alpha=ar, n=nr)

    pdf   = zfit.pdf.SumPDF([pdf_1, pdf_2], fr)

    nev   = zfit.Parameter('n_sig', 30000, 0,  100000)
    sig   = pdf.create_extended(nev) 

    return sig
#------------------------
def get_dscb():
    mu  = zfit.Parameter('mu', 3000,  2990, 3010)
    sg  = zfit.Parameter('sg',   40,    30,   50)

    al  = zfit.Parameter('al', 0.6, 0.1,  5.0)
    ar  = zfit.Parameter('ar',-0.2,-5.0, -0.1)

    nl  = zfit.Parameter('nl', 5.0, 0.1,  8.0)
    nr  = zfit.Parameter('nr', 2.0, 0.1, 10.0)

    pdf = zfit.pdf.DoubleCB(obs=data.obs, mu=mu, sigma=sg, alphal=al, nl=nl, alphar=ar, nr=nr)

    nev = zfit.Parameter('n_sig', 30000, 0,  100000)
    sig = pdf.create_extended(nev) 

    #nl.floating = False 
    nr.floating = False 

    #al.floating = False 
    ar.floating = False 

    return sig
#------------------------
def get_gaus():
    mu  = zfit.Parameter('mu', 3000,  2990, 3010)
    sg  = zfit.Parameter('sg',   40,    30,   50)

    pdf = zfit.pdf.Gauss(obs=data.obs, mu=mu, sigma=sg)
    nev = zfit.Parameter('n_sig', 30000, 0,  100000)
    sig = pdf.create_extended(nev) 

    return sig
#------------------------
def get_background():
    lam = zfit.Parameter('lam', -0.005, -0.01, 0.0)
    bkg = zfit.pdf.Exponential(lam=lam, obs=data.obs, name='')
    nbk = zfit.Parameter('n_bkg', 20000, 0.0, 200000)
    bkg = bkg.create_extended(nbk)

    return bkg
#------------------------
def get_model():
    sig = get_dscb()
    bkg = get_background()

    mod = zfit.pdf.SumPDF([sig, bkg])

    return mod 
#------------------------
def test_simple():
    pdf = get_model()

    obj = ucal(pdf, poi_name='n_sig')
    obj.plot_dir = utnr.make_dir_path(f'{data.plot_dir}/simple')
    df  = obj.get_df()
#------------------------
def test_constrain():
    pdf = get_model()

    obj          = ucal(pdf, poi_name='n_sig')
    obj.plot_dir = utnr.make_dir_path(f'{data.plot_dir}/constraint')
    obj['mu']    = 0.1
    obj['sg']    = 0.1
    obj['nl']    = math.inf 
    obj['al']    = 0.0
    df           = obj.get_df()
#------------------------
def main():
    test_simple()
    test_constrain()
#------------------------
if __name__ == '__main__':
    main()

