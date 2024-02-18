import sys
import os

from rk.model import zmodel

import utils_noroot      as utnr
import matplotlib.pyplot as plt
import zfit

from fitter      import zfitter
from zutils.plot import plot    as zfp

log=utnr.getLogger(__name__)

#--------------------------
def test_sign(year, trig, obs):
    mod=zmodel(proc='ctrl', trig=trig, year=year, q2bin='jpsi', obs=obs, mass='mass_jpsi')
    pdf=mod.get_model(suffix='', signal=True)
#--------------------------
def test_model(year, trig, proc, suff, obs):
    mod=zmodel(proc=proc, trig=trig, year=year, q2bin='psi2', obs=obs, mass='mass_psi2')
    pdf=mod.get_model(suffix=suff, skip_csp = True, prc_kind='ke_split')

    dat  = pdf.create_sampler()
    res  = None
    obj  = zfp(data=dat, model=pdf, result=res)
    obj.plot()

    out_dir = 'tests/zmodel/test_model'

    os.makedirs(out_dir, exist_ok=True)

    plt.savefig(f'{out_dir}/plot.png')
#--------------------------
def main():
    obs = zfit.Space('mass', limits=(4000, 6000))
    test_model('2018', 'ETOS', 'ctrl'       , 'ele', obs)
    #test_model('2018', 'MTOS', 'ctrl_binned', 'muo', obs)
#--------------------------
if __name__ == '__main__':
    main()
#--------------------------

