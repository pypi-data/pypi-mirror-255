from rk.pr_shapes import pr_maker as prm

#---------------------------------------
def test_simple():
    obj = prm('bpXcHs_ee', '2018', 'ETOS', 'v10.18is', 'jpsi')
    obj.save_data(version='test')
#---------------------------------------
def main():
    test_simple()
#---------------------------------------
if __name__ == '__main__':
    main()

