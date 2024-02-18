import ROOT
import utils
import os

#------------------------------------
def get_hist(name, x=None, y=None, z=None):
    xmin, xmax, nx = x
    ymin, ymax, ny = y
    mu_z, sg_z     = z

    h=ROOT.TH2F(name, '', nx, xmin, xmax, ny, ymin, ymax)
    ran = ROOT.TRandom3(0)
    for x_bin in range(1, nx + 1):
        for y_bin in range(1, ny + 1):
            val = ran.Gaus(mu_z, sg_z)
            h.SetBinContent(x_bin, y_bin, val)

    return h
#------------------------------------
def make_maps(filename, histname, eff, err):
    os.makedirs(dirname, exist_ok=True)
    filepath='{}/{}'.format(dirname, filename)
    ofile=ROOT.TFile(filepath, 'recreate')
    h = get_hist(histname, x=(0, 10, 400), y=(0, 10, 400), z=(eff, err))
    h.Write()

    plotname = filename.replace('.root', '.png')
    c = ROOT.TCanvas('c', '', 600, 600)
    h.Draw('colz')
    c.SaveAs('{}/{}'.format(plotdir, plotname))
    ofile.Close()
#------------------------------------
plotdir='tests/pid_toy_maps'
os.makedirs(plotdir, exist_ok=True)

l_ee_map = ['PArange_Fit_PolBoth_Year2011_nBrem0_merge_toys.root', 'PArange_Fit_PolBoth_Year2011_nBrem1_merge_toys.root']
dirname='/publicfs/ucas/user/campoverde/calibration/PID/v0/Electron'
for filename in l_ee_map:
    histname = 'XXX_All_0'
    make_maps(filename, histname, 0.7, 0.05)

dirname='/publicfs/ucas/user/campoverde/calibration/PID/v0/Muon'
l_mm_map = ['PerfHists_Mu_2011_MagUp_JpsiMu_DLLmu_ismuon_P_ETA_updated_toys.root', 'PerfHists_Mu_2011_MagDown_JpsiMu_DLLmu_ismuon_P_ETA_updated_toys.root']
for filename in l_mm_map:
    histname = 'Mu_DLLmu>-3 && IsMuon==1_All_0'
    make_maps(filename, histname, 0.7, 0.05)

dirname='/publicfs/ucas/user/campoverde/calibration/PID/v0/Kaon'
l_ke_map = ['PerfHists_K_2011_MagUp_D0K_probNN_ee_P_ETA_updated_toys.root', 'PerfHists_K_2011_MagDown_D0K_probNN_ee_P_ETA_updated_toys.root']
for filename in l_ke_map:
    histname = 'K_MC12TuneV2_ProbNNK>0.2 && DLLe<0_All_0'
    make_maps(filename, histname, 0.9, 0.02)

l_km_map = ['PerfHists_K_2011_MagUp_D0K_probNN_P_ETA_updated_toys.root', 'PerfHists_K_2011_MagDown_D0K_probNN_P_ETA_updated_toys.root']
for filename in l_km_map:
    histname = 'K_MC12TuneV2_ProbNNK>0.2_All_0'
    make_maps(filename, histname, 0.9, 0.02)
#-----------------------------------

