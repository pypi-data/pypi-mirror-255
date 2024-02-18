import os

from rk.descriptors import descriptors as dsc 

import utils_noroot as utnr

log=utnr.getLogger(__name__)
#---------------------------------------------------------
class data:
    d_par_file = {}
    d_par_file['B0sig']        = 'bdXcHs.dec'
    d_par_file['B-sig']        = 'bpXcHs.dec'

    d_par_file['B_s0sig']      = 'bsXcHs.dec'
    d_par_file['Lambda_b0sig'] = 'lbXcHs.dec'
#---------------------------------------------------------
def test(mother, dec_file):
    dd = dsc(mother=mother, dec_file=dec_file)
    dd.out_dir = 'tests/descriptors'
    dd.save_match(mother_alias='Beauty')

    log.visible('Passed')
#---------------------------------------------------------
if __name__ == '__main__':
    for mother, dec_file in data.d_par_file.items():
        test(mother, dec_file)

