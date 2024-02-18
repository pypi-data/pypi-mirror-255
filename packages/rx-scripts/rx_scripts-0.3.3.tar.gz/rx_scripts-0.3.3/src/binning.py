import ROOT
import utils
import math
import collections
import bisect
import numpy
import os

import utils_noroot as utnr

#----------------------------------------
class binning:
    log=utnr.getLogger(__name__)
    #----------------------------------------
    def __init__(self, arr_point, d_opt):
        self.__arr_point = arr_point
        self.__d_opt     = d_opt

        self.__arr_x     = None
        self.__arr_y     = None
        self.__hist      = None

        self.__flt_wthr  = 0.95
        self.__flt_ethr  = 0.70

        self.__initialized=False
    #----------------------------------------
    def __initialize(self):
        if self.__initialized:
            return

        _ = utnr.get_from_dic(self.__d_opt,  'nbins')
        _ = utnr.get_from_dic(self.__d_opt, 'xrange')
        _ = utnr.get_from_dic(self.__d_opt, 'yrange')

        self.__arr_point = self.__filter_data(self.__arr_point)
        try:
            self.__arr_x = self.__arr_point.T[0]
            self.__arr_y = self.__arr_point.T[1]
        except:
            self.log.error('Cannot extract X and Y arrays of data from array with shape:')
            print(self.__arr_point.shape())
            raise

        if 'nbins_y' in self.__d_opt:
            self.__nbins_y = self.__d_opt['nbins_y']
        else:
            nbins=self.__d_opt['nbins']
            self.__nbins_y=math.floor(math.sqrt(nbins))

        self.log.info('Using {} bins in Y'.format(self.__nbins_y))

        self.__initialized = True
    #----------------------------------------
    def __filter_data(self, arr_xy):
        npoints_org = numpy.size(arr_xy, axis=0)

        xmin, xmax = self.__d_opt['xrange']
        ymin, ymax = self.__d_opt['yrange']

        #---------------------
        arr_x = arr_xy.T[0]
        arr_y = arr_xy.T[1]

        arr_x_bool  = numpy.logical_and(arr_x > xmin, arr_x < xmax)
        arr_y_bool  = numpy.logical_and(arr_y > ymin, arr_y < ymax)
        arr_xy_bool = numpy.logical_and(arr_x_bool, arr_y_bool)

        arr_x = arr_x[arr_xy_bool]
        arr_y = arr_y[arr_xy_bool]

        arr_xy = numpy.array([arr_x, arr_y]).T
        #---------------------

        npoints_flt = numpy.size(arr_xy, axis=0)

        frac = npoints_flt/npoints_org 
        if   frac < self.__flt_ethr:
            self.log.error(  'Filtered events below threshold: {}/{} = {:.3f}'.format(npoints_flt, npoints_org, frac))
            raise
        elif frac < self.__flt_wthr:
            self.log.warning('Filtered events below threshold: {}/{} = {:.3f}'.format(npoints_flt, npoints_org, frac))
        else:
            self.log.info('Filtered events: {}/{} = {:.3f}'.format(npoints_flt, npoints_org, frac))

        return arr_xy
    #----------------------------------------
    def __get_borders(self, arr_val, nbins):
        size=len(arr_val)
        arr_val_sort=sorted(arr_val)

        bin_size=math.floor(size/nbins)
        if bin_size <= 0:
            self.log.error('Zero bin size found')
            self.log.error('Size = {}'.format(size ))
            self.log.error('Nbins= {}'.format(nbins))
            raise
    
        l_border=[]
        for index in range(0, size, bin_size):
            val = arr_val_sort[index]
            l_border.append(val)
            if len(l_border) == nbins + 1:
                break

        #If size/nbins divides exactly (small nbins) last border not reachable
        nborder=len(l_border)
        if nborder == nbins:
            l_border.append(max(arr_val_sort))
            nborder=len(l_border)

        if nborder != nbins + 1:
            self.log.error('Wrong number of borders')
            self.log.error('Size    = {}'.format(    size) )
            self.log.error('NBins   = {}'.format(   nbins) )
            self.log.error('NBorder = {}'.format( nborder) )
            self.log.error('Bin size= {}'.format(bin_size) )
            print(l_border)
            raise

        return l_border
    #----------------------------------------
    def __adjust_borders(self, arr_border, range_name):
        try:
            rmin, rmax = self.__d_opt[range_name]
        except:
            self.log.error('Wrong range name {}, allowed:'.format(range_name))
            print(self.__d_opt.keys())
            raise

        arr_border[ 0] = rmin
        arr_border[-1] = rmax
    #----------------------------------------
    def __build_histogram(self, name, l_arr_border_x, arr_border_y):
        xmin, xmax = self.__d_opt['xrange']
        ymin, ymax = self.__d_opt['yrange']

        hist=ROOT.TH2Poly(name, '', xmin, xmax, ymin, ymax)

        size_y=len(  arr_border_y)

        for i_y in range(0, size_y - 1):
            low_y = arr_border_y[i_y + 0]
            hig_y = arr_border_y[i_y + 1]

            try:
                size_x = len(l_arr_border_x[i_y])
            except:
                print('Cannot read {} element from:'.format(i_y))
                print(l_arr_border_x)
                raise

            for i_x in range(0, size_x - 1):
                low_x = l_arr_border_x[i_y][i_x + 0]
                hig_x = l_arr_border_x[i_y][i_x + 1]

                hist.AddBin(low_x, low_y, hig_x, hig_y)

        return hist
    #----------------------------------------
    def __check_borders(self, l_arr_border_x, arr_border_y):
        nbins_y = len(l_arr_border_x)
        nbord_y = len(arr_border_y)

        if nbins_y != nbord_y - 1:
            print('Y bins: {}'.format(nbins_y))
            print('Y borders: {}'.format(nbord_y))
            raise
    #----------------------------------------
    def save_histogram(self, filepath, name='h_poly', fill=False):
        self.__initialize()

        filedir  = os.path.dirname(filepath)
        utnr.make_dir_path(filedir)

        hist=self.get_histogram(name, fill)

        ofile=ROOT.TFile(filepath, 'recreate')
        hist.Write()
        ofile.Close()
    #----------------------------------------
    def get_histogram(self, name, fill=False):
        self.__initialize()

        if self.__hist is not None: 
            return self.__hist

        arr_border_y=self.__get_borders(self.__arr_y, self.__nbins_y)
        self.__adjust_borders(arr_border_y, 'yrange')

        nborder_y=len(arr_border_y)
        size     =len(self.__arr_x)

        d_l_val_x={}
        for x, y in self.__arr_point:
            i_y=bisect.bisect_left(arr_border_y, y)

            utnr.add_to_dic_lst(d_l_val_x, i_y - 1, x)

        l_l_val_x = list(d_l_val_x.values())

        l_arr_border_x=[]
        nbins=self.__d_opt['nbins']
        counter=0
        for l_val_x in l_l_val_x:
            slice_size=len(l_val_x)
            frac=slice_size/float(size)
            slice_nbins=math.floor(frac * nbins)

            if slice_nbins == 0:
                slice_nbins = 1

            arr_border_x = self.__get_borders(l_val_x, slice_nbins)
            self.__adjust_borders(arr_border_x, 'xrange')
            l_arr_border_x.append(arr_border_x)
            counter+=1

        self.__check_borders(l_arr_border_x, arr_border_y)

        hist=self.__build_histogram(name, l_arr_border_x, arr_border_y)

        if fill:
            for x, y in self.__arr_point:
                hist.Fill(x, y)

        self.__hist = hist

        return hist
#----------------------------------------

