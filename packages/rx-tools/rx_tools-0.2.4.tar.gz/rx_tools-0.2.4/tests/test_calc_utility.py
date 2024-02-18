import sys 

sys.path = ['python'] + sys.path

import rk.calc_utility as cu
import rk.utilities    as rkut
import utils_noroot    as utnr 

from log_store import log_store

log=log_store.add_logger('rx_tools:test_calc_utility')
#-------------------------------------
def test_geo_eff():
    l_proc = []
    l_proc.append('psi2_ee')
    l_proc.append('psi2_mm')
    l_proc.append('ctrl_ee')
    l_proc.append('ctrl_mm')
    l_proc.append('sign_ee')
    l_proc.append('sign_mm')

    l_year = ['2011', '2012', '2015', '2016', '2017', '2018']
    
    log.info('-' * 50)
    log.info(f'{"Process":<20}{"Year":<10}{"Efficiency":<10}{"Error":<10}')
    log.info('-' * 50)
    for proc in l_proc:
        for year in l_year:
            try:
                eff, err = cu.getGeomEff(proc, year)
            except:
                log.warning(f'Missing {proc}/{year}')
                continue

            log.info(f'{proc:<20}{year:<10}{eff:<10.3f}{err:<10.3e}')
        log.info('-' * 50)
#-------------------------------------
if __name__ == '__main__':
    test_geo_eff()

