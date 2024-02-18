import utils
import numpy

import scipy.stats       as stats
import matplotlib.pyplot as plt
import pandas            as pnd
import utils_noroot      as utnr

log=utnr.getLogger(__name__)
#-------------------------------------------
class corr():
    log=utnr.getLogger('corr')
    #----------------------------------
    def __init__(self, l_exp_main, l_exp_refe, df):
        self._l_exp_main = l_exp_main
        self._l_exp_refe = l_exp_refe
        self._df         = df
        self._nevs       = df.Count().GetValue()

        self._l_var_main = [] 
        self._l_var_refe = [] 

        self._d_exp_lab  = {} 
        self._d_lab_var  = {} 
        self._d_var_exp  = {} 
        self._d_exp_var  = {} 

        self._d_df       = None 
        self._d_sp       = None 

        self._out_dir    = None
        self._initialized= False
    #----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._l_var_main = self._add_variables(self._l_exp_main)
        self._l_var_refe = self._add_variables(self._l_exp_refe)

        self._get_labels(self._l_exp_main)
        self._get_labels(self._l_exp_refe)

        self._calculate_correlations()

        self._initialized=True
    #----------------------------------
    def _get_labels(self, l_exp):
        for exp in l_exp:
            lab = exp.replace('TMath::', '')
            lab = lab.replace('_OWNPV' , '')
            lab = lab.replace('B_'     , '')
            self._d_exp_lab[exp] = lab
            self._d_lab_var[lab] = self._d_exp_var[exp]
    #----------------------------------
    def _add_variables(self, l_exp):
        l_col = self._df.GetColumnNames()

        l_var = []
        for exp in l_exp:
            if exp in l_col:
                self._d_var_exp[exp] = exp
                self._d_exp_var[exp] = exp 
                l_var.append(exp)
                continue

            var = utnr.get_var_name(exp)
            self.log.info(f'{exp:<30}{"->":10}{var:<30}')
            self._df = self._df.Define(var, exp)

            self._d_var_exp[var] = exp
            self._d_exp_var[exp] = var 
            l_var.append(var)

        return l_var
    #----------------------------------
    def _get_scatter(self, arr_main, arr_refe):
        arr_bin               = utnr.get_binning(10, arr_refe)
        try:
            arr_mean, arr_edge, _ = stats.binned_statistic(arr_refe, arr_main, statistic='median', bins=arr_bin)
        except:
            self.log.error('Cannot calculate scatter mean for data in arrays:')
            self.log.error(arr_refe)
            self.log.error(arr_main)
            self.log.error(arr_bin)
            raise

        arr_keep_1            = numpy.logical_and(arr_main > arr_edge[0], arr_main < arr_edge[-1])
        arr_keep_2            = numpy.logical_and(arr_refe > arr_edge[0], arr_refe < arr_edge[-1])
        arr_keep              = numpy.logical_or(arr_keep_1, arr_keep_2)

        arr_main              = arr_main[arr_keep] 
        arr_refe              = arr_refe[arr_keep]

        return arr_mean, arr_edge, arr_main[:2000], arr_refe[:2000]
    #----------------------------------
    def _plot_scatter(self, rho, pvl, arr_mean, arr_edge, arr_refe, arr_main, lab_refe, lab_main):
        plot_dir = utnr.make_dir_path(f'{self._out_dir}/scatter')

        var_main = utnr.get_var_name(lab_main)
        var_refe = utnr.get_var_name(lab_refe)
        plot_path= f'{plot_dir}/{var_main}_{var_refe}.png'
        self.log.visible(f'Saving to: {plot_path}')

        plt.hlines(arr_mean, arr_edge[:-1], arr_edge[1:], colors='r', lw=3, label='Median')
        plt.scatter(arr_refe, arr_main, s=1, alpha=0.5, label='Data')
        plt.title(f'$\\rho={rho:.3f}$; p-value={pvl:.3f}')
        plt.xlabel(lab_refe)
        plt.ylabel(lab_main)
        plt.legend()
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close('all')
    #----------------------------------
    def _get_corr(self, var_main, var_refe):
        [arr_x, arr_y] = utils.getMatrix(self._df, [var_main, var_refe]).T

        tau, pvl = stats.kendalltau(arr_x, arr_y)

        arr_mu, arr_ed, arr_main, arr_refe = self._get_scatter(arr_x, arr_y)

        return arr_mu, arr_ed, tau, pvl, arr_main, arr_refe 
    #----------------------------------
    def _calculate_correlations(self):
        self.log.info(f'Calculating correlations')
        d_df = {}
        d_sp = {}
        for var_refe in self._l_var_refe:
            d_corr = {'Expression' : [], 'Correlation' : [], 'P-Value' : []} 
            d_bins = {}
            for var_main in self._l_var_main:
                self.log.debug(f'{var_main:<20}{var_refe:<20}')
                arr_mu, arr_ed, corr, pvl, arr_main, arr_refe = self._get_corr(var_main, var_refe)

                exp_main = self._d_var_exp[var_main]

                lab = self._d_exp_lab[exp_main]
                d_corr['Expression' ].append(lab)
                d_corr['Correlation'].append(corr)
                d_corr['P-Value'    ].append(pvl)

                d_bins[exp_main] = (arr_mu, arr_ed, corr, pvl, arr_main, arr_refe)

            exp_refe = self._d_var_exp[var_refe]
            lab_refe = self._d_exp_lab[exp_refe]
            d_df[lab_refe] = pnd.DataFrame(d_corr)
            d_sp[lab_refe] = d_bins

        self._d_df = d_df
        self._d_sp = d_sp
    #----------------------------------
    def _quant_to_matrix(self, quant, d_df):
        l_arr_qnt = []
        for lab_ref, df in d_df.items():
            arr_qnt = df[quant].to_numpy()
            l_arr_qnt.append(arr_qnt)

            l_xvar  = df['Expression'].to_numpy()

        mat_qnt = numpy.array(l_arr_qnt)
        l_yvar  = list(d_df.keys())

        return mat_qnt, l_xvar, l_yvar
    #----------------------------------
    def _save_matrix(self, kind):
        if kind == 'Correlation':
            name = 'rho'
            zran = (-1, +1)
        elif kind == 'P-Value':
            name = 'pvl'
            zran = ( 0, +1)
        else:
            log.error(f'Invalid kind of matrix: {kind}')
            raise

        mat_val, l_xvar, l_yvar = self._quant_to_matrix(kind, self._d_df)
        plot_path = f'{self._out_dir}/{name}_mat.png'
        self.log.visible(f'Saving to: {plot_path}')
        utnr.plot_matrix(plot_path, l_xvar, l_yvar, mat_val, title=kind, upper=None, zrange=zran, form='{:.3f}')
    #----------------------------------
    def save(self, out_dir, title=''):
        self._initialize()
        self._out_dir = utnr.make_dir_path(out_dir)

        self._save_matrix('P-Value')
        self._save_matrix('Correlation')

        out_path = f'{out_dir}/rho.png'
        fig = plt.figure(figsize=(10, 6))
        ax  = fig.add_subplot(1, 1, 1)

        for lab_ref, df_ref in self._d_df.items():
            ax=df_ref.plot(x='Expression', y='Correlation', label=f'$\\rho ({lab_ref})$', ax=ax)
            ax=df_ref.plot(x='Expression', y='P-Value'    , label=f'p-value ({lab_ref})', ax=ax)

        l_loc, l_lab = utnr.get_axis(df_ref, 'Expression')

        plt.xticks(l_loc, l_lab, rotation=90)
        plt.title(f'#Events={self._nevs}; {title}')
        plt.ylabel('')
        plt.xlabel('')
        plt.tight_layout()
        plt.grid()
        plt.ylim([-1, +1])
        plt.legend()
        plt.savefig(out_path)
        plt.close('all')

        for lab_ref, df_ref in self._d_df.items():
            var_ref = self._d_lab_var[lab_ref]
            out_path = f'{out_dir}/rho_{var_ref}.tex'
            df_ref.to_latex(out_path, index=False, formatters={'P-Value' : lambda val: f'{val:.3f}' , 'Correlation' : lambda val: f'{val:.3f}'})

        for exp_ref, d_bins in self._d_sp.items():
            for exp_main, (arr_mu, arr_ed, corr, pval, arr_main, arr_refe) in d_bins.items():
                self._plot_scatter(corr, pval, arr_mu, arr_ed, arr_refe, arr_main, exp_ref, exp_main)
    #----------------------------------
    def get_bin_scatter(self, ref=None):
        self._initialize()

        utnr.check_none(ref)

        return self._d_sp[ref]
#-------------------------------------------
def overlay_scatters(d_sct_1, d_sct_2, plot_dir, ref_name='', lab1='', lab2='', title=''):
    l_key_1 = d_sct_1.keys()
    l_key_2 = d_sct_2.keys()

    if l_key_1 != l_key_2:
        log.error(f'Keys for binned scatter dictionaries are different')
        raise

    for yvar in l_key_1:
        arr_mu_1, arr_ed_1, corr_1, pvl_1, arr_y_1, arr_x_1 = d_sct_1[yvar]
        arr_mu_2, arr_ed_2, corr_2, pvl_2, arr_y_2, arr_x_2 = d_sct_2[yvar]

        plt.hlines(arr_mu_1, arr_ed_1[:-1], arr_ed_1[1:], colors = 'r', lw=2, label=f'$p_{{no-corr}}$={corr_1:<.3f}; {lab1}')
        plt.hlines(arr_mu_2, arr_ed_2[:-1], arr_ed_2[1:], colors = 'b', lw=2, label=f'$p_{{no-corr}}$={corr_2:<.3f}; {lab2}')

        plt.scatter(arr_x_1, arr_y_1, color='r', s=2, alpha=0.1)
        plt.scatter(arr_x_2, arr_y_2, color='b', s=2, alpha=0.1)

        yname     = utnr.get_var_name(yvar)
        plot_path = f'{plot_dir}/{yname}.png'
        log.visible(f'Saving to: {plot_path}')

        plt.xlabel(ref_name)
        plt.ylabel(yvar)
        plt.title(title)
        plt.legend()
        plt.savefig(plot_path)
        plt.close('all')
#-------------------------------------------

