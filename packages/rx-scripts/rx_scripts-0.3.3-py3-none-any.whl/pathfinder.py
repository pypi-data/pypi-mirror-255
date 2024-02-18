import utils_noroot as utnr
import os
import json
import glob

#--------------------------------
class pathfinder:
    l_json = []
    log=utnr.getLogger(__name__)
    jsondir= 'json/paths'
    use_remote = False
    #--------------------------------
    @classmethod
    def add_json(self, jsonpath):
        utnr.check_file(jsonpath)
        self.l_json.append(jsonpath)
    #--------------------------------
    @classmethod
    def pick_json(self):
        for jsonpath in glob.glob(self.jsondir + '/*.json'):
            self.log.info('Adding ' + jsonpath)
            self.l_json.append(jsonpath)
    #--------------------------------
    def __init__(self):
        self.__initialized = False
    #--------------------------------
    def __initialize(self):
        if self.__initialized:
            return

        self.__initialized = True
    #--------------------------------
    def __find_remote(self, local_path):
        for jsonpath in self.l_json:
            d_path = json.load(open(jsonpath))
            try:
                remote_path = d_path[local_path]
                return remote_path
            except:
                pass

        return None
    #--------------------------------
    def get_path(self, local_path):
        self.__initialize()

        if not self.use_remote and os.path.isfile(local_path):
            self.log.info('Path {} found locally'.format(local_path))
            return local_path

        remote_path = self.__find_remote(local_path)

        if remote_path is None:
            self.log.error('Missing remote path for missing local path ' +  local_path)
            raise

        self.log.info('Using remote path {}'.format(remote_path))

        return remote_path
#--------------------------------
def get_path(localpath):
    obj  = pathfinder()
    path = obj.get_path(localpath)

    return path
#--------------------------------

