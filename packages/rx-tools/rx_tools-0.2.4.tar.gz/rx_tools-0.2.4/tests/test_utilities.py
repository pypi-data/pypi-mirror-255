import rk.utilities as rkut 
import utils_noroot as utnr

from rk.scale_dcw import scale_gen_mat
from rk           import utilities     as rkut

import ROOT
import zfit
import numpy
import utils
import style
import pprint
import pandas as pnd

log=utnr.getLogger(__name__)

#-------------------------
class data:
    l_dset = ['r1', 'r2p1']
    l_year = ['2011', '2012', '2015', '2016', '2017', '2018']
    l_proc = ['ctrl', 'psi2']
    l_chan = ['ee', 'mm']
#-------------------------
def get_gen_mat_skim(skimmed):
    for proc in data.l_proc[:1]:
        for chan in data.l_chan[:1]:
            for year in data.l_year[:1]:
                mat = rkut.get_gen_mat(proc, chan, year, skimmed = skimmed)
                print(mat)
#-------------------------
def get_gen_mat():
    for proc in data.l_proc[:1]:
        for chan in data.l_chan[:1]:
            for year in data.l_year[:1]:
                mat_u = rkut.get_gen_mat(proc, chan, year, 'up')
                mat_d = rkut.get_gen_mat(proc, chan, year, 'dn')
                mat_b = rkut.get_gen_mat(proc, chan, year      )

                mat_t = numpy.concatenate((mat_d, mat_u))

                if not numpy.array_equal(mat_t, mat_b):
                    log.error('Merged matrices are inconsistent:')
                    print(mat_u)
                    print(mat_d)
                    print(mat_b)
                    print(mat_t)
                    raise
                else:
                    print(mat_u)
                    print(mat_d)
                    print(mat_b)
                    print('')
#-------------------------
def get_lumi():
    log.info('{0:<20}{1:<20}{2:<20}'.format('year', 'polarization', 'luminosity'))

    d_opt={}
    d_opt['zeroerrors'] = True
    d_opt['sty'] = ['text45']
    d_opt['yname'] = 'Luminosity [pb^{-1}]' 
    for polarization in ['dn', 'up', 'both']:
        l_data=[]
        plotpath = 'tests/utilities/get_lumi/lumi_pol_{}.png'.format(polarization)
        for year in data.l_year + data.l_dset:
            lumi = rkut.get_lumi(year, polarization)
            log.info('{0:<20}{1:<20}{2:<20}'.format(year, polarization, lumi))
            l_data.append([year, lumi])


        arr_data = numpy.array(l_data)
        utils.plot_arrays({'.' : arr_data}, plotpath, 1, 0, 0, d_opt=d_opt)
#-------------------------
def get_measurement():
    log.info('{0:<20}{1:<20}{2:<20}'.format('year', 'polarization', 'luminosity'))

    l_quantity = ['fu', 'br_Bp_Jpsi', 'br_Bp_ctrl', 'br_Bp_Psi2', 'br_Bp_psi2', 'br_Jpsi_ee', 'br_ctrl_ee', 'br_Jpsi_mm', 'br_ctrl_mm', 'br_Psi2_ee', 'br_psi2_ee', 'br_Psi2_mm', 'br_psi2_mm', 'xsec_Bp', 'xsec_bb']
    for year in data.l_year + data.l_dset:
        log.info(year)
        for quantity in l_quantity:
            val, err = rkut.get_measurement(quantity, year)
            log.info('{0:<4}{1:<20}{2:<10.3e}{3:<10.3e}'.format('', quantity, val, err))
#-------------------------
def selection():
    d_pres=rkut.getPreselection('reso'        , 3, '12153001')
    print(d_pres['q2'])
    
    d_pres=rkut.getPreselection('rare_central', 3, '12153001')
    print(d_pres['q2'])
    
    d_pres=rkut.getPreselection('rare_high'   , 3, '12153001')
    print(d_pres['q2'])
#-------------------------
def reformat_mat():
    arr_wgt = numpy.random.normal(1,   0.1, 10000)
    arr_pol = numpy.random.choice([-1, +1], 10000)
    
    mat=numpy.array([arr_wgt, arr_pol]).T
    
    d_args={'proc' : 'ctrl', 'chan' : 'ee', 'year' : '2018'}
    
    arr_scl, _, _, _ = scale_gen_mat(d_args, mat)
    sum_1 = numpy.sum(arr_scl)
    
    mat=rkut.reformat_mat(mat)
    arr_scl, _, _, _ = scale_gen_mat(d_args, mat)
    sum_2 = numpy.sum(arr_scl)

    if abs(1 - sum_1/sum_2) > 1e-7:
        log.error('Sums of weights are different: {:.3f}/{:.3f}={:.9f}'.format(sum_1, sum_2, sum_1/sum_2))
        raise
#-------------------------
def extract_df_cutflow():
    rdf = ROOT.RDataFrame(100)
    rdf = rdf.Define('x', 'TRandom3 ran; return ran.Uniform(0, 1);')
    rdf = rdf.Filter('x > 0.5', 'xcut')

    df  = rkut.extract_df_cutflow(rdf, l_cut=['x > 0.5'])

    print(df)
#-------------------------
def get_ctfl_df():
    wc = '/home/angelc/pfs_lhcb/Data/cache/tools/apply_selection/hlt_calibration/ctrl/v10.18is/2018_ETOS/*.root'
    df = rkut.get_ctfl_df(wc, suffix='_eff.json')

    print(df)
#-------------------------
def test_result_to_dict():
    obs          = zfit.Space('x', limits=(-10, 10))
    mu           = zfit.Parameter("mu", 2.4, -1, 5)
    sg           = zfit.Parameter("sg", 1.3,  0, 5)
    gauss        = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)
    
    nll          = zfit.loss.UnbinnedNLL(model=gauss, data=gauss.create_sampler(n=1000))
    minimizer    = zfit.minimize.Minuit()
    result       = minimizer.minimize(nll)
    result.hesse()

    d_result = rkut.result_to_dict(result)

    pprint.pprint(d_result)
    print(result)
#-------------------------
def main():
    test_result_to_dict()
    
    return

    get_ctfl_df()
    extract_df_cutflow()
    get_measurement()
    get_gen_mat_skim(True)
    get_gen_mat_skim(False)
    get_gen_mat()
    get_lumi()
    selection()
    reformat_mat()
#-------------------------
if __name__ == '__main__':
    main()
    
