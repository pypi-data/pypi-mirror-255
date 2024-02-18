import rk.selection  as rk_sel
import utils_noroot  as utnr
import json
import os 

log=utnr.getLogger(__name__)
#---------------------------------------
class cut_getter:
    directory=None
    log=utnr.getLogger(__name__)
    def __init__(self):
        self.__initialized = False
        self.__l_mode      = ['rare_central', 'reso', 'psi', 'rare_high']
        self.__d_pres      = {'electron' : 3, 'muon' : 1}
        self.__d_file      = {}
    #------------------------------------
    def __initialize(self):
        if self.__initialized:
            return

        if self.directory is None:
            try:
                self.directory = os.environ['SELDIR']
                self.log.info('Using selection directory ' + self.directory)
            except:
                self.log.error('Directory member not specified and SELDIR environment variable not set')
                raise

        utnr.check_dir(self.directory)

        for mode in self.__l_mode:
            for chan, pres in self.__d_pres.items():
                jsonpath = '{}/{}_{}_{}.json'.format(self.directory, mode, pres, chan)
                utnr.check_file(jsonpath)
                self.__d_file[(mode, chan)] = jsonpath

        self.__initialized = True
    #------------------------------------
    def get_cut(self, cut, mode, chan, year):
        self.__initialize()

        #------------------
        if   chan in list(self.__d_pres.keys()):
            pass
        elif chan in ['ETOS', 'GTIS', 'HTOS', 'KEE']:
            chan = 'electron'
        elif chan in ['MTOS', 'KMM']:
            chan = 'muon'
        else:
            log.error('Invalid channel ' + chan)
            raise
        #------------------
        if   mode in self.__l_mode:
            pass
        elif mode == 'ctrl':
            mode = 'reso'
        elif mode == 'psi2':
            mode = 'psi'
        elif mode in ['sign_ee', 'sign_mm']:
            self.log.error('Process {}, cannot be associated to mode unambiguously, could be central or high'.format(mode))
            raise
        else:
            self.log.error('Invalid process ' + mode)
            raise
        #------------------
        jsonpath = self.__d_file[(mode, chan)]
        d_cut = json.load(open(jsonpath))

        try:
            cut = d_cut[cut]
        except:
            self.log.error('Cut {} not found in:'.format(cut))
            print(d_cut.keys())

        return cut 
#------------------------------------
def get_cut(cut, mode, chan, year):
    ob=cut_getter()
    cut = ob.get_cut(cut, mode, chan, year)

    return cut 
#------------------------------------

