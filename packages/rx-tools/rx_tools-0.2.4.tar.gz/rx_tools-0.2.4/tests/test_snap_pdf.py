from rk.snap_pdf import snap_pdf as spdf

import zfit
#----------------------------------
def get_pdf():
    obs = zfit.Space('x', limits=(-10, 10))
    mu  = zfit.Parameter("mu", 2.4, -1, 5)
    sg  = zfit.Parameter("sg", 1.3,  0, 5, floating=False)
    pdf = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)
    nev = zfit.Parameter("nev", 0, 0,  1000)

    pdf = pdf.create_extended(nev, 'pdf')

    return pdf
#----------------------------------
def test_simple():
    pdf=get_pdf()

    obj=spdf(pdf)
    obj.save('simple')
    obj.load('simple')
#----------------------------------
def main():
    test_simple()
#----------------------------------
if __name__ == '__main__':
    main()
