import sys

from rk.selection import selection as rksl

import utils_noroot as utnr

#-------------------------------
def test_simple():
    d_sel = rksl('final_no_truth_mass_bdt', 'ETOS', '2016', 'ctrl_ee')
    utnr.pretty_print(d_sel, sort=False)
#-------------------------------
if __name__ == '__main__':
    test_simple()

