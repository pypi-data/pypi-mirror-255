import ROOT
import sys
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import poisson, norm
from scipy.optimize import curve_fit

import utils_noroot                   as utnr
from   rk.bootstrapping import reader as bootsreader 

log=utnr.getLogger(__name__)
#---------------------------------
def make_data(nentries=10000):
    df = ROOT.RDataFrame(nentries)
    df = df.Define('eventNumber'  , 'TRandom3 ran(0); return ran.Integer(15000000);')

    return df
#---------------------------------
def Poisson(k, lamb):
    return poisson.pmf(k, lamb)
#---------------------------------
def Gaussian(x, mean, sigma):
    return norm.pdf(x, mean, sigma)
#---------------------------------
def test(df, kind):
    plt.rcParams['text.usetex'] = True

    rdr1     = bootsreader()
    rdr1.setYear("2012")
    wgt      = rdr1.getWeight(df, "29")

    bin_width = 1
    x_start   = 0
    x_end     = 10
    bins     = np.arange(x_start,x_end,bin_width)
    
    entries, _, _          = plt.hist(wgt, bins=len(bins), range=(x_start, x_end), density=True, alpha=0.9, align="left")
    parameters, cov_matrix = curve_fit(Poisson, bins, entries)

    plt.plot( bins, Poisson(bins, *parameters), alpha=1, color="red")
    plt.text(5.5, 0.2, '$ \lambda={:.4f} \pm {:.4f} $'.format(parameters[0], np.sqrt(np.diag(cov_matrix,0)[0])), fontsize=16, color="gray")
    
    plot_dir =utnr.make_dir_path('tests/bootstrap')
    plot_path=f'{plot_dir}/{kind}.png'

    log.visible(f'Saving to: {plot_path}')
    plt.savefig(plot_path)
    plt.close('all')
#---------------------------------
def test_wofig(df, n_test):
    rdr1     = bootsreader()
    rdr1.setYear("2012")
    wgt      = rdr1.getWeight(df, n_test)
    return wgt.sum()
#---------------------------------
def test_yields(n_test, n_data, kind):
    plt.rcParams['text.usetex'] = True
    y = []
    df = make_data(n_data)
    for i in range(n_test):
        y.append(test_wofig(df, i))
        print("{}/{}".format(i, n_test))
    
    bin_width = 10
    x_start   = n_data - 3*(n_data**0.5)
    x_end     = n_data + 3*(n_data**0.5)
    bins     = np.arange(x_start,x_end,bin_width)
    x        = np.arange(x_start,x_end,0.1)
    
    fig, ax = plt.subplots(1)
    
    entries, _, _          = plt.hist(y, bins=len(bins), range=(x_start, x_end), density=True, alpha=0.9)
    parameters, cov_matrix = curve_fit(Gaussian, bins, entries, p0=(n_data, n_data**0.5))

    ax.plot( x, Gaussian(x, *parameters), alpha=1, color="red")
    ax.text( 0.6, 0.8, '$ \mu={:.1f} \pm {:.1f} $'.format(parameters[0], np.sqrt(np.diag(cov_matrix,0)[0])), fontsize=12, color="gray", transform=ax.transAxes)
    ax.text( 0.6, 0.7, '$ \sigma={:.1f} \pm {:.1f} $'.format(parameters[1], np.sqrt(np.diag(cov_matrix,0)[1])), fontsize=12, color="gray", transform=ax.transAxes)
    plot_dir =utnr.make_dir_path('tests/bootstrap')
    plot_path=f'{plot_dir}/{kind}.png'

    log.visible(f'Saving to: {plot_path}')
    fig.savefig(plot_path)
    plt.close('all')
#---------------------------------
if __name__ == '__main__':
    df = make_data(20000)
    test(df, "Toy")
    
    test_yields(2, 20000, "yields")
#---------------------------------

