import ROOT

import numpy
import utils_noroot as utnr

from cf_checker import cf_checker

log=utnr.getLogger(__name__)
#------------------------------------------------------
def get_data(nentries):
    arr_x = numpy.random.normal(0, 0.1, nentries)
    arr_y = numpy.random.normal(0, 0.1, nentries)
    
    d_data={'x' : arr_x, 'y' : arr_y}
    
    df = ROOT.RDF.MakeNumpyDataFrame(d_data)

    return df
#------------------------------------------------------
def fil_df(df, kind):
    v_cut=ROOT.std.vector('std::string')()
    if   kind == 'cf_t1':
        v_cut.push_back('x > 0')
        v_cut.push_back('y < 0')
    elif kind == 'cf_t2':
        v_cut.push_back('x < 0')
        v_cut.push_back('y > 0')
    else:
        log.error('Wrong cut: ' + kind)
        raise

    df=df.Filter(v_cut[0], 'xcut')
    df=df.Filter(v_cut[1], 'ycut')

    return (df, v_cut)
#------------------------------------------------------
def get_reports(l_kind):
    df=get_data(1000)
    
    l_rep = []
    for kind in l_kind:
        df_fil, v_cut=fil_df(df, kind)
        o_rep=df_fil.Report()
        c_rep=ROOT.CutFlowReport(o_rep, "", v_cut) 
        c_rep.SetName(kind)
        l_rep.append(c_rep)
        #c_rep.Print()

    return l_rep
#------------------------------------------------------
if __name__ == '__main__':
    l_kind_1 = ['cf_t1', 'cf_t2']
    l_kind_2 = ['cf_t1', 'cf_t2']
    
    l_rep_1 = get_reports(l_kind_1)
    l_rep_2 = get_reports(l_kind_2)
    
    ch=cf_checker(l_rep_1, l_rep_2)
    ch.are_equal()
#------------------------------------------------------
    

