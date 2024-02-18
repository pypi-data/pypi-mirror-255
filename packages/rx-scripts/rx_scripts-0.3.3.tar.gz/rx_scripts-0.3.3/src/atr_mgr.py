import utils_noroot as utnr

class mgr:
    log=utnr.getLogger(__name__)
    #------------------------
    def __init__(self, df):
        self.d_in_atr = {}
        
        self.__store_atr(df)
    #------------------------
    def __store_atr(self, df):
        self.d_in_atr = self.__get_atr(df)
    #------------------------
    def __get_atr(self, df):
        l_atr = dir(df)
        d_atr = {}
        for atr in l_atr:
            val = getattr(df, atr)
            d_atr[atr] = val

        return d_atr
    #------------------------
    def add_atr(self, df):
        d_ou_atr = self.__get_atr(df)

        key_in_atr = set(self.d_in_atr.keys())
        key_ou_atr = set(     d_ou_atr.keys())

        key_to_add = key_in_atr.difference(key_ou_atr)

        for key in key_to_add:
            val = self.d_in_atr[key]
            self.log.info('Adding attribute ' + key)
            setattr(df, key, val)

        return df
    #------------------------

