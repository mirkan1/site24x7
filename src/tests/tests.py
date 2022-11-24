from site24x7_plugin_helper.connector.redis_client import RedisClient
from site24x7_plugin_helper.connector.database_client import DatabaseClient
from site24x7_plugin_helper.connector.cache_client import CacheClient
from site24x7_plugin_helper.connector.request_client import RequestClient
from site24x7_plugin_helper.utils.util import *
from time import sleep


def testRedisClient():
    class RedisInst(RedisClient):
        def clientSize(self):
            return 2
    RedisInst = RedisInst(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
    RedisInst.redis.set('test', 'test', ex=6, nx=True, xx=False)
    RedisInst.redis.execute_command('SET test_column test_value EX 5 NX')
    assert RedisInst.redis.get('test_column') == 'test_value'
    assert RedisInst.redis.get('test') == 'test'
    assert RedisInst.clientSize() == 2
    sleep(6)
    try:
        RedisInst.redis.get('test_column')
    except KeyError:
        assert 1 == 1
    try:
        RedisInst.redis.get('test')
    except KeyError:
        assert 1 == 1
    print("Redis client... Passed")


# def testDatabaseClient():
#     class DatabaseInst(DatabaseClient):
#         def databaseType(self):
#             return "msSQL"
#     DatabaseInst = DatabaseInst(server='localhost', database='test', username='test', password='password', driverLocation='C:\\Program Files\\Microsoft SQL Server\\110\\Tools\\ODBC\\ODBC.INI')
#     assert DatabaseInst.databaseType() == "msSQL"
#     print("client... Passed")


# def testCacheClient():
#     class CacheInst(CacheClient):
#         pass
#     # create dummy json file
#     expected_output = {'test': 'test'}
#     instance_1 = CacheInst(cacheFileFullPath="/home/kali/Desktop/dummy.json", force=True)
#     instance_1.save(expected_output)
#     instance_2 = CacheInst(cacheFileFullPath="/home/kali/Desktop/dummy.json", force=False)
#     assert instance_2.dict==expected_output
#     print("client... Passed")

# def testRequestClient():

#     client = RequestClient()
#     req = client.get("https://www.google.com", headers={"kaka":"true"})
#     print(req);
#     print(req.status_code);
#     print(req.text);
#     print(req.headers);

if __name__ == "__main__":
    testRedisClient()
    # testDatabaseClient()
    # testCacheClient()
