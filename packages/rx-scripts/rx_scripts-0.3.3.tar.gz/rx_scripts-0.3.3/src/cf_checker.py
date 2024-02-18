import ROOT

import utils_noroot as utnr

log=utnr.getLogger(__name__)
class cf_checker():
    def __init__(self, l_cf_1, l_cf_2):
        self.l_cf_1 = l_cf_1
        self.l_cf_2 = l_cf_2

        self._initialized = False
    #----------------------
    def __initialize(self):
        if self._initialized:
            return

        l_cf_1 = self.l_cf_1
        l_cf_2 = self.l_cf_2

        sz_1 = len(l_cf_1)
        sz_2 = len(l_cf_2)

        if sz_1 != sz_2:
            log.error('Set of cf objects are not the same size: {}/{}'.format(sz_1, sz_2))
            raise

        for cf_1, cf_2 in zip(l_cf_1, l_cf_2):
            if type(cf_1) != ROOT.CutFlowReport:
                log.error('Instance is not a cutflow object')
                print(cf_1)
                raise

            if type(cf_2) != ROOT.CutFlowReport:
                log.error('Instance is not a cutflow object')
                print(cf_2)
                raise

            name_1 = cf_1.GetName()
            name_2 = cf_2.GetName()

            if name_1 != name_2:
                log.error('Names of cf objects are different: {}/{}'.format(name_1, name_2))
                raise

        self._initialized = True
    #----------------------
    def are_equal(self):
        self.__initialize()



        return True
    #----------------------
