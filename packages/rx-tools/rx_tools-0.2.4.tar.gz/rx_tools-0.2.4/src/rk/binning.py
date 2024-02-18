import utils_noroot as utnr

import numpy
import math
import re 

from collections import UserDict

#--------------------------------
class binning(UserDict):
    log = utnr.getLogger(__name__)
    #--------------------------------
    def __init__(self):
        self._regex = r'(.*)\[(\d+)\]'

        super().__init__()
    #--------------------------------
    @property
    def arr_vars(self):
        l_var_arr = [ var for var in self.vars if re.match(self._regex, var)]

        return l_var_arr
    #--------------------------------
    @property
    def vars(self):
        l_var = list(self.data.keys())
        return l_var 
    #--------------------------------
    def arr_to_var(self):
        '''
        Will transform all keys from array like to variable like, i.e.: 
        var[i] -> var
        '''

        d_var = {}
        for var, val in self.data.items():
            mtch = re.match(self._regex, var)
            if not mtch:
                d_var[var] = val
                continue

            new_var = mtch.group(1)
            d_var[new_var] = val

            self.log.info(f'{var:<20}{"->":<10}{new_var:<50}')

        self.data = d_var
    #--------------------------------
    def __setitem__(self, var_name, l_bound):
        self.data[var_name] = l_bound
    #--------------------------------
    def __getitem__(self, var_name):
        if var_name in self.data:
            l_bound = self.data[var_name]
            return l_bound

        self.log.error(f'Key {var_name} not found among:')
        self.log.error(self.data.keys())

        raise KeyError
    #--------------------------------
    def get_bounds(self, var_name):
        if var_name not in self.data:
            self.log.error(f'Variable {var_name} not found among {self.vars}')
            raise

        return self.data[var_name]
    #--------------------------------
    def __str__(self):
        msg = f'\n----------------------------------\n'
        msg+= f'{"Variable":<20}{"Binning":<40}\n'
        msg+= f'----------------------------------\n'
        for var_name, l_bound in self.data.items():
            l_bound_str = [ f'{bound:.3e}' for bound in l_bound ]
            str_l_bound = str(l_bound_str)
            msg        += f'{var_name:<20}{str_l_bound:<100}\n'

        return msg
    #--------------------------------
    def find_bin(self, var_name, var_val):
        l_bound  = self.get_bounds(var_name)
        arr_bound= numpy.array(l_bound)

        try:
            arr_diff = numpy.absolute(arr_bound - var_val)
        except:
            self.log.error(f'Cannot find difference array for: {var_name}')
            self.log.error(arr_bound)
            self.log.error(var_val)
            raise

        index    = arr_diff.argmin()

        ibin     = index if arr_bound[index] > var_val else index + 1

        return ibin
    #--------------------------------
    def find_bin_bounds(self, var_name, var_val):
        l_bound = self.__getitem__(var_name)
        ibin    = self.find_bin(var_name, var_val)

        low  = - math.inf if ibin < 1                else l_bound[ibin - 1]
        hig  = + math.inf if ibin > len(l_bound) - 1 else l_bound[ibin + 0]

        return (low, hig) 
#--------------------------------

