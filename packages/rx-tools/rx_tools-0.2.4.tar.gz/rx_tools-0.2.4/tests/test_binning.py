from rk.binning import binning

import math
#-------------------------------------
def test_simple():
    obj = binning()
    obj['x'] = [1, 2, 3, 4]
    obj['y'] = [1, 2, 3]

    print(obj)
    
    ibin = obj.find_bin('x', -1)
    assert(ibin == 0)
    
    ibin = obj.find_bin('x', 1.2)
    assert(ibin == 1)
    
    ibin = obj.find_bin('x', 5.2)
    assert(ibin == 4)
#-------------------------------------
def test_bound():
    obj = binning()
    obj['x'] = [1, 2, 3, 4]
    obj['y'] = [1, 2, 3]

    print(obj)
    
    bnd = obj.find_bin_bounds('x', 0.2)
    assert(bnd == (-math.inf, 1))

    bnd = obj.find_bin_bounds('x',  3.1)
    assert(bnd == (3,4))
    
    bnd = obj.find_bin_bounds('x', 1.2)
    assert(bnd == (1,2))
    
    bnd = obj.find_bin_bounds('x', 2.2)
    assert(bnd == (2,3))

    bnd = obj.find_bin_bounds('x', 4.2)
    assert(bnd == (4, math.inf))
#-------------------------------------
def test_arr_var():
    obj = binning()
    obj['m[0]'] = [1, 2, 3]
    obj['x']    = [1, 2, 3, 4]
    obj['y']    = [1, 2, 3]

    assert(obj.arr_vars == ['m[0]'])
#-------------------------------------
def test_arr_to_var():
    obj = binning()
    obj['m[0]'] = [1, 2, 3]
    obj['x[3]'] = [1, 2, 3, 4]
    obj['y']    = [1, 2, 3]
    obj.arr_to_var()

    assert( list(obj.keys()) == ['m', 'x', 'y'])
#-------------------------------------
def main():
    test_arr_to_var()
    test_arr_var()
    test_simple()
    test_bound()
#-------------------------------------
if __name__ == '__main__':
    main()

