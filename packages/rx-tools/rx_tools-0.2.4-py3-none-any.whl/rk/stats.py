import utils_noroot as utnr
import os
import ROOT

#--------------------------------
class gen_yld:
    log=utnr.getLogger('gen_yld')
    #--------------------------------
    def __init__(self, proc=None, year=None, vers=None):
        self._proc = proc
        self._year = year
        self._vers = vers

        self._l_proc = ['sign_ee', 'sign_mm', 'ctrl_ee', 'ctrl_mm', 'psi2_ee', 'psi2_mm']
        self._l_year = ['2011', '2012', '2015', '2016', '2017', '2018']

        self._tree_name   = 'gen'

        self._initialized = False
    #--------------------------------
    def _initialize(self):
        if self._initialized:
            return

        utnr.check_included(self._proc, self._l_proc)
        utnr.check_included(self._year, self._l_year)

        self._initialized = True
    #--------------------------------
    def _get_path(self):
        dat_dir = os.environ['DATDIR']

        dat_path = f'{dat_dir}/{self._proc}/{self._vers}/{self._year}.root'

        utnr.check_file(dat_path)

        return dat_path
    #--------------------------------
    def nevents(self):
        self._initialize()

        file_path = self._get_path()
        df        = ROOT.RDataFrame(self._tree_name, file_path)
        value     = df.Count().GetValue()

        if value <= 0:
            self.log.error(f'Invalid number of entries: {value}')
            raise

        return value
#--------------------------------

