import ROOT
import array
import copy
import os
import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from scipy.optimize import curve_fit

from rk.oscillator import oscillator as osc
import utils
import utils_noroot as utnr

#---------------------------------
class data:
    log=utnr.getLogger(__name__)
#---------------------------------
def Gaussian(x, mean, sigma):
    return norm.pdf(x, mean, sigma)
#---------------------------------
def make_data(nentries=10000):
    ROOT.gInterpreter.ProcessLine('TRandom3 ran(0);')
    
    df = ROOT.RDataFrame(nentries)
    df = df.Define('x', 'ran.Uniform(-0.1, 1.1)')
    df = df.Define('y', 'ran.Uniform(-0.1, 1.1)')
    df = df.Define('z', 'ran.Uniform(-0.1, 1.1)')

    return df
#-------------------------------------------
def adjust_point(x, y, z):
    if x < 0:
        x = 0
    elif x > 1:
        x = 1
        
    if y < 0:
        y = 0
    elif y > 1:
        y = 1
        
    if z < 0:
        z = 0
    elif z > 1:
        z = 1

    return (x, y, z)
#-------------------------------------------
def get_target_weight(df, Hist, osc_ntest):
    wgt = []
    arr_points = utils.getMatrix(df, [ f'x', f'y', f'z'])
    
    osc.ntest = osc_ntest
    
    tem_osc_obj = osc()
    Hist = tem_osc_obj.get_oscillated_map( "ToyTest", Hist )
    
    for [x, y, z] in arr_points:
        x, y, z = adjust_point(x, y, z)
            
        curr_globalbin = Hist.FindBin(x, y, z)
        curr_wgt = Hist.GetBinContent(curr_globalbin)

        wgt.append(curr_wgt)
    return np.array(wgt)
#---------------------------------
def GetEdges(Hist, axis = "x"):
    if axis == "x":
        Nbins = Hist.GetNbinsX()
        HAxis    = Hist.GetXaxis()
    elif axis == "y":
        Nbins = Hist.GetNbinsY()
        HAxis    = Hist.GetYaxis()
    elif axis == "z":
        Nbins = Hist.GetNbinsZ()
        HAxis    = Hist.GetZaxis()
        
    edge_list = []
    for i in range(1, Nbins + 2):
        if i == Nbins + 1:
            list.append( HAxis.GetBinUpEdge(i)  )
        else:
            list.append( HAxis.GetBinLowEdge(i) )
    return edge_list
#---------------------------------
def GetContentAndError(self):
    content_list = []
    error_list = []
    for i in range(1, self.GetNbinsX() + 1):
        content_list.append( self.GetBinContent(i))
        error_list.append(   self.GetBinError(  i))
    return content_list, error_list
#---------------------------------
def make_1dhistogram():
    edgeX_list = [ 0.0, 0.2, 0.4, 0.6, 0.8, 1.0 ]
    edgeX      = array.array('d', edgeX_list)
    weight = [ 0.5, 0.8, 0.3, 0.05, 0.98 ]
    error  = [ 0.02, 0.015, 0.03, 0.04, 0.03 ]
    
    map = ROOT.TH1D("Toy_1d_weight_map", "Toy_1d_weight_map", len(edgeX) - 1, edgeX)
    
    for i in range( 1, map.GetNbinsX() + 1 ):
        map.SetBinContent(i, weight[i-1])
        map.SetBinError(  i, error[i-1] )
        
    return map
#---------------------------------
def test_yields(n_test, n_data=20000):
    map = make_1dhistogram()
    df  = make_data(n_data)
    
    wgt_sum = []
    for i in range(n_test):
        wgt_sum.append(get_target_weight(df, map, i).sum())
        print(f"{i+1}/{n_test}")
    n_data = wgt_sum[0]
    wgt_sum = wgt_sum[1:]
    bin_width = 100
    x_start   = n_data - 5*5*(n_data**0.5)
    x_end     = n_data + 5*5*(n_data**0.5)
    bins     = np.arange(x_start,x_end,bin_width)
    x        = np.arange(x_start,x_end,0.1)
    
    fig, ax = plt.subplots(1)
    entries, _, _          = plt.hist(wgt_sum, bins=len(bins), range=(x_start, x_end), density=True, alpha=0.9)
    parameters, cov_matrix = curve_fit(Gaussian, bins, entries, p0=(n_data, 5*(n_data**0.5)))

    ax.plot( x, Gaussian(x, *parameters), alpha=1, color="red")
    plt.axvline(n_data, color = 'green', alpha=0.9)
    ax.text( 0.65, 0.9, 'input:{:.1f}'.format(n_data), fontsize=12, color="gray", transform=ax.transAxes)
    ax.text( 0.65, 0.8, '$ \mu={:.1f} \pm {:.1f} $'.format(parameters[0], np.sqrt(np.diag(cov_matrix,0)[0])), fontsize=12, color="gray", transform=ax.transAxes)
    ax.text( 0.65, 0.7, '$ \sigma={:.1f} \pm {:.1f} $'.format(parameters[1], np.sqrt(np.diag(cov_matrix,0)[1])), fontsize=12, color="gray", transform=ax.transAxes)
    plot_dir =utnr.make_dir_path('tests/oscillator')
    plot_path=f'{plot_dir}/yields_keeppositive.png'

    data.log.visible(f'Saving to: {plot_path}')
    fig.savefig(plot_path)
    plt.close('all')

    assert(True)
#---------------------------------
def test_simple(n_osc):
    map_old = make_1dhistogram()
    map = map_old
    obj = osc()
    
    verror = []
    arr = []
    
    for i in range(0, n_osc):
        obj.ntest = i
        map_new  = obj.get_oscillated_map("ToyHist", map)
        value, error = GetContentAndError(map_new)
        arr.append(value)
        if verror == []:
            verror = error
    arr = np.array(arr).T

    for idx, ws in enumerate(arr):
        w0 = ws[0]
        ws = ws[1:]
        e0 = verror[idx]
        
        u = w0
        sig = e0
        x = np.linspace( u - 5*sig, u + 5*sig, 100)
        
        y = np.exp(-(x - u) ** 2 / (2 * sig ** 2)) / (math.sqrt(2*math.pi)*sig)
        
        itg = 0
        ritg = 0
        for xidx, xx in enumerate(x):
            if xx < 1 and xx > 0:
                ritg += y[xidx]
            itg += y[xidx]
        y = y * (itg/ritg)
        
        plt.plot(x, y, color = 'red', alpha=0.6)
        # plt.axvline(w0, color = 'green', alpha=0.9)
        plt.hist(ws, bins=150, color = 'blue', range=(-0.1, 1.1), alpha=0.8, density=True)

        cwd = os.getcwd()
        plot_dir=utnr.make_dir_path(f'{cwd}/tests/oscillator')
        plot_path=f'{plot_dir}/No_{idx+1}_bin.png'
        data.log.visible(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')

    assert(True)
#---------------------------------
def test_off(n_osc):
    map_old = make_1dhistogram()
    obj = osc()
    
    verror = []
    arr = []
    
    obj.ntest = 0
    map_new = obj.get_oscillated_map("ToyHist", map_old)

    assert(map_new is map_old)
#---------------------------------
def main():
    test_off(10000)
    test_simple(10000)
    # test_yields(2001, 20000) # First run to get the unweighted yields.
#---------------------------------
if __name__ == '__main__':
    main()
#---------------------------------