import ROOT
import utils
import os

from rk.bdtreader import reader as bdtrd

#-----------------------------
def plot(arr_bdt_fil, arr_bdt_rdr):
    h_bdt_fil = utils.arr_to_hist('h_bdt_fil',   'File', 50, 0.6, 1.1, arr_bdt_fil)
    h_bdt_rdr = utils.arr_to_hist('h_bdt_rdr', 'Reader', 50, 0.6, 1.1, arr_bdt_rdr)

    plotpath='{}/{}'.format(plotdir, 'bdt_dist.png')

    d_opt={}
    d_opt['sty']    = 'hist'
    d_opt['ratio']  =  True 
    d_opt['legend'] =  1 

    utils.plotHistograms([h_bdt_fil, h_bdt_rdr], plotpath, d_opt=d_opt)
#-----------------------------
plotdir='tests/bdtreader/'
os.makedirs(plotdir, exist_ok=True)

bdtdir='/publicfs/ucas/user/campoverde/Data/RK/MVA/bdt_v7.4.4.a0v1x7y4z4'
filepath='/publicfs/ucas/user/campoverde/Data/RK/ctrl_ee/v10.10.a0v1x7y4z4.3.0.1.0.0/2012_reso_skimmed.root'
ifile=ROOT.TFile(filepath)
itree=ifile.ETOS

df=ROOT.RDataFrame(itree)
arr_bdt_fil=df.AsNumpy(['BDT'])['BDT']

reader=bdtrd(bdtdir)
arr_bdt_rdr=reader.predict_weights(filepath, 'ETOS', 'ETOS')

plot(arr_bdt_fil, arr_bdt_rdr)

ifile.Close()
