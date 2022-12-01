import redis
from .models.model import ClientModel

class RedisClient(ClientModel):
    ''' redis client is a client model that is used to get and set data from a redis server '''
    def __init__(self, host, port, db, *args, charset="utf-8", decode_responses=True, **kwargs):
        self.host=host
        self.port=port
        self.db=db
        self.charset=charset
        self.decode_responses=decode_responses
        self.redis=redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            charset=self.charset,
            decode_responses=self.decode_responses
        )
        super().__init__(*args, **kwargs)

    def hset(
        self,
        array_name:str,
        key:str,
        value:str
    ):
        ''' Set a key/value pair in a hash '''
        self.redis.hset(array_name, key, value)

    def hgetall(self, array_name:str) -> list:
        ''' Get all the values in a hash '''
        return self.redis.hgetall(array_name)

    def set_dict_using_global_selector(self, global_selector:str, array_name:str, set_item_key:str):
        ''' Set a key/value pair into the main dictionary '''
        array = self.hgetall(array_name)
        for key in array:
            if key.startswith(global_selector):
                self.__setitem__(set_item_key, array[key])
                return
        raise KeyError("Key not found")
