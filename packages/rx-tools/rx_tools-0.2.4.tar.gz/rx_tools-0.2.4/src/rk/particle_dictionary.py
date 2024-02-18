import pandas as pnd
import os

import utils_noroot as utnr 

#-------------------------------
class particle_dictionary:
    log = utnr.getLogger('particle_dictionary')
    #-------------------------------
    def __init__(self):
        self._initialized = False

        self._d_evt_par   = None
        self._d_par_evt   = None
    #-------------------------------
    def _initialize(self):
        self._load_data()
        self._make_dictionaries()
        self._initialized = True
    #-------------------------------
    def _load_data(self):
        table_dir   = os.environ['DBBDIR']
        table_path  = f'{table_dir}/ParticleTable.csv'
        utnr.check_file(table_path)

        try:
            self._df=pnd.read_csv(table_path, sep=';')
        except:
            self.log.error(f'Could not load: {table_path}')
            raise
    #-------------------------------
    def _make_dictionaries(self):
        self._d_evt_par = dict(zip(self._df.EVTGENNAME, self._df.PARTICLE  ))
    #-------------------------------
    def get_particle_name(self, evtg_name = None):
        self._initialize()

        try:
            par_name = self._d_evt_par[evtg_name]
        except:
            self.log.error(f'Cannot get particle name for {evtg_name}')
            raise

        return par_name
#-------------------------------


