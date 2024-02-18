from logzero     import logger as log
from zutils.plot import plot   as zfp

import matplotlib.pyplot as plt
import zutils.utils      as zut
import utils_noroot      as utnr
import pandas            as pnd

import os
import tqdm
import zfit
import numpy
import time

#---------------------------------
class analyzer:
    '''
    This tool is meant to provide diagnostic information on an extended PDF as
    implemented by Zfit
    '''
    #---------------------------------
    def __init__(self, pdf=None, d_const=None, nev_fac=1):
        self._pdf     = pdf
        self._d_cns   = d_const
        self._nev_fac = nev_fac

        self._dat     = None
        self._nll     = None
        self._mnz     = None
        self._out_dir = None
        self._min_obs = None
        self._max_obs = None
        self._l_nam   = None
        self._d_inival= dict()
        self._d_info  = dict()

        self._initialized = False
    #---------------------------------
    @property
    def out_dir(self):
        return self._out_dir

    @out_dir.setter
    def out_dir(self, value):
        if value is None:
            return

        try:
            os.makedirs(value, exist_ok=True)
        except:
            log.error(f'Cannot make: {value}')
            raise

        self._out_dir = value
    #---------------------------------
    def _initialize(self):
        if self._initialized:
            return

        zfit.settings.changed_warnings.all = False

        self._check_pdf()
        log.debug('Creating sampler')
        self._dat = self._pdf.create_sampler(fixed_params=False)
        self._prepare_fit()

        self._initialized = True
    #---------------------------------
    def _get_const(self):
        if self._d_cns is None:
            return

        l_par = [ par                      for par in self._pdf.get_params() if par.name in self._d_cns] 

        if len(l_par) == 0:
            log.warning(f'Found no floating parameters to constrain')
            return

        l_val = [ self._d_cns[par.name][0] for par in l_par ] 
        l_err = [ self._d_cns[par.name][1] for par in l_par ] 

        return zfit.constraint.GaussianConstraint(l_par, l_val, l_err)
    #---------------------------------
    def _prepare_fit(self):
        log.debug('Preparing fit')
        cons      = self._get_const()
        self._nll = zfit.loss.ExtendedUnbinnedNLL(model=self._pdf, data=self._dat, constraints=cons)
        self._mnz = zfit.minimize.Minuit()
    #---------------------------------
    def _check_pdf(self):
        log.debug('Checking PDF')
        if self._pdf is None:
            log.error(f'Missing PDF')
            raise

        if not self._pdf.is_extended:
            log.error(f'Only extended PDFs supported')
            raise

        s_par       = self._pdf.get_params()
        self._l_nam = [ par.name for par in s_par ]

        self._d_inival = { par.name : par.value().numpy() for par      in s_par }
        d_yield        = { key      : self._nev_fac * val for key, val in self._d_inival.items() if key.startswith('n')}

        self._d_inival.update(d_yield)
    #---------------------------------
    def _reset_pdf(self):
        s_par = self._pdf.get_params()
        for par in s_par:
            ini_val = self._d_inival[par.name]
            par.set_value(ini_val)
    #---------------------------------
    def _plot_data(self, i_fit, nfit):
        if self._out_dir is None:
            return
        elif i_fit == 10 or (i_fit == nfit - 1):
            plot_path = f'{self._out_dir}/data.png'
            plt.savefig(plot_path)
            plt.close('all')
            return
        elif i_fit > 10:
            return

        arr_val = self._dat.numpy().flatten()
        if (self._min_obs is None) or (self._max_obs is None):
            self._min_obs = min(arr_val)
            self._max_obs = max(arr_val)

        plt.hist(arr_val, bins=30, range=[self._min_obs, self._max_obs], histtype='step')
    #---------------------------------
    def _plot_fit(self, i_fit):
        if self._out_dir is None:
            return
        elif i_fit > 10:
            return

        obj=zfp(data=self._dat, model=self._pdf, result=None)
        obj.plot(nbins=50, stacked=False)

        plot_path = f'{self._out_dir}/fits/{i_fit:03}.png'
        utnr.make_path_dir(plot_path)

        plt.savefig(plot_path)
        plt.close('all')
    #---------------------------------
    def _run_minimization(self, nfit, kind=None):
        l_res = []

        log.info(f'Running fits, for {kind}')
        for i_fit in tqdm.trange(nfit, ascii=' -'):
            self._reset_pdf()
            zut.print_pdf(self._pdf, txt_path=f'{self._out_dir}/model/pre_{i_fit:03}.txt', d_const=self._d_cns)
            self._dat.resample()
            self._plot_fit(i_fit)
            res=self._mnz.minimize(self._nll)
            zut.print_pdf(self._pdf, txt_path=f'{self._out_dir}/model/pos_{i_fit:03}.txt', d_const=self._d_cns)
            l_res.append(res)

        return l_res
    #---------------------------------
    def _run_hesse(self, l_res):
        log.info('Running Hesse')
        for res in tqdm.tqdm(l_res, ascii=' -'):
            try:
                res.hesse()
            except:
                log.warning('Hesse failed, skipping')
                continue
    #---------------------------------
    def speed(self, nfit=100):
        '''
        Run fit multiple times and time it

        Parameters:
        -------------------
        nfit (int): Number of fits over which to average the fitting time
        '''
        self._initialize()
        log.info(f'Using {nfit} fits')


        t_1   = time.time()
        l_res = self._run_minimization(nfit, kind='speed')
        t_2   = time.time()
        self._run_hesse(l_res)
        t_3   = time.time()

        t_fit = (t_2 - t_1) / nfit
        t_hes = (t_3 - t_2) / nfit

        self._d_info['Fit/second'] = t_fit
        self._d_info['Hes/second'] = t_hes 
        self._d_info['#Fits']      = nfit 

        log.info(f'Fit takes: {t_fit:.3} seconds')
        log.info(f'Hesse takes: {t_hes:.3} seconds')

        self._finalize()
    #---------------------------------
    def _plot_pulls(self, df):
        pull_dir = f'{self._out_dir}/pulls'
        os.makedirs(pull_dir, exist_ok=True)

        for column in df.columns:
            arr_pull=df[column].values
            zut.fit_pull(arr_pull, plot=True, var_name=column)
            pull_path = f'{pull_dir}/{column}.png'
            plt.savefig(pull_path)
            plt.close('all')
    #---------------------------------
    def fit(self, nfit=100):
        '''
        Used to make toy fits and make pull distributions 

        Parameters
        ------------------
        nfit (int): Number of fits over which to average the fitting time
        '''
        self._initialize()

        l_res = self._run_minimization(nfit, kind='pulls')
        self._run_hesse(l_res)

        df_ini, df_val, df_err, df_pul = self._get_fit_df(l_res)
        self._plot_pulls(df_pul)

        return df_ini, df_val, df_err
    #---------------------------------
    def _get_val_err(self, res):
        l_ini = []
        l_val = []
        l_err = []

        res.freeze()
        for nam in self._l_nam:
            d_val = res.params[nam]
            ini   = self._d_inival[nam]
            val   = d_val['value']
            err   = d_val['hesse']['error'] 

            l_ini.append(ini)
            l_val.append(val)
            l_err.append(err)

        return l_ini, l_val, l_err
    #---------------------------------
    def _get_fit_df(self, l_res):
        df_ini = pnd.DataFrame(columns=self._l_nam)
        df_val = pnd.DataFrame(columns=self._l_nam)
        df_err = pnd.DataFrame(columns=self._l_nam)

        for res in l_res:
            l_ini, l_val, l_err = self._get_val_err(res)

            df_ini = utnr.add_row_to_df(df_ini, l_ini)
            df_val = utnr.add_row_to_df(df_val, l_val)
            df_err = utnr.add_row_to_df(df_err, l_err)

        df_pul = (df_val - df_ini) / df_err

        return df_ini, df_val, df_err, df_pul
    #---------------------------------
    def sampling_speed(self, nsample=100):
        [[min_x]], [[max_x]] = self._pdf.space.limits
        arr_xval = numpy.linspace(min_x, max_x, nsample)

        log.info(f'Sampling {self._pdf}')
        [ self._pdf.pdf(xval) for xval in tqdm.tqdm(arr_xval, ascii=' -') ]

        for pdf in self._pdf.pdfs:
            log.info(f'Sampling {pdf.name}')
            [ pdf.pdf(xval) for xval in tqdm.tqdm(arr_xval, ascii=' -') ]
    #---------------------------------
    def _finalize(self):
        if self._out_dir is None:
            return

        out_path = f'{self._out_dir}/info.json'
        utnr.dump_json(self._d_info, out_path)

        log.info(f'Saving to: {out_path}')
#---------------------------------

