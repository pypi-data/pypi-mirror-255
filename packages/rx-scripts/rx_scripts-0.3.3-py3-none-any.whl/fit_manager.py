import ROOT
import utils_noroot as utnr
import math
import utils

#-----------------------------
class fit_manager:
    log = utnr.getLogger(__name__)
    #-----------------------------
    def __init__(self, pdf, tree, d_opt):
        self.__pdf            = pdf
        self.__tree           = tree 
        self.__d_opt          = d_opt

        self.__is_initialized = False 

        self.__outdir         = None
        self.__nbins          = None
        self.__eff_nbins      = None

        self.__nfloat_par     = None
        self.__nfixed_par     = 0 
        self.__d_par_fix      = None

        self.__hist_bin_name  = 'h_poly'

        self.__bins_gof       = None
        self.__group_size     = None
        self.__bins_thr       = None
        self.__l_dat          = None
        self.__minw           = None
        self.__maxw           = None
        self.__max_attempts   = None
        self.__cp             = None
        self.__pl             = None 
        self.__pval_threshold = None
        self.__obs            = None
        self.__weight         = None

        self.__minw           = -10
        self.__minw           = +10
        self.__ncpu           = 1
        self.__gof_dof        = 10
        self.__shuffle_rate   = 0.1
        self.__print_level    = -1 
        self.__ran            = ROOT.TRandom3(0)

        self.__er             = ROOT.RooFit.SumW2Error(False)
        self.__sv             = ROOT.RooFit.Save()
        self.__mn             = ROOT.RooFit.Minimizer('Minuit2', 'migrad')
        self.__of             = ROOT.RooFit.Offset(True)
        self.__op             = ROOT.RooFit.Optimize(True)
        self.__pf             = ROOT.RooFit.PrefitDataFraction(0.1)
        self.__st             = ROOT.RooFit.Strategy(2)

        self._l_good_status   = [0]
        self.__fitted         = False 
        self.__d_fit_par      = {}
    #-----------------------------
    def  __initialize(self):
        if self.__is_initialized:
            return

        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)

        if not self.__pdf:
            self.log.error('PDF introduced is null')
            raise
        #----------------------
        self.__check_opt('outdir')
        self.__check_opt('nbins')
        self.__check_opt('max_attempts')
        self.__check_opt('bin_threshold')
        self.__check_opt('pval_threshold')
        self.__check_opt('weight')
        self.__check_opt('fix_par')

        self.__outdir         = utnr.make_dir_path(self.__d_opt['outdir'])
        self.__nbins          = self.__d_opt['nbins']
        self.__max_attempts   = self.__d_opt['max_attempts']
        self.__bins_thr       = self.__d_opt['bin_threshold']
        self.__pval_threshold = self.__d_opt['pval_threshold']
        self.__weight         = self.__d_opt['weight']
        self.__d_par_fix      = self.__d_opt['fix_par']
        #----------------------
        if 'print_level' in self.__d_opt:
            self.__print_level  = self.__d_opt['print_level']

        if 'ncpu' in self.__d_opt:
            self.__ncpu         = self.__d_opt['ncpu']

        if 'gof_dof' in self.__d_opt:
            self.__gof_dof      = self.__d_opt['gof_dof']

        if 'shuffle_rate' in self.__d_opt:
            self.__shuffle_rate = self.__d_opt['shuffle_rate']

        if 'good_status'  in self.__d_opt:
            self._l_good_status = self.__d_opt['good_status']
        #----------------------
        self.__cp = ROOT.RooFit.NumCPU(self.__ncpu)
        self.__pl = ROOT.RooFit.PrintLevel(self.__print_level)
        #----------------------
        self.__obs   = self.__get_observable()

        s_par = self.__pdf.getParameters(ROOT.RooArgSet(self.__obs))

        if self.__d_par_fix is not None:
            self.__check_fix_par(s_par)
            self.__nfixed_par = len(self.__d_par_fix)

        self.__nfloat_par   = s_par.getSize() - self.__nfixed_par
        bins_gof, eff_nbins = self.__get_binning()
        l_dat               = self.__get_data(self.__obs, eff_nbins)
        self.__bins_gof     = bins_gof 
        self.__eff_nbins    = eff_nbins 
        self.__l_dat        = l_dat 
        self.__group_size   = int(eff_nbins / bins_gof)

        self.log.info('{0:<20}{1:<20}'.format('GoF binning', self.__bins_gof))
        self.log.info('{0:<20}{1:<20}'.format('GoF DoF'    , self.__gof_dof))
        self.log.info('{0:<20}{1:<20}'.format('Binning'    , self.__nbins))
        self.log.info('{0:<20}{1:<20}'.format('Float pars' , self.__nfloat_par))
        self.log.info('{0:<20}{1:<20}'.format('Fixed pars' , self.__nfixed_par))
        self.log.info('{0:<20}{1:<20}'.format('eff Binning', self.__eff_nbins))
        self.log.info('{0:<20}{1:<20}'.format('Group size' , self.__group_size))

        self.__is_initialized = True
    #-----------------------------
    def __get_nslices(self):
        if 'slicing' not in self.__d_opt:
            return 1

        hist_path, _, _ = self.__d_opt['slicing']

        hist, ifile = utils.get_from_file(self.__hist_bin_name, hist_path, kind='TH2Poly')
        l_bin       = hist.GetBins()
        nbins       = l_bin.GetEntries()

        return nbins
    #-----------------------------
    def __check_fix_par(self, s_par):
        nslice = self.__get_nslices()

        for par, l_val in self.__d_par_fix.items():
            obj = s_par.find(par)
            if not obj:
                self.log.error(f'Cannot fix "{par}", not found in PDF')
                s_par.Print()
                print(self.__d_par_fix)
                raise

            nfix = len(l_val)
            if nfix != nslice:
                self.log.error(f'Number dissagreement nfix/nslice: {nfix}/{nslice}')
                raise
    #-----------------------------
    def __get_observable(self):
        l_branch = self.__tree.GetListOfBranches()
        l_var    = self.__pdf.getVariables()

        s_var_name=set()
        for var in l_var:
            var_name = var.GetName()
            s_var_name.add(var_name)

        s_branch_name=set()
        for branch in l_branch:
            branch_name = branch.GetName()
            s_branch_name.add(branch_name)

        s_int = s_var_name.intersection(s_branch_name)
        if len(s_int) != 1:
            self.log.error('Cannot find one and only one observable')
            print(s_branch_name)
            print(s_var_name)
            print(s_int)
            self.__pdf.Print()
            raise

        obsname = list(s_int)[0]
        tmp = l_var.find(obsname)
        obs = ROOT.RooRealVar(tmp)

        return obs
    #-----------------------------
    def __get_binning(self):
        bins_gof = self.__gof_dof + 1 + self.__nfloat_par 
        divisor  = math.ceil(self.__nbins/float(bins_gof))

        eff_nbins = divisor * bins_gof
        self.log.visible('{0:<20}{1:20}{2:<20}'.format(self.__nbins, '--->', eff_nbins))

        return (bins_gof, eff_nbins)
    #-----------------------------
    def __get_data(self, obs, eff_nbins):
        treename = self.__tree.GetName()
        if 'slicing' not in self.__d_opt:
            data   = utils.get_dataset('data_{}_00'.format(treename), self.__tree, obs, self.__weight)
            data   = self.__reformat(data, obs, eff_nbins)
            return [data]

        l_cut =self.__get_cut_list()
        l_data=[]
        for i_cut, cut in enumerate(l_cut):
            bin_tree = self.__tree.CopyTree(cut)
            if bin_tree.GetEntries() == 0:
                self.log.warning(f'Found empty dataset for cut: {cut}, skipping it')
                l_data.append(None)
                continue

            ar_tre   = ROOT.RooFit.Import(bin_tree)

            dataname = f'data_{treename}_{i_cut:02}'
            data = utils.get_dataset(dataname, bin_tree, obs, self.__weight) 
            data = self.__reformat(data, obs, eff_nbins)
            l_data.append(data)

        return l_data
    #-----------------------------
    def __get_cut_list(self):
        histpath, xvar, yvar = self.__d_opt['slicing']

        utnr.check_file(histpath)
        ifile=ROOT.TFile(histpath)
        try:
            hist  = ifile.h_poly
            l_bin = hist.GetBins()
        except:
            self.log.error('Cannot find TH2Poly with binning in file:')
            ifile.ls()
            raise

        l_cut = []
        self.log.info('Slicing with cuts:')
        for bin_ in l_bin:
            min_x = bin_.GetXMin()
            max_x = bin_.GetXMax()
            min_y = bin_.GetYMin()
            max_y = bin_.GetYMax()

            cut_x = '({} > {}) && ({} < {})'.format(xvar, min_x, xvar, max_x)
            cut_y = '({} > {}) && ({} < {})'.format(yvar, min_y, yvar, max_y)
            cut   = '({}) && ({})'.format( cut_x,  cut_y)

            pcut_x= '({} > {:.3e}) && ({} < {:.3e})'.format(xvar, min_x, xvar, max_x)
            pcut_y= '({} > {:.3e}) && ({} < {:.3e})'.format(yvar, min_y, yvar, max_y)
            pcut  = '({}) && ({})'.format(pcut_x, pcut_y)
            self.log.info(pcut)

            l_cut.append(cut)

        ifile.Close()

        return l_cut
    #-----------------------------
    def __reformat(self, data, obs, eff_nbins):
        if not data.InheritsFrom('RooDataSet'):
            class_name = data.Class().GetName()
            self.log.error('Dataset does not inherit from RooDataSet but ' + class_name)
            raise

        if data.numEntries() < self.__bins_thr:
            self.log.info('Using unbinned dataset for fit')
            return data

        self.log.info('Using binned dataset with {} bins'.format(eff_nbins))
        obs.setBins(eff_nbins)

        dataname  = data.GetName()
        datatitle = data.GetTitle()
        data.SetName('unbinned_' + dataname)

        data_h = ROOT.RooDataHist(dataname, datatitle, ROOT.RooArgSet(obs), data)

        return data_h
    #-----------------------------
    def __check_opt(self, opt):
        if opt not in self.__d_opt:
            self.log.error('Missing "{}" setting'.format(opt))
            raise
    #-----------------------------
    #-----------------------------
    def __reshuffle_pars(self, data):
        s_par = self.__pdf.getParameters(ROOT.RooArgSet(self.__obs))
        for par in s_par:
            parname = par.GetName()
            if par.isConstant():
                continue

            if parname.startswith('n'):
                continue

            min_val = par.getMin()
            old_val = par.getVal()
            max_val = par.getMax()
            new_val = self.__ran.Gaus(old_val, (max_val - min_val) * self.__shuffle_rate)

            par.setVal(new_val)
            self.log.info('{0:<40}{1:<20.3e}{2:}{3:>20.3e}'.format(parname, old_val, '--->', new_val))
    #-----------------------------
    def __get_fit_pvalue(self, data, attempt):
        return self.__get_chi2_fit_pvalue(data, attempt) 
    #-----------------------------
    def __get_chi2_fit_pvalue(self, data, attempt):
        self.__obs.setBins(self.__eff_nbins)

        if self.__pdf.InheritsFrom('RooProdPdf'):
            self.log.info('Found RooProdPdf, assuming constrained case, using first component')
            l_pdf = self.__pdf.pdfList()
            pdf   = l_pdf.at(0)
        else:
            pdf   = self.__pdf

        dataname = data.GetName()
        histname = 'h_data_pval_{}_{}'.format(dataname, attempt)
        h_data   = data.createHistogram(histname, self.__obs)
        h_data.Rebin(self.__group_size)

        data_h = ROOT.RooDataHist("data_h_pval", "", ROOT.RooArgList(self.__obs), h_data)

        plot = self.__obs.frame()
        data_h.plotOn(plot, ROOT.RooFit.Name('data'))
        pdf.plotOn(plot, ROOT.RooFit.Name('pdf'))
        pull = plot.pullHist('data', 'pdf', True)

        npoints = pull.GetN()
        chi2    = 0
        for i_point in range(npoints):
            pull_val = pull.GetPointY(i_point)
            chi2    += pull_val ** 2

        pvalue = ROOT.ROOT.Math.chisquared_cdf_c(chi2, self.__gof_dof)

        return pvalue
    #-----------------------------
    def __fix_parameters(self, i_bin):
        self.log.info('-----------------------------------------')
        self.log.info(f'Fixing values for slice: {i_bin}')
        self.log.info(f'{"Parameter":<30}{"Value":<30}')
        self.log.info('-----------------------------------------')

        s_par = self.__pdf.getParameters(ROOT.RooArgSet(self.__obs))
        for par_name, l_par_val in self.__d_par_fix.items():
            par = s_par.find(par_name)
            utils.check_null(par, par_name)
            val = l_par_val[i_bin]

            par.setVal(val)
            par.setConstant()
            self.log.info(f'{par_name:<30}{val:<10.3e}')
        self.log.info('-----------------------------------------')
    #-----------------------------
    def __do_fit(self, data, snap_pref, i_bin):
        d_pv_result = {}
        d_pv_snapsh = {}

        if self.__d_par_fix is not None:
            self.__fix_parameters(i_bin)
        else:
            self.log.visible('Not fixing any parameters')

        attempt = 1
        index   = 1
        s_par = self.__pdf.getParameters(ROOT.RooArgSet(self.__obs))

        while attempt < self.__max_attempts:
            result = self.__pdf.fitTo(data, self.__er, self.__sv, self.__mn, self.__cp, self.__of, self.__op, self.__st, self.__pl)
            pvalue = self.__get_fit_pvalue(data, index)

            good_fit = pvalue > self.__pval_threshold
            status   = result.status()
            if   status in self._l_good_status:
                snapname   = '{}_{:02d}'.format(snap_pref, attempt)
                str_pvalue = '{:.4f}'.format(pvalue)
                d_pv_result[str_pvalue] = result
                d_pv_snapsh[str_pvalue] = snapname 

                self.__wks.saveSnapshot(snapname, s_par, True)

            if   status in self._l_good_status and good_fit == True:
                self.log.info(f'Fit {i_bin} converged at attempt {attempt} with p-value: {pvalue:.4f}')
                break
            elif status in self._l_good_status and good_fit == False:
                self.log.info(f'Fit {i_bin} ended at attempt {attempt} with p-value: {pvalue:.4e}')
                attempt+=1
            else:
                self.log.info(f'Fit {index} failed with status: {status}')

            self.__reshuffle_pars(data)
            index+=1

        nfits = len(self.__l_dat)
        self.log.visible(f'{i_bin+1:03}/{nfits:03}; p-value: {pvalue:.4f}; attempts: {attempt:03}; status:{result.status():03}')

        l_pv_result=list(d_pv_result.items())
        l_pv_result.sort(reverse=True)

        str_max_pvalue, result = l_pv_result[0]
        snapname = d_pv_snapsh[str_max_pvalue]

        self.__wks.loadSnapshot(snapname)
        self.__wks.saveSnapshot(snap_pref, s_par, False)

        result.SetTitle(str_max_pvalue)

        d_stat = {'nattempt' : attempt, 'status' : result.status()}

        return (result, d_stat)
    #-----------------------------
    def __add_fit_pars(self, result):
        if   result is None and len(self.__d_fit_par) == 0:
            self.log.error(f'First fit was found to be empty')
            raise
        elif result is None:
            self.log.info('Padding fit results, due to no data')
            for par_name in self.__d_fit_par:
                self.__d_fit_par[par_name].append([0, 0])

            return

        s_fit_par = result.floatParsFinal()
        for fit_par in s_fit_par:
            par_name = fit_par.GetName()
            value    = fit_par.getVal()
            error    = fit_par.getError()

            if par_name not in self.__d_fit_par:
                self.__d_fit_par[par_name]     = [[value, error]]
            else:
                self.__d_fit_par[par_name].append([value, error])
    #-----------------------------
    def fit(self):
        self.__initialize()

        resultspath = f'{self.__outdir}/fit_results.root'
        ofile=ROOT.TFile(resultspath, 'recreate')

        self.__wks=ROOT.RooWorkspace('wks', '')

        s_par   = self.__pdf.getParameters(ROOT.RooArgSet(self.__obs))
        pdfname = self.__pdf.GetName()

        self.__wks.Import(self.__pdf)
        self.__wks.saveSnapshot('prefit', s_par, True)

        self.__pdf = self.__wks.pdf(pdfname)
        self.__pdf.SetName('model')

        l_stat = []
        self.log.visible('Fitting')
        for i_data, data in enumerate(self.__l_dat):
            snap_pref = f'{self.__tree.GetName()}_{i_data:02}'
            if data is None:
                result = None
                d_stat = {}
            else:
                result, d_stat = self.__do_fit(data, snap_pref, i_data)
                ofile.cd()
                result.SetName(f'result_{snap_pref}')
                result.Write()
                self.__wks.Import(data)

            l_stat.append(d_stat)
            self.__add_fit_pars(result)

        ofile.cd()
        self.__wks.Write()
        ofile.Close()

        self.__fitted = True

        return l_stat
    #-----------------------------
    def get_pars(self):
        if not self.__fitted:
            self.error('Fit has not been run yet')
            raise

        if self.__get_nslices() == 1:
            d_fit_par = {par_name : [par_val, par_err] for par_name, [[par_val, par_err]] in self.__d_fit_par.items()}
        else:
            d_fit_par = self.__d_fit_par

        return d_fit_par
#-----------------------------

