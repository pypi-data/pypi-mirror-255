import os

import ROOT
import numpy
import math 

import utils

import utils_noroot as utnr

#-----------------------------------------
class HIS:
    log = utnr.getLogger('HIS')
    #-----------------------------------------
    def __init__(self, arr_original, arr_target, arr_original_weight=None, arr_target_weight=None):
        self._hm          = hist_maker(arr_original, arr_target, arr_original_weight=arr_original_weight, arr_target_weight=arr_target_weight)
        self._arr_bin_x   = None 
        self._arr_bin_y   = None 
        self._arr_bin_z   = None 

        self._hr          = None

        self._initialized = False
    #---------------------------------------
    @property
    def arr_bin_x(self, value):
        return self._arr_bin_x

    @arr_bin_x.setter
    def arr_bin_x(self, value):
        self._arr_bin_x = value

    @property
    def arr_bin_y(self, value):
        return self._arr_bin_y

    @arr_bin_y.setter
    def arr_bin_y(self, value):
        self._arr_bin_y = value

    @property
    def arr_bin_z(self, value):
        return self._arr_bin_z

    @arr_bin_z.setter
    def arr_bin_z(self, value):
        self._arr_bin_z = value
    #---------------------------------------
    def _initialize(self):
        if self._initialized:
            return
        #----------------------------------
        self._hm.arr_bin_x = self._arr_bin_x 
        self._hm.arr_bin_y = self._arr_bin_y 
        self._hm.arr_bin_z = self._arr_bin_z 
        #----------------------------------
        h_dt, h_mc = self._hm.get_maps()
        self._hr   = hist_reader(dt=h_dt, mc=h_mc)

        self._initialized = True
    #---------------------------------------
    def get_histograms(self):
        self._initialize()

        return self._hm.get_maps()
    #---------------------------------------
    def predict_weights(self, data, method='hist'):
        self._initialize()

        return self._hr.predict_weights(data)
#-----------------------------------------
class hist_maker:
    log = utnr.getLogger('hist_maker')
    #-----------------------------------------
    def __init__(self, arr_original, arr_target, arr_original_weight=None, arr_target_weight=None):
        self._arr_original       = arr_original
        self._arr_target         = arr_target
        self._arr_original_weight= arr_original_weight
        self._arr_target_weight  = arr_target_weight

        self._arr_bin_x          = None 
        self._arr_bin_y          = None 
        self._arr_bin_z          = None 

        self.prefix              = 'nopref' 
        self._ndim               = None

        self.ran                 = ROOT.TRandom3(0)

        self._unc_no_wgt         = 1.234
        self._initialized        = False
    #-----------------------------------------
    @property
    def arr_bin_x(self, value):
        return self._arr_bin_x

    @arr_bin_x.setter
    def arr_bin_x(self, value):
        self._arr_bin_x = value

    @property
    def arr_bin_y(self, value):
        return self._arr_bin_y

    @arr_bin_y.setter
    def arr_bin_y(self, value):
        self._arr_bin_y = value

    @property
    def arr_bin_z(self, value):
        return self._arr_bin_z

    @arr_bin_z.setter
    def arr_bin_z(self, value):
        self._arr_bin_z = value
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        #----------------------------------
        utnr.check_none(self._arr_bin_x)
        utnr.check_none(self._arr_bin_y)
        utnr.check_none(self._arr_bin_y)
        #----------------------------------
        self._check_ndim(self._arr_original, 'original')
        self._check_ndim(self._arr_target  ,   'target')

        self._check_weights(self._arr_original, self._arr_original_weight)
        self._check_weights(self._arr_target  , self._arr_target_weight)
        #----------------------------------

        self._initialized = True
    #---------------------------------------
    def _get_2d_histograms(self):
        ran_id=self.ran.Integer(1000000000)

        num_name=f'h_num_{ran_id}'
        den_name=f'h_den_{ran_id}'

        h_num=ROOT.TH2F(num_name, 'Numerator'  , self._arr_bin_x.size - 1, self._arr_bin_x, self._arr_bin_y.size - 1, self._arr_bin_y)
        h_num.SetDirectory(0)
        h_num.Sumw2(True)

        h_den=ROOT.TH2F(den_name, 'Denominator', self._arr_bin_x.size - 1, self._arr_bin_x, self._arr_bin_y.size - 1, self._arr_bin_y)
        h_den.SetDirectory(0)
        h_den.Sumw2(True)

        return h_num, h_den
    #---------------------------------------
    def _get_3d_histograms(self):
        ran_id=self.ran.Integer(1000000000)

        num_name=f'h_num_{ran_id}'
        den_name=f'h_den_{ran_id}'

        h_num=ROOT.TH3F(num_name, 'Numerator'  , self._arr_bin_x.size - 1, self._arr_bin_x, self._arr_bin_y.size - 1, self._arr_bin_y, self._arr_bin_z.size - 1, self._arr_bin_z)
        h_num.SetDirectory(0)
        h_num.Sumw2(True)

        h_den=ROOT.TH3F(den_name, 'Denominator', self._arr_bin_x.size - 1, self._arr_bin_x, self._arr_bin_y.size - 1, self._arr_bin_y, self._arr_bin_z.size - 1, self._arr_bin_z)
        h_den.SetDirectory(0)
        h_den.Sumw2(True)

        return h_num, h_den
    #---------------------------------------
    def _fill_histograms_2d(self):
        h_num, h_den = self._get_2d_histograms()

        for [x, y], w in zip(self._arr_target,   self._arr_target_weight):
            h_num.Fill(x, y, w)
        self.log.info(f'Filled target, with {self._arr_target_weight.size} entries')

        for [x, y], w in zip(self._arr_original, self._arr_original_weight):
            h_den.Fill(x, y, w)
        self.log.info(f'Filled original with {self._arr_original_weight.size} entries')

        return h_num, h_den
    #---------------------------------------
    def _fill_histograms_3d(self):
        h_num, h_den = self._get_3d_histograms()

        for [x, y, z], w in zip(self._arr_target,   self._arr_target_weight):
            h_num.Fill(x, y, z, w)
        self.log.debug("Filled target")

        for [x, y, z], w in zip(self._arr_original, self._arr_original_weight):
            h_den.Fill(x, y, z, w)
        self.log.debug("Filled original")

        return h_num, h_den
    #---------------------------------------
    def _check_histogram(self, hist):
        if   hist.InheritsFrom('TH2'):
            nbins = (hist.GetNbinsX() + 2) * (hist.GetNbinsY() + 2)
        elif hist.InheritsFrom('TH3'):
            nbins = (hist.GetNbinsX() + 2) * (hist.GetNbinsY() + 2) * (hist.GetNbinsZ() + 2)
        else:
            self.log.error(f'Histogram is neither 2D nor 3D:')
            raise

        for i_bin in range(0, nbins + 1):
            bc=hist.GetBinContent(i_bin)
            if bc < 0:
                self.log.debug(f'Bin {i_bin} in histogram {hist.GetName()} has content {bc}, setting it to zero')
                hist.SetBinContent(i_bin, 0)
    #---------------------------------------
    def _check_ndim(self, arr_point, preffix):
        ndim_exp    = 2 if self._arr_bin_z is None else 3
        _, ndim_fnd = arr_point.shape
        
        if ndim_exp != ndim_fnd:
            self.log.error(f'Wrong ndim for {preffix} array, expected/got: {ndim_exp}/{ndim_fnd}')
            raise

        self._ndim = ndim_exp
    #---------------------------------------
    def _check_weights(self, container, weights):
        c_s=len(container)
        w_s=len(weights)

        if c_s == 0:
            self.log.error('Container with data is empty')
            raise

        if c_s != w_s: 
            self.log.error(f'Container and weights disagree in size c/w:{c_s}/{c_w}')
            raise

        if w_s == 0:
            weights = [1] * c_s
    #-----------------------------------------
    def get_maps(self):
        self._initialize()

        if   self._ndim == 2:
            h_num, h_den = self._fill_histograms_2d()
        elif self._ndim == 3:
            h_num, h_den = self._fill_histograms_3d()
        else:
            self.log.error(f'Invalid ndim: {self._ndim}')
            raise

        h_num.Scale(1./h_num.Integral())
        h_den.Scale(1./h_den.Integral())

        self._check_histogram(h_num)
        self._check_histogram(h_den)

        self.log.debug(f'Filled {self._ndim}D histograms')

        return h_num, h_den
    #---------------------------------------
    def save_maps(self, map_path, extension="png", d_opt={}):
        self._initialize()

        h_num, h_den = self.get_maps()

        if extension != "png":
            self.log.error('Only PNG is supported')
            raise

        for kind, hist in [ ('num', h_num), ('den' , h_den) ] :
            self._save_map(map_path, kind, hist, d_opt) 
    #---------------------------------------
    def _save_map(self, map_path, kind, hist, d_opt):
        hist = self._format_hist(hist, kind, d_opt)

        if 'style' in d_opt:
            style = d_opt['style']
        elif self._ndim == 2:
            style = 'COLZ'
        elif self._ndim == 3:
            style = 'BOX2 Z'
        else:
            self.log.error(f'Invalid ndim = {self._ndim}')
            raise

        if 'width' in d_opt:
            width = d_opt['width']
        else:
            width = 800

        mapdir = os.path.dirname(map_path)
        os.makedirs(mapdir, exist_ok=True)

        plot_path=f'{map_path}/{kind}.png'
        self.log.visible(f'Saving: {plot_path}')
        canv=ROOT.TCanvas(f'c_{kind}', '', width, 600)
        hist.Draw(style)
        canv.SaveAs(plot_path)

        self._save_projection(hist, kind, width, plot_path, d_opt)
    #---------------------------------------
    def _save_projection(self, hist, kind, width, plot_path, d_opt):
        if not isinstance(hist, ROOT.TH3D):
            return

        nbins = hist.GetZaxis().GetNbins()
        if nbins != 1:
            self.log.info(f'Found {nbins} bins, not plotting projection')
            return

        hist_proj = hist.Project3D('yx NOF NUF')
        hist_proj = self._format_hist(hist_proj, kind, d_opt)
        plot_path = plot_path.replace('.png', '_proj.png')

        self.log.visible(f'Saving: {plot_path}')
        canv=ROOT.TCanvas(f'c_{kind}_proj', '', width, 600)
        hist_proj.Draw('COLZ')
        utils.reformat_2D_hist(hist_proj)
        canv.SaveAs(plot_path)
    #---------------------------------------
    def _format_hist(self, hist, kind, d_opt):
        if   kind == 'err':
            hist.SetMinimum(0)
            hist.SetMaximum(1)
        elif kind == 'rat' and 'rrange' in d_opt:
            rmin, rmax = d_opt['rrange']
            hist.SetMinimum(rmin)
            hist.SetMaximum(rmax)

        if "xname" in d_opt:
            xname=d_opt['xname']
            hist.GetXaxis().SetTitle(xname)

        if "yname" in d_opt:
            yname=d_opt['yname']
            hist.GetYaxis().SetTitle(yname)

        if "zname" in d_opt:
            zname=d_opt['zname']
            hist.GetZaxis().SetTitle(zname)

        return hist
#-----------------------------------------
class hist_reader:
    log = utnr.getLogger('hist_reader')
    #-----------------------------------------
    def __init__(self, dt=None, mc=None):
        self._h_dt        = dt
        self._h_mc        = mc
        self._ndim        = None

        self._tp_range_x  = None
        self._tp_range_y  = None 
        self._tp_range_z  = None 
        self._epsilon     = 1e-7

        self._initialized = False
    #-----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._h_dt.Scale(1./self._h_dt.Integral())
        self._h_mc.Scale(1./self._h_mc.Integral())

        if self._h_dt is self._h_mc:
            self.log.error('Data and MC histograms are the same')
            raise

        self._check_ndim()
        self._get_ranges()

        self._initialized = True
    #---------------------------------------
    def _get_ranges(self):
        xax = self._h_dt.GetXaxis()
        yax = self._h_dt.GetYaxis()
        zax = self._h_dt.GetZaxis()

        self._tp_range_x = (xax.GetXmin(), xax.GetXmax())
        self._tp_range_y = (yax.GetXmin(), yax.GetXmax())
        if self._ndim == 3:
            self._tp_range_z = (zax.GetXmin(), zax.GetXmax())
    #---------------------------------------
    def _check_ndim(self):
        if   self._h_dt.InheritsFrom('TH2') and self._h_mc.InheritsFrom('TH2'):
            self._ndim = 2
        elif self._h_dt.InheritsFrom('TH3') and self._h_mc.InheritsFrom('TH3'):
            self._ndim = 3
        else:
            self.log.error('Maps have wrong dimensions')
            self._h_dt.Print()
            self._h_mc.Print()
            raise
    #---------------------------------------
    def _check_data(self, data):
        if data.size == 0:
            self.log.warning('Data is empty')

        _, ndim = data.shape

        if ndim != self._ndim:
            self.log.error(f'Dataset with wrong dimension, expected/obtained: {self._ndim}/{ndim}')
            raise
    #-----------------------------------------
    def _get_axis(self, value, minv, maxv, axis):
        if   value <  minv:
            x       =  minv + self._epsilon
            self.log.debug(f'{axis}: {value} -> {minv}')
        elif value >  maxv:
            x       =  maxv - self._epsilon
            self.log.debug(f'{axis}: {value} -> {maxv}')
        else:
            x       = value 

        return x
    #---------------------------------------
    def _push_in_map(self, point): 
        minx, maxx = self._tp_range_x
        x = self._get_axis(point[0], minx, maxx, 'x')

        miny, maxy = self._tp_range_y
        y = self._get_axis(point[1], miny, maxy, 'y')

        if self._tp_range_z is None:
            return numpy.array([x, y])
        else:
            minz, maxz = self._tp_range_z
            z = self._get_axis(point[2], minz, maxz, 'z')

            return numpy.array([x, y, z])
    #-----------------------------------------
    def _get_map_yld(self, point, hist):
        if   self._ndim == 2:
            i_bin=hist.FindBin(point[0], point[1])
        elif self._ndim == 3:
            i_bin=hist.FindBin(point[0], point[1], point[2])
        else:
            self.log.error(f'Invalid ndim: {self._ndim}')
            raise
    
        if i_bin <= 0:
            self.log.error('Found bin {i_bin} for {val}')
            raise
    
        bc = hist.GetBinContent(i_bin)
        be = hist.GetBinError(i_bin)

        return bc, be 
    #-----------------------------------------
    def _get_weight(self, point):
        dat, e_dat = self._get_map_yld(point, self._h_dt)
        sim, e_sim = self._get_map_yld(point, self._h_mc)

        if dat == sim:
            self.log.debug(f'Data = MC = {dat:.3f} at {point}')

        if dat < 0:
            dat = 0

        if   sim == 0:
            return 1 
        elif sim >  0:
            return dat/sim 
        else:
            self.log.error(f'Invalid values for data and simulation yields: {dat:.3f}, {sim:.3f}')
            raise
    #-----------------------------------------
    def get_histograms(self):
        self._initialize()

        return [ self._h_dt, self._h_mc ]
    #-----------------------------------------
    def predict_weights(self, data):
        self._initialize()

        self._check_data(data)

        self.log.info('Regularizing dataset')
        l_point = [ self._push_in_map(point)  for point in data ]
        data    = numpy.array(l_point)

        self.log.info('Extracting weights')
        l_wgt   = [ self._get_weight(point)   for point in data ]
        arr_wgt = numpy.array(l_wgt)

        return arr_wgt 
#-----------------------------------------

