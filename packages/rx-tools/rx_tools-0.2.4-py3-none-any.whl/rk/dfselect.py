import utils_noroot   as utnr
import utils

import read_selection as rs
import logging

from rk.selection import selection as rksl

#--------------------------------------------------
class selection:
    """
    Class used to apply selections to dataframes
    """
    log=utnr.getLogger('selection')
    #--------------------------------------------------
    def __init__(self, df, sample=None, trigger=None, year=None, kind=None, q2bin=None):
        self.__l_sample = ['data_ee', 'data_mm', 'ctrl_ee', 'ctrl_mm', 'psi2_ee', 'psi2_mm', 'test']
        self.__l_trigger= ['MTOS', 'ETOS', 'GTIS', 'test']
        self.__l_year   = ['2011', '2012', '2015', '2016', '2017', '2018']
        self.__l_kind   = ['all_gorder', 'final_nobdt_gorder', 'calibration', 'test', 'loose_000']
        self.__l_q2bin  = ['jpsi', 'psi2']

        self.__df       = df 
        self.__sample   = sample
        self.__trigger  = trigger
        self.__year     = year
        self.__kind     = kind
        self.__q2bin    = q2bin 

        self.__check_args()
    #--------------------------------------------------
    def __check_args(self):
        utnr.check_included(self.__sample , self.__l_sample )
        utnr.check_included(self.__trigger, self.__l_trigger)
        utnr.check_included(self.__kind   , self.__l_kind   )
        utnr.check_included(self.__year   , self.__l_year   )
    #--------------------------------------------------
    def get_df(self, fraction):
        d_cut = rksl(self.__kind, self.__trigger, self.__year, self.__sample, q2bin=self.__q2bin)

        if  0 < fraction < 1:
            self.log.info(f'Using {fraction} fraction of dataset')
            df = utils.filter_df(self.__df, fraction)
        elif fraction == 1:
            df = self.__df
        else:
            self.log.error(f'Invalid value of fraction: {fraction}')
            raise

        for key, cut in d_cut.items():
            self.log.debug(f'{"Adding":<10}{"--->":<10}{key:<20}')
            df = df.Filter(cut, key)

        self.log.debug('Applying selection')
        if self.log.level < logging.WARNING:
            rep = df.Report()
            rep.Print()

        return df
#--------------------------------------------------
def apply_selection(df, sample=None, trigger=None, year=None, kind=None, q2bin=None, fraction=1):
    utnr.check_numeric(fraction)

    obj = selection(df, sample=sample, trigger=trigger, year=year, kind=kind, q2bin=q2bin)
    df  = obj.get_df(fraction)

    return df
#--------------------------------------------------
