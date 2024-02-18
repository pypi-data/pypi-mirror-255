import ROOT
import os
import logging

from rk.dfselect import apply_selection
from rk.dfselect import selection 

import utils_noroot   as utnr

#----------------------------------
class data:
    data_dir  = os.environ['DATDIR']
    d_sam_tre = {'ctrl_ee' : 'KEE', 'data_ee' : 'KEE', 'ctrl_mm' : 'KMM', 'data_mm' : 'KMM'}

    log = utnr.getLogger(__name__)
#----------------------------------
def get_df(sample, version, year):
    file_path = f'{data.data_dir}/{sample}/{version}/{year}.root'
    tree_name = utnr.get_from_dic(data.d_sam_tre, sample)

    data.log.visible(f'Reading: {file_path}:{tree_name}')
    df = ROOT.RDataFrame(tree_name, file_path)

    return df
#----------------------------------
def test_toy():
    ROOT.gInterpreter.ProcessLine('TRandom3 r(0);')
    
    df = ROOT.RDataFrame(10000)
    df = df.Define('a', 'r.Gaus(0, 1)')
    df = df.Define('b', 'r.Gaus(0, 1)')
    df = df.Define('c', 'r.Gaus(0, 1)')
    
    df = apply_selection(df, trigger='test', sample='test', kind='test')
#----------------------------------
def test_simple(sample=None, trigger=None):
    df = get_df(sample, 'v10.11tf', '2016')

    df = apply_selection(df, sample=sample, trigger=trigger, year='2016', kind='final_nobdt_gorder', q2bin='jpsi', fraction=0.01)
#----------------------------------
if __name__ == '__main__':
    selection.log.setLevel(logging.DEBUG)

    test_simple(sample='ctrl_ee', trigger='ETOS')
    test_simple(sample='data_ee', trigger='ETOS')

    test_simple(sample='ctrl_mm', trigger='MTOS')
    test_simple(sample='data_mm', trigger='MTOS')

    #test_toy()

