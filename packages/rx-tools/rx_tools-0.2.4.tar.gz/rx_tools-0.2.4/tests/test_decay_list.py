from rk.decay_finder import decay_list as dec_lst 

#---------------------------------------
def test(l_part):
    obj=dec_lst()
    df = obj.get_decays(l_part)
    print(df)
#---------------------------------------
if __name__ == '__main__':
    test(['Bu', 'ee', 'psi'])
    test(['Bd', 'ee', 'psi'])

