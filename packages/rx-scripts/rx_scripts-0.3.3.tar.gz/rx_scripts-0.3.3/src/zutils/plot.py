import zfit
import hist
import mplhep
import pprint
import pandas            as pd
import numpy             as np
import matplotlib.pyplot as plt
import tensorflow        as tf
import utils_noroot      as utnr
import warnings

from log_store import log_store

log = log_store.add_logger('scripts:plot')
#----------------------------------------
class plot:
    def __init__(self, data=None, model=None, weights=None, result=None, suffix=''):
        '''
        obs: zfit space you are using to define the data and model
        data: the data you are fit on
        weights: 1D numpy array of weights
        total_model: the final total fit model
        '''

        self.obs               = model.space 
        self.data              = self._data_to_zdata(model.space, data, weights) 
        self.lower, self.upper = self.data.data_range.limit1d
        self.total_model       = model
        self.x                 = np.linspace(self.lower, self.upper, 2000)
        self.data_np           = zfit.run(self.data.unstack_x())
        self.data_weight_np    = np.ones_like(self.data_np) if self.data.weights is None else zfit.run(self.data.weights)

        self.binned_data       = None
        self.errors            = []
        self._result           = result
        self._suffix           = suffix
        self._leg              = {}
        self._l_blind          = None
        self.axs               = None

        # zfit.settings.advanced_warnings['extend_wrapped_extended'] = False
        warnings.filterwarnings("ignore")
    #----------------------------------------
    def _data_to_zdata(self, obs, data, weights):
        if isinstance(data, np.ndarray):
            data = zfit.Data.from_numpy (obs=obs, array=data           , weights=weights)
        elif isinstance(data, pd.Series):
            data = zfit.Data.from_pandas(obs=obs, df=pd.DataFrame(data), weights=weights)
        elif isinstance(data, pd.DataFrame):
            data = zfit.Data.from_pandas(obs=obs, df=data              , weights=weights)
        elif isinstance(data, zfit.data.Data):
            data = data
        else:
            log.error(f'Passed data is of usupported type {type(data)}')
            raise

        return data
    #----------------------------------------
    def _get_errors(self, data_hist, errorbars, nbins):
        lines = errorbars[0].errorbar[2]
        segs = lines[0].get_segments()
        values = data_hist.values()
        for i in range(nbins):
            low = values[i] - segs[i][0][1]
            up = segs[i][1][1] - values[i]
            self.errors.append((low, up))
    #----------------------------------------
    def _get_range_data(self, l_range): 
        sdat  = self.data_np
        swgt  = self.data_weight_np
        dmat  = np.array([sdat, swgt]).T

        if self._l_blind is not None:
            log.debug(f'Blinding data with: {self._l_blind}')
            _, min_val, max_val = self._l_blind
            dmat = dmat[(dmat.T[0] < min_val) | (dmat.T[0] > max_val)]

        if l_range is None:
            [dat, wgt] = dmat.T
            return dat, wgt 

        l_dat = []
        l_wgt = []
        for lo, hi in l_range:
            dmat_f = dmat[(dmat.T[0] > lo) & (dmat.T[0] < hi)]

            [dat, wgt] = dmat_f.T

            l_dat.append(dat)
            l_wgt.append(wgt)

        dat_f = np.concatenate(l_dat)
        wgt_f = np.concatenate(l_wgt)

        return dat_f, wgt_f
    #----------------------------------------
    def _plot_data(self, ax, nbins=100, l_range=None):
        dat, wgt  = self._get_range_data(l_range)
        data_hist = hist.Hist.new.Regular(nbins, self.lower, self.upper, name=self.obs.obs[0], underflow=False, overflow=False)
        data_hist = data_hist.Weight()
        data_hist.fill(dat, weight=wgt)

        self.binned_data = data_hist
        errorbars = mplhep.histplot(
            data_hist,
            yerr=True,
            color="black",
            histtype="errorbar",
            label=self._leg.get("Data", "Data"),
            ax=ax,
        )
        self._get_errors(data_hist, errorbars, nbins)
    #----------------------------------------
    def _pull_hist(self, pdf_hist, nbins=None):
        pdf_values  = pdf_hist.values()
        data_values = self.binned_data.values()
        pull_errors = [[], []]
        pulls       = []

        for [low, up], pdf_val, dat_val in zip(self.errors, pdf_values, data_values):
            res = 0   if dat_val == 0 else dat_val - pdf_val 
            res = float(res)
            err = low if res      > 0 else up

            pulls.append(res / err)
            pull_errors[0].append(low / err)
            pull_errors[1].append(up  / err)

        hst            = hist.axis.Regular(nbins, self.lower, self.upper, name="pulls")
        pull_hist      = hist.Hist(hst)
        pull_hist[...] = pulls

        return pull_hist, pull_errors
    #----------------------------------------
    def _plot_pulls(self, ax, nbins=100): 
        obs_name   = self.obs.obs[0]
        binning    = zfit.binned.RegularBinning(bins=nbins, start=self.lower, stop=self.upper, name=obs_name)
        binned_obs = zfit.Space(obs_name, binning=binning)
        binned_pdf = zfit.pdf.BinnedFromUnbinnedPDF(self.total_model, binned_obs)
        pdf_hist   = binned_pdf.to_hist()

        pull_hist, pull_errors = self._pull_hist(pdf_hist, nbins=nbins) 

        mplhep.histplot(
            pull_hist,
            color   = "black",
            histtype= "errorbar",
            yerr    = np.array(pull_errors),
            ax      = ax,
        )
    #----------------------------------------
    def _get_zfit_gof(self):
        if not hasattr(self._result, 'gof'):
            return
    
        chi2, ndof, pval = self._result.gof
    
        rchi2 = chi2/ndof
    
        return f'$\chi^2$/NdoF={chi2:.2f}/{ndof}={rchi2:.2f}\np={pval:.3f}'
    #----------------------------------------
    def _get_text(self, ext_text):
        gof_text = self._get_zfit_gof()

        if   ext_text is     None and gof_text is     None:
            return
        elif ext_text is not None and gof_text is     None:
            return ext_text
        elif ext_text is     None and gof_text is not None:
            return gof_text
        else:
            return f'{ext_text}\n{gof_text}'
    #----------------------------------------
    def _get_pars(self):
        '''
        Will return a dictionary with:
        ```
        par_name -> [value, error]
        ```

        if error is not available, will assign zeros
        '''
        pdf = self.total_model

        if self._result is not None:
            d_par = {}
            for par, d_val in self._result.params.items():
                val = d_val['value']
                try:
                    err = d_val['hesse']['error']
                except:
                    log.warning('Cannot extract Hesse errors, using zeros')
                    err = 0

                name = par if isinstance(par, str) else par.name
                d_par[name] = [val, err]
        else:
            s_par = pdf.get_params()
            d_par = {par.name : [par.value(), 0] for par in s_par}

        return d_par
    #----------------------------------------
    def _add_pars_box(self, add_pars):
        '''
        Will add parameter values to box to the right of fit plot

        Parameters:
        ------------------
        add_pars (list|str): List of names of parameters to be added or string with value 'all' to add all fit parameters.
        '''
        d_par = self._get_pars()

        line = f''
        for name, [val, err] in d_par.items():
            if add_pars != 'all' and name not in add_pars:
                continue

            line += f'{name:<20}{val:>10.3e}{"+/-":>5}{err:>10.3e}\n'
        
        plt.text(0.65, 0.75, line, fontsize=12, transform=plt.gcf().transFigure)
    #----------------------------------------
    def _get_axis(self, add_pars):
        if add_pars is None:
            plt.style.use(mplhep.style.LHCb2)
            fig       = plt.figure()
            gs        = fig.add_gridspec(nrows=2, ncols=1, hspace=0.1, height_ratios=[4, 1])
            axs       = gs.subplots(sharex=True)

            return axs.flat

        fig = plt.figure(figsize=(13, 7))
        ax1 = plt.subplot2grid((4,40),(0, 0), rowspan=3, colspan=25)
        ax2 = plt.subplot2grid((4,40),(3, 0), rowspan=1, colspan=25)
        plt.subplots_adjust(hspace=0.2)

        self._add_pars_box(add_pars)

        return [ax1, ax2]
    #----------------------------------------
    def _plot_model_components(self, nbins, stacked):
        if not hasattr(self.total_model, 'pdfs'):
            return

        y = None
        for model in self.total_model.pdfs: 
            if not model.is_extended:
                continue

            par  = model.get_yield()
            nevt = float(par.value())
            ax   = self.axs[0]

            this_y = model.pdf(self.x) * nevt / nbins * (self.upper - self.lower)

            if stacked:
                y = this_y if y is None else y + this_y
            else:
                y = this_y

            if (self._l_blind is not None) and (model.name == self._l_blind[0]):
                log.debug(f'Blinding: {model.name}')
                y = self._blind_pdf_val(y)

            ax.plot(self.x, y, linestyle='--', label=self._leg.get(model.name, model.name))
    #----------------------------------------
    def _plot_model(self, ax, model, yields, nbins=100, linestyle="-"):
        y = model.pdf(self.x) * yields / nbins * (self.upper - self.lower)

        if self._l_blind is not None:
            log.debug(f'Blinding: {model.name}')
            y = self._blind_pdf_val(y)

        ax.plot(self.x, y, linestyle, label=self._leg.get(model.name, model.name))
    #----------------------------------------
    def _blind_pdf_val(self, arr_y):
        log.debug(f'Blinding PDF values')

        arr_x   = self.x
        arr_bld = (arr_x > self._l_blind[1]) & (arr_x < self._l_blind[2])
        arr_y   = np.where(arr_bld, 0, arr_y)

        return arr_y 
    #----------------------------------------
    def _get_labels(self, xlabel, ylabel, unit, nbins):
        if xlabel == "":
            xlabel = f"{self.obs.obs[0]} [{unit}]"

        if ylabel == "":
            width  = (self.upper-self.lower)/nbins
            ylabel = f'Candidates / ({width:.3f} {unit})'

        return xlabel, ylabel
    #----------------------------------------
    def _get_xcoor(self, plot_range):
        if plot_range is not None:
            try:
                self.lower, self.upper = plot_range
            except TypeError:
                log.error(f'plot_range argument is expected to be a tuple with two numeric values')
                raise TypeError

        return np.linspace(self.lower, self.upper, 2000)
    #----------------------------------------
    @utnr.timeit
    def plot(self, 
            stacked           = False, 
            blind             = None, 
            no_data           = False, 
            ranges            = None, 
            nbins: int        = 100, 
            unit: str         = "$\\rm{MeV}/\\it{c}^{2}$", 
            xlabel: str       = "", 
            ylabel: str       = "", 
            d_leg: dict       = {}, 
            plot_range: tuple = None, 
            ext_text : str    = None, 
            add_pars          = None, 
            ymax              = None,
            skip_pulls        = False):
        '''
        stacked (bool): If true will stack the PDFs
        ranges:     List of tuples with ranges if any was used for the fit, e.g. [(0, 3), (7, 10)]
        nbins:      Bin numbers
        unit:       Unit for x axis, default is MeV/c^2
        no_data (bool): If true data won't be plotted as well as pull
        xlabel:     xlabel
        ylabel:     ylabel
        d_leg:      Customize legend
        plot_range: Set plot_range
        ext_text:   Text that can be added to plot
        add_pars (list|str): List of names of parameters to be added or string with value 'all' to add all fit parameters. If this is used, plot won't use LHCb style.
        skip_pulls(bool) : Will not draw pulls if True, default False
        ymax (float) : Optional, if specified will be used to set the maximum in plot 
        blind (list) : Optional, if specified will remove data in given range, e.g. [var , -1, +1] as well as pulls, the PDF named "var" will also be blinded
        '''
        self._leg     = d_leg
        self.x        = self._get_xcoor(plot_range)
        self.axs      = self._get_axis(add_pars)
        self._l_blind = blind
        total_entries = self.data_weight_np.sum()

        if not stacked:
            self._plot_model(self.axs[0], self.total_model,  total_entries, nbins)

        self._plot_model_components(nbins, stacked)

        if not no_data:
            self._plot_data(self.axs[0], nbins, ranges)

        if not skip_pulls and not no_data:
            self._plot_pulls(self.axs[1], nbins=nbins)

        text           = self._get_text(ext_text)
        xlabel, ylabel = self._get_labels(xlabel, ylabel, unit, nbins)

        self.axs[0].legend(title=text, fontsize=20, title_fontsize=20)
        self.axs[0].set(xlabel=xlabel, ylabel=ylabel)
        self.axs[0].set_xlim([self.lower, self.upper])

        if ymax is not None:
            self.axs[0].set_ylim([0, ymax])

        self.axs[1].set(xlabel=xlabel, ylabel="pulls")
        self.axs[1].set_xlim([self.lower, self.upper])

        for ax in self.axs:
            ax.label_outer()
#----------------------------------------

