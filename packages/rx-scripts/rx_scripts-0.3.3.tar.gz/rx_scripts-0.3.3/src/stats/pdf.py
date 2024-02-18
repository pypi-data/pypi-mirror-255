import scipy.stats as st
import numpy

from scipy.integrate import quad
import utils_noroot as utnr

log=utnr.getLogger(__name__)
#----------------------------------
class test(st.rv_continuous):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scale, _ = quad(self.__form, self.a, self.b)
    #--------------------------
    def __form(self, x):
        return x + numpy.exp(-x)
    #--------------------------
    def _pdf(self, x):
        return self.__form(x) / self.scale
#----------------------------------
class sigmoid(st.rv_continuous):
    def __init__(self, m=0, s=1, *args, **kwargs):
        self.m = m
        self.s = s
        super().__init__(*args, **kwargs)

        self.normalization = self.__integral(self.b) - self.__integral(self.a)
    #--------------------------
    def __integral(self, x):
        u = self.s * numpy.exp(self.m - x)

        return numpy.log( (1 + u) / u)
    #--------------------------
    def __form(self, x):
        return 1. / (1 + self.s * numpy.exp(self.m-x))
    #--------------------------
    def _pdf(self, x):
        return self.__form(x) / self.normalization
#----------------------------------
class pos_tanh(st.rv_continuous):
    def __init__(self, m=0, s=1, *args, **kwargs):
        self.m = m
        self.s = s
        super().__init__(*args, **kwargs)

        upper = self.__integral(self.b)
        lower = self.__integral(self.a)
        normalization = upper - lower

        if normalization <= 0:
            log.error('Found normalization {} = {:.3e} - {:.3e}, in range ({:.3e},{:.3e})'.format(normalization, upper, lower, self.a, self.b))
            raise
        else:
            self.normalization = normalization 
    #--------------------------
    def __integral(self, x):
        u = self.s * (x - self.m)

        return x + numpy.log(numpy.cosh(u)) / self.s
    #--------------------------
    def _cdf(self, x):
        area = self.__integral(x) - self.__integral(self.a)

        cdf = area / self.normalization 

        return cdf
#----------------------------------

