import ROOT
import numpy
import utils

import sys

from rk.hist_map import hist_map
from logzero     import logger   as log

#----------------------------------
def get_maps(kind=None):
    hname = 'h_data_{}'.format(kind)
    hist = ROOT.TH2Poly(hname, '', 0, 3, 0, 3)

    counter = 1
    for ymin in numpy.arange(0, 3, 1):
        ymax = ymin + 1
        for xmin in numpy.arange(0, 3, 1):
            xmax = xmin + 1

            hist.AddBin(xmin, ymin, xmax, ymax)
            if   kind == 'Data':
                content = counter + 0.00 * counter ** 2
            elif kind == 'Simulation':
                content = counter + 0.05 * counter ** 2
            elif kind == 'Other':
                content = counter + 0.10 * counter ** 2
            else:
                log.error(f'Invalid kind: {kind}')
                raise

            hist.SetBinContent(counter, content)
            hist.SetBinError(counter, 0.1)
            counter += 1

    return hist, hist
#----------------------------------
def test_simple():
    d_opt = {'legend' : True, 'plot_id' : 'id', 'xname' : 'xname'}
    
    obj = hist_map(d_opt = d_opt)
    
    h_pas, h_fal = get_maps(kind='Data')
    obj.add_hist(h_pas, h_fal, data=True)
    
    h_pas, h_fal = get_maps(kind='Simulation')
    obj.add_hist(h_pas, h_fal, data=False)
    
    obj.plot_maps('tests/hist_map/simple/')
#----------------------------------
def test_multiple():
    d_opt = {'legend' : True, 'plot_id' : 'id', 'xname' : 'xname'}
    
    obj = hist_map(d_opt = d_opt)
    
    h_pas, h_fal = get_maps(kind='Data')
    obj.add_hist(h_pas, h_fal, data='Data')
    
    h_pas, h_fal = get_maps(kind='Simulation')
    obj.add_hist(h_pas, h_fal, data='Simulation')

    h_pas, h_fal = get_maps(kind='Other')
    obj.add_hist(h_pas, h_fal, data='Other')
    
    obj.plot_maps('tests/hist_map/multiple/')
#----------------------------------
def main():
    test_multiple()
    test_simple()
#----------------------------------
if __name__ == '__main__':
    main()

