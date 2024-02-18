import numpy
import math

from rk.reso_extractor import extractor as rext

#---------------------------
class data:
    noise = 1
#---------------------------
def reso(x):
    return x**2 
#---------------------------
def ee_reso(res_x, res_y):
    return numpy.sqrt(res_x ** 2 + res_y ** 2)
#---------------------------
def get_vals(arr_coor):
    arr_x = arr_coor.T[0]
    arr_y = arr_coor.T[1]

    arr_rx = reso(arr_x)
    arr_ry = reso(arr_y)

    arr_val = ee_reso(arr_rx, arr_ry) + get_noise()
    arr_err = numpy.full(arr_x.size, data.noise)

    arr_res = numpy.array([arr_val, arr_err]).T

    return arr_res
#---------------------------
def get_coor(nbins):
    l_point = []
    for i_x in range(1, nbins + 1):
        for i_y in range(1, nbins + 1):
            point = [i_x, i_y]
            l_point.append(point)

    return numpy.array(l_point)
#---------------------------
def get_noise():
    return numpy.random.normal(0, data.noise)
#---------------------------
def get_data(nbins):
    arr_coor   = get_coor(nbins)
    arr_vals   = get_vals(arr_coor)

    return { tuple(coo.tolist()) : [val, err] for coo, [val, err] in zip(arr_coor, arr_vals)}
#---------------------------
def main():
    nbins = 10
    d_dat = get_data(nbins)

    obj = rext(data=d_dat, nbins=nbins)
    res = obj.calculate()

    print(res)
#---------------------------
if __name__ == '__main__':
    main()

