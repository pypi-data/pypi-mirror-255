import ROOT
import pickle
import rk.utils

#-----------------------
def getVariables(expr):
    if       rk.utils.isElectron(eventType) and len(l_ee_var) == 0:
        l_branch=getBranches(sign_ee, "KEE")
    elif not rk.utils.isElectron(eventType) and len(l_mm_var) == 0:
        l_branch=getBranches(sign_mm, "KMM")
    elif     rk.utils.isElectron(eventType) and len(l_ee_var) != 0:
        l_branch=l_ee_var
    elif not rk.utils.isElectron(eventType) and len(l_ee_var) != 0:
        l_branch=l_mm_var
    else:
        ROOT.Error("This should not happen")
        exit(1)

    l_res=[]
    for branch in l_branch:
        if branch in expr:
            l_res.append(branch)

    return l_res
#-----------------------
def getBranches(filepath, treepath):
    l_branchname=[]
    ifile=ROOT.TFile(filepath)
    if not hasattr(ifile, treepath):
        ROOT.Error("Cannot find {} tree in {}".format(treepath, filepath) )
        exit(1)

    tree=getattr(ifile, treepath)
    l_branch=tree.GetListOfBranches()
    for branch in l_branch:
        l_branchname.append(branch.GetName())

    ifile.Close()

    return l_branchname
#-----------------------
def getCut():
    global eventType
    if channel == "electron":
        eventType="12153001"
        trigger=ROOT.eTOS
        trigger=ROOT.hTOS
        trigger=ROOT.gTIS
        preselection=3

        l_cut_1=rk.utils.getCuts(eventType, mode, preselection, ROOT.eTOS)
        l_cut_2=rk.utils.getCuts(eventType, mode, preselection, ROOT.hTOS)
        l_cut_3=rk.utils.getCuts(eventType, mode, preselection, ROOT.gTIS)

        l_cut = l_cut_1 + l_cut_2 + l_cut_3
        l_cut = set(l_cut)
    else:
        eventType="12143001"
        preselection=1

        l_cut=rk.utils.getCuts(eventType, mode, preselection, ROOT.mTOS)

    return str(l_cut)
#-----------------------
l_mm_var=[]
l_ee_var=[]
rk.utils.loadCPP()

evientType=""
mode="reso"
channel="muon"

sign_ee="/publicfs/ucas/user/campoverde/Data/RK/sign_ee/v9.9.a0v1x7y4z4/files/_lhcb_user_a_acampove_2020_11_421818_421818243_12123003_2016_MagUp.root"
sign_mm="/publicfs/ucas/user/campoverde/Data/RK/sign_mm/v9.9.a0v0x9y9z1/files/_lhcb_user_a_acampove_2020_03_353011_353011507_12113002_2016_MagUp.root"

str_cut=getCut()
l_variable=getVariables(str_cut)

l_disc=[]
l_cont=[]

l_extra=["H_L0Calo_HCAL_realET", "L0Data_Muon1_Pt", "BDTGRun2T", "nSPDHits", "kl", "kl_M_ltrack2pi", "BDTGETOSRun2T", "kl_M_k2l", "kl_M_l2pi"]
for variable in l_variable:
    if "Hlt" in variable or "_TOS" in variable or "_TIS" in variable:
        l_disc.append(variable)
    elif "_ID" in variable or "TRUEID" in variable or "TCK" in variable or "InMuonAcc" in variable or "_has" in variable:
        l_disc.append(variable)
    elif "ECAL" in variable or "CHI2" in variable or variable.endswith("_PT") or "Prob" in variable or variable.endswith("_P")  or variable.endswith("_M") or variable in l_extra:
        l_cont.append(variable)
    else:
        print(variable)

d_var={'disc' : l_disc , 'cont' : l_cont }
pickle.dump(d_var, open(channel + "_vars.pickle", "wb"))

