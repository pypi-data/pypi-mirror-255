from rk.syst_check import check as sck

import os
import ROOT

#----------------------------------
class data:
    cas_dir = os.environ['CASDIR']
    nentries= 2000
#----------------------------------
def get_rdf(proc=None, trig=None, year=None):
    file_wc = f'{data.cas_dir}/tools/apply_selection/syst_check/{proc}/v10.18is/{year}_{trig}/*.root'
    rdf = ROOT.RDataFrame(trig, file_wc)
    rdf = rdf.Range(data.nentries)
    rdf = rdf.Define('nbrem', 'L1_BremMultiplicity + L2_BremMultiplicity')
    rdf = rdf.Filter('nbrem == 0')

    rdf.filepath = file_wc
    rdf.treename = trig
    rdf.trigger  = trig
    rdf.year     = year 
    rdf.preffix  = f'{proc}_{trig}_{year}'

    return rdf
#----------------------------------
def test_simple():
    rdf     = get_rdf(proc='ctrl', trig='ETOS', year='2018')
    out_dir = f'tests/syst_check/simple/{rdf.preffix}'

    obj         = sck(rdf, out_dir)
    obj.cal_dir = '/publicfs/ucas/user/campoverde/Test/Jobdir'
    obj.run()
#----------------------------------
def main():
    test_simple()
#----------------------------------
if __name__ == '__main__':
    main()

