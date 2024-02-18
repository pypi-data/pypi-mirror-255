import utils_noroot      as utnr
import matplotlib.pyplot as plt
import numpy 
import logging
import utils 

from atr_mgr import mgr as amgr

#----------------------------------------------------
class plotter:
    log=utnr.getLogger(__name__)
    #---------------------------
    def __init__(self, d_df, l_expr, nbins=30):
        self._d_df  = d_df
        self._l_expr= l_expr
        self._nbins = nbins 
        self._quant = 0.02

        self._s_var = set()

        self._d_xrange = {}

        self._initialized = False
    #---------------------------
    def _initialize(self):
        if self._initialized:
            return

        d_df = {}
        for key, df in self._d_df.items():
            d_df[key] = self._add_vars(df)
        self._d_df = d_df

        utils.log.setLevel(logging.WARNING)
        amgr.log.setLevel(logging.WARNING)

        self._initialized = True
    #---------------------------
    def _get_var_name(self, exp):
        exp=exp.replace('(', '_')
        exp=exp.replace(')', '_')
        exp=exp.replace(':', '_')

        return exp
    #---------------------------
    def _add_vars(self, df):
        mg = amgr(df)
        l_col = df.GetColumnNames()
        for expr in self._l_expr:
            if expr in l_col:
                self._s_var.add(expr)
                continue

            name = self._get_var_name(expr)
            self._s_var.add(name)
    
            df = df.Define(name, expr)

            self.log.info(f'{name:<20}{"->":<10}{expr:<40}')

        df = mg.add_atr(df)
    
        return df
    #---------------------------
    def _filter(self, mat, var, key):
        s_size = mat.shape[0]
        mat    = [ row for row in mat if True not in numpy.isnan(row) ]
        mat    = [ row for row in mat if True not in numpy.isinf(row) ]
        mat    = numpy.array(mat)
        f_size = mat.shape[0]

        if s_size != f_size:
            self.log.warning(f'Data was filtered for {var}/{key}: {s_size} -> {f_size}')

        return mat 
    #---------------------------
    def _get_range(self, var, arr_var):
        if var not in self._d_xrange:
            min_x = numpy.quantile(arr_var,     self._quant)
            max_x = numpy.quantile(arr_var, 1 - self._quant)

            if numpy.isnan(min_x) or numpy.isnan(max_x):
                self.log.error(f'Range [{min_x}, {max_x}] contains NaNs')
                self.log.info(f'{"Quantile":<10}{self._quant:<.3f}')
                print(arr_var)
                raise

            self._d_xrange[var] = (min_x, max_x)

        rng = self._d_xrange[var]

        return rng
    #---------------------------
    def _get_data(self, df, var, key):
        if not hasattr(df, 'weight'):
            self.log.info(f'Not using any weight')
            df = df.Define('weight', '1')
        else:
            self.log.info(f'Using user-defined weight: {df.weight}')
            df = df.Define('weight', df.weight)

        mat = utils.getMatrix(df, [var, 'weight'])
        mat = self._filter(mat, var, key)

        arr_var = mat.T[0]
        arr_wgt = mat.T[1]

        return arr_var, arr_wgt 
    #---------------------------
    def _plot(self, df, var, key):
        arr_var, arr_wgt = self._get_data(df, var, key)
        rng              = self._get_range(var, arr_var)

        try:
            plt.hist(arr_var, weights=arr_wgt, bins=self._nbins, density=True, histtype='step', range=rng, label=key)
        except:
            self.log.error('Cannot plot:')
            self.log.info(f'{"NBins":<10}{self._nbins:<20}')
            self.log.info(f'{"Range":<10}{str(rng):<20}')
            self.log.info(f'{"Key":<10}{key:<20}')
            self.log.info(f'{"Expr":<10}{var:<30}')
            print(arr_var)

            raise
    #---------------------------
    def save(self, out_dir, title=None):
        self._initialize()

        for var in self._s_var:
            for key, df in self._d_df.items():
                self._plot(df, var, key)

            plt.title(title)
            plt.legend()
            plt.ylabel('Normalized')
            plt.xlabel(var)
            plt.tight_layout()

            plot_path = f'{out_dir}/{var}_lin.png'
            self.log.visible(f'Saving: {plot_path}')
            plt.yscale('linear')
            plt.savefig(plot_path)

            plot_path = f'{out_dir}/{var}_log.png'
            self.log.visible(f'Saving: {plot_path}')
            plt.yscale('log')
            plt.savefig(plot_path)

            plt.close('all')
#----------------------------------------------------

