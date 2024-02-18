from rk.differential_yield import dyield_calculator as dyc
from rk.differential_yield import dyield
from rk.binning            import binning
from ndict                 import ndict

import ROOT
import numpy
import utils_noroot as utnr

#-------------------------------------
class data:
    nentries = 10000
    log      = utnr.getLogger(__name__)
    out_dir  = utnr.make_dir_path('tests/dyield')

    ROOT.gInterpreter.ProcessLine('TRandom3 ran(1);')
#-------------------------------------
def get_binning():
    bins      = binning()
    bins['x'] = [1, 2, 3, 4]
    bins['y'] = [10, 20]

    return bins
#-------------------------------------
def get_data():
    rdf = ROOT.RDataFrame(data.nentries)
    rdf = rdf.Define('x', 'ran.Uniform(-1,  7)')
    rdf = rdf.Define('y', 'ran.Uniform(0,  30)')
    rdf = rdf.Define('w', 'ran.Gaus(1, 0.1)')

    arr_wgt = rdf.AsNumpy(['w'])['w']

    return (rdf, arr_wgt)
#-------------------------------------
def make_json(proc, trig, dset, var):
    json_path = f'{data.out_dir}/from_json/{proc}_{trig}_{dset}_{var}.json'

    l_fit = []
    l_fit.append((0, 1, 1000, 10))
    l_fit.append((1, 2, 2000, 15))
    l_fit.append((2, 3, 3000, 20))

    utnr.dump_json(l_fit, json_path)

    return json_path
#-------------------------------------
def test_simple():
    bins         = get_binning()
    rdf, arr_wgt = get_data()
    
    obj  = dyc(rdf, arr_wgt, bins)
    dy_x = obj.get_yields(var='x')

    print(dy_x)
    data.log.visible('Passed test_simple')
#-------------------------------------
def test_divide_arr():
    bins         = get_binning()
    rdf, arr_pas = get_data()
    arr_fal      = numpy.random.normal(1, 0.1, size=arr_pas.size)
    arr_tot      = numpy.concatenate((arr_pas, arr_fal))
    
    obj  = dyc(rdf, arr_pas, bins)
    dy_x = obj.get_yields(var='x')
    deff = dy_x / arr_tot 

    print(deff)
    print(deff.efficiency())
    data.log.visible('Passed test_divide_arr')
#-------------------------------------
def test_divide_deff():
    bins         = get_binning()
    rdf, arr_pas = get_data()
    arr_fal      = numpy.random.normal(1, 0.1, size=arr_pas.size)
    arr_tot      = numpy.concatenate((arr_pas, arr_fal))
    
    obj  = dyc(rdf, arr_pas, bins)
    dy_x = obj.get_yields(var='x')
    deff = dy_x / arr_tot 
    dy_y = dy_x / deff

    print(dy_x)
    print(deff)
    print(dy_y)
    data.log.visible('Passed test_divide_deff')
#-------------------------------------
def test_dyield():
    d_bnd_wgt = ndict()
    d_bnd_wgt[0, 1] = numpy.random.normal(1, 0.1, size=100)
    d_bnd_wgt[1, 3] = numpy.random.normal(1, 0.1, size=200)
    d_bnd_wgt[3, 4] = numpy.random.normal(1, 0.1, size=100)

    obj = dyield(d_bnd_wgt, varname='x')
    print(obj)
    data.log.visible('Passed test_dyield')
#-------------------------------------
def test_from_json(proc, trig, dset, var):
    json_path = make_json(proc, trig, dset, var)
    dy = dyield(json_path)
    print(dy)
#-------------------------------------
def main():
    test_from_json('ctrl', 'ETOS', 'r1p2', 'BDT')
    test_dyield()
    test_divide_deff()
    test_simple()
    test_divide_arr()
#-------------------------------------
if __name__ == '__main__':
    main()

