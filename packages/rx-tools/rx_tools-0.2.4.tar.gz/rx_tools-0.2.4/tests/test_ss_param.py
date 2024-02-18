from rk.model import ss_param 

#---------------------------------------
def test():
    ssp = ss_param('ctrl', 'ETOS', '2016')
    ssp.val_dir = 'tests/ss_param'
    d_par = ssp.get_pars(model='exp')
#---------------------------------------
if __name__ == '__main__':
    test()

