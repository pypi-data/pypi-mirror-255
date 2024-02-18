from hep_ml.reweight import GBReweighter as gb_rwt

import numpy
import ROOT
import utils_noroot as utnr

#-------------------------------------------------------
class BDT:
    log = utnr.getLogger('BDT')
    #----------------------------
    def __init__(self, arr_sim_val, arr_dat_val, arr_sim_wgt=None, arr_dat_wgt=None):
        max_depth           = 4
        n_estimators        = 75 
        learning_rate       = 0.12
        min_samples_leaf    = 200
        loss_regularization = 500
        self._rwt           = gb_rwt(n_estimators, learning_rate, max_depth, min_samples_leaf, loss_regularization)

        self._arr_sim_val   = arr_sim_val 
        self._arr_dat_val   = arr_dat_val
        self._arr_sim_wgt   = arr_sim_wgt
        self._arr_dat_wgt   = arr_dat_wgt

        self._epsilon       = 0.00001
        self._fitted        = False

        self.storage        = None
    #----------------------------
    @property
    def rwt(self):
        return self._rwt
    #----------------------------
    def _print_data(self, kind, arr_val, arr_wgt):
        tval = arr_val.dtype.name
        sval = str(arr_val.shape)

        twgt = arr_wgt.dtype.name
        swgt = str(arr_wgt.shape)

        self.log.info(f'{"Kind" :<15}{kind:<15}')
        self.log.info(f'{"Type" :<15}{tval:<15}{twgt:<15}')
        self.log.info(f'{"Shape":<15}{sval:<15}{swgt:<15}')
        self.log.info('')
    #----------------------------
    def fit(self):
        self.log.info('Fitting')
        try:
            self._rwt.fit(self._arr_sim_val, self._arr_dat_val, self._arr_sim_wgt, self._arr_dat_wgt)
        except:
            self.log.error(f'Cannot fit data:')
            self._print_data('Simulation ', self._arr_sim_val, self._arr_sim_wgt)
            self._print_data('Data       ', self._arr_dat_val, self._arr_dat_wgt)
            raise

        self._fitted = True
    #----------------------------
    def _normalize_weights(self, arr_wgt):
        avg = arr_wgt.sum() / arr_wgt.size
        arr_wgt = arr_wgt / avg

        return arr_wgt
    #----------------------------
    def _check_weights(self, arr_wgt):
        assert (arr_wgt > 0.).all(),           self.log.error('Negative weights found')
        assert (~numpy.isnan(arr_wgt)).all(), self.log.error('At least one weight is NaN')
        assert (~numpy.isinf(arr_wgt)).all(), self.log.error('At least one weight is Inf')
    #----------------------------
    def predict_weights(self, arr_val, arr_wgt = None):
        if not self._fitted:
            self.fit()

        self.log.info('Predicting weights')

        arr_wgt = self._rwt.predict_weights(arr_val, arr_wgt)

        self._check_weights(arr_wgt)
        arr_wgt = self._normalize_weights(arr_wgt)

        return arr_wgt
#-------------------------------------------------------

