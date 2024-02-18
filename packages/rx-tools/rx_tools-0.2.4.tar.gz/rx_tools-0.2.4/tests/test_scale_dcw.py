from rk.scale_dcw import scale
from rk.scale_dcw import scale_gen_mat
from rk.scale_dcw import get_gen_yld
from rk.scale_dcw import get_gen_cor

import numpy
import ROOT

import rk.utilities as rkut 
import utils_noroot as utnr
import utils

log=utnr.getLogger(__name__)

#--------------------------
#TODO: Implement test with 
#comparison of values
#--------------------------
def get_gen_cor_1():
    for year in ['0', '1']:
        corr = get_gen_cor(year, '', scale= True)
        print(corr)
        corr = get_gen_cor(year, '', scale=False)
        print(corr)
#--------------------------
def get_gen_yld_1():
    log.info('{0:<20}{1:<20}{2:<20}{3:<20}'.format('process', 'channel', 'year', 'nevs'))
    d_opt={}
    d_opt['zeroerrors'] = True
    d_opt['yname']      = 'Events' 

    for process in ['ctrl', 'psi2']:
        for channel in ['ee', 'mm'] + ['ETOS', 'GTIS', 'MTOS']: 
            plotpath = 'tests/scale_dcw/evs_{}_{}.png'.format(process, channel)
            d_data={}
            l_data=[]

            for dset in l_dset:
                y1, y2 = rkut.getYears(dset)

                nevs   = get_gen_yld(process, channel, dset, scale=False)
                nevs_1 = get_gen_yld(process, channel,   y1, scale=False)
                nevs_2 = get_gen_yld(process, channel,   y2, scale=False)

                if nevs == nevs_1 + nevs_2:
                    log.info('{0:<20}{1:<20}{2:<20}{3:<20.7e}'.format(process, channel,   y1, nevs_1))
                    log.info('{0:<20}{1:<20}{2:<20}{3:<20.7e}'.format(process, channel,   y2, nevs_2))
                    log.info('{0:<20}{1:<20}{2:<20}{3:<20.7e}'.format(process, channel, dset,   nevs))
                else:
                    log.error('{0:<20}{1:<20}{2:<20}{3:<20.7e}'.format(process, channel,   y1, nevs_1))
                    log.error('{0:<20}{1:<20}{2:<20}{3:<20.7e}'.format(process, channel,   y2, nevs_2))
                    log.error('{0:<20}{1:<20}{2:<20}{3:<20.7e}'.format(process, channel, dset,   nevs))
                    raise

                l_data.append([y1  , nevs_1])
                l_data.append([y2  , nevs_2])
                l_data.append([dset,   nevs])

            arr_data = numpy.array(l_data)
            d_data[''] = arr_data

            utils.plot_arrays(d_data, plotpath, 1, 0, 0, d_opt=d_opt)
#--------------------------
def get_gen_yld_2():
    scale.verbose = True
    for year in ['0', '1', '01']:
        yld_s = get_gen_yld('', '', year, scale =  True)
        yld_n = get_gen_yld('', '', year, scale = False)

        if   year == '0'  and yld_s != 1.5:
            log.error('{0:<20}{1:<20}  '.format('Year'    ,  year))
            log.error('{0:<20}{1:<20.3}'.format('Value'   , yld_s))
            log.error('{0:<20}{1:<20.3}'.format('Expected',   1.5))
            raise
        elif year == '1'  and yld_s != 6.0:
            log.error('{0:<20}{1:<20}  '.format('Year'    ,  year))
            log.error('{0:<20}{1:<20.3}'.format('Value'   , yld_s))
            log.error('{0:<20}{1:<20.3}'.format('Expected',   6.0))
            raise
        elif year == '01' and yld_s != 12: 
            log.error('{0:<20}{1:<20}  '.format('Year'    ,  year))
            log.error('{0:<20}{1:<20.3}'.format('Value'   , yld_s))
            log.error('{0:<20}{1:<20.3}'.format('Expected',   12.))
            raise
        else:
            log.info('Year : ' + year)
            log.info('Scale: {:.3f}'.format(yld_s))
            log.info('No Scale: {:.3f}'.format(yld_n))
#--------------------------
def get_alpha(year):
    if year not in ['2011', '2012', '2015', '2016', '2017', '2018', '0', '1']:
        log.error('Only non-composite years are allowed')
        raise

    lum_u = rkut.get_lumi(year, 'up')
    lum_d = rkut.get_lumi(year, 'dn')

    sim_u = get_gen_yld('', '', year, 'up', scale=False)
    sim_d = get_gen_yld('', '', year, 'dn', scale=False)

    alpha = (sim_d / sim_u) * (lum_u/lum_d)

    return alpha
#--------------------------
def get_beta(y1, y2):
    alpha_1  = get_alpha(y1)
    alpha_2  = get_alpha(y2)
    #---------
    lum_y1_u = rkut.get_lumi(y1, 'up')
    lum_y1_d = rkut.get_lumi(y1, 'dn')

    lum_y2_u = rkut.get_lumi(y2, 'up')
    lum_y2_d = rkut.get_lumi(y2, 'dn')

    lum_y1   = lum_y1_d + lum_y1_u
    lum_y2   = lum_y2_d + lum_y2_u
    #---------
    sim_y1_u = get_gen_yld('', '', y1, 'up', scale=False)
    sim_y1_d = get_gen_yld('', '', y1, 'dn', scale=False)

    sim_y2_u = get_gen_yld('', '', y2, 'up', scale=False)
    sim_y2_d = get_gen_yld('', '', y2, 'dn', scale=False)
    #---------
    num = (sim_y2_u * alpha_2 + sim_y2_d)
    den = (sim_y1_u * alpha_1 + sim_y1_d)

    beta = (num / den) * (lum_y1 / lum_y2)

    return beta
#--------------------------
def get_mat(year):
    df = ROOT.RDataFrame(2)
    df = df.Define('year', str(year))

    treename = 'tree'
    filepath = '/tmp/test_scale_{}.root'.format(year)

    df.Snapshot(treename, filepath)

    df = ROOT.RDataFrame(treename, filepath)
    df.treename = treename
    df.filepath = filepath 

    mat = numpy.array([[1., -1], [1., +1]])

    return (mat, df)
#--------------------------
#--------------------------
def test_pol(d_arg):
    year       = d_arg['year']
    mat, _     = get_mat(year)

    arr_wgt    = mat.T[0]
    wt_dn_n    = arr_wgt[ 0]
    wt_up_n    = arr_wgt[+1]

    scl        = scale()
    mat_scl, _ = scl.combine_polarizations(mat, d_arg) 

    arr_wgt    = mat_scl.T[0]
    wt_dn_s    = arr_wgt[ 0]
    wt_up_s    = arr_wgt[+1]

    alpha      = get_alpha(year)
    if wt_dn_s == wt_dn_n and wt_up_s == alpha * wt_up_n:
        log.info('{0:<20}{1:<20}{2:<20}{3:<20.3}{4:<20.3}{5:<20.3}'.format(year, proc, chan, alpha, wt_up_s, wt_dn_s))
    else:
        log.error('{0:<20}{1:<20}{2:<20}{3:<20.3}{4:<20.3}{5:<20.3}'.format(year, proc, chan, alpha, wt_up_s, wt_dn_s))
        raise
#--------------------------
def test_yar(d_arg):
    y1   = d_arg['y1']
    y2   = d_arg['y2']

    mat_y1, df_y1 = get_mat(y1)
    mat_y2, df_y2 = get_mat(y2)

    alpha_X   = get_alpha(y1) 
    alpha_Y   = get_alpha(y2) 
    beta      = get_beta(y1, y2)

    d_loc = dict(d_arg)
    d_loc.update({'df_y1' : df_y1, 'df_y2' : df_y2})

    scl       = scale()
    for i in range(3):
        d_cmb     = scl.combine_years(mat_y1, mat_y2, d_loc)

        tp_wgt_y1 = d_cmb['tp_wgt_y1']
        tp_wgt_y2 = d_cmb['tp_wgt_y2']
        tp_wgt    = d_cmb['tp_wgt'   ]


        bt   = tp_wgt_y1[0][0]
        ax_b = tp_wgt_y1[0][1]
        one  = tp_wgt_y2[0][0]
        ay   = tp_wgt_y2[0][1]

        ax   = ax_b / bt

        log.info('{0:<20}{1:<20}{2:<20}'.format('Quantity',  'Calculated', 'Expected'))
        if ax == alpha_X and ay == alpha_Y and bt == beta and one == 1:
            log.info('{0:<20}{1:<20}{2:<20}'.format('alpha_X',  ax, alpha_X))
            log.info('{0:<20}{1:<20}{2:<20}'.format('alpha_Y',  ay, alpha_Y))
            log.info('{0:<20}{1:<20}{2:<20}'.format('Beta'   ,  bt,    beta))
            log.info('{0:<20}{1:<20}{2:<20}'.format('1'      , one,       1))
        else:
            log.error('{0:<20}{1:<20}{2:<20}'.format('alpha_X', ax, alpha_X))
            log.error('{0:<20}{1:<20}{2:<20}'.format('alpha_Y', ay, alpha_Y))
            log.error('{0:<20}{1:<20}{2:<20}'.format('Beta'   , bt,    beta))
            log.error('{0:<20}{1:<20}{2:<20}'.format('1'      , one,      1))

            raise
#--------------------------
def test_scale_pola(d_arg):
    year         = d_arg['year']

    (mat_org, _)     = get_mat(year)
    arr_scl, _, _, _ = scale_gen_mat(d_arg, mat_org)

    alpha = get_alpha(year)

    ax = arr_scl[1]

    if alpha != ax:
        log.error('Alpha calculated: {}'.format(ax))
        log.error('Alpha expected: {}'.format(alpha))
        raise

    print(mat_org)
    print(arr_scl)
#--------------------------
def test_scale_year(d_arg):
    y1 = d_arg['y1']
    y2 = d_arg['y2']

    (mat_org_1, _) = get_mat(y1)
    (mat_org_2, _) = get_mat(y2)

    _, ax, ay, bt  = scale_gen_mat(d_arg, mat_org_1, mat_org_2)

    alpha_X = get_alpha(y1)
    alpha_Y = get_alpha(y2)
    beta    = get_beta(y1, y2)

    if alpha_X == ax and alpha_Y == ay and beta == bt:
        log.info('{0:<20}{1:<20}{2:<20}'.format('alpha_X',  ax, alpha_X))
        log.info('{0:<20}{1:<20}{2:<20}'.format('alpha_Y',  ay, alpha_Y))
        log.info('{0:<20}{1:<20}{2:<20}'.format('Beta'   ,  bt,    beta))
    else:
        log.error('{0:<20}{1:<20}{2:<20}'.format('alpha_X',  ax, alpha_X))
        log.error('{0:<20}{1:<20}{2:<20}'.format('alpha_Y',  ay, alpha_Y))
        log.error('{0:<20}{1:<20}{2:<20}'.format('Beta'   ,  bt,    beta))

        raise
#--------------------------
#--------------------------
def test_no_scale_pola(d_arg):
    year         = d_arg['year']

    (mat_org, _)     = get_mat(year)
    arr_scl, _, _, _ = scale_gen_mat(d_arg, mat_org, do_scale=False)

    arr_org = mat_org.T[0]

    print(arr_org)
    print(arr_scl)

    if not numpy.array_equal(arr_org, arr_scl):
        log.error('Arrays differ')
        raise
#--------------------------
def test_no_scale_year(d_arg):
    y1 = d_arg['y1']
    y2 = d_arg['y2']

    (mat_org_1, _) = get_mat(y1)
    (mat_org_2, _) = get_mat(y2)

    mat_org          = numpy.concatenate((mat_org_1, mat_org_2))
    arr_org          = mat_org.T[0]
    arr_scl, _, _, _ = scale_gen_mat(d_arg, mat_org_1, mat_org_2, do_scale=False)

    print(arr_org)
    print(arr_scl)
    if not numpy.array_equal(arr_org, arr_scl):
        log.error('Arrays differ')
        raise
#--------------------------
#--------------------------
proc = ''
chan = ''

l_dset=['r1', 'r2p1', 'r2p2']

get_gen_cor_1()
get_gen_yld_1()
get_gen_yld_2()

d_arg = {'proc' : proc, 'chan' : chan, 'year' : '0', 'df' : None}
test_pol(d_arg)

d_arg = {'proc' : proc, 'chan' : chan, 'year' : '1', 'df' : None}
test_pol(d_arg)

d_arg = {'proc' : proc, 'chan' : chan, 'y1' : '0', 'y2' : '1', 'df' : None}
test_yar(d_arg)

d_arg = {'proc' : proc, 'chan' : chan, 'year' : '0'}
test_scale_pola(d_arg)

d_arg = {'proc' : proc, 'chan' : chan, 'year' : '0'}
test_scale_pola(d_arg)

d_arg = {'proc' : proc, 'chan' : chan, 'y1' : '0', 'y2' : '1'}
test_scale_year(d_arg)


d_arg = {'proc' : proc, 'chan' : chan, 'year' : '0'}
test_no_scale_pola(d_arg)

d_arg = {'proc' : proc, 'chan' : chan, 'y1' : '0', 'y2' : '1'}
test_no_scale_year(d_arg)

