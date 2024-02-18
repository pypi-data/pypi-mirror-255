import numpy
import os
import ROOT
import utils_noroot as utnr

from rk.dilep_reso import calculator as calc_reso
from rk.dilep_reso import plot_reso 

ROOT.gInterpreter.ProcessLine('TRandom3 ran(1);')
#----------------------------
class data:
    log = utnr.getLogger(__name__)
#----------------------------
def get_real_data():
    dat_dir   = os.environ['DATDIR']
    file_path = f'{dat_dir}/ctrl_ee/v10.11tf/2018.root'

    rdf = ROOT.RDataFrame('KEE', file_path)

    return rdf
#----------------------------
def get_toy_data(kind, is_mc):
    if   kind == 'sig':
        rdf = ROOT.RDataFrame(100000)
    elif kind == 'bkg':
        rdf = ROOT.RDataFrame(1000000)

    if kind != 'tot':
        if is_mc:
            rdf = rdf.Define('L1_TRUEID'  ,  '11')
            rdf = rdf.Define('L2_TRUEID'  ,  '11')
            rdf = rdf.Define('Jpsi_TRUEID', '443')

        rdf = rdf.Define('L1_HasBremAdded', 'ran.Integer(2)')
        rdf = rdf.Define('L2_HasBremAdded', 'ran.Integer(2)')
        rdf = rdf.Define('L1_P', 'ran.Uniform(0, 100000)')
        rdf = rdf.Define('L2_P', 'ran.Uniform(0, 100000)')

    if   kind == 'sig':
        rdf = rdf.Define('Jpsi_M', 'ran.Gaus(3000, 117 - (L1_P + L2_P)/1000 )')
    elif kind == 'bkg':
        rdf = rdf.Define('Jpsi_M', 'ran.Exp(1000)')
    elif kind == 'tot':
        rdf_s = get_toy_data('sig', is_mc)
        rdf_b = get_toy_data('bkg', is_mc)
        rdf   = merge_rdf(rdf_s, rdf_b)
    else:
        data.log.error(f'Invalid kind: {kind}')
        raise

    rdf.is_mc = is_mc

    return rdf
#----------------------------
def merge_rdf(rdf_1, rdf_2):
    d_data_1 = rdf_1.AsNumpy()
    d_data_2 = rdf_2.AsNumpy()

    d_data   = {}
    for key in d_data_1:
        arr_1 = d_data_1[key]
        arr_2 = d_data_2[key]

        d_data[key] = numpy.concatenate([arr_1, arr_2])

    return ROOT.RDF.MakeNumpyDataFrame(d_data)
#----------------------------
def key_tuple_to_str(d_res):
    return { str(key) : val for key, val in d_res.items()}
#----------------------------
def test_simple(kind, brem):
    data.log.info(f'Creating toy data')
    df      = get_toy_data(kind, kind == 'sig')
    arr_bin = numpy.array([0., 15000., 19000., 25000., 30000., 50000, 100000]) 

    d_bin        = {}
    d_bin['p1']  = arr_bin.tolist()
    d_bin['p2']  = arr_bin.tolist()
    
    data.log.info(f'Calculating resolution')
    obj          = calc_reso(df, binning=d_bin, fit=True, d_par={}, signal='gauss')
    obj.plot_dir = 'tests/dilep_reso/simple/real'
    d_res, d_par = obj.get_resolution(brem=brem)

    data.log.info(f'Dumping to JSON')
    d_res = key_tuple_to_str(d_res)
    d_par = key_tuple_to_str(d_par)

    utnr.dump_json(d_res, f'tests/dilep_reso/simple/real/res_brem_{brem}.json')
    utnr.dump_json(d_par, f'tests/dilep_reso/simple/real/par_brem_{brem}.json')
#----------------------------
def par_to_res(d_par):
    d_res = {}
    for sbin, d_fit_par in d_par.items():
        if d_fit_par == {}:
            d_res[sbin] = numpy.nan 
            continue

        [sg, _] = d_fit_par['sg']

        d_res[sbin] = sg

    return d_res
#----------------------------
def plot_simple(brem, kind):
    d_res = utnr.load_json(f'tests/dilep_reso/simple/real/{kind}_brem_{brem}.json')

    if kind == 'par':
        d_res = par_to_res(d_res)
    else:
        d_res = { key : val if isinstance(val, float) else numpy.nan for key, val in d_res.items()}

    l_val = list(d_res.values())
    l_val = [ val for val in l_val if isinstance(val, float)]
    minv  = min(l_val)
    maxv  = max(l_val)

    plot_reso(d_res, plot_dir='tests/dilep_reso/simple/real', suffix=f'{kind}_{brem}', rng=(minv, maxv))
#----------------------------
def main():
    test_simple('tot', 0)
    plot_simple(0, 'par')
    plot_simple(0, 'res')
#----------------------------
if __name__ == '__main__':
    main()

