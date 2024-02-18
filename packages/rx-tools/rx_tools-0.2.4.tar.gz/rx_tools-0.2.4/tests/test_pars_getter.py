import sys

sys.path = ['Efficiencies'] + sys.path

import pandas as pnd

from model import pars_getter 

import utils_noroot as utnr

log=utnr.getLogger(__name__)

#--------------------------------
def test_simple(trig):
    proc         = 'ctrl'
    year         = '2016'
    sim_fit_vers = 'v10'

    pgt   = pars_getter(proc, trig, year, sim_fit_vers) 
    pgt.val_dir = 'tests/pars_getter'
    d_par, df = pgt.get_pars()

    print(df)
#--------------------------------
if __name__ == '__main__':
    for trig in ['MTOS', 'ETOS', 'GTIS', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0MuonALL1']:
        test_simple(trig)

