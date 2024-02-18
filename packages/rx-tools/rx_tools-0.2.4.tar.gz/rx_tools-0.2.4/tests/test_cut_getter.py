import sys

sys.path = ['python'] + sys.path

import rk.selection as rk_sel

import utils_noroot               as utnr
import cut_getter                 as ctgt

from   cut_getter import cut_getter as ctgt_cl

log=utnr.getLogger(__name__)
#---------------------------------------
def print_cut(cut, mode, chan, year):
    value = ctgt.get_cut(cut, mode, chan, year)
    log.info('{0:<10}{1:<20}{2:<100}'.format(cut, mode, value))
#---------------------------------------
def test_0():
    cut_dir = 'tests/selection/'

    ctgt_cl.directory = cut_dir
    rk_sel.write(cut_dir)
    for mode in ['reso', 'psi', 'rare_central', 'rare_high']:
        for chan in ['electron', 'muon']:
            for year in ['2016']:
                print_cut('q2', mode, chan, year)
#---------------------------------------
def test_1():
    ctgt_cl.directory = None 
    for mode in ['reso', 'psi', 'rare_central', 'rare_high']:
        for chan in ['electron', 'muon']:
            for year in ['2016']:
                print_cut('q2', mode, chan, year)
#---------------------------------------
if __name__ == '__main__':
    test_0()
    test_1()
#---------------------------------------

