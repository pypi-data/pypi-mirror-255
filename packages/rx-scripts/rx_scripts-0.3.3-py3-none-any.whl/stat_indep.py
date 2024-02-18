import utils_noroot as utnr
import numpy

from resample import permutation as perm
#-----------------------------
class calculator:
    log=utnr.getLogger(__name__)
    #-----------------------------
    def __init__(self, l_array):
        self._l_array = l_array

        self._initialized = False
    #-----------------------------
    def _initialize(self):
        if self._initialized:
            return

        utnr.check_type(self._l_array, list)
        self._check_sizes()


        self._initialzed = True
    #-----------------------------
    def _check_sizes(self):
        size = None
        for arr_data in self._l_array:
            tmp = self._get_array_size(arr_data)

            if   size is None:
                size = tmp
                continue
            elif size != tmp:
                self.log.error(f'Incompatible sizes found: {size}/{tmp}')
                raise
            else:
                pass
    #-----------------------------
    def _get_array_size(self, arr_data):
        try:
            size, = arr_data.shape
        except:
            self.log.error(f'Invalid array of shape: {arr_data.shape}')
            raise

        return size
    #-----------------------------
    def _get_pvalue(self, arr_x, arr_y):
        w, x, y = numpy.histogram2d(arr_x, arr_y, bins=20)

        r = perm.usp(w, random_state=1)

        return r.pvalue
    #-----------------------------
    def get_pvalue_matrix(self):
        self._initialize()

        size = len(self._l_array)
        mat  = numpy.empty((size, size))
        for i_arr in range(0, size):
            for j_arr in range(i_arr, size):
                arr_x = self._l_array[i_arr]
                arr_y = self._l_array[j_arr]

                pvalue= self._get_pvalue(arr_x, arr_y)

                mat[i_arr, j_arr] = pvalue

        return mat
#-----------------------------

