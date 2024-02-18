import ROOT

import os
import glob
import pickle 

import utils
import utils_noroot as utnr

log=utnr.getLogger(__name__)

class transform:
    def __init__(self, filespath, treename, l_selection):
        self.filespath   = filespath
        self.treename    = treename
        self.l_selection = l_selection
        self.event_name  = 'eventNumber'
        self.epsilon     = 1e-7
        self.diagnostics = False
        self.prefix      = None
        self.weightsdir  = None
    #-------------------------------------------------------
    def save_weights(self, weightspath):
        weightsdir = os.path.dirname(weightspath)
        os.makedirs(weightsdir, exist_ok=True)

        self.weightsdir=weightsdir

        d_weight = self.__get_weights()

        pickle.dump(d_weight, open(weightspath, 'wb'))
    #-------------------------------------------------------
    def __get_dataframe(self, branchname):
        l_files=glob.glob(self.filespath)
        if len(l_files) == 0:
            log.error('Cannot find files in ' + self.filespath)
            raise

        df = ROOT.RDataFrame(self.treename, self.filespath)
        df = df.Filter('TMath::Abs({}) > {}'.format(branchname, self.epsilon))

        return df
    #-------------------------------------------------------
    def __get_weights(self):
        l_br_df = []
        for selection in self.l_selection:
            branchname = 'sw_' + selection
            df=self.__get_dataframe(branchname)
            l_br_df.append((branchname, df))


        d_weight={}
        for branchname, df in l_br_df:
            log.info('Extracting weights for ' + branchname)

            d_data = df.AsNumpy([branchname, self.event_name])

            arr_event  = d_data[self.event_name]
            arr_weight = d_data[branchname]

            if self.diagnostics:
                self.__plot(arr_event , 'eventNumber_' + branchname)
                self.__plot(arr_weight, branchname)

            d_tmp={}
            for event, weight in zip(arr_event, arr_weight):
                d_tmp[event] = weight

            d_weight[branchname] = d_tmp

        return d_weight
    #-------------------------------------------------------
    def __plot(self, arr_data, branchname):
        if self.prefix     is None:
            log.error('Missing prefix')
            raise

        if self.weightsdir is None:
            log.error('Weights directory not defined')
            raise

        name='h_' + branchname
        hist = utils.arr_to_hist(name, '', 30, 0, 0, arr_data, color=1, d_opt={})

        outdir=self.weightsdir + '/plots'
        os.makedirs(outdir, exist_ok=True)
        outpath='{}/{}_{}.png'.format(outdir, self.prefix, branchname)

        log.visible('Saving ' + outpath)
        utils.plotHistograms([hist], outpath, d_opt={'width' : 800, 'xname' : branchname}) 
    #-------------------------------------------------------

