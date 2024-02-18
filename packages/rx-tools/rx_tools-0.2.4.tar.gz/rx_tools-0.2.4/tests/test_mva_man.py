import ROOT
import utils
import utils_noroot as utnr
import os
import numexpr
import style
import logging
import numpy
import matplotlib.pyplot as plt

from rk.mva import mva_man 

log=utnr.getLogger(__name__)
#-----------------------------
def get_df_data(df):
    d_data_in = df.AsNumpy()
    d_data_fl = {}
    for name, data in d_data_in.items():
        str_data_type = str(data.dtype)

        elm          = data[0]
        elm_type     = type(elm)
        str_elm_type = str(elm_type)

        if   numpy.issubdtype(data.dtype, numpy.number) or 'RVec<float>' in str_elm_type:
            pass
        elif data.dtype == numpy.dtype(object):
            try:
                data = data.astype(int)
                log.warning('Transforming column {} of type {} to int'.format(name, str_data_type))
            except:
                log.error('Could not transform {} of type {} to int'.format(name, str_data_type))
                print(data)
                raise
        elif not numpy.issubdtype(data.dtype, numpy.number):
            log.warning('Skipping column {} of type {}'.format(name, str_data_type))
            continue

        d_data_fl[name] = data

    return d_data_fl
#-----------------------------
class data:
    bdtdir =f'{os.environ["MVADIR"]}/electron/bdt_v10.14.a0v2ss'
    dir_ee =f'{os.environ["DATDIR"]}/ctrl_ee/v10.11tf.a0v1.3.0.1.0.0_v3'
    dir_mm =f'{os.environ["DATDIR"]}/ctrl_mm/v10.11tf.a0v1.1.1.1.0.0_v3'
    plotdir= 'tests/mva_man'

    os.makedirs(plotdir, exist_ok=True)
#-----------------------------
def plot(arr_bdt_fil, arr_bdt_rdr, plotdir, treename):
    l_h_bdt = []
    h_bdt_fil = utils.arr_to_hist('h_bdt_fil',   'File', 100, 0, 1.1, arr_bdt_fil)
    l_h_bdt.append(h_bdt_fil)

    h_bdt_rdr = utils.arr_to_hist('h_bdt_rdr', 'Reader', 100, 0, 1.1, arr_bdt_rdr)
    l_h_bdt.append(h_bdt_rdr)

    plotpath='{}/{}_{}.png'.format(plotdir, treename, 'bdt_dist')

    d_opt={}
    d_opt['sty']    = ['hist'] * len(l_h_bdt)
    d_opt['ratio']  = True if len(l_h_bdt) > 1 else False
    d_opt['yminr']  = 0.98 
    d_opt['ymaxr']  = 1.02 
    d_opt['legend'] = 1 

    utils.plot_histograms(l_h_bdt, plotpath, d_opt=d_opt)
#-----------------------------
def test_cut(wp, df, arr_bdt_rdr):
    expr_fil = 'BDT > {}'.format(wp)
    expr_wrt = 'BDT_wrt > {}'.format(wp)

    arr_flg_rdr = numexpr.evaluate(expr_fil, {'BDT' : arr_bdt_rdr})
    arr_int_rdr = arr_flg_rdr.astype(int)
    rdr_pas     = arr_int_rdr.sum() 
    rdr_tot     = arr_int_rdr.size
    rdr_eff     = rdr_pas / rdr_tot

    df_fil      = df.Filter(expr_fil)
    df_wrt      = df.Filter(expr_wrt)

    fil_tot     = df.Count().GetValue()
    fil_pas     = df_fil.Count().GetValue()
    fil_eff     = fil_pas / fil_tot

    wrt_tot     = df.Count().GetValue()
    wrt_pas     = df_wrt.Count().GetValue()
    wrt_eff     = wrt_pas / wrt_tot

    log.info(expr_fil)
    log.info(expr_wrt)
    log.info('{0:<20}{1:<20}{2:<20}{3:.5f}'.format('Reader' , rdr_tot, rdr_pas, rdr_eff))
    log.info('{0:<20}{1:<20}{2:<20}{3:.5f}'.format('File'   , fil_tot, fil_pas, fil_eff))
    log.info('{0:<20}{1:<20}{2:<20}{3:.5f}'.format('Written', wrt_tot, wrt_pas, wrt_eff))
#-----------------------------
@utnr.timeit
def test_add_score(df, treename):
    plotdir='tests/mva/test_add_score/'
    utnr.make_dir_path(plotdir)
    
    man=mva_man(df, data.bdtdir, treename)
    df=man.add_scores('bdt')
    
    arr_bdt_fil=df.AsNumpy(['BDT'])['BDT']
    arr_bdt_rdr=df.AsNumpy(['bdt'])['bdt']

    plot(arr_bdt_fil, arr_bdt_rdr, plotdir, treename)
#-----------------------------
def run_tests(ifile_path, itree_path):
    '''Check if mva_man.add_scores works'''
    log.visible('')
    log.visible(f'Testing: test_add_score for {itree_path}')
    df_mm=ROOT.RDataFrame(itree_path, ifile_path)
    test_add_score(df_mm, itree_path)
    log.visible(f'Passed: test_add_score for {itree_path}')
#-----------------------------
def test_empty():
    df = ROOT.RDataFrame(10)
    df = df.Define('KFold', '1')
    df = df.Filter('KFold == 2')

    man=mva_man(df, data.bdtdir, 'ETOS')
    man.get_scores()
#-----------------------------
def test_allyears():
    for year in ['2011', '2012', '2015', '2016', '2017', '2018']:
        file_path =f'{data.dir_ee}/{year}_skimmed.root'
        run_tests(file_path, 'ETOS')

        file_path =f'{data.dir_mm}/{year}_skimmed.root'
        run_tests(file_path, 'MTOS')
#-----------------------------
def get_rdf(proc=None, version=None, year=None, nentries=1000):
    filepath = f'{os.environ["DATDIR"]}/{proc}/{version}/{year}.root'

    rdf = ROOT.RDataFrame('KEE', filepath)
    rdf = rdf.Range(nentries)

    return rdf
#-----------------------------
def plot_bdt(rdf):
    arr_bdt_prc = rdf.AsNumpy(['bdt_prc'])['bdt_prc']
    arr_bdt_cmb = rdf.AsNumpy(['bdt_cmb'])['bdt_cmb']

    plt.hist(arr_bdt_prc, bins=30, range=[0, 1], histtype='step', label='Prec')
    plt.hist(arr_bdt_cmb, bins=30, range=[0, 1], histtype='step', label='SS')

    plot_path = f'{data.plotdir}/prc_cmb.png'
    log.visible(f'Saving to: {plot_path}')

    plt.legend()
    plt.grid()
    plt.savefig(plot_path)
    plt.close('all')
#-----------------------------
def test_prec():
    rdf      = get_rdf(proc='data_ee', version='v10.18is', year='2018')
    bdtdir   = f'{os.environ["MVADIR"]}/electron/bdt_v10.18is.prec'
    treename = 'ETOS'

    man=mva_man(rdf, bdtdir, treename)
    rdf=man.add_scores('bdt')
#-----------------------------
def test_comb():
    rdf      = get_rdf(proc='data_ee', version='v10.18is', year='2018')
    bdtdir   = f'{os.environ["MVADIR"]}/electron/bdt_v10.11tf.a0v2ss'
    treename = 'ETOS'

    man=mva_man(rdf, bdtdir, treename)
    rdf=man.add_scores('bdt')
#-----------------------------
def test_both():
    rdf      = get_rdf(proc='data_ee', version='v10.18is', year='2018', nentries=50000)

    bdt_prc  = f'{os.environ["MVADIR"]}/electron/bdt_v10.18is.prec'
    bdt_cmb  = f'{os.environ["MVADIR"]}/electron/bdt_v10.11tf.a0v2ss'
    treename = 'ETOS'

    man_cmb=mva_man(rdf, bdt_cmb, treename)
    rdf=man_cmb.add_scores('bdt_cmb')

    man_prc=mva_man(rdf, bdt_prc, treename)
    rdf=man_prc.add_scores('bdt_prc')

    plot_bdt(rdf)
#-----------------------------
def test_tmva():
    rdf      = get_rdf(proc='data_ee', version='v10.18is', year='2018')
    bdtdir   = f'{os.environ["MVADIR"]}/electron/bdt_v10.11tf.a0v2ss'
    treename = 'ETOS'



    #man=mva_man(rdf, bdtdir, treename)
    #rdf=man.add_scores('bdt')
#-----------------------------
def main():
    test_tmva()

    return
    test_empty()
    test_prec()
    test_comb()
    test_both()
#-----------------------------
if __name__ == '__main__':
    main()
#-----------------------------

