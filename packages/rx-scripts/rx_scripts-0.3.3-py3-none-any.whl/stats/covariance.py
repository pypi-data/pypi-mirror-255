import utils_noroot as utnr

import numpy
#-----------------------------------------
class covariance:
    '''
    Used to calculate covariance matrices from array of nominal measurements
    2D matrix where instead nominal measurements a row of measurements are added. 
    '''
    log=utnr.getLogger(__name__)
    #-----------------------------------------
    def __init__(self, arr_meas, arr_nom):
        self._arr_meas = arr_meas
        self._arr_nom  = arr_nom

        self._nvar     = None
        self._nmes     = None

        self._initialized = False
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        xm = self._get_shape(self._arr_meas, 2)
        xn = self._get_shape(self._arr_nom , 1)

        if xn != xm:
            self.log.error(f'Measurement and nominal arrays are not compatible: {xn}-{xm}')
            raise

        self._nvar = xm

        self.log.info(f'Found {self._nvar} variables and {self._nmes} measurements')

        self._initialized = True
    #-----------------------------------------
    def _get_shape(self, arr, size):
        try:
            if size   == 2:
                x, y = arr.shape
                self._nmes = y
            elif size == 1:
                x,   = arr.shape
            else:
                self.log.error(f'Testing for invalid size {size}')
                raise
        except:
            self.log.error(f'Cannot retrieve shape of size {size} for array:')
            print(arr)
            raise

        return x 
    #-----------------------------------------
    def get_cov(self):
        self._initialize()

        l_arr_dev = []
        for arr_meas, nom in zip(self._arr_meas, self._arr_nom):
            arr_dev = arr_meas - nom 
            l_arr_dev.append(arr_dev)

        mat = numpy.zeros((self._nvar, self._nvar))

        for i_var in range(self._nvar):
            dev_i = l_arr_dev[i_var]
            for j_var in range(self._nvar):
                dev_j = l_arr_dev[j_var]

                mat[i_var][j_var] = numpy.dot(dev_i , dev_j) / self._nmes

        return mat 
#-----------------------------------------

