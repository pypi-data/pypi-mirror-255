from rk.df_getter import df_getter as dfg

import utils_noroot as utnr

#-------------------------------------------------
class data:
    log        = utnr.getLogger(__name__)
    out_dir    = utnr.make_dir_path('tests/df_getter')
    version    = 'v10.14'
    selection  = 'all_gorder'
    partition  = (1, 500)
    truth_corr = 'final_no_truth_mass_bdt'
#-------------------------------------------------
def test_simple(sample='ctrl_ee', year='2016', trigger='ETOS'):
    obj    = dfg(sample, year, data.version, data.partition)
    df_gen = obj.get_df('gen')
    
    df_rec = obj.get_df('rec')
    utnr.df_to_tex(df_rec.cf.df_eff, f'{data.out_dir}/simple/rec_{sample}_{year}_{trigger}.tex', hide_index=False)
    
    df_sel = obj.get_df('sel', trigger=trigger, selection=data.selection, truth_corr_type=data.truth_corr, using_wmgr=True)
    utnr.df_to_tex(df_sel.cf.df_eff, f'{data.out_dir}/simple/sel_{sample}_{year}_{trigger}.tex', hide_index=False)
#-------------------------------------------------
def test_redefine(sample='psi2_ee', year='2018', trigger='GTIS'):
    obj                = dfg(sample, year, data.version, data.partition)
    obj.var_arr['sel'] = ['B_const_mass_M[0]']

    df_sel = obj.get_df('sel', trigger=trigger, selection=data.selection, truth_corr_type=data.truth_corr, using_wmgr=True)

    arr_mass = df_sel.AsNumpy(['B_const_mass_M'])['B_const_mass_M']
#-------------------------------------------------
def print_vars(df):
    l_var   = df.GetColumnNames()
    l_pyvar = [ str(var.c_str()) for var in l_var]
    for var in sorted(l_pyvar):
        data.log.info(f'{"":<5}{var}')
#-------------------------------------------------
def main():
    test_redefine('ctrl_ee', '2016', 'ETOS')

    test_simple('ctrl_ee', '2016', 'ETOS')
    test_simple('ctrl_ee', '2016', 'GTIS')

    test_simple('psi2_ee', '2016', 'ETOS')
    test_simple('psi2_ee', '2016', 'GTIS')

    test_simple('ctrl_mm', '2016', 'MTOS')
    test_simple('psi2_mm', '2016', 'MTOS')
#-------------------------------------------------
if __name__ == '__main__':
    main()

