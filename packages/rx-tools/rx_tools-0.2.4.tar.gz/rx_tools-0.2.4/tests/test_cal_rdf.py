from rk.cal_rdf import cal_rdf as crdf

import matplotlib.pyplot as plt

from logzero import logger as log

import os

#-----------------------------------------
class data:
    ee_dat_ver= 'v10.11tf.3.0.x.x.0_v1'
    mm_dat_ver= 'v10.11tf.1.1.x.x.0_v1'

    preffix = 'gen'
#-----------------------------------------
def get_weights_list():
    if   data.preffix == 'gen':
        l_wgt = ['pid', 'trk']
    elif data.preffix == 'rec':
        l_wgt = ['pid', 'trk', 'gen', 'lzr', 'hlt']
    elif data.preffix == 'bdt':
        l_wgt = ['pid', 'trk', 'gen', 'lzr', 'hlt', 'rec']
    else:
        log.error(f'Invalid preffix: {preffix}')
        raise

    return l_wgt
#-----------------------------------------
def test_noswt():
    trig = 'ETOS'
    year = '2018'

    out_dir = f'tests/cal_rdf/noswt_{data.preffix}_{trig}_{year}'

    obj            = crdf(data.preffix, trig, year)
    obj.maxentries = 1000
    obj.dat_ver    = data.ee_dat_ver
    obj.cal_sys    = 'nom'
    obj.out_dir    = out_dir 
    obj.weights    = get_weights_list()

    rdf_dt, rdf_mc = obj.get_rdf(sweights='none')

    check_df(rdf_dt, out_dir, 'data')
    check_df(rdf_mc, out_dir, 'ctrl')
#-----------------------------------------
def test_ysswt():
    trig = 'ETOS'
    year = '2018'

    out_dir = f'tests/cal_rdf/ysswt_{data.preffix}_{trig}_{year}'

    obj            = crdf(data.preffix, trig, year)
    obj.maxentries = 1000
    obj.dat_ver    = data.ee_dat_ver
    obj.cal_sys    = 'nom'
    obj.out_dir    = out_dir 
    obj.weights    = get_weights_list()

    rdf_dt, rdf_mc = obj.get_rdf(sweights='v5')

    check_df(rdf_dt, out_dir, 'data')
    check_df(rdf_mc, out_dir, 'ctrl')
#-----------------------------------------
def check_df(rdf, dir_name, sample):
    os.makedirs(dir_name, exist_ok=True)
    plot_path = f'{dir_name}/{sample}.png'

    arr_wgt = rdf.AsNumpy(['weight'])['weight']
    plt.hist(arr_wgt, range=(0,2), bins=100)

    log.visible(f'Saving to: {plot_path}')
    plt.yscale('log')
    plt.title(sample)
    plt.savefig(plot_path)
    plt.close('all')
#-----------------------------------------
def main():
    data.preffix = 'bdt'
    test_noswt()

    return
    test_ysswt()

    data.preffix = 'gen'
    test_noswt()
    test_ysswt()

    data.preffix = 'rec'
    test_noswt()
    test_ysswt()
#-----------------------------------------
if __name__ == '__main__':
    main()

