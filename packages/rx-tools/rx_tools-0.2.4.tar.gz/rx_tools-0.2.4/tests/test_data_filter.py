import os
import re
import ROOT
import pprint
import logging

from rk.data_filter   import filter_zeros as dfzero

import utils_noroot  as utnr

log=utnr.getLogger(__name__)
#----------------------------
class data:
    l_trig = ['MTOS', 'ETOS', 'GTIS']
    l_proc = ['jpsi', 'psi2']

    dat_dir   = os.environ['DATDIR']
    version   = 'v10.11tf'
def get_data(trig, year, proc, nentries = 1000):
    if   trig in ['ETOS', 'GTIS']:
        filepath=f'{data.dat_dir}/data_ee/{data.version}/{year}.root'
        treename='KEE'
    elif trig == 'MTOS': 
        filepath=f'{data.dat_dir}/data_mm/{data.version}/{year}.root'
        treename='KMM'
    else:
        log.error(f'Incorrect trigger: {trig}')
        raise

    df=ROOT.RDataFrame(treename, filepath)
    if nentries > 0:
        df = df.Range(nentries)

    df          = filter_dilepton(df, proc)
    df.treename = trig 
    df.year     = year
    df.filepath = filepath

    return df 
#----------------------------
def filter_dilepton(df, proc):
    v_name = df.GetColumnNames()
    l_name = [ name.c_str() for name in v_name ]

    #If data, then this will be assigned by hand, i.e. no filter needed
    if 'Jpsi_TRUEID' not in l_name:
        return df

    if   proc == 'jpsi':
        pdgid = '443'
    elif proc == 'psi2':
        pdgid = '100443'
    else:
        log.error(f'Wrong  process: {proc}')
        raise

    df = df.Filter(f'Jpsi_TRUEID == {pdgid}', 'jpsi')

    rep= df.Report()

    rep.Print()

    return df
#----------------------------
def test(year, nentries = 1000):
    for trig in data.l_trig:
        for proc in data.l_proc: 
            plotsdir=f'tests/data_filter/{trig}_{proc}_{year}'

            df        = get_data(trig, year, proc)
            df.proc   = proc
            df.trigger= trig

            df        = dfzero(df, plotsdir)

            print(df.d_zeros)
#----------------------------
if __name__ == '__main__':
    test('2018') 
#----------------------------

