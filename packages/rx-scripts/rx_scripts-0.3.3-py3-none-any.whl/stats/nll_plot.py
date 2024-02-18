from iminuit import Minuit

#---------------------------------
class plotter:
    def __init__(self, nll=None):
        self._nll   = nll
        self._d_val = None
        self._d_par = None

        self._initialized = False
    #---------------------------------
    def _initialize(self):
        if self._initialized:
            return

        s_par        = self._nll.get_params()
        l_par        = list(s_par)

        self._l_par  = [par                            for par in l_par]
        self._d_val  = {par.name : par.value().numpy() for par in l_par}
        self._l_name = [par.name                       for par in l_par]

        Minuit.errordef = Minuit.LIKELIHOOD

        self._initialized = True
    #---------------------------------
    def _cost(self, *args):
        for par, val in zip(self._l_par, args):
            par.set_value(val)
    
        return self._nll.value()
    #---------------------------------
    def make_mncontour(self, x=None, y=None, cl=None):
        self._initialize()

        m = Minuit(self._cost, **self._d_val, name=self._l_name) 
        m.migrad()
        m.draw_mncontour(x, y, cl=cl)
#---------------------------------

