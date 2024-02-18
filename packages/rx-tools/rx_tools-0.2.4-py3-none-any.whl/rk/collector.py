import ROOT
import os
import numpy
import glob

import utils
import utils_noroot as utnr

class collector:
    log=utnr.getLogger(__name__)
    def __init__(self):
        self.d_data={}
    #-------------------------------------------
    def add(self, key, value, exists_ok=False):
        if   not exists_ok and key in self.d_data:
            self.log.error('Trying to add {}:{}'.format(key, value))
            self.log.error('Key:Value {}:{} are already in the container'.format(key, self.d_data[key]))
            raise
        elif     exists_ok and key in self.d_data:
            self.log.debug('Key already stored, skipping')
            return
        else:
            self.log.debug('Adding ' + key)
            self.d_data[key] = value
    #-------------------------------------------
    def add_list(self, key, value):
        if   value is None and key not in self.d_data:
            self.d_data[key] = []
        elif value is None and key     in self.d_data:
            return
        elif                   key not in self.d_data:
            self.log.debug('Adding element to ' + key)
            self.d_data[key]=[value]
        else:
            self.log.debug('Adding element to ' + key)
            self.d_data[key].append(value)
    #-------------------------------------------
    def get(self, key):
        if key not in self.d_data:
            return None

        return self.d_data[key]
    #-------------------------------------------
    def get_data(self, as_list = False):
        if as_list:
            l_tp_data = list(self.d_data.items())
            l_tp_data.sort()

            return l_tp_data

        return self.d_data
    #-------------------------------------------
    def Print(self, opt='', path=None):
        if path is not None:
            self.log.visible('Dumping storage data to ' + path)
            ofile=open(path, 'w')

        for key, val in sorted(self.d_data.items()):
            if 'keys' in opt and path is     None:
                self.log.info(key)

            if 'keys' in opt and path is not None:
                ofile.write(key + '\n')

            if 'types' in opt and path is     None:
                typ=type(val)
                self.log.info(str(typ))

            if 'types' in opt and path is not None:
                typ=type(val)
                ofile.write(str(typ) + '\n')
    #-------------------------------------------

