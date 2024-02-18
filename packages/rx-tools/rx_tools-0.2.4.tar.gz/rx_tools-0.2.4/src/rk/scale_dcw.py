import numpy
import ROOT

import utils_noroot as utnr 
import rk.utilities as rkut

log=utnr.getLogger(__name__)
#------------------------------
class scale:
    verbose=False
    def __init__(self, do_scale = True):
        self.do_scale = do_scale
        self.storage  = None
    #------------------------------
    def combine_polarizations(self, mat, d_arg):
        if not self.do_scale:
            return (mat, 1)

        year = utnr.get_from_dic(d_arg, 'year')
        proc = utnr.get_from_dic(d_arg, 'proc')
        chan = utnr.get_from_dic(d_arg, 'chan')

        arr_wgt = mat.T[0]
        arr_pol = mat.T[1]
    
        str_arr = numpy.array2string(arr_wgt)
        log.debug('Array before polarity combination: ' + str_arr)

        if 'index' in d_arg:
            index = d_arg['index']
        else:
            index = None
    
        arr_wgt, scale = self.__scale_by_polarization(arr_wgt, arr_pol, year, proc, chan, index = index)
    
        mat_scl = numpy.array([arr_wgt, arr_pol]).T
    
        str_arr = numpy.array2string(arr_wgt)
        log.debug('Array before polarity combination: ' + str_arr)
    
        return (mat_scl, scale)
    #------------------------------
    def combine_years(self, mat_y1, mat_y2, d_arg): 
        chan  = utnr.get_from_dic(d_arg, 'chan')
        proc  = utnr.get_from_dic(d_arg, 'proc')

        y1    = utnr.get_from_dic(d_arg, 'y1')
        y2    = utnr.get_from_dic(d_arg, 'y2')

        if   'df_y1'     in d_arg and 'df_y2'     in d_arg:
            df_y1 = d_arg['df_y1']
            df_y2 = d_arg['df_y2']
        elif 'df_y1' not in d_arg and 'df_y2' not in d_arg:
            df_y1 = None 
            df_y2 = None 
        else:
            log.error('Either dataframe is missing from input')
            raise
        #-----------------
        d_arg_y1 = dict(d_arg)
        d_arg_y1.update({'year' : y1})

        d_arg_y2 = dict(d_arg)
        d_arg_y2.update({'year' : y2})

        #Get alphas
        mat_y1_scl, alpha_y1 = self.combine_polarizations(mat_y1, d_arg_y1)
        mat_y2_scl, alpha_y2 = self.combine_polarizations(mat_y2, d_arg_y2)
    
        log.debug('{0:<20}{1:<20}'.format('alpha_X', alpha_y1))
        log.debug('{0:<20}{1:<20}'.format('alpha_Y', alpha_y2))

        #Get beta
        if self.do_scale:
            s_y1_up = get_gen_yld(proc, chan, y1, 'up', scale=False)
            s_y1_dn = get_gen_yld(proc, chan, y1, 'dn', scale=False)
            s_y2_up = get_gen_yld(proc, chan, y2, 'up', scale=False)
            s_y2_dn = get_gen_yld(proc, chan, y2, 'dn', scale=False)
    
            lumi_y1 = rkut.get_lumi(y1, 'up') + rkut.get_lumi(y1, 'dn')
            lumi_y2 = rkut.get_lumi(y2, 'up') + rkut.get_lumi(y2, 'dn')
    
            r_sim = (s_y2_up * alpha_y2 + s_y2_dn) / (s_y1_up * alpha_y1 + s_y1_dn)
            r_lum = lumi_y1 / lumi_y2
    
            beta  = r_sim * r_lum
        else:
            beta  = 1
        #-------------
        #Scale
        #-------------
        arr_wgt_y1  = mat_y1_scl.T[0]
        arr_wgt_sc  = beta * arr_wgt_y1

        tp_y1       = (arr_wgt_sc, df_y1)
        #-------------
        arr_wgt_y2  = mat_y2_scl.T[0]
        tp_y2       = (arr_wgt_y2 , df_y2)

        tp_wgt      = self.__merge_tuples(tp_y1, tp_y2)
        #-------------
        y1_sum = numpy.sum(arr_wgt_y1)
        sc_sum = numpy.sum(arr_wgt_sc)
        y2_sum = numpy.sum(arr_wgt_y2)
        res    = numpy.sum(tp_wgt[0])

        line = '{}{}{}{}{}{}{}'.format(y1_sum, '*', beta, '+', y2_sum, '=', res)
        if self.verbose:
            log.visible(line)
        #-------------
        return {'tp_wgt' : tp_wgt, 'tp_wgt_y1' : tp_y1, 'tp_wgt_y2' : tp_y2, 'alpha_y1' : alpha_y1, 'alpha_y2' : alpha_y2, 'beta' : beta}
    #------------------------------
    def __scale_by_polarization(self, arr_wgt, arr_pol, year, process, channel, index=None):
        #Need the actual yield at gen level, i.e. not scaled by luminosity or year
        gen_dn = float( get_gen_yld(process, channel, year, 'dn', scale=False) )
        gen_up = float( get_gen_yld(process, channel, year, 'up', scale=False) )
    
        lum_dn = rkut.get_lumi(year, 'dn') 
        lum_up = rkut.get_lumi(year, 'up') 
    
        scale  = (gen_dn / gen_up) * (lum_up / lum_dn)

        arr_scl= numpy.where(arr_pol == 1, scale, 1.)
        arr_pos= numpy.where(arr_pol == 1,     1, 0.)
        arr_neg= numpy.where(arr_pol == 1,     0, 1.)

        arr_wgt_pos = arr_wgt * arr_pos
        arr_wgt_neg = arr_wgt * arr_neg
        arr_wgt_scl = arr_wgt * arr_scl

        sum_pos = numpy.sum(arr_wgt_pos) 
        sum_neg = numpy.sum(arr_wgt_neg) 
        sum_aft = numpy.sum(arr_wgt_scl)

        key = 'scl_pol_{}_{}_{}_{}'.format(year, process, channel, index)
        idn = '{},{},{},{}'.format(year, process, channel, index)
        val = '{0:<20}{1:<20}{2:<3}{3:<3.3f}{4:<3}{5:<20}{6:<3}{7:20.3f}'.format(idn, sum_pos, '*', scale, '+', sum_neg, '=', sum_aft)
        if self.verbose:
            log.visible(val)

        if self.storage is not None:
            self.storage.add(key, val)

        return (arr_wgt_scl, scale)
    #------------------------------
    def __merge_tuples(self, tp_1, tp_2):
        arr_1, df_1 = tp_1
        arr_2, df_2 = tp_2

        arr_mrg = numpy.concatenate((arr_1, arr_2))
        if df_1 is None and df_2 is None:
            return (arr_mrg, None)
    
        utnr.check_attr(df_1, 'treename')
        utnr.check_attr(df_1, 'filepath')
        utnr.check_attr(df_2, 'treename')
        utnr.check_attr(df_2, 'filepath')
    
        treename_1 = df_1.treename
        treename_2 = df_2.treename
    
        if treename_1 != treename_2:
            log.error('Tree {} and {} are not the same.'.format(treename_1, treename_2))
            raise
    
        l_filepath = [df_1.filepath, df_2.filepath]
        df = ROOT.RDataFrame(treename_1, l_filepath)
        df.treename = treename_1
        df.filepath = l_filepath 
    
        return (arr_mrg, df)
#------------------------------
def scale_gen_mat(d_args, mat_y1, mat_y2 = None, do_scale=True, storage=None):
    scl=scale(do_scale=do_scale)
    scl.storage = storage

    if mat_y2 is None:
        (mat, alpha) = scl.combine_polarizations(mat_y1, d_args)
        arr=mat.T[0]
        tp_res = (arr, alpha, 1, 1)
    else:
        d_sta   = scl.combine_years(mat_y1, mat_y2, d_args)
        arr, _  = d_sta['tp_wgt']
        alpha_1 = d_sta['alpha_y1']
        alpha_2 = d_sta['alpha_y2']
        beta    = d_sta[    'beta']

        tp_res = (arr, alpha_1, alpha_2, beta)

    return tp_res 
#------------------------------
def get_gen_yld(process, channel, dset, polarization=None, skimmed=False, scale=True):
    d_args = {'proc' : process, 'chan' : channel}

    if dset in ['r1', 'r2p1', 'r2p2', '01']:
        y1, y2 = rkut.getYears(dset)
        mat_1  = rkut.get_gen_mat(process, channel, y1, polarization=polarization, skimmed=skimmed)
        mat_2  = rkut.get_gen_mat(process, channel, y2, polarization=polarization, skimmed=skimmed)
        if scale == False:
            mat = numpy.concatenate((mat_1, mat_2))
            arr_yld = mat.T[0]
        else:
            d_args.update({'y1' : y1, 'y2' : y2})
            arr_yld, _, _, _ = scale_gen_mat(d_args, mat_1, mat_2)
    else:
        d_args.update({'year' : dset})
        mat = rkut.get_gen_mat(process, channel, dset, polarization=polarization, skimmed=skimmed)
        if scale == False:
            arr_yld = mat.T[0]
        else:
            arr_yld, _, _, _ = scale_gen_mat(d_args, mat   ,   None)

    return numpy.sum(arr_yld)
#------------------------------
def get_gen_cor(year, process, scale=True):
    if year not in ['0', '1', '01'] and process not in ['ctrl', 'psi2']:
        log.error('Unsupported process ' + process)
        raise

    mm_yld = get_gen_yld(process, 'mm', year, scale=scale)
    ee_yld = get_gen_yld(process, 'ee', year, scale=scale)
    
    fac = mm_yld / float(ee_yld)

    return fac 
#------------------------------

