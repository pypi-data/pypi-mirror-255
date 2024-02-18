import ROOT

import os
import pickle
import numpy 

import utils
import utils_noroot as utnr

log=utnr.getLogger(__name__)
class swreader:
    def __init__(self, picklepath):
        self.picklepath=picklepath
        self.__initialized=False
    #---------------------------------
    def __initialize(self):
        if self.__initialized:
            return

        if not os.path.isfile(self.picklepath):
            log.error('Cannot find ' + self.picklepath)
            raise

        self.d_weights=pickle.load(open(self.picklepath, 'rb'))

        self.__initialized=True
    #---------------------------------
    def print_branches(self):
        self.__initialize()

        l_key = self.d_weights.keys()
        for key in l_key:
            log.info(key)
    #---------------------------------
    def predict_weights(self, arr_event, branchname):
        self.__initialize()

        if branchname not in self.d_weights:
            log.error('Cannot find {} among branches')
            print(self.d_weights.keys())
            raise

        d_data=self.d_weights[branchname]

        l_weight=[]
        missing=0
        for event in arr_event:
            try:
                weight=d_data[event]
            except:
                missing+=1
                weight=0

            l_weight.append(weight)

        arr_weight = numpy.array(l_weight)

        total=arr_event.size
        if missing != 0:
            log.warning('Missing/Total:{}/{}'.format(missing, total))
        else:
            log.info('Missing/Total:{}/{}'.format(missing, total))

        log.info('Number of weights: {}'.format(len(d_data)))

        return arr_weight
    #---------------------------------
    def attach_weights(self, df, branchname):
        self.__initialize()

        arr_event = df.AsNumpy(['eventNumber'])['eventNumber']

        arr_sweight = self.predict_weights(arr_event, branchname)

        df = utils.add_df_column(df, arr_sweight, branchname)

        return df
    #---------------------------------

