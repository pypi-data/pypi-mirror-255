from rk.fithst import extractor as ext 

import zfit
import ROOT 
import os
import numpy 
import utils_noroot as utnr

#-----------------------------------------------------------
class data:
    log     = utnr.getLogger(__name__)
    dat_dir = utnr.make_dir_path(f'{os.getcwd()}/tests/extractor/simple/data')
    fit_dir = utnr.make_dir_path(f'tests/extractor/simple/output')

    nentries_s = 100000
    nentries_b1= 200000
    nentries_b2=  25000

    dat_ver = 'v0'
#-----------------------------------------------------------
def get_pdfs():
    obs = zfit.Space('m', limits=(0, 10))

    mu  = zfit.Parameter('mu', 5.3,  4.5, 5.5)
    sg  = zfit.Parameter('sg', 1.3,  0.2, 1.5)
    ap  = zfit.Parameter('ap', 1.0,  0.1, 5.0)
    pw  = zfit.Parameter('pw', 1.0,  0.1, 5.0)
    sig = zfit.pdf.CrystalBall(obs=obs, mu=mu, sigma=sg, alpha=ap, n=pw)

    mu_p= zfit.Parameter('mu_pr', 0.1,  -1, 1)
    sg_p= zfit.Parameter('sg_pr', 1.0,  0.2, 1.5)
    prc = zfit.pdf.Gauss(obs=obs, mu=mu_p, sigma=sg_p)
    
    lam = zfit.Parameter('lam', -1.2,  -2.3, -0.01)
    exp = zfit.pdf.Exponential(obs=obs, lam=lam)
    
    nsg = zfit.Parameter(f'nsg', 100, 0.1, 200000)
    nex = zfit.Parameter(f'nex', 100, 0.1, 200000)
    npr = zfit.Parameter(f'npr', 100, 0.1, 200000)
    
    sig = sig.create_extended(nsg)
    prc = prc.create_extended(npr)
    exp = exp.create_extended(nex)
    
    return [sig, prc, exp]
#-----------------------------------------------------------
def get_binning():
    d_bin                                 = {}
    d_bin['TMath::Log(B_IPCHI2_OWNPV)']   = [-2, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0] 
    d_bin['TMath::Log(B_ENDVERTEX_CHI2)'] = [-2, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0] 
    d_bin['TMath::ACos(B_DIRA_OWNPV)']    = [0.00, 10.00] 

    return d_bin
#-----------------------------------------------------------
def test_simple(rdf_mc, rdf_dt):
    obj         = ext()
    obj.data    = rdf_mc, rdf_dt
    obj.model   = get_pdfs()
    obj.res_dir = data.fit_dir
    obj.binning = get_binning()

    obj.get_histograms()
#-----------------------------------------------------------
def make_data(kind):
    file_dir = utnr.make_dir_path(f'{data.dat_dir}/{kind}/{data.dat_ver}')
    file_path= f'{file_dir}/data.root'
    tree_name= 'tree'

    if os.path.isfile(file_path):
        data.log.info(f'Using cached {file_path}')
        return ROOT.RDataFrame(tree_name, file_path)
    else:
        data.log.info(f'Remaking {file_path}')

    d_data                     = {}
    d_data['B_IPCHI2_OWNPV']   = get_dist('ipch', kind)
    d_data['B_ENDVERTEX_CHI2'] = get_dist('vtch', kind)
    d_data['B_DIRA_OWNPV']     = get_dist('dira', kind)
    d_data['mass']             = get_dist('mass', kind)

    rdf = ROOT.RDF.MakeNumpyDataFrame(d_data) 
    rdf.Snapshot(tree_name, file_path)

    return rdf
#-----------------------------------------------------------
def get_dist(var, kind):
    if   var == 'mass': 
        arr = numpy.random.normal(5, 0.3, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.exponential(10, size=data.nentries_b1)
            arr_b_2 = numpy.random.normal(0, 0.6, size=data.nentries_b2)
            arr_b_2 = numpy.absolute(arr_b_2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var == 'dira':
        arr = numpy.random.exponential(0.01, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(0, 1.5, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(0, 1.5, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    elif var in ['ipch', 'vtch']:
        arr = numpy.random.chisquare(4, size=data.nentries_s)
        if kind == 'data':
            arr_b_1 = numpy.random.uniform(0, 100, size=data.nentries_b1)
            arr_b_2 = numpy.random.uniform(0, 100, size=data.nentries_b2)
            arr     = numpy.concatenate((arr, arr_b_1, arr_b_2))
    else:
        data.log.error(f'Variable {var} not recognized')
        raise

    if var == 'dira':
        arr = numpy.cos(arr)

    return arr
#-----------------------------------------------------------
def main():
    rdf_mc = make_data('ctrl')
    rdf_dt = make_data('data')

    test_simple(rdf_mc, rdf_dt)
#-----------------------------------------------------------
if __name__ == '__main__':
    main()

