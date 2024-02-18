from rk.stats import gen_yld as gyld

#------------------------------------
class data:
    vers = 'v10.21p2'
    
    l_proc = ['sign_ee', 'sign_mm', 'ctrl_ee', 'ctrl_mm', 'psi2_ee', 'psi2_mm']
    l_year = ['2011', '2012', '2015', '2016', '2017', '2018']
#------------------------------------
def test(proc, year):
    obj = gyld(proc=proc, year=year, vers=data.vers)
    nev = obj.nevents()

    print(f'{nev:>20}{proc:>20}{year:>20}')
#------------------------------------
if __name__ == '__main__':
    for proc in data.l_proc:
        for year in data.l_year:
            test(proc, year)

