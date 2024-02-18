from rk.pulls import result_reader as rrd

import utils_noroot as utnr 

#----------------------------
def test():
    l_rfile = []
    l_rfile.append('tests/pulls/plots_1p000_001/fits.root')
    l_rfile.append('tests/pulls/plots_1p000_002/fits.root')

    rob = rrd(l_rfile)
    d_data = rob.get_data()

    out_dir = utnr.make_dir_path('tests/result_reader')
    out_path= f'{out_dir}/merged.json'

    utnr.dump_json(d_data, out_path)
#----------------------------
if __name__ == '__main__':
    test()
#----------------------------

