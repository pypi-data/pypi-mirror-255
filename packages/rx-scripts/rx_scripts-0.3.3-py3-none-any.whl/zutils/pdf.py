import zfit
import math
import numpy
import tensorflow      as tf
import scipy.integrate as spi

from scipy.interpolate import interp1d
from zfit              import z 

#--------------------------------------------------
class dscb(zfit.pdf.ZPDF):
    _N_OBS  = 1 
    _PARAMS = ['mu', 'sg', 'al', 'ar', 'nl', 'nr']

    def _unnormalized_pdf(self, x): 
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        sg   = self.params['sg']
        al   = self.params['al']
        ar   = self.params['ar']
        nl   = self.params['nl']
        nr   = self.params['nr']

        p1  = (x-mu)/sg
        p2  = z.pow(nl/z.numpy.abs(al), nl) * z.exp(-al * al / 2)
        p3  = z.pow(nr/z.numpy.abs(ar), nr) * z.exp(-ar * ar / 2)
        p4  = nl/z.numpy.abs(al) - z.numpy.abs(al)
        p5  = nr/z.numpy.abs(ar) - z.numpy.abs(ar)

        v_1 = p2 * z.pow(p4 - p1, -nl)
        v_2 = p3 * z.pow(p5 + p1, -nr)
        v_3 = z.exp(-p1 ** 2 / 2)

        flg = z.numpy.where(p1 <-al , 1  , z.numpy.where(p1 > ar ,   2,   3)) 

        res = z.numpy.where(flg == 1, v_1, z.numpy.where(flg == 2, v_2, v_3))

        return res 
#-------------------------------------------------------------------
class shape(zfit.pdf.ZPDF):
    '''
    Class used to build a Zfit PDF from arrays of x and y values
    '''
    _N_OBS  = 1
    _PARAMS = []
    #--------------------------------------------
    @staticmethod
    def shape_integral(limits, params, model):
        [[[min_x]], [[max_x]]] = (limits.limits)

        result, error = spi.quad(model._ifun, min_x, max_x, limit=200)

        return result 
    #--------------------------------------------
    def __init__(self, obs, arr_x=None, arr_y=None, name='shape_pdf', **params):
        super().__init__(obs, name, **params)
        tf.config.run_functions_eagerly(True)
        self._arr_x= arr_x
        self._arr_y= arr_y
        self._ifun = interp1d(arr_x, arr_y, kind='cubic')

        limits = zfit.Space(axes=0, limits=(zfit.Space.ANY_LOWER, zfit.Space.ANY_UPPER))
        shape.register_analytic_integral(func=shape.shape_integral, limits=limits)
    #--------------------------------------------
    def _unnormalized_pdf(self, x):
        l_xval = x.value().numpy().flatten()
        l_yval = [ self._ifun(xval) for xval in l_xval ]
 
        return numpy.array(l_yval)
#-------------------------------------------------------------------
class hypexp(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'alpha', 'beta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        ap   = self.params['alpha']
        bt   = self.params['beta']

        u   = (x - mu) 
        val = z.exp(-bt * x) / (1 + z.exp(-ap * u))

        return val 
#-------------------------------------------------------------------
class modexp(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'alpha', 'beta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        ap   = self.params['alpha']
        bt   = self.params['beta']

        u   = (x - mu) 
        val = (1 - z.exp(-ap * u)) * z.exp(-bt * u)

        return val 
#-------------------------------------------------------------------
class genexp(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'sg', 'alpha', 'beta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        sg   = self.params['sg']
        ap   = self.params['alpha']
        bt   = self.params['beta']

        u   = (x - mu) / sg
        val = (1 - z.exp(-ap * u)) * z.exp(-bt * u)

        return val 
#-------------------------------------------------------------------
class SUJohnson(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'lm', 'gamma', 'delta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        lb   = self.params['lm']
        gm   = self.params['gamma']
        dl   = self.params['delta']

        u = (x - mu) / lb

        a = dl / (lb * z.sqrt(2 * math.pi))
        b = 1  / z.sqrt(1 + u ** 2)
        c = - 1/2 * (gm + dl * tf.math.asinh(u)) ** 2

        val = a * b * z.exp(c)

        return val 
#-------------------------------------------------------------------
class FermiDirac(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'ap']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        ap   = self.params['ap']

        exp  = (x - mu) / ap
        den  = 1 + z.exp(exp)

        return 1. / den
#-------------------------------------------------------------------
def fd_integral(limits, params, model):
    lower, upper = limits.limit1d
    mu           = params['mu']
    ap           = params['ap']

    exp1         = (upper - mu) / ap
    exp2         = (lower - mu) / ap

    num          = 1 + math.exp(exp1) 
    den          = 1 + math.exp(exp2) 

    val = upper - lower - ap * math.log(num/den);

    if math.isnan(val) or math.isinf(val) or val <= 0:
        print(f'Invalid value: {val}')
        raise

    return val
#-------------------------------------------------------------------
#limits = zfit.Space.from_axes(axes=0, limits=(zfit.Space.ANY_LOWER, zfit.Space.ANY_UPPER))
#FermiDirac.register_analytic_integral(func=fd_integral, limits=limits)
#-------------------------------------------------------------------

