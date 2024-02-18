import utils
import utils_noroot as utnr

import numpy as np

class dcm_reader():
    log=utnr.getLogger(__name__)

    def __init__(self):
        self._map_path = ''
        self._default_hist = 'sign_ee_weight_gen.json'

    @property
    def map_path(self):
        return self._map_path

    @map_path.setter
    def map_path(self, map_path):
        self.log.info(f'Path of map is set to be {map_path}')
        if not isinstance(map_path, str):
            self.log.warning(f'Path of maps must be a \'str\'.')
            raise TypeError
        self._map_path = map_path

    def _get_weight_hist(self, file_name):
        file_path = f'{self.map_path}/{file_name}'

        utnr.load_json(file_path)
        return utnr.load_json(file_path)

    def get_target_weight(self, df):
        df = df.Define('q2_temp', 'Jpsi_M*Jpsi_M')

        df = utils.getMatrix(df, [ f'q2_temp'])

        hist    = self._get_weight_hist(self._default_hist)
        bound   = hist['bound']
        wgt_map = hist['wgt']

        all_wgt = []

        for [q2] in df:
            if q2 < 15500000:
                q2 = 15500000+1
            elif q2 > 22000000:
                q2 = 22000000-1

            index_bin = np.digitize( q2, bound )
            try:
                wgt       = wgt_map[index_bin-1]
            except:
                self.log.error(f'q2({q2}) belongs to the {index_bin-1} bin.')

            all_wgt.append(wgt)

        return np.array(all_wgt)

