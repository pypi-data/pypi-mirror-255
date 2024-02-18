
#----------------------
class settings:
    _d_proc_evt= {}
    _d_evt_proc= {}
    _l_year    = ['2011', '2012', '2015', '2016', '2017', '2018']
    _l_electron= []
    _l_muon    = []
    #----------------------
    if True:
        _d_evt_proc['12143001']="ctrl_mm"
        _d_evt_proc['12143020']="psi2_mm"
        _d_evt_proc['12113002']="sign_mm"
        
        _d_evt_proc['12153001']="ctrl_ee"
        _d_evt_proc['12153012']="psi2_ee"
        _d_evt_proc['12123003']="sign_ee"
        
        _d_evt_proc['11453001']="bdXcHs_ee"
        _d_evt_proc['12952000']="bpXcHs_ee"
        
        _d_evt_proc['12153020']="ctrl_pi_ee"
        _d_evt_proc['12143010']="ctrl_pi_mm"
        
        _d_evt_proc['12155100']="bpks_jpsi_ee"
        _d_evt_proc['11154001']="bdks_jpsi_ee"
        
        _d_evt_proc['11124002']="bdks_ee"
        _d_evt_proc['12123445']="bpks_ee"
        
        _d_evt_proc['11154011']="psi2Kstr_ee"
    
        _d_proc_evt['ctrl_mm'] = '12143001'
        _d_proc_evt['psi2_mm'] = '12143020'
        _d_proc_evt['sign_mm'] = '12113002'
        
        _d_proc_evt['ctrl_ee'] = '12153001'
        _d_proc_evt['psi2_ee'] = '12153012'
        _d_proc_evt['sign_ee'] = '12123003'
        
        _d_proc_evt['bdXcHs_ee'] = '11453001'
        _d_proc_evt['bpXcHs_ee'] = '12952000'
        
        _d_proc_evt['ctrl_pi_ee'] = '12153020'
        _d_proc_evt['ctrl_pi_mm'] = '12143010'
        
        _d_proc_evt['bpks_jpsi_ee'] = '12155100'
        _d_proc_evt['bdks_jpsi_ee'] = '11154001'
        
        _d_proc_evt['bdks_ee'] = '11124002'
        _d_proc_evt['bpks_ee'] = '12123445'
        
        _d_proc_evt['psi2Kstr_ee'] = '11154011'
    if True:
        _l_electron.append("electron")
        _l_electron.append("data_ee")
        _l_electron.append("toy_ee")
        _l_electron.append("12153011")
        _l_electron.append("12153012")
        _l_electron.append("15454101")
        _l_electron.append("11124001")
        _l_electron.append("11124002")
        _l_electron.append("12425000")
        _l_electron.append("12153001")
        _l_electron.append("13454001")
        _l_electron.append("12425011")
        _l_electron.append("12123444")
        _l_electron.append("12123445")
        _l_electron.append("12153020")
        _l_electron.append("12952000")
        _l_electron.append("11453001")
        _l_electron.append("11154001")
        _l_electron.append("12155100")
        _l_electron.append("11154011")
        _l_electron.append("12183004")
        _l_electron.append("12583013")
        _l_electron.append("12583021")
        _l_electron.append("12123002")
        _l_electron.append("12123003")
        _l_electron.append("12123005")
    if True:
         _l_muon.append("muon")
         _l_muon.append("data_mm")
         _l_muon.append("toy_mm")
         _l_muon.append("12143001")
         _l_muon.append("12143020")
         _l_muon.append("12143010")
         _l_muon.append("12113001")
         _l_muon.append("12113002")

    @classmethod
    def get_years(self):
        return list(self._l_year)

    @classmethod
    def get_evt(self, proc):
        return self._d_proc_evt[proc]

    @classmethod
    def get_proc(self, evt):
        return self._d_evt_proc[evt]

    @classmethod
    def is_electron(self, evt):
        return evt in self._l_electron

    @classmethod
    def is_muon(self, evt):
        return evt in self._l_muon
#----------------------

