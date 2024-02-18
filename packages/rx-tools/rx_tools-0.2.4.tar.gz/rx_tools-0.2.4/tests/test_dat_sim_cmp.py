import sys
import numpy
import ROOT

from rk.dat_sim_cmp import compare 

#--------------------------------
def get_arr_bdt(size=10000):
    arr_dat_bdt = numpy.random.normal(0.5, 0.1, size)
    arr_sim_bdt = numpy.random.normal(0.9, 0.1, size)

    return (arr_dat_bdt, arr_sim_bdt)
#--------------------------------
def get_dat(size=10000):
    ROOT.gROOT.ProcessLine('''
    TRandom3 r_1(1);
    TRandom3 r_2(2);
    TRandom3 r_3(3);
    ''')

    df = ROOT.RDataFrame(size)
    df = df.Define('x', 'r_1.Uniform(0, 10)') 
    df = df.Define('y', 'r_2.Exp(3)') 
    df = df.Define('z', 'r_3.Gaus(0, 1)') 

    arr_w = numpy.random.normal(1.0, 0.1, size)
    
    df.arr_weight = arr_w 

    return df
#--------------------------------
def get_sim(size=10000):
    ROOT.gROOT.ProcessLine('''
    TRandom3 r_4(4);
    TRandom3 r_5(5);
    TRandom3 r_6(6);
    ''')

    df = ROOT.RDataFrame(size)
    df = df.Define('x', 'r_4.Uniform(0, 10)') 
    df = df.Define('y', 'r_5.Exp(3)') 
    df = df.Define('z', 'r_6.Gaus(0, 1)') 

    arr_w1 = numpy.random.normal(1.0, 0.1, size)
    arr_w2 = numpy.random.normal(1.0, 0.1, size)
    arr_w3 = numpy.random.normal(1.0, 0.1, size)

    d_arr_weight = {'w1' : arr_w1, 'w2' : arr_w2, 'w3' : arr_w3}
    
    df.d_arr_weight = d_arr_weight 

    return df
#--------------------------------
def check_eff(df_eff):
    df_eff['eff'] = 100 * df_eff['Passed'] / df_eff['Total']
    dev = abs(df_eff['eff'] - 50)

    assert (dev < 1).all()
#--------------------------------
def test_0():
    df_dat = get_dat()
    df_sim = get_sim()

    d_var_hist = {}
    d_var_hist['x'] = ROOT.RDF.TH1DModel('h_x', 'x', 10, 0, 10)
    d_var_hist['y'] = ROOT.RDF.TH1DModel('h_y', 'y', 10, 0, 10)
    d_var_hist['z'] = ROOT.RDF.TH1DModel('h_z', 'z', 10,-4, +4)
    
    hist_path= 'tests/dat_sim_cmp/hist_0.pickle'
    effi_path= 'tests/dat_sim_cmp/effi_0.pickle'
    
    obj=compare(df_dat, df_sim, d_var_hist)
    obj['x'] = 'x > 5'
    _, _, df_eff = obj.run(hist_path, effi_path = effi_path)

    check_eff(df_eff)
#--------------------------------
def test_1():
    df_dat = get_dat()
    df_sim = get_sim()

    d_var_hist = {}
    d_var_hist['x'] = ROOT.RDF.TH1DModel('h_x', 'x', 10, 0, 10)
    d_var_hist['y'] = ROOT.RDF.TH1DModel('h_y', 'y', 10, 0, 10)
    d_var_hist['z'] = ROOT.RDF.TH1DModel('h_z', 'z', 10,-4, +4)
    
    hist_path= 'tests/dat_sim_cmp/hist_1.pickle'
    effi_path= 'tests/dat_sim_cmp/effi_1.pickle'

    arr_dat_bdt, arr_sim_bdt = get_arr_bdt()
    hist_bdt =  ROOT.RDF.TH1DModel('h_b', 'b', 20, 0, 2)
    
    obj=compare(df_dat, df_sim, d_var_hist)
    obj.add_ext_var('b', arr_dat = arr_dat_bdt, arr_sim = arr_sim_bdt, hist = hist_bdt)
    obj.run(hist_path, effi_path = effi_path)
#--------------------------------
if __name__ == '__main__':
    test_0()
    #test_1()
#--------------------------------

