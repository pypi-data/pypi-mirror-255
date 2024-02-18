from rk.mc_map_calc import calculator as mapc

#-------------------------
def test_simple():
    obj=mapc(year='2018', trigger='ETOS', version='v10.18is')
    d_map = obj.get_maps()

    print(d_map)
#-------------------------
if __name__ == '__main__':
    test_simple()

