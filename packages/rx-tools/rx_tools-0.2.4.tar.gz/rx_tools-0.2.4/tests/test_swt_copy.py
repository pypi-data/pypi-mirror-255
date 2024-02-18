from rk.swt_copy import copy as swcp

import ROOT
import numpy
import os
import matplotlib.pyplot as plt

#-----------------------------------------------
def add_mass_array(rdf):
    rdf = rdf.Define('B_const_mass_M', 'ROOT::RVecD{mass}')

    return rdf
#-----------------------------------------------
def get_rdf_src(nentries=10000):
    d_data = {}
    arr_mass       = numpy.random.uniform(0, 1, size=nentries)

    d_data['sw_x'] = - arr_mass ** 2 + arr_mass / 2 + 0.25
    d_data['sw_y'] = arr_mass /  2 
    d_data['mass'] = arr_mass
    d_data[   'b'] = numpy.random.normal(0, 1, size=nentries)

    rdf = ROOT.RDF.FromNumpy(d_data)
    rdf = add_mass_array(rdf)

    return rdf
#-----------------------------------------------
def get_rdf_tgt(nentries=10000):
    d_data = {}
    d_data['mass'] = numpy.random.uniform(0, 1, size=nentries)
    d_data[   'b'] = numpy.random.normal(0, 1, size=nentries)

    rdf = ROOT.RDF.FromNumpy(d_data)
    rdf = add_mass_array(rdf)

    return rdf
#-----------------------------------------------
def plot(rdf, var):
    d_data = rdf.AsNumpy(['mass', var])
    arr_mass = d_data['mass']
    arr_swt  = d_data[   var]

    plt.scatter(x=arr_mass, y=arr_swt, label=var)
#-----------------------------------------------
def test_simple():
    rdf_src=get_rdf_src()
    rdf_tgt=get_rdf_tgt()

    obj=swcp(src=rdf_src, tgt=rdf_tgt)
    rdf=obj.attach_swt(l_wgt_name=['sw_x', 'sw_y'])

    plot(rdf, 'sw_x')
    plot(rdf, 'sw_y')

    dir_path = 'tests/swt_copy/test_simple'
    os.makedirs(dir_path, exist_ok=True)

    plt.grid()
    plt.savefig(f'{dir_path}/plot.png')
    plt.close('all')
#-----------------------------------------------
if __name__ == '__main__':
    test_simple()

