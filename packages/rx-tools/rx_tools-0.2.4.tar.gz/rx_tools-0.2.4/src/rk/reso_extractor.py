import math
import numpy

import utils_noroot as utnr
import numdifftools as ndt

from scipy.optimize import minimize

#---------------------------
class extractor:
    log = utnr.getLogger('reso_extractor')
    #---------------------------
    def __init__(self, data=None, method = None, bounds=None, init_x = None, nbins=10):
        self._d_data = data
        self._nbins  = nbins

        self._bounds = bounds 
        self._method = method 
        self._init_x = init_x 

        self._initialized = False
    #---------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._nbins >= 2:
            pass
        else:
            self.log.error(f'Invalid value for number of bins: {self._nbins}')
            raise ValueError

        if self._bounds is None:
            self.log.info('Bounds not specified, using non-negative bounds')
            self._bounds = self._nbins * [[0, None]]

        if self._method is None:
            self.log.info('Method not specified, using default')

        if self._init_x is None:
            self.log.info('Starting point not specified, using origin')
            self._init_x = self._nbins * [0]

        try:
            self._check_data()
        except:
            self.log.error(f'Invalid data found in dictionary:')
            self.log.info(self._d_data)
            raise

        self._initialized = True
    #---------------------------
    def _check_data(self):
        for (x, y), [ree, eee] in self._d_data.items():
            if not isinstance(  x, (float, int)):
                self.log.error(f'Invalid type for X coordinate: {x}')
                raise TypeError

            if not isinstance(  y, (float, int)):
                self.log.error(f'Invalid type for Y coordinate: {y}')
                raise TypeError

            if not isinstance(ree, float):
                self.log.error(f'Invalid type for ee resolution: {ree}')
                raise TypeError

            if not isinstance(eee, float):
                self.log.error(f'Invalid type for ee resolution: {eee}')
                raise TypeError

            if ree <= 0:
                self.log.error(f'Invalid dielectron resolution value found: {ree}')
                raise ValueError

            if eee <= 0:
                self.log.error(f'Invalid dielectron resolution error found: {eee}')
                raise ValueError
    #---------------------------
    def _ee_reso(self, res_x, res_y):
        return math.sqrt(res_x ** 2 + res_y ** 2)
    #---------------------------
    def _chi2(self, arr_res):
        chi2 = 0
        for (x, y), [mes, err] in self._d_data.items():
            r_x = arr_res[x - 1]
            r_y = arr_res[y - 1]
    
            pred = self._ee_reso(r_x, r_y)
    
            chi2+= (mes - pred) ** 2 / err ** 2
    
        return chi2
    #---------------------------
    def _get_errors(self, arr_val):
        h   = ndt.Hessian(self._chi2)
        hes = h(arr_val)
        cov = 2 * numpy.linalg.inv(hes)
        dia = numpy.diag(cov)
        err = numpy.sqrt(dia)

        return err
    #---------------------------
    def calculate(self):
        self._initialize()

        self.log.info(f'Minimizing')
        res     = minimize(self._chi2, self._init_x, method=self._method, bounds=self._bounds)
        arr_val = res.x

        self.log.info(f'Calculating errors')
        arr_err = self._get_errors(arr_val)
        arr_res = numpy.array([arr_val, arr_err]).T

        return arr_res 
#---------------------------

