import utils_noroot as utnr

from collections import UserDict
from logzero     import logger   as log

#------------------------------------------------
class collector(UserDict):
    """
    Class used to collect information (settings, input paths, etc)
    throughout the code and dump it at the end.
    """
    #-------------------------------
    def __init__(self, allow_repeated=False):
        """
        Parameters
        -----------------
        allow_repeated (bool): If False, will raise exception when key is already in dictionary
        """

        self._allow_repeated = allow_repeated
        super().__init__()
    #-------------------------------
    def __setitem__(self, key, val):
        if key in self.data and not self._allow_repeated:
            old_val = self.data[key]
            log.error('Key already found:')
            log.info(f'{key:<50}{old_val:<50}')
            log.error('Cannot insert:')
            log.info(f'{key:<50}{val:<50}')
            raise ValueError
        elif key in self.data:
            log.debug(f'Overriding key: {key}')

        self.data[key] = val
    #-------------------------------
    def save(self, file_path, sort_keys=False):
        log.info(f'Saving to: {file_path}')
        utnr.dump_json(self.data, file_path, sort_keys=sort_keys)
#------------------------------------------------

