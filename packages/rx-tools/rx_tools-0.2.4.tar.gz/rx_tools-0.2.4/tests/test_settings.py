import sys
import utils_noroot as utnr

sys.path = ['python'] + sys.path

from settings import settings as rkst

log=utnr.getLogger(__name__)

#---------------------------
def test():
    l_proc = []
    l_proc.append("psi2_ee")
    l_proc.append("ctrl_mm")
    l_proc.append("ctrl_ee")
    l_proc.append("psi2_mm")
    l_proc.append("sign_ee")
    l_proc.append("sign_mm")

    for year in rkst.get_years():
        for pol in ['MagUp', 'MagDown']:
            for proc in l_proc:
                evt = rkst.get_evt(proc)
                line = '{0:<20}{1:<20}{2:<20}{3:<20}'.format(year, pol, proc, evt)
                log.info(line)
#---------------------------
if __name__ == '__main__':
    test()
