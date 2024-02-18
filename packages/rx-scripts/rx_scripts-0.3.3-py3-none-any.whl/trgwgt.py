import ROOT

import numpy
import os
import utils
import style
import logging

import utils_noroot as utnr

#----------------------------------
class trg_map:
    log=utnr.getLogger('trg_map') 
    #----------------------------------
    def __init__(self, tag, year, binning_dir, version=None):
        self._tag          = tag
        self._year         = year 
        self._binning_dir  = binning_dir 
        self._version      = version 
        self._l_year       = [2011, 2012, 2015, 2016, 2017, 2018]
        self._epsilon      = 1e-10

        self._skip_direct  = False
        self._d_hist_file  = {}
        self._initialized  = False

        [ self._fill_hist_dict(year) for year in self._l_year ]

        self._d_tupl={}
        self._d_hpas={}
        self._d_hfal={}
        self._d_heff={}
        self._d_hwps={}
        self._d_hwfl={}
    #----------------------------------
    def _fill_hist_dict(self, year):
        self._d_hist_file[('HLT_ETOS'     , year)]=f'HLTElectron_NA_{year}.root'
        self._d_hist_file[('HLT_HTOS'     , year)]=f'HLTHadron_NA_{year}.root'
        self._d_hist_file[('HLT_GTIS'     , year)]=f'HLTGTIS_NA_{year}.root'
        self._d_hist_file[('HLT_MTOS'     , year)]=f'HLTMuon_NA_{year}.root'

        self._d_hist_file[('L0ElectronTIS', year)]=f'L0Electron_NA_{year}.root'
        self._d_hist_file[('L0ElectronHAD', year)]=f'L0Electron_NA_{year}.root'
        self._d_hist_file[('L0ElectronFAC', year)]=f'L0ElectronFAC_NA_{year}.root'

        self._d_hist_file[('L0MuonTIS'    , year)]=f'L0Muon_NA_{year}.root'
        self._d_hist_file[('L0MuonHAD'    , year)]=f'L0Muon_NA_{year}.root'
        self._d_hist_file[('L0MuonMU1'    , year)]=f'L0Muon_NA_{year}.root'
        self._d_hist_file[('L0MuonALL1'   , year)]=f'L0Muon_NA_{year}.root'

        self._d_hist_file[('L0HadronMuTIS', year)]=f'L0Hadron_NA_{year}.root'
        self._d_hist_file[('L0HadronMuMU' , year)]=f'L0Hadron_NA_{year}.root'

        self._d_hist_file[('L0HadronElTIS', year)]=f'L0Hadron_NA_{year}.root'
        self._d_hist_file[('L0HadronElEL' , year)]=f'L0Hadron_NA_{year}.root'

        self._d_hist_file[('L0TIS_MM'     , year)]=f'L0GMH_NA_{year}.root'
        self._d_hist_file[('L0TIS_EM'     , year)]=f'L0GMH_NA_{year}.root'
        self._d_hist_file[('L0TIS_MH'     , year)]=f'L0GEM_NA_{year}.root'
        self._d_hist_file[('L0TIS_BN'     , year)]=f'L0GBN_NA_{year}.root'
    #----------------------------------
    def __str__(self):
        self.__initialize()
        for key, tup in self._d_tupl.items():
            nval = len(arr_val)
            nwgt = len(arr_wgt)
            nevt = len(arr_evt)
            swgt = numpy.sum(arr_wgt)
    
            self.log.info('_____________________')
            self.log.info(header)
            self.log.info('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
            self.log.info('{0:20}{1:20}'.format('Values'         , nval))
            self.log.info('{0:20}{1:20}'.format('Weights'        , nwgt))
            self.log.info('{0:20}{1:20}'.format('Events'         , nevt))
            self.log.info('{0:20}{1:20.3f}'.format('Sum of weights' , swgt))
            self.log.info('‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾')
    #----------------------------------
    def __initialize(self):
        if self._initialized:
            return

        utnr.check_none(self._binning_dir) 
        utnr.check_none(self._version) 

        utnr.check_dir(self._binning_dir) 
        
        try:
            self._year=int(self._year)
        except:
            self.log.error(f'Cannot cast year:{self._year} as integer')
            raise

        key=(self._tag, self._year)
        filename=self._d_hist_file[key]
        self.__cacheHistograms(filename)
        self._fill_map(replica=0)
        self._initialized = True
    #----------------------------------
    def __cacheHistograms(self, filename):
        histpath=f'{self._binning_dir}/{filename}'

        if not os.path.isfile(histpath):
            self.log.error(f'Cannot find {histpath}')
            raise

        ifile=ROOT.TFile(histpath)
        try:
            hist = ifile.h_poly
            hist = hist.Clone("h_binning")
            hist.SetDirectory(0)

            self.log.info('Cached histogram from ' + filename)
            ifile.Close()

            self.hist = hist
        except:
            self.log.error('Cannot find or retrieve h_poly')
            ifile.ls()
            ifile.Close()
            raise

        self.hist.Reset('ICES')
        if self.log.getEffectiveLevel() <= logging.DEBUG:
            utils.print_poly2D(self.hist)
    #------------------------------
    def __calc_eff_map(self, name, h_pas, h_fal, replica):
        l_bin_pas = h_pas.GetBins()
        l_bin_fal = h_fal.GetBins()

        if len(l_bin_pas) != len(l_bin_fal):
            self.log.error("Cannot divide histograms with different numbers of bins")
            self.log.error("Pass/Fail:{}/{}".format(len(l_bin_pas), len(l_bin_fal)))
            raise

        h_eff=h_pas.Clone(name)
        l_bin_eff=h_eff.GetBins()

        self.log.debug('-----------------------------------------')
        self.log.debug('Filling ' + name)
        self.log.debug('-----------------------------------------')
        self.log.debug('{0:<20}{1:<20}{2:<20}{3:<20}{4:<20}{5:<20}{6:<20}'.format('Bin', 'Passed', 'Error', 'Failed', 'Error', 'Efficiency', 'Error'))

        nbins  = h_pas.GetNumberOfBins()
        nempty = 0
        for index in range(1, nbins + 1):
            pas  =h_pas.GetBinContent(index)
            pas_e=h_pas.GetBinError(index)

            fal  =h_fal.GetBinContent(index)
            fal_e=h_fal.GetBinError(index)

            if pas < 0:
                self.log.warning('For replica {}, passed yield is {:.3e} at bin {}'.format(replica, pas, index))
                pas = 0

            if fal < 0:
                self.log.warning('For replica {}, failed yield is {} at bin {}'.format(replica, fal, index))
                fal = 0

            if pas == 0 and fal == 0:
                self.log.debug('For replica {}, both passed and failed yields are zero at bin {}'.format(replica, index) )
                eff=-1
                err= 0
                nempty += 1
            else:
                eff, err=utils.effTandP(pas, pas_e, fal, fal_e)

            self.log.debug('{0:<20}{1:<20.3e}{2:<20.3e}{3:<20.3e}{4:<20.3e}{5:<20.3e}{6:<20.3e}'.format(index, pas, pas_e, fal, fal_e, eff, err))

            h_eff.SetBinContent(index, eff)
            h_eff.SetBinError(index, err)
        self.log.debug('-----------------------------------------')
        #----------------------
        rate = nempty / float(nbins)

        if nempty > 0:
            self.log.warning('Non zero rate of invalid efficiencies = {:.3f} = {}/{}'.format(rate, nempty, nbins))

        empty_total = '{}/{} = {:.3f}'.format(nempty, nbins, rate)
        self.log.debug('{0:<20}{1:<20}'.format('Efficiency', empty_total))

        h_eff.SetMaximum(1.)
        h_eff.SetMinimum(0.)
        #----------------------

        return h_eff
    #----------------------------------
    def __do_fill(self, replica, key):
        try:
            arr_val, arr_wgt, arr_evt = self._d_tupl[key]
        except:
            self.log.error(f'Cannot find {key} in:')
            print(self._d_tupl.keys())
            raise

        try:
            arr_wgt=utils.weightData(arr_wgt, arr_evt, replica)
        except:
            self.log.error('Cannot get weighted array with:')
            str_arr_wgt = str(arr_wgt)
            str_arr_evt = str(arr_evt)

            self.log.info('{0:<20}{1:<50}'.format('Replica',     replica))
            self.log.info('{0:<20}{1:<50}'.format('Weights', str_arr_wgt))
            self.log.info('{0:<20}{1:<50}'.format('Events' , str_arr_evt))

            raise

        histname=f'h_{key}_{self._tag}_{replica}'
        if 'wgt' in key:
            arr_dat = numpy.array([arr_val, arr_wgt]).T
            hist    = utils.arr_to_hist(histname, '', 40, 0, 0, arr_dat)
            return hist

        h_yield = self.hist.Clone(histname)

        nval = len(arr_val)
        nwgt = len(arr_wgt)

        for val, wgt in zip(arr_val, arr_wgt):
            xval=val[0]
            yval=val[1] + self._epsilon 

            h_yield.Fill(xval, yval, wgt)

        l_bin  = h_yield.GetBins()
        nbins  = 0
        nempty = 0
        for _bin in l_bin:
            bc = _bin.GetContent()
            nbins += 1
            if bc == 0:
                nempty += 1

        rate = nempty / float(nbins)
        empty_total = f'{nempty}/{nbins} = {rate:.3f}'
        self.log.debug(f'{"key":<20}{"empty_total":<20}')

        self.log.debug(f'Filled {histname}')
        if self.log.getEffectiveLevel() <= logging.DEBUG:
            utils.print_poly2D(h_yield)

        return h_yield
    #----------------------------------
    def __overlay(self, h_dat, h_sim, h_dir, filedir, suffix, d_set={}):
        l_h_row_dat = utils.poly2D_to_1D(h_dat, suffix)
        l_h_row_sim = utils.poly2D_to_1D(h_sim, suffix)
        l_h_row_dir = utils.poly2D_to_1D(h_dir, suffix)

        row=1 if ('L0Muon' in self._tag or 'L0TIS' in self._tag) else 0
        for h_row_dat, h_row_sim, h_row_dir in zip(l_h_row_dat, l_h_row_sim, l_h_row_dir):
            h_row_dat.SetTitle('Data')
            h_row_sim.SetTitle('Simulation')
            h_row_dir.SetTitle('True')

            leg_tag = self._tag.replace('L0Electron', '').replace('L0Muon', '').replace('L0Hadron', '').replace('L0TIS_', '')

            header=f'{leg_tag}, {self._year}, {self._version}, sPlot'

            d_opt             = {}
            d_opt['leg_head'] = header 
            d_opt['xname']    = self.__getXName()
            d_opt['xgrid']    = True
            d_opt['ygrid']    = True
            d_opt['width']    = 1000
            d_opt['height']   =  800

            name = f'{filedir}/{suffix}_{row:02}.png'
            self.log.debug('Plotting row {row}')

            if   'eff_' in suffix:
                d_opt['yname']      = '#varepsilon(L_{0})'
                d_opt['ratio']      = True
                d_opt['legend']   = -1
                if   self._tag in ['L0TIS_EM', 'L0TIS_MM']:
                    d_opt['yrange'] = (0, 0.4)
                elif 'L0TIS_MH' == self._tag:
                    d_opt['yrange'] = (0, 0.6)
                else:
                    d_opt['yrange'] = (0, 1.0)

                if 'L0Muon' in self._tag:
                    d_opt['ymax_r'] = 1.2
                    d_opt['ymin_r'] = 0.8
                else:
                    d_opt['ymax_r'] = 1.5
                    d_opt['ymin_r'] = 0.5
                #----------------
                #Override options
                #----------------
                if 'ovr_yrange' in d_set:
                    d_opt['yrange'] = d_set['ovr_yrange']

                if 'ovr_ymaxr' in d_set:
                    d_opt['ymaxr'] = d_set['ovr_ymaxr']

                if 'ovr_yminr' in d_set:
                    d_opt['yminr'] = d_set['ovr_yminr']
            elif 'pas_' in suffix or 'fal_' in suffix:
                d_opt['yname']      = 'Yield'
                d_opt['legend']     = +1
            else:
                self.log.error('Invalid suffix: ' + suffix)
                raise
            #----------------
            utils.plot_histograms([h_row_sim, h_row_dat, h_row_dir], name, d_opt)
            row+=1
        self.log.debug('-----------------------------------------')

        return (l_h_row_dat, l_h_row_sim, l_h_row_dir)
    #----------------------------------
    def __getXName(self):
        if   self._tag.startswith('L0Electron'):
            return 'E_{T}(e_{probe})[MeV]'
        elif self._tag.startswith('L0Muon'):
            return 'p_{T}(#mu_{probe})[MeV]'
        elif self._tag.startswith('L0Hadron'):
            return 'E_{T}(K_{probe})[MeV]'
        elif self._tag.startswith('L0TIS_EM'):
            return 'p_{T}(B)[MeV]'
        elif self._tag.startswith('L0TIS_MM'):
            return 'p_{T}(B)[MeV]'
        elif self._tag.startswith('L0TIS_MH'):
            return 'max(p_{T}(e^{+}), p_{T}(e^{-}))[MeV]'
        elif self._tag.startswith('HLT_'):
            return 'p_{T}(B)[MeV]'
        else:
            self.log.error('Cannot assign xname to ' + self._tag)
            raise
    #----------------------------------
    def plot_maps(self, filedir, replica = None, extension=None, skip_direct=False, d_opt={}):
        utnr.make_dir_path(filedir)
        utnr.check_none(replica)
        utnr.check_none(extension)

        self.__initialize()
        self._skip_direct=skip_direct
        if replica not in self._d_heff:
            self._fill_map(replica)

        _ = self.__do_plot_map(filedir, self._d_hpas, replica, 'pas', extension, d_opt)
        _ = self.__do_plot_map(filedir, self._d_hfal, replica, 'fal', extension, d_opt)

        d_opt['legend'] = -1 
        tp_h_eff = self.__do_plot_map(filedir, self._d_heff, replica, 'eff', extension, d_opt)

        d_opt['legend'] = +1 
        d_opt['logy']   = True
        d_opt['xname']  = 'Total weight' 
        d_opt['yname']  = 'Entries' 

        return tp_h_eff
    #----------------------------------
    def __do_plot_map(self, filedir, d_his, replica, kind, extension, d_opt):
        suffix = f'{kind}_r{replica:03}'

        h_dat=d_his[replica][0]
        h_sim=d_his[replica][1]
        h_dir=d_his[replica][2]

        tp_hist = self.__overlay(h_dat, h_sim, h_dir, filedir, suffix, d_set = d_opt)

        return tp_hist
    #----------------------------------
    def _fill_map(self, replica = None):
        utnr.check_none(replica)
        self.log.debug('')
        self.log.debug(f'Replica: {replica}')
        self.log.debug(f'{"Quantity":<20}{"Empty/Total=rate":<20}')
        self.log.debug('----')
        h_pas_dat=self.__do_fill(replica, 'data_passed')
        h_fal_dat=self.__do_fill(replica, 'data_failed')
        h_wgt_dps=self.__do_fill(replica, 'wgt_dat_pas')
        h_wgt_dfl=self.__do_fill(replica, 'wgt_dat_fal')
        h_eff_dat=self.__calc_eff_map(f'h_eff_dat_{replica}', h_pas_dat, h_fal_dat, replica)
        self.log.debug('----')
        h_pas_sim=self.__do_fill(replica,  'sim_passed')
        h_fal_sim=self.__do_fill(replica,  'sim_failed')
        h_wgt_sps=self.__do_fill(replica,  'wgt_sim_pas')
        h_wgt_sfl=self.__do_fill(replica,  'wgt_sim_fal')
        h_eff_sim=self.__calc_eff_map(f'h_eff_sim_{replica}', h_pas_sim, h_fal_sim, replica)
        self.log.debug('----')

        if not self._skip_direct:
            h_pas_dir=self.__do_fill(replica,  'dir_passed')
            h_fal_dir=self.__do_fill(replica,  'dir_failed')
            h_wgt_Dps=self.__do_fill(replica,  'wgt_dir_pas')
            h_wgt_Dfl=self.__do_fill(replica,  'wgt_dir_fal')
            h_eff_dir=self.__calc_eff_map('h_eff_dir_{}'.format(replica), h_pas_dir, h_fal_dir, replica)
            self.log.debug('----')
        else:
            h_pas_dir=None
            h_fal_dir=None
            h_eff_dir=None
            h_wgt_Dps=None
            h_wgt_Dfl=None

        self._d_hpas[replica] = (h_pas_dat, h_pas_sim, h_pas_dir)
        self._d_hfal[replica] = (h_fal_dat, h_fal_sim, h_fal_dir)
        self._d_heff[replica] = (h_eff_dat, h_eff_sim, h_eff_dir)
        self._d_hwps[replica] = (h_wgt_dps, h_wgt_sps, h_wgt_Dps)
        self._d_hwfl[replica] = (h_wgt_dfl, h_wgt_sfl, h_wgt_Dfl)
    #----------------------------------
    def _get_histograms(self):
        self.__initialize()

        d_hst = {}

        d_hst['pas'] = self._d_hpas[0]
        d_hst['fal'] = self._d_hfal[0]
        d_hst['eff'] = self._d_heff[0]
        d_hst['wps'] = self._d_hwps[0]
        d_hst['wfl'] = self._d_hwfl[0]

        return d_hst
    #----------------------------------
    def save_maps(self, map_dir=None):
        self.__initialize()

        if map_dir is None:
            cal_dir = os.environ['CALDIR']
            map_dir = f'{cal_dir}/TRG'

        file_dir  = utnr.make_dir_path(f'{map_dir}/{self._version}')
        file_path = f'{file_dir}/{self._tag}_{self._year}.root'

        d_hist = self._get_histograms()

        self.log.visible(f'Saving maps to: {file_path}')
        ofile=ROOT.TFile(file_path, 'recreate')
        for key, l_hist in d_hist.items():
            ofile.mkdir(key)
            ofile.cd(key)
            [hist.Write() for hist in l_hist]
            ofile.cd('..')

        ofile.Close()

        return file_path
    #----------------------------------
    def set_array(self, tup, key):
        if key not in ['data_passed', 'data_failed', 'sim_passed', 'sim_failed', 'dir_passed', 'dir_failed']:
            self.log.error(f'Wrong key: {key}')
            raise

        if len(tup) != 3:
            self.log.error(f'Tuple has wrong size: {str(len(tup))}')
            raise

        if key in self._d_tupl:
            self.log.warning(f'Attempting to store with used key: {key}')
            return

        self._d_tupl[key] = tup

        _, arr_wgt, arr_evt = tup
        arr_one = numpy.ones(arr_evt.size)

        if key == 'data_passed':
            self._d_tupl['wgt_dat_pas'] = (arr_wgt, arr_one, arr_evt)

        if key == 'data_failed':
            self._d_tupl['wgt_dat_fal'] = (arr_wgt, arr_one, arr_evt)

        if key == 'sim_passed':
            self._d_tupl['wgt_sim_pas'] = (arr_wgt, arr_one, arr_evt)

        if key == 'sim_failed':
            self._d_tupl['wgt_sim_fal'] = (arr_wgt, arr_one, arr_evt)

        if key == 'dir_passed':
            self._d_tupl['wgt_dir_pas'] = (arr_wgt, arr_one, arr_evt)

        if key == 'dir_failed':
            self._d_tupl['wgt_dir_fal'] = (arr_wgt, arr_one, arr_evt)
#----------------------------------
class trg_rwt:
    log=utnr.getLogger('trg_rwt') 
    #----------------------------------
    def __init__(self, tag, year, map_dir):
        self._tag         = tag 
        self._year        = year 
        self._map_dir     = map_dir

        self._h_eff_dat   = None
        self._h_eff_sim   = None
        self._h_eff_dir   = None

        self._epsilon     = 1e-10

        self._initialized = False
    #----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        map_path= f'{self._map_dir}/{self._tag}_{self._year}.root'
        utnr.check_file(map_path)

        ifile = ROOT.TFile(map_path)
        ifile.cd('eff')

        self._h_eff_dat = ROOT.gDirectory.h_eff_dat_0
        self._h_eff_sim = ROOT.gDirectory.h_eff_sim_0
        self._h_eff_dir = ROOT.gDirectory.h_eff_dir_0

        self._h_eff_dat.SetDirectory(0)
        self._h_eff_sim.SetDirectory(0)
        self._h_eff_dir.SetDirectory(0)

        ifile.Close()

        self._initialized = True
    #----------------------------------
    @property
    def maps(self):
        self._initialize()
        return (self._h_eff_dat, self._h_eff_sim, self._h_eff_dir) 

    @maps.setter
    def maps(self, value):
        self._h_eff_dat, self._h_eff_sim, self._h_eff_dir = value
    #----------------------------------
    def _check_efficiency(self, eff, xval, yval):
        if   eff < 0: 
            self.log.warning('For tag {} year {} point ({:.3f},{:.3f})'.format(self._tag, self._year, xval, yval) )
            self.log.warning('Efficiency {} ---> 0'.format(eff))
            eff = 0
        elif eff == 0:
            self.log.debug('For tag {} year {} point ({:.3f},{:.3f}), efficiency = 0'.format(self._tag, self._year, xval, yval) )
        elif eff == 1:
            self.log.debug('For tag {} year {} point ({:.3f},{:.3f}), efficiency = 1'.format(self._tag, self._year, xval, yval) )
        elif eff > 1: 
            self.log.warning('For tag {} year {} point ({:.3f},{:.3f})'.format(self._tag, self._year, xval, yval) )
            self.log.warning('Efficiency {} ---> 1'.format(eff))
            eff = 1

        return eff
    #----------------------------------
    def get_efficiencies(self, arr_point, treename):
        self._initialize()

        self.treename = treename

        l_eff=[]

        xmax=self._h_eff_dat.GetXaxis().GetXmax()
        xmin=self._h_eff_dat.GetXaxis().GetXmin()

        ymax=self._h_eff_dat.GetYaxis().GetXmax()
        ymin=self._h_eff_dat.GetYaxis().GetXmin()

        nyval_neg=0
        for [xval, yval] in arr_point:
            #If Y coordinate is the calorimeter region (calotag), make efficiencies zero
            #for objects outside calorimeter, (negative region)
            calotag = ('L0Electron' in self._tag) or ('L0Hadron' in self._tag)
            if calotag and yval < 0:
                l_eff.append([0, 0])
                nyval_neg+=1
                continue

            #Make sure point is inside map
            if xval <= xmin:
                self.log.debug('For tag {}, year {} x={:.3f} ---> x={:.3f}'.format(self._tag, self._year, xval, xmin))
                xval = xmin + self._epsilon

            if xval >= xmax:
                self.log.debug('For tag {}, year {} x={:.3f} ---> x={:.3f}'.format(self._tag, self._year, xval, xmax))
                xval = xmax - self._epsilon

            if yval <  ymin:
                self.log.debug('For tag {}, year {} y={:.3f} ---> y={:.3f}'.format(self._tag, self._year, yval, ymin))
                yval = ymin + self._epsilon

            if yval >  ymax:
                self.log.debug('For tag {}, year {} y={:.3f} ---> y={:.3f}'.format(self._tag, self._year, yval, ymax))
                yval = ymax - self._epsilon

            if yval == ymin:
                yval = ymin + self._epsilon

            if yval == ymax:
                yval = ymax - self._epsilon

            i_bin   = self._h_eff_dat.FindBin(xval, yval) 
            eff_dat = self._h_eff_dat.GetBinContent(i_bin)
            eff_sim = self._h_eff_sim.GetBinContent(i_bin)

            eff_dat = self._check_efficiency(eff_dat, xval, yval)
            eff_sim = self._check_efficiency(eff_sim, xval, yval)

            #Either efficiency is zero therefore we do not know it and do not apply weights
            if (eff_dat * eff_sim) == 0 and (eff_dat + eff_sim) > 0:
                eff_dat = 0
                eff_sim = 0

            l_eff.append([eff_dat, eff_sim])

        self.log.debug('{"Negative Y":<20}{nyval_neg:<20}')
        arr_eff = numpy.array(l_eff)

        return arr_eff 
#----------------------------------

