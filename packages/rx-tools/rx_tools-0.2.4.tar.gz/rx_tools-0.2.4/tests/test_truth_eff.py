import utils_noroot as utnr
import sys
sys.path = ['python'] + sys.path

from rk.truth_eff import get_eff as get_truth_eff

log=utnr.getLogger(__name__)
#--------------------------------------
def test():
    version='v10.21p2'
    kind   ='final_no_truth_mass_bdt'
    for trig in ['MTOS', 'ETOS', 'GTIS']:
        for sample in ['ctrl', 'psi2', 'sign']:
            for year in ['2011', '2012', '2015', '2016', '2017', '2018']:
                eff = get_truth_eff(sample, year, trig, version, kind)
                log.info(f'{eff:<10.3e}{sample:<20}{year:<20}')
#--------------------------------------
if __name__ == '__main__':
    test()

