from rk.model_constraints import model_const 

#----------------------
def test():
    obj    = model_const(eff='v16', yld='v11') 
    mu, sg = obj.get_pars()

    print(mu)
#----------------------
if __name__ == '__main__':
    test()

