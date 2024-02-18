import sys
import numpy
import ROOT

sys.path = ['python'] + sys.path

from dat_sim_cmp import plot 

#-------------------------------------------------------
def test_toy():
    hist_path= 'tests/dat_sim_cmp/hist_0.pickle'
    plot_dir = 'tests/dat_sim_cmp/test_0'
    
    d_opt = {}
    d_opt['legend'] = -1
    d_opt['yname']  = 'Entries'
    d_opt['ratio']  = True 
    d_opt['ymin_r'] = 0.8 
    d_opt['ymax_r'] = 1.2 
    
    obj=plot(hist_path, d_opt=d_opt)
    obj.save(plot_dir)
#-------------------------------------------------------
def test_ext():
    hist_path= 'tests/dat_sim_cmp/hist_0.pickle'
    plot_dir = 'tests/dat_sim_cmp/test_0'
    
    d_opt = {}
    d_opt['legend'] = -1
    d_opt['yname']  = 'Entries'
    d_opt['ratio']  = True 
    d_opt['ymin_r'] = 0.8 
    d_opt['ymax_r'] = 1.2 

    hist=ROOT.TH1F('h_x', '', 10, 0, 10)
    for i_bin in range(1, 11):
        hist.SetBinContent(i_bin, 1200)
    
    obj=plot(hist_path, d_opt=d_opt)
    obj.add_distribution('x', 'Data', hist)
    obj.save(plot_dir)
#-------------------------------------------------------
if __name__ == '__main__':
    ROOT.lhcbStyle()
    test_ext()

