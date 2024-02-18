from rk.ds_getter import ds_getter as dsg

import utils_noroot as utnr
import os

#-------------------------------------------------
class data:
    log        = utnr.getLogger(__name__)
    out_dir    = utnr.make_dir_path('tests/ds_getter')
    tst_dir    = None
    version    = 'v10.21p2'
    selection  = 'all_gorder'
    partition  = (1, 500)
#-------------------------------------------------
def do_test(q2bin='jpsi', year='2016', trig='ETOS', kind='sign'):
    obj = dsg(q2bin, trig, year, data.version, data.partition, kind, data.selection)
    if kind == 'cmb' and trig == 'MTOS':
        rdf  = obj.get_df(remove_cuts=['mass', 'acceptance'])
    else:
        rdf  = obj.get_df(remove_cuts=['mass'])

    utnr.df_to_tex(rdf.cf.df_eff, f'{data.out_dir}/simple/{kind}_{q2bin}_{year}_{trig}.tex', hide_index=False)
    rdf.cf.df_cut.to_csv(f'{data.out_dir}/simple/{kind}_{q2bin}_{year}_{trig}.csv')
    ctf=rdf.cf
    ctf.to_json(f'{data.out_dir}/{data.tst_dir}/{kind}_{q2bin}_{year}_{trig}.json')
#-------------------------------------------------
def test_ss_data():
    data.tst_dir = 'ss_data'
    do_test(q2bin='high', year='2018', trig='ETOS', kind= 'cmb')
    do_test(q2bin='high', year='2018', trig='GTIS', kind= 'cmb')
    do_test(q2bin='high', year='2018', trig='MTOS', kind= 'cmb')
#-------------------------------------------------
def test_os_data():
    data.tst_dir = 'os_data'
    do_test(q2bin='jpsi', year='2018', trig='ETOS', kind='data')
    do_test(q2bin='jpsi', year='2018', trig='GTIS', kind='data')
    do_test(q2bin='jpsi', year='2018', trig='MTOS', kind='data')
#-------------------------------------------------
def test_mc():
    data.tst_dir = 'mc'
    do_test(q2bin='jpsi', year='2018', trig='ETOS', kind='sign')
    do_test(q2bin='jpsi', year='2018', trig='ETOS', kind='bp_x')
    do_test(q2bin='jpsi', year='2018', trig='ETOS', kind='bd_x')
#-------------------------------------------------
def test_redefine():
    obj = dsg('jpsi', 'ETOS', '2018', data.version, data.partition, 'sign', data.selection)
    rdf = obj.get_df(d_redefine={'bdt' : 'BDT > 0.5'})

    file_dir = f'tests/ds_getter/redefine/'
    os.makedirs(file_dir, exist_ok=True)

    rdf.Snapshot('tree', f'{file_dir}/file.root')
#-------------------------------------------------
def test_dset():
    data.tst_dir = 'dset'
    do_test(q2bin='jpsi', year='r1'  , trig='ETOS', kind='data')
    do_test(q2bin='jpsi', year='r2p1', trig='ETOS', kind='data')
    do_test(q2bin='jpsi', year='2017', trig='ETOS', kind='data')
    do_test(q2bin='jpsi', year='2018', trig='ETOS', kind='data')
#-------------------------------------------------
def test_cutflow():
    data.tst_dir = 'cutflow'
    do_test(q2bin='jpsi', year='2018', trig='MTOS', kind='cmb')
#-------------------------------------------------
def main():
    test_ss_data()
    test_cutflow()
    test_dset()
    test_os_data()
    test_redefine()
    test_mc()
#-------------------------------------------------
if __name__ == '__main__':
    main()

