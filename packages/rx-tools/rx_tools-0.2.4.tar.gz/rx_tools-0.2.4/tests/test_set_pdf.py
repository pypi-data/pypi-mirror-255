from rk.set_pdf import set_pdf

import zfit

from rk.model import zmodel

#------------------------------------------
def get_model():
    obs = zfit.Space('mass', limits=(5180, 5600) ) 
    mod = zmodel(proc='ctrl', trig='ETOS', q2bin='jpsi', year='2018', obs=obs, mass='mass_jpsi')
    pdf = mod.get_model(suffix='dt', prc_kind='ke_merged', use_br_wgt=True)

    pdf.proc = 'ctrl'
    pdf.year = '2018'
    pdf.trig = 'ETOS'

    return pdf
#------------------------------------------
def test_simple():
    pdf = get_model()

    obj = set_pdf(pdf)
    pdf = obj.get_pdf(fit_version = 'v20')
    pdf = obj.get_pdf()
#------------------------------------------
if __name__ == '__main__':
    test_simple()

