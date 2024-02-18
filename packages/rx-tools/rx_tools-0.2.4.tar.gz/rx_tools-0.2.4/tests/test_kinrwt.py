import ROOT

import os
import numpy
import pandas            as pnd
import matplotlib.pyplot as plt

import utils
import utils_noroot as utnr

from rk.kinrwt import rwt as krwt

from hep_cl import hist_reader as hrdr

log=utnr.getLogger(__name__)
#--------------------------------------
class data:
    swt_ver = 'v5'
#--------------------------------------
def get_data(inputdir, year, kind, nentries=10000):
    filepath = f'{inputdir}/sweights_{data.swt_ver}/{year}_{kind}_trigger_weights_sweighted.root'
    treename = 'TRG'
    file_dir = utnr.make_dir_path(os.path.dirname(filepath))

    if os.path.isfile(filepath):
        df = ROOT.RDataFrame(treename, filepath)
        log.visible('Reusing input')

        return df

    log.info('Making input')

    df = ROOT.RDataFrame(nentries)
    df = df.Define('x'          , 'TRandom3 r(rdfentry_ + 1); return r.Uniform(-1, 11);')
    df = df.Define('y'          , 'TRandom3 r(rdfentry_ + 2); return r.Uniform(-1, 11);')
    df = df.Define('z'          , 'TRandom3 r(rdfentry_ + 3); return r.Uniform(-1, 11);')
    df = df.Define('pid_eff'    ,                                                   '1')
    df = df.Define('B_TRUEETA'  ,  'TRandom3 r(rdfentry_ + 4); return r.Uniform(0, 3);')
    df = df.Define('Jpsi_TRUEID',                                                 '443')

    df = df.Define('H_PX'       ,  'TRandom3 r(rdfentry_ + 5); return r.Uniform(1000, 10000);')
    df = df.Define('H_PY'       ,  'TRandom3 r(rdfentry_ + 6); return r.Uniform(1000, 10000);')
    df = df.Define('H_PZ'       ,  'TRandom3 r(rdfentry_ + 7); return r.Uniform(1000, 10000);')
    df = df.Define('Jpsi_M'     ,  'TRandom3 r(rdfentry_ + 8); return r.Uniform(1000,  4000);')

    if   kind == 'dt':
        df = df.Define(f'weight',                  '1')
    elif kind == 'mc':
        df = df.Define(f'weight', '1 + 0.01 * (x - 2 * y + z)')

    df.Snapshot(treename, filepath)

    return df
#--------------------------------------
def make_settings(prefix, trigger, year, out_dir, syst):
    d_setting={}
    d_setting['arr_x_1']  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    d_setting['arr_y_1']  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    d_setting['arr_z_1']  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    d_setting['arr_x_2']  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    d_setting['arr_y_2']  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    d_setting['arr_z_2']  = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    d_setting['rwt_vars'] = ['x', 'y', 'z']

    set_dir   = utnr.make_dir_path(f'{out_dir}/share')
    json_path = f'{set_dir}/kinematics_{syst}.json'

    utnr.dump_json({f'{prefix}_{trigger}_{year}' : d_setting}, json_path)
#--------------------------------------
def test_toy_hist():
    kind    = 'toy'
    trigger = 'TRG'
    year    = '2018'
    syst    = 'trg' 
    method  = 'hist'
    toy_dir = f'tests/kinrwt/toy_{method}'

    make_settings(kind, trigger, year, toy_dir, syst)

    rdf_dt   = get_data(toy_dir, year, 'dt', nentries=100000)
    rdf_mc   = get_data(toy_dir, year, 'mc', nentries=100000)

    setdir    = utnr.make_dir_path(f'{toy_dir}/share')
    rootdir   = utnr.make_dir_path(f'{toy_dir}/root')
    
    rwt            = krwt(dt=rdf_dt, mc=rdf_mc)
    rwt.wgt_ver    = 'v0.1'
    rwt.wgt_dir    = rootdir 
    rwt.set_dir    = setdir 
    rwt.method     = method
    rwt.syst       = syst 
    rwt.save_reweighter(name=f'{trigger}_{year}_{kind}_{syst}')
    l_var          = rwt.vars
    [h_dt, h_mc]   = rwt.reweighter
    obj            = hrdr(dt=h_dt, mc=h_mc)

    check_weights(obj, rdf_dt, rdf_mc, trigger, method, l_var, 'toy')
#--------------------------------------
def test_toy_hepml():
    kind    = 'toy'
    trigger = 'TRG'
    year    = '2018'
    syst    = 'trg' 
    method  = 'hep_ml'
    toy_dir = f'tests/kinrwt/toy_{method}'

    make_settings(kind, trigger, year, toy_dir, syst)

    rdf_dt   = get_data(toy_dir, year, 'dt', nentries=100000)
    rdf_mc   = get_data(toy_dir, year, 'mc', nentries=100000)

    setdir   = utnr.make_dir_path(f'{toy_dir}/share')
    rootdir  = utnr.make_dir_path(f'{toy_dir}/root')
    
    rwt            = krwt(dt=rdf_dt, mc=rdf_mc)
    rwt.wgt_ver    = 'v0.1'
    rwt.wgt_dir    = rootdir 
    rwt.set_dir    = setdir 
    rwt.method     = method
    rwt.save_reweighter(name=f'{trigger}_{year}_{kind}_{syst}')
    l_var          = rwt.vars
    obj            = rwt.reweighter

    check_weights(obj, rdf_dt, rdf_mc, trigger, method, l_var, 'toy')
#--------------------------------------
def add_columns(rdf, l_col):
    v_name = rdf.GetColumnNames()
    l_name = [ name.c_str() for name in v_name ]
    l_var  = []

    for col in l_col:
        if col in l_name:
            l_var.append(col)
            continue

        var = utils.get_var_name(col)
        rdf = rdf.Define(var, col)

        l_var.append(var)

    return rdf, l_var
#--------------------------------------
def check_weights(reweighter, rdf_dt, rdf_mc, trigger, method, l_var, kind):
    rdf_dt, l_var_rdf = add_columns(rdf_dt, l_var)
    rdf_mc, l_var_rdf = add_columns(rdf_mc, l_var)

    l_col        = l_var_rdf + ['weight']

    d_dt         = rdf_dt.AsNumpy(l_col)
    df_dt        = pnd.DataFrame(d_dt)

    d_mc         = rdf_mc.AsNumpy(l_col)
    df_mc        = pnd.DataFrame(d_mc)

    arr_wgt_dt   = d_dt['weight']
    arr_wgt_mc   = d_mc['weight']
    #------------------
    df_mc_axis   = df_mc[l_var_rdf]
    mat          = df_mc_axis.to_numpy()
    arr_wgt_rw   = reweighter.predict_weights(mat)

    arr_wgt      = arr_wgt_rw * arr_wgt_mc
    avg          = arr_wgt.sum() / arr_wgt.size
    arr_wgt_rw   = arr_wgt_rw / avg
    #------------------
    plot_dir = f'tests/kinrwt/{kind}_{method}/plots'
    os.makedirs(plot_dir, exist_ok=True)

    plt.hist(arr_wgt_rw, range=(0, 2), bins=100)
    plt.savefig(f'{plot_dir}/weights.png')
    plt.close('all')
    #------------------
    save_proj_data(df_dt, df_mc, arr_wgt_rw, arr_wgt_mc, arr_wgt_dt, kind, method, axis=l_var_rdf[0])
    save_proj_data(df_dt, df_mc, arr_wgt_rw, arr_wgt_mc, arr_wgt_dt, kind, method, axis=l_var_rdf[1])
    save_proj_data(df_dt, df_mc, arr_wgt_rw, arr_wgt_mc, arr_wgt_dt, kind, method, axis=l_var_rdf[2])

    nrm_before = numpy.sum(arr_wgt_mc)
    nrm_after  = numpy.sum(arr_wgt_mc * arr_wgt_rw)
    #------------------
    tol = 2 * abs(nrm_before - nrm_after) / (nrm_before + nrm_after)
    if tol > 1e-3:
        log.warning(f'Normalization differs by {tol:.3e}: {nrm_before:.0f} -> {nrm_after:.0f}')
    else:
        log.visible(f'Normalization differs by {tol:.3e}')
#--------------------------------------
def save_proj_data(df_dt, df_mc, arr_mc_rwt, arr_mc_wgt, arr_dt_wgt, kind, method, axis='none'):
    ax=None
    ax=df_dt.hist(bins=30, column=axis, range=(0, 10), linestyle='solid', histtype='step', density=True, label='Data'         , ax=ax, weights=arr_dt_wgt)
    ax=df_mc.hist(bins=30, column=axis, range=(0, 10), linestyle='solid', histtype='step', density=True, label='MC'           , ax=ax, weights=arr_mc_wgt)
    ax=df_mc.hist(bins=30, column=axis, range=(0, 10), linestyle='solid', histtype='step', density=True, label='MC reweighted', ax=ax, weights=arr_mc_wgt * arr_mc_rwt)

    plotpath = f'tests/kinrwt/{kind}_{method}/plots/comparison_{axis}.png'
    plt.title(f'{axis} axis')
    plt.legend(loc='lower left')
    plt.savefig(plotpath)
    plt.close('all')
#--------------------------------------
def main():
    ROOT.gROOT.ProcessLine(".L lhcbStyle.C")
    ROOT.lhcbStyle()

    test_toy_hist()
    test_toy_hepml()
#--------------------------------------
if __name__ == '__main__':
    main()

