import ROOT
import math
import utils_noroot as utnr
import numpy
import pandas       as pnd

import matplotlib.pyplot as plt

#----------------------------------
class splitter:
    log = utnr.getLogger(__name__)
    #----------------------------------
    def __init__(self, rdf, d_bound, spectators=[]):
        self._rdf         = rdf
        self._d_bound     = d_bound
        self._l_var       = list(d_bound.keys()) + spectators

        self._plot_dir    = None

        self._initialized = False
    #----------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_data()
        self._check_vars()
        self._check_dir()

        self._initialized = True
    #----------------------------------
    def _check_data(self):
        if isinstance(self._rdf, pnd.DataFrame):
            self.log.info(f'Found pandas dataframe, transforming to ROOT')
            self._pandas_to_root()

        try:
            ROOT.RDF.AsRNode(self._rdf)
        except:
            self.log.error('Dataframe is not of the right type:')
            self.log.error(self._rdf)
            raise TypeError
    #----------------------------------
    def _pandas_to_root(self):
        d_tmp_1 = self._rdf.to_dict()
        d_tmp_2 = { key : list(d_val.values()) for key, d_val in d_tmp_1.items() }
        d_data  = { key : numpy.array(l_val) for key, l_val in d_tmp_2.items() }
    
        self._rdf = ROOT.RDF.FromNumpy(d_data)
    #----------------------------------
    @property
    def plot_dir(self):
        return self._plot_dir

    @plot_dir.setter
    def plot_dir(self, value):
        self._plot_dir = value
    #----------------------------------
    def _check_dir(self):
        if self._plot_dir is None:
            return

        utnr.make_dir_path(self._plot_dir)
    #----------------------------------
    def _check_vars(self):
        l_col = self._rdf.GetColumnNames()
        for var in self._l_var:
            if var not in l_col:
                self.log.error(f'Bound variable "{var}" not found among columns: {l_col}')
                raise
    #----------------------------------
    def _get_data(self):
        nentries = self._rdf.Count().GetValue()
        self.log.info(f'Extracting {nentries} entries from RDF for variables: {self._l_var}')
        d_data = self._rdf.AsNumpy(self._l_var)

        l_data = [ d_data[var] for var in self._l_var]

        return numpy.array(l_data).T
    #----------------------------------
    def _split_dataset(self, l_point, arr_bound, i_axis):
        '''
        Takes 
        1. l_point: numpy array of points (arrays)
        2. Array of floats

        Returns

        {bound -> data}

        where bound is a tuple of tuples ((x1, x2), ...)

        It will sort the dictionary by keys and it will also padd missing keys with empty arrays as values
        '''
        d_data = {}
        for point in l_point:
            val   = point[i_axis]
            index = (numpy.abs(arr_bound - val)).argmin()
            index = index if arr_bound[index] <= val else index - 1

            minx = arr_bound[index + 0] if index !=                -1 else - math.inf
            maxx = arr_bound[index + 1] if index != arr_bound.size -1 else + math.inf
            utnr.add_to_dic_lst(d_data, (minx, maxx), point)

        d_data_s  = dict(sorted(d_data.items()))
        d_data_sa = {bound : numpy.array(l_point) for bound, l_point in d_data_s.items()}
        d_data_sap= self._pad_split_dataset(d_data_sa, arr_bound)

        return d_data_sap
    #----------------------------------
    def _pad_split_dataset(self, d_data, arr_bound):
        '''
        Takes {bound -> data} and array of floats

        Builds bounds and checks if any is missing, if so pads with empty array
        '''

        for index in range(-1, arr_bound.size):
            minx = arr_bound[index + 0] if index !=                -1 else - math.inf
            maxx = arr_bound[index + 1] if index != arr_bound.size -1 else + math.inf

            axis_bound = (minx, maxx)

            if axis_bound in d_data:
                continue

            d_data[axis_bound] = numpy.array([])

        return d_data
    #----------------------------------
    def _update_bounds(self, d_data, old_bound):
        d_res = {}
        for axis_bound, data in d_data.items():
            total_bound        = (axis_bound, ) if old_bound is None else old_bound + (axis_bound, )
            d_res[total_bound] = data 

        return d_res
    #----------------------------------
    def _split_datasets(self, d_data, l_bound, i_axis):
        d_split = {}

        arr_bound = numpy.array(l_bound)
        for bound, data in d_data.items():
            d_tmp    = self._split_dataset(data, arr_bound, i_axis)
            d_tmp    = self._update_bounds(d_tmp, bound)

            l_size   = [ str(numpy.ma.size(data, axis=0)) for data in d_tmp.values() ]
            sizes    = ','.join(l_size)
            split    = f'{len(d_tmp):<20}({sizes:<20})'

            self.log.debug(f'({len(data):04}) -> {split}')

            d_split.update(d_tmp)

        self.log.info(f'Splitting {len(d_data):04} -> {len(d_split):04} datasets along {i_axis} axis')

        return d_split
    #----------------------------------
    def _plot_stats(self, d_data):
        if self._plot_dir is None:
            return

        plot_path = f'{self._plot_dir}/nentries.png'

        l_size = [ len(data) for data in d_data.values()]

        plt.plot(l_size)
        plt.ylim(bottom=0)
        plt.savefig(plot_path)
        plt.close('all')
    #----------------------------------
    def _check_split(self, d_data, data):
        ntot = len(data)
        nsum = 0

        for dst in d_data.values():
            nsum += len(dst)

        if nsum != ntot:
            self.log.error(f'Sum and total differ: {nsum}/{ntot}')
            raise
    #----------------------------------
    def _get_df(self, data, index):
        if data.size == 0:
            df=pnd.DataFrame(columns=self._l_var)
            df.ibin = index
        else:
            df=pnd.DataFrame(data, columns=self._l_var)
            df.ibin = index

        return df
    #----------------------------------
    def _symmetrize(self, d_data):
        self.log.info(f'Symmetrizing 2D dataset')

        d_data_sym = {}
        for (x, y), vxy in d_data.items():
            vyx = d_data[(y, x)]
            if vxy is None:
                d_data_sym[(x, y)] = numpy.array([])
                continue

            if x == y:
                d_data_sym[(x, y)] = vxy
                continue
            
            if   vxy.size == 0 and vyx.size == 0:
                vsm = vxy
            elif vxy.size == 0:
                vsm = vyx
            elif vyx.size == 0:
                vsm = vxy
            else:
                try:
                    vsm = numpy.concatenate([vxy, vyx])
                except:
                    self.log.error('Cannot concatenate:')
                    print(vxy)
                    print(vyx)
                    raise

            d_data[(y, x)]     = None
            d_data_sym[(x, y)] = vsm

        return d_data_sym
    #----------------------------------
    def _is_flow(self, tup_bound):
        for bound in tup_bound:
            if +math.inf in bound:
                return True

            if -math.inf in bound:
                return True

        return False
    #----------------------------------
    def get_datasets(self, as_type = 'list', symmetrize=False, noflow=False):
        '''Provides container of datasets split according to specified binning

        Parameters
        ------------------
        as_type (str): Specifies if container is list of datasets or dictionary, allowed values: list, dict
        symmetrize(bool): Should elements in (x,y) and (x,-y) be placed in the same dataset?
        If dataset is 2D, produce only the lower side of the data matrix by adding i,j and j,i dataset. 
        The upper side entries wil be empty, i.e. dataframe with no rows
        noflow (bool): Will remove overflow and undeflow datasets

        Returns
        ------------------
        1. List of dataframes with data 
        2. Dictionary {bound -> df} mapping tuples of bounds ((x1, x2), (y1, y2)...) for a corresponding dataframe

        Special cases
        ------------------
        If no data ends up in bin, dataframe is None.
        '''
        self._initialize()

        l_l_bound = [l_bound for _, l_bound in self._d_bound.items()]
        arr_data  = self._get_data()

        d_data = {None : arr_data}
        for i_axis, l_bound in enumerate(l_l_bound):
            d_data = self._split_datasets(d_data, l_bound, i_axis)

        if symmetrize and len(self._d_bound) == 2:
            d_data = self._symmetrize(d_data)

        self._check_split(d_data, arr_data)
        self._plot_stats(d_data)

        edata = enumerate(d_data.items())
        d_data= { bounds : self._get_df(data, index) for index, (bounds, data) in edata}
        if noflow:
            self.log.info('Removing overflow and underflow data')
            d_data= { key : val for key, val in d_data.items()  if not self._is_flow(key)}

        if as_type == 'list':
            obj = [ data for data in d_data.values() ]
        else:
            obj = d_data

        return obj
#----------------------------------

