import ROOT
import utils
import utils_noroot as utnr
import numpy
import os

from rk.mv_reweighter import mv_reweighter

log=utnr.getLogger(__name__)
nentries=100000
#-----------------------------------
def get_data_2D(sigma_x, sigma_y, weight=''):
    df=ROOT.RDataFrame(nentries)
    df=df.Define('x', 'auto ran=TRandom3(0); return ran.Gaus(0, {});'.format(sigma_x))
    df=df.Define('y', 'auto ran=TRandom3(0); return ran.Gaus(0, {});'.format(sigma_y))

    if weight != '':
        df=df.Define('wgt', 'auto ran = TRandom3(0); return ran.Gaus(1, 0.1);')

    df=utils.reload_df(df)

    return df
#-----------------------------------
def get_data_ND(is_data=None, weight=''):
    if is_data:
        w_sigma = 1.0
        x_tau   = 1.0
        y_sigma = 1.0
        z_mean  = 0.0
    else:
        w_sigma = 1.5
        x_tau   = 2.0
        y_sigma = 2.0
        z_mean  = 1.0

    df=ROOT.RDataFrame(nentries)

    arr_ran_w = utils.get_ran_array(nentries, 'TMath::Gaus(x, 0, {})  '.format(w_sigma), 0, 14, seed=1)
    arr_ran_x = utils.get_ran_array(nentries, 'TMath::Exp(-x/{})      '.format(x_tau  ), 0, 14, seed=2)
    arr_ran_y = utils.get_ran_array(nentries, 'TMath::Landau(x, 0, {})'.format(y_sigma), 0, 14, seed=3)
    arr_ran_z = utils.get_ran_array(nentries, 'TMath::Gaus(x, {}, 1)  '.format(z_mean ), 0, 14, seed=4)

    d_data={'w' : arr_ran_w, 'x' : arr_ran_x, 'y' : arr_ran_y, 'z' : arr_ran_z}
    df = ROOT.RDF.MakeNumpyDataFrame(d_data)

    if weight != '':
        df=df.Define(weight, 'auto ran = TRandom3(0); return ran.Gaus(1, 0.1);')

    return df
#-----------------------------------
def plot_2D(name, df_d, df_s):
    df_s=df_s.Define('wgt_tot', 'wgt * rwt')

    h_d=df_d.Histo2D(ROOT.RDF.TH2DModel('hd', '', 30, -4, 4, 30, -4, 4),'x', 'y')
    h_s=df_s.Histo2D(ROOT.RDF.TH2DModel('hs', '', 30, -4, 4, 30, -4, 4),'x', 'y', 'wgt')
    h_r=df_s.Histo2D(ROOT.RDF.TH2DModel('hr', '', 30, -4, 4, 30, -4, 4),'x', 'y', 'wgt_tot')

    h_w=df_s.Histo2D(ROOT.RDF.TH2DModel('hw', '', 30, -4, 4, 30,  0, 2),'x', 'y', 'rwt')
    g_w=df_s.Graph('x', 'rwt')
    
    c=ROOT.TCanvas('c', '', 1200, 600)
    c.Divide(2, 2)

    c.cd(1)
    h_d.Draw('col')

    c.cd(2)
    h_s.Draw('col')

    c.cd(3)
    h_r.Draw('col')

    pad=c.cd(4)
    pad.SetLogy()
    g_w.Draw('ap')

    c.SaveAs(plotsdir + '/' + name)
#-----------------------------------
def plot_ND(df_d, df_s, l_var):
    df_s=df_s.Define('wgt_tot', 'wgt * rwt')

    for var_name, arr_bound in l_var:
        nbins=arr_bound.size - 1

        h_d=df_d.Histo1D(ROOT.RDF.TH1DModel('h_{}_d'.format(var_name), 'Data'                  , nbins, arr_bound), var_name           )
        h_s=df_s.Histo1D(ROOT.RDF.TH1DModel('h_{}_s'.format(var_name), 'Simulation, original'  , nbins, arr_bound), var_name, 'wgt'    )
        h_r=df_s.Histo1D(ROOT.RDF.TH1DModel('h_{}_s'.format(var_name), 'Simulation, reweighted', nbins, arr_bound), var_name, 'wgt_tot')

        d_opt={}
        d_opt['legend']=True
        d_opt['text'  ]=('var: ' + var_name, 1)
        d_opt['ratio'] =True
        d_opt['yminr'] =0.8
        d_opt['ymaxr'] =1.2

        h_d=h_d.GetValue()
        h_s=h_s.GetValue()
        h_r=h_r.GetValue()

        utils.plotHistograms([h_d, h_s, h_r], '{}/ND_{}.png'.format(plotsdir, var_name), d_opt=d_opt)
#-----------------------------------
def test_2D():
    df_d = get_data_2D(0.5, 1.0, 'wgt')
    df_s = get_data_2D(1.0, 0.5, 'wgt')
    
    arr_bound = numpy.linspace(-4, +4, 31)
    x_tup=('x', arr_bound)
    y_tup=('y', arr_bound)
    
    l_var=[x_tup, y_tup]
    rwt=mv_reweighter(data=df_d, simulation=(df_s, 'wgt'), l_var=l_var)
    rwt.plotsdir=plotsdir
    arr_rwt = rwt.get_weights()
    
    utils.declare_struc()
    vec_rwt = ROOT.VecOps.AsRVec(arr_rwt)
    df_s = df_s.Define('counter', 'counter++')
    df_s = ROOT.RDFAddArray(ROOT.RDF.AsRNode(df_s), vec_rwt, 'rwt') 
    df_s = utils.reload_df(df_s)
    
    plot_2D('plot_2D.png', df_d, df_s)
#-----------------------------------
def test_ND():
    df_d = get_data_ND(is_data=True , weight='wgt')
    df_s = get_data_ND(is_data=False, weight='wgt')
    
    arr_bound_w = numpy.linspace(0, 14, 31)
    arr_bound_x = numpy.linspace(0, 14, 31)
    arr_bound_y = numpy.linspace(0, 14, 31)
    arr_bound_z = numpy.linspace(0, 14, 31)

    w_tup=('w', arr_bound_w)
    x_tup=('x', arr_bound_x)
    y_tup=('y', arr_bound_y)
    z_tup=('z', arr_bound_z)
    
    l_var=[w_tup, x_tup, y_tup, z_tup]

    rwt=mv_reweighter(data=(df_d, 'wgt'), simulation=(df_s, 'wgt'), l_var=l_var)
    rwt.plotsdir=plotsdir
    arr_rwt = rwt.get_weights()

    df_s=utils.add_df_column(df_s, arr_rwt, 'rwt')
    
    plot_ND(df_d, df_s, l_var) 

    df_s.Display().Print()
#-----------------------------------
plotsdir='tests/mv_reweighter'
os.makedirs(plotsdir, exist_ok=True)

#test_2D()
test_ND()

