import json
from .models.model import ClientModel

class CacheClient(ClientModel):
    '''cache client is a client model that is used to store data in a cache file'''
    def __init__(self, cache_file_path, *args, force=False, **kwargs):
        self.cache_file_path = cache_file_path
        try:
            self.dict = self.loads()
        except FileNotFoundError as err:
            if not force:
                raise Exception("Cache file not found") from err
            else:
                self.save()
                self.dict = self.loads()
        super().__init__(self.dict, *args, **kwargs)

    def loads(self, path=None):
        '''loads the data from the cache file'''
        if path is None:
            path = self.cache_file_path
        return json.loads(open(path, encoding='utf8').read())

    def save(self, data=None):
        '''save the data to the cache file'''
        if data is None:
            data = self.dict
        open(self.cache_file_path, 'w', encoding='utf8').write(
            self.dumps(data)
        )

    def dumps(self, data:dict, indent=4, sort_keys=False):
        '''dumps the data and return its pretty print version'''
        return json.dumps(data, indent=indent, sort_keys=sort_keys)
