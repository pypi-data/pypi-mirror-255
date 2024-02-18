import utils_noroot as utnr
import zutils.utils as zfu

import zfit
import numpy 
import tqdm 
import logging
import matplotlib.pyplot as plt

from zutils.plot import plot    as zfp
from fitter      import zfitter

#---------------------------------
class mcpull_fit:
    log = utnr.getLogger('mcpull_fit')
    #---------------------------------
    def __init__(self, gen=None, fit=None, nsamples=None, fit_constraints=None, plot_format="png"):
        self._gen_pdf     = gen
        self._fit_pdf     = fit if fit is not None else gen
        self._fit_constraints = {} if fit_constraints is None else fit_constraints
        self._nsamples    = nsamples 

        self._l_res       = []
        self._plot_dir    = None
        self._sampler     = None

        self._initialized = False
        self._plot_format = plot_format
    #---------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir
    #---------------------------------
    @plot_dir.setter
    def plot_dir(self, value):
        self._plot_dir = utnr.make_dir_path(value)
    #---------------------------------
    def _initialize(self):
        if self._initialized:
            return
        
        if not isinstance(self._gen_pdf, zfit.pdf.BasePDF):
            self.log.error(f'Generating PDF is of invalid type: {type(self._gen_pdf)}')
            raise

        if not isinstance(self._fit_pdf, zfit.pdf.BasePDF):
            self.log.error(f'Fitting PDF is of invalid type: {type(self._fit_pdf)}')
            raise

        if self._gen_pdf is self._fit_pdf:
            self.log.info(f'Using same PDF for generating and fitting toys')
        else:
            self.log.info(f'Using different PDFs for generating and fitting toys')

        self._sampler = self._get_sampler()

        zfitter.log.setLevel(logging.WARNING)

        self._initialized = True
    #---------------------------------
    def _get_sampler(self):
        if   isinstance(self._nsamples, int) and self._nsamples > 0:
            nsamples = self._nsamples
        elif isinstance(self._nsamples, int):
            self.log.error(f'Incorrect number of samples: {self._nsamples}')
            raise
        elif self._nsamples is None and     self._gen_pdf.is_extended:
            par      = self._gen_pdf.get_yield() 
            nsamples = par.value().numpy()
        elif self._nsamples is None and not self._gen_pdf.is_extended:
            self.log.error(f'No number of samples specified for non-extended PDF')
            raise
        else:
            self.log.error(f'Wrong value of number of samples: {self._nsamples}')
            raise

        nsamples = int(nsamples)
        self.log.info(f'Sampler number of entries : {nsamples}')

        return self._gen_pdf.create_sampler(nsamples)
    #---------------------------------
    @property
    def results(self):
        return self._l_res
    #---------------------------------
    def run(self, ntoys=None):
        self._initialize()
        if not isinstance(ntoys, int) or ntoys <= 0:
            self.log.error(f'Number of toys not an integer bigger than zero: {ntoys}')
            raise

        for itoy in tqdm.trange(ntoys, ascii=' -'):
            # pdf  = zfu.copy_model(self._fit_pdf)
            pdf  = self._fit_pdf
            self._sampler.resample()

            obj  = zfitter(pdf, self._sampler)
            res  = obj.fit(d_const=self._fit_constraints)
            res.hesse()
            res.freeze()

            if self._plot_dir is not None:
                self._plot_fit(pdf, res, itoy)

            self._l_res.append(res)
    #---------------------------------
    def _plot_fit(self, pdf, res, ind):
        dat   = self._sampler
        obj   = zfp(data=dat, model=pdf, result=res)

        arr_minx, arr_maxx = pdf.space.limits
        minx = arr_minx.flatten()[0]
        maxx = arr_maxx.flatten()[0]

        obj.plot(plot_range = [minx, maxx])

        plt_dir = utnr.make_dir_path(f'{self._plot_dir}/fits')
        plt_path= f'{plt_dir}/fit_{ind:03}.{self._plot_format}'
        plt.savefig(plt_path, bbox_inches='tight')
        plt.close('all')
#---------------------------------
class mcpull_plt:
    log = utnr.getLogger('mcpull_plt')
    #---------------------------------
    def __init__(self, l_res, d_par, plot_format='png'):
        '''
        Takes:
        1. A list of fit result objects from zfit, all the objects must be frozen
        2. A dictionary {varname -> var value}, where the values are the ones before the fit
        '''
        self._l_res = l_res
        self._d_par = d_par

        self._l_par_name  = None
        self._plot_dir    = None

        self._nbins       = 30

        self._initialized = False
        self._plot_format = plot_format
    #---------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir
    #---------------------------------
    @plot_dir.setter
    def plot_dir(self, value):
        self._plot_dir = utnr.make_dir_path(value)
    #---------------------------------
    def _initialize(self):
        if self._initialized:
            return

        if self._plot_dir is None:
            self.log.error(f'Plotting directory not specified')
            raise

        if len(self._l_res) == 0:
            self.log.error(f'No results found')
            raise

        if not all(isinstance(res, zfit.minimizers.fitresult.FitResult) for res in self._l_res):
            self.log.error(f'Not all objects in input list are results')
            [ print(type(res)) for res in self._l_res]
            raise TypeError

        self._l_par_name = self._get_parnames()
        for parname in self._l_par_name:
            if parname in self._d_par:
                continue

            self.log.error(f'Fit parameter {parname} not found among model parameters:')
            self.log.error(self._d_par.keys())
            raise

        self._initialized = True
    #---------------------------------
    def _get_parnames(self):
        res = self._l_res[0]

        d_par = res.params

        return [ parname for parname in d_par ]
    #---------------------------------
    def _get_data(self, varname, l_status):
        '''
        Takes variable name and list of fit statuses
        Returns arrays of parameter values and errors, also the parameter value used to generate the data.
        It only picks up data from a fit if the status is among l_status
        '''
    
        l_fit_val = [ res.params[varname]['value']          for res in self._l_res if res.status in l_status]
        l_fit_err = [ res.params[varname]['hesse']['error'] for res in self._l_res if res.status in l_status]
        ini_val   = self._d_par[varname]
    
        return numpy.array(l_fit_val), numpy.array(l_fit_err), ini_val 
    #---------------------------------
    def _get_range(self, arr_data):
        arr_data = utnr.remove_outliers(arr_data, l_zscore=[4, 4, 3])

        return numpy.min(arr_data), numpy.max(arr_data)
    #---------------------------------
    def _plot_var(self, varname, l_status):
        arr_fit_val, arr_fit_err, ini_val = self._get_data(varname, l_status)

        arr_resi = arr_fit_val -     ini_val
        arr_pull = arr_resi    / arr_fit_err

        self._plot_residual(varname, arr_resi)
        self._plot_error   (varname, arr_fit_err)
        self._plot_dist    (varname, arr_fit_val, ini_val)
        self._plot_pull    (varname, arr_pull)
    #---------------------------------
    def _plot_residual(self, varname, arr_resi):
        plot_dir = utnr.make_dir_path(f'{self._plot_dir}/{varname}')

        plt.hist(arr_resi, bins=self._nbins, range=self._get_range(arr_resi), histtype='step')
        plt.xlabel('Fitted - Model')
        plt.ylabel('Entries')

        plot_path = f'{plot_dir}/residual.{self._plot_format}'

        self.log.visible(f'Saving to: {plot_path}')
        plt.title(f'Residual for {varname}')
        plt.savefig(plot_path)
        plt.close('all')
    #---------------------------------
    def _plot_error(self, varname, arr_error):
        plot_dir = utnr.make_dir_path(f'{self._plot_dir}/{varname}')
        _, maxe  = self._get_range(arr_error)

        plt.hist(arr_error, bins=self._nbins, range=[0, maxe], histtype='step')
        plt.xlabel(f'$\\varepsilon({varname})$')
        plt.ylabel('Entries')

        plot_path = f'{plot_dir}/error.{self._plot_format}'

        self.log.visible(f'Saving to: {plot_path}')
        plt.title(f'Error for {varname}')
        plt.savefig(plot_path)
        plt.close('all')
    #---------------------------------
    def _plot_pull(self, varname, arr_pull):
        plot_dir = utnr.make_dir_path(f'{self._plot_dir}/{varname}')
        mu=numpy.mean(arr_pull)
        sg=numpy.std (arr_pull)

        plt.hist(arr_pull, bins=self._nbins, range=(-4,4), histtype='step', label='Pull')
        plt.axvline(x=mu   , color='red', label='$\mu$')
        plt.axvline(x=mu+sg, color='red', label='$\mu+\sigma$', linestyle=':')
        plt.axvline(x=mu-sg, color='red', label='$\mu-\sigma$', linestyle='--')

        plt.xlabel(r'$\frac{fit - model}{\varepsilon}$')
        plt.ylabel('Entries')
        plt.legend()

        plot_path = f'{plot_dir}/pull.{self._plot_format}'

        self.log.visible(f'Saving to: {plot_path}')
        plt.title(f'Pull for {varname}')
        plt.savefig(plot_path)
        plt.close('all')
    #---------------------------------
    def _plot_dist(self, varname, arr_fit_val, ini_val):
        plot_dir = utnr.make_dir_path(f'{self._plot_dir}/{varname}')
        plt.hist(arr_fit_val, bins=self._nbins, range=self._get_range(arr_fit_val), histtype='step', label='Fitted')
        plt.axvline(x=ini_val, color='red', label='Model', linestyle=':')
        plt.xlabel(varname)
        plt.ylabel('Entries')
        plt.legend()

        plot_path = f'{plot_dir}/distribution.{self._plot_format}'

        self.log.visible(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
    #---------------------------------
    def plot_var(self, varname, l_status=[0]):
        self._initialize()

        if varname not in self._l_par_name:
            self.log.error(f'Parameter {varname} not found among:')
            self.log.error(self._l_parname)
            raise

        self._plot_var(varname, l_status)
    #---------------------------------
    def plot_status(self):
        l_status  = [ str(res.status) for res in self._l_res ] 

        plt.hist(l_status)
        plt.xlabel('Fit status')
        plt.ylabel('Entries')
        plt.grid()

        plot_path = f'{self._plot_dir}/status.{self._plot_format}'
        self.log.visible(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')
#---------------------------------

