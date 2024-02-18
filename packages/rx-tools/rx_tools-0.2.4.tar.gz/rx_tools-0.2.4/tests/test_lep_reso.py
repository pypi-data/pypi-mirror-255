import numpy
import os
import ROOT
import utils_noroot as utnr

from rk.lep_reso import calculator as calc_reso
#----------------------------
def get_data():
    dat_dir   = os.environ['DATDIR']
    file_path = f'{dat_dir}/ctrl_ee/v10.11tf/2018.root'

    rdf = ROOT.RDataFrame('KEE', file_path)

    return rdf
#----------------------------
def test_simple():
    df          = get_data()
    arr_bin_low = numpy.linspace(2000, 20000, 7)
    arr_bin_hig = numpy.array([25000, 30000, 60000])
    arr_bin     = numpy.concatenate([arr_bin_low, arr_bin_hig])
    
    obj         = calc_reso(df, binning={'p' : arr_bin.tolist() })
    obj.plot_dir= 'tests/lep_reso/simple'
    d_res_0, d_res_1 = obj.get_resolution()

    utnr.dump_json(d_res_0, 'tests/lep_reso/simple/0_brem.json')
    utnr.dump_json(d_res_1, 'tests/lep_reso/simple/1_brem.json')
#----------------------------
def main():
    test_simple()
#----------------------------
if __name__ == '__main__':
    main()

