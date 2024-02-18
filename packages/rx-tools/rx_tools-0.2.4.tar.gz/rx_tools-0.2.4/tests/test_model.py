import sys

from rk.model import model
from rk.model import pars_getter 

import utils_noroot as utnr

log=utnr.getLogger(__name__)

#--------------------------
def test_sign(year, trig):
    mod=model('ctrl', trig, year)
    mod.val_dir = 'tests/sign_model'

    wks=mod.get_sign_model()
#--------------------------
def test_full(year, trig):
    proc         = 'ctrl'

    mod=model(proc, trig, year)
    mod.val_dir = 'tests/set_fix'
    wks=mod.get_full_model(sim_fit_vers=None)
    yld=mod.get_yield()

    log.visible(f'Total yield: {yld}')
#--------------------------
if __name__ == '__main__':
    for year in ['2012', 'r1', '2016', 'r2p1', '2017']:
        for trig in ['MTOS', 'ETOS', 'GTIS', 'L0TIS_EM', 'L0TIS_MH', 'L0ElectronTIS', 'L0MuonALL1']:
            test_sign(year, trig)
            test_full(year, trig)
#--------------------------

