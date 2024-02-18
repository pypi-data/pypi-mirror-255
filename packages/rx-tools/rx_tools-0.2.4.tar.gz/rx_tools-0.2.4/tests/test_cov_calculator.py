from rk.ckcov import calculator as ckcal
from logzero  import logger     as log

#----------------------------------
def test_mode():
    obj = ckcal(eff_version='v62', yld_version='v24', mode='cx', unc='sys', years=['2018'])
    obj.plot_dir = 'tests/ckcov/mode/cx'
    d_cov = obj.cov()

    obj = ckcal(eff_version='v62', yld_version='v24', mode='rx', unc='sys', years=['2018'])
    obj.plot_dir = 'tests/ckcov/mode/rx'
    d_cov = obj.cov()
#----------------------------------
def test_off():
    obj = ckcal(eff_version='v62', yld_version='v24', mode='cx', unc='sys', years=['2017', '2018'], turn_off=['pid_kp_el', 'pid_kp_mu'])
    obj.plot_dir = 'tests/ckcov/off'
    d_d_cov = obj.cov()

    d_cov = d_d_cov['cx']
    for kind, cov in d_cov.items():
        log.info(kind)
        log.info(cov)
        log.info(20 * '-')
#----------------------------------
def test_proc():
    obj = ckcal(eff_version='v62', yld_version='v24', mode='cx', unc='sys', years=['2018'], proc=['ctrl', 'psi2'])
    obj.plot_dir = 'tests/ckcov/proc'
    d_d_cov = obj.cov()
#----------------------------------
def main():
    test_proc()
    test_off()
    test_mode()
#----------------------------------
if __name__ == '__main__':
    main()

