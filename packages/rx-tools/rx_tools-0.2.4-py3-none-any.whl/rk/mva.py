import ROOT
import numpy
import tqdm
import sys

import rk.utilities as rk_utils
import utils_noroot as utnr
import utils

#------------------------------------------
class mva_man:
    log=utnr.getLogger(__name__)
    no_bar        = False
    etos_for_mtos = True 
    #------------------------------------------
    def __init__(self, df, bdtdir, trigger):
        self.df          = df
        self.bdtdir      = bdtdir
        self.trigger     = trigger 
        self.initialized = False
        self.d_reader    = {}
        self.l_variable  = []

        self.__year      = None
        self.__arr_score = None
        self._empty_rdf  = None
        self.__year_col  = 'yearLabbel'
    #------------------------------------------
    def __initialize(self):
        if self.initialized:
            return

        self.df = self._define_vars()

        self._is_empty = True if self.df.Count().GetValue() == 0 else False
        if self._is_empty:
            self.log.warning(f'Input dataframe is empty')
            return

        if self.etos_for_mtos not in [True, False]:
            self.log.error('Invalid value for member "etos_for_mtos":{}'.format(self.etos_for_mtos))
            raise
        
        arr_fold = self.__get_folds()
        for fold in arr_fold:
            bdtpath = self.__get_bdtpath(fold)
            str_bdtpath = ROOT.std.string(bdtpath)

            self.d_reader[fold]  = ROOT.TMVA.Experimental.RReader(str_bdtpath)
            self.log.info('{0:<10}{1:<3}{2:100}'.format(fold, '>', bdtpath))

        l_item      = list(self.d_reader.items())
        _, reader   = l_item[0]
        l_expresion = reader.GetVariableNames()

        preffix=id(self)
        for i_var, expresion in enumerate(l_expresion):
            varname=f'tmva_{preffix}_{i_var}'
            self.log.info(f'{varname:<30}{">":<3}{expresion.c_str():40}')
            self.df = self.df.Define(varname, '(float){}'.format(expresion) )

            self.l_variable.append(varname)

        self.initialized = True
    #------------------------------------------
    def _define_vars(self):
        df = self.df

        self.log.info('-------------------')
        self.log.info('Defining variables:')

        if 'prec' in self.bdtdir:
            df = self._define_var(df, "min_SPT",       'TMath::Min(B_L1_CC_SPT,B_L2_CC_SPT)')
            df = self._define_var(df, "max_SPT",       'TMath::Max(B_L1_CC_SPT,B_L2_CC_SPT)')
            df = self._define_var(df, "min_IT",        'TMath::Min(B_L1_CC_IT,B_L2_CC_IT)')
            df = self._define_var(df, "max_MULT",      'TMath::Max(B_L1_CC_MULT,B_L2_CC_MULT)')
            df = self._define_var(df, "min_ll_IPCHI2", 'TMath::Min(TMath::Sqrt(L1_IPCHI2_OWNPV),TMath::Sqrt(L2_IPCHI2_OWNPV))')
        self.log.info('-------------------')

        return df
    #------------------------------------------
    def _define_var(self, df, name, expr):
        v_col = df.GetColumnNames()
        l_col = [ col.c_str() for col in v_col ]

        if name in l_col:
            self.log.info(f'{"Skipping":<20}{name:>20}{"--->":20}{expr:>50}')
            return df

        self.log.info(f'{"Defining":<20}{name:>20}{"--->":20}{expr:>50}')
        df = df.Define(name, expr)

        return df
    #------------------------------------------
    def __set_year(self):
        if self.__year is not None:
            return

        utils.df_has_col(self.df, self.__year_col, fail=True)

        arr_year = self.df.AsNumpy([self.__year_col])[self.__year_col]
        arr_year = numpy.unique(arr_year)
        arr_year = arr_year.astype(int)
        arr_year = arr_year.astype(str)
        l_year   = arr_year.tolist()

        if len(l_year) != 1:
            self.log.error(f'Not found one and only one year: l_year')
            raise

        self.__year = l_year[0]
        if self.__year not in ['2011', '2012', '2015', '2016', '2017', '2018']:
            self.log.error(f'Unrecognized year {year}')
            raise
    #------------------------------------------
    def __get_bdtpath(self, fold):
        self.__set_year()

        if   self.trigger == 'ETOS':
            bdtpath = '{}/{}/RK_{}_ETOS_BDTG.weights.xml'.format(self.bdtdir, self.__year, fold)
        elif self.trigger in ['HTOS', 'GTIS']:
            bdtpath = '{}/{}/RK_{}_ALLTRIG_BDTG.weights.xml'.format(self.bdtdir, self.__year, fold)
        elif self.trigger == 'MTOS' and self.etos_for_mtos == True:
            bdtpath = '{}/{}/RK_{}_ETOS_BDTG.weights.xml'.format(self.bdtdir, self.__year, fold)
        elif self.trigger == 'MTOS' and self.etos_for_mtos == False:
            bdtpath = '{}/{}/RK_{}_MTOS_BDTG.weights.xml'.format(self.bdtdir, self.__year, fold)
            self.log.warning('Using separate BDT for mTOS category: ' + bdtpath)
        else:
            self.log.error('Trigger {} not recognized'.format(self.trigger))
            raise

        utnr.check_file(bdtpath)

        return bdtpath
    #------------------------------------------
    def __get_folds(self):
        arr_fold = self.df.AsNumpy(['KFold'])['KFold']
        arr_fold = numpy.unique(arr_fold)
        arr_fold = numpy.sort(arr_fold)

        if arr_fold.size <= 0:
            self.log.error(f'Found invalid number of folds in tree: {arr_fold.size}')
            raise
        else:
            self.log.info(f'Found folds: {arr_fold}')

        return arr_fold
    #------------------------------------------
    def __get_data(self):
        df=self.df
        arr_fold = self.df.AsNumpy(['KFold'])['KFold']
    
        d_vars = df.AsNumpy(self.l_variable)
    
        l_vals = list(d_vars.values())
    
        arr_arr_vals = numpy.array(l_vals)
        arr_arr_vals = arr_arr_vals.T
        
        return (arr_fold, arr_arr_vals)
    #------------------------------------------
    def __get_score(self, fold, arr_vals):
        fold=fold.item()
        try:
            model=self.d_reader[fold]
        except:
            self.log.error('Cannot find model for fold {}'.format(fold))
            raise

        arr_vals = arr_vals.copy(order='C')
        v_vals=ROOT.std.vector['float'](arr_vals)

        mva=model.Compute(v_vals)

        global pbar
        pbar.update(1)

        mva_val = mva[0]

        mva_val=rk_utils.transform_bdt(mva_val)

        return mva_val
    #------------------------------------------
    def get_scores(self):
        self.__initialize()
        if self._is_empty:
            return numpy.array([])

        if self.__arr_score is not None:
            return self.__arr_score

        self.log.info('Getting BDT scores')

        arr_fold, arr_arr_vals = self.__get_data()

        global pbar
        with tqdm.tqdm(total=arr_fold.size, file=sys.stdout, ascii=' -', disable=mva_man.no_bar) as pbar:
            v_get_mva=numpy.vectorize(self.__get_score, signature='(),(m)->()')
            arr_rdr = v_get_mva(arr_fold, arr_arr_vals)

        self.__arr_score = arr_rdr

        return self.__arr_score
    #------------------------------------------
    def add_scores(self, branchname):
        self.__initialize()
        if self._is_empty:
            return df 

        self.log.info(f'Adding BDT scores in column: {branchname}')

        arr_score=self.get_scores()

        df = utils.add_df_column(self.df, arr_score, branchname)

        return df
#------------------------------------------

