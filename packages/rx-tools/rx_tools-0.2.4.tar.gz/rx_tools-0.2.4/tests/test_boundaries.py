from rk.boundaries import boundaries
import random

#--------------------------------
def test_sort():
    l_tp = []
    for ix in range(1, 4):
        for iy in range(1, 4):
            tp = ((ix + 0, ix + 1), (iy + 0, iy + 1))
            l_tp.append(tp)
    
    random.shuffle(l_tp)
    
    d_data_org = { boundaries(tp) : 'x' for tp in l_tp }
    d_data_srt = dict(sorted(d_data_org.items()))
    
    for (key_org, _), (key_srt, _) in zip(d_data_org.items(), d_data_srt.items()):
        print(f'{key_srt}')
#--------------------------------
def test_string(stup):
    obj=boundaries(stup)

    print(obj)
#--------------------------------
def test_simple():
    tp=((1.0, 2.0), (3.0, 4.0))
    obj=boundaries(tp)

    print(obj)
#--------------------------------
def test_strings():
    tp1 ='(( 1.0, 2.0), (3.0, 4.0))'
    tp2 ='((-inf, 2.0), (3.0, 4.0))'
    tp3 ='((1.0, 2.0), (3.0, inf))'
    
    test_string(tp1)
    test_string(tp2)
    test_string(tp3)
#--------------------------------
def test_inf(tup, value):
    obj=boundaries(tup)

    assert obj.has_inf() == value
#--------------------------------
def test_infs():
    tp1 ='(( 1.0, 2.0), (3.0, 4.0))'
    tp2 ='((-inf, 2.0), (3.0, 4.0))'
    tp3 ='((1.0, 2.0), (3.0, inf))'

    test_inf(tp1, False)
    test_inf(tp2,  True)
    test_inf(tp3,  True)
#--------------------------------
def test_identifier():
    tp=((1.0, 2.0), (3.0, 4.0))
    obj=boundaries(tp)

    print(obj.identifier)
#--------------------------------
def main():
    test_identifier()

    return

    test_sort()
    test_infs()
    test_simple()
    test_strings()
#--------------------------------
if __name__ == '__main__':
    main()

