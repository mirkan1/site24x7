import os
import json
import argparse # use argparse to parse the arguments
from subprocess import call
from time import strftime
from dotenv import load_dotenv
from site24x7_plugin_helper.connector.database_client import DatabaseClient
from site24x7_plugin_helper.connector.redis_client import RedisClient
from site24x7_plugin_helper.connector.request_client import RequestClient
from site24x7_plugin_helper.utils.util import validatePluginData

# setting up the argument parser
parser = argparse.ArgumentParser(description='This is a helper script for Site24x7 plugins.')
parser.add_argument('--plugin',
    help='Unique plugin name that will be shown in site24x7 plugin list',
    required=True,
    type=str)
parser.add_argument('--query',
    help='MSSQL query to be executed',
    required=False,
    type=str)
parser.add_argument('--version',
    help="Which step of the plugin is this? (1, 2, 3, etc.)",
    required=False,
    type=int)
parser.add_argument('--server', help='Most of the time an IPv4 or IPv6', type=str)
##
parser.add_argument('--connection_type', help='Connection types: redis, request, database', required=True, type=str)
parser.add_argument('--database', help='Database name that belongs to the server', default=None, type=str)
parser.add_argument('--redis', help='Redis connection', default=None, type=str)
parser.add_argument('--request', help='Http(s) connection', default=None, type=str)
##
parser.add_argument('--env', help='Path to .env file', default=None, type=str)
parser.add_argument('--username', help='Username for connection_type', default=None, type=str)
parser.add_argument('--password', help='Password for connection_type', default=None, type=str)
parser.add_argument('--database_driver_path', help="database driver's location if exists", default=None, type=str)
# default="/usr/local/lib/python3.6/dist-packages/pyodbc/drivers/pyodbc.so", type=str)

# load the environment variables from file location if exists
if parser.parse_args().env:
    load_dotenv(dotenv_path=parser.parse_args().env)

def special_strftime():
    ''' expected output: Aug 22nd, 2022 '''
    dic = {
        '01':'st,','21':'st,','31':'st,',
        '02':'nd,','22':'nd,',
        '03':'rd,','23':'rd,'
    }
    x = strftime('%b %d')
    year = strftime(' %Y')
    return x + dic.get(x[-2:], 'th,') + year

if __name__ == "__main__":
    this_plugin_name = parser.parse_args().plugin or os.environ.get("THIS_PLUGIN_NAME")
    this_plugin_name = this_plugin_name.replace("/", "")
    query = parser.parse_args().query or os.environ.get("QUERY")
    version = parser.parse_args().version or os.environ.get("VERSION")
    server = parser.parse_args().server or os.environ.get("SERVER")
    username = parser.parse_args().username or os.environ.get("USERNAME")
    password = parser.parse_args().password or os.environ.get("PASSWORD")
    connection_type = parser.parse_args().connection_type or os.environ.get("CONNECTION_TYPE")
    database = None
    redis = None
    http = None
    if connection_type == "database":
        database = parser.parse_args().database or os.environ.get("DATABASE")
        database_driver_path = parser.parse_args().database_driver_path or os.environ.get("DATABASE_DRIVER_PATH")
    elif connection_type == "redis":
        redis = parser.parse_args().redis or os.environ.get("REDIS")
    elif connection_type == "request":
        request = parser.parse_args().request or os.environ.get("REQUEST")
    if version is None:
        version = "1"
    if server is None:
        raise Exception("Server is not defined")
    if database is None:
        raise Exception("Database is not defined")
    if username is None:
        raise Exception("Username is not defined")
    if password is None:
        raise Exception("Password is not defined")
    cache = {
        "database":database,
        "query":query,
        "this_plugin_name":this_plugin_name,
        "version":version,
    }
    if database:
        # create a DatabaseClient instance
        client = DatabaseClient(server, database, username, password, database_driver_path)
        cursor = client.cursor
        print("connnected")
        # existing query that returns all rows from the table for caching
        rows = client.fetchall(query)
        for i in enumerate(rows):
            key = rows[i][1]
            value = rows[i][2]
            cache[key] = value
    elif redis:
        client = RedisClient(server, database, username, password)
        print("connnected")
    elif request:
        client = RequestClient(server, database, username, password)
        print("connnected")
    ## validate data before saving to cache
    if not validatePluginData(cache):
        raise Exception("Data validation failed")
    # save cache to file as this_plugin_name
    cache_file_name = "/tmp/" + this_plugin_name + ".cache"
    open(cache_file_name, 'w', encoding='utf8').write(
        json.dumps(cache, indent=4)
    )
    print(json.dumps(cache, indent=4, sort_keys=True))

    SITE24X7_LOCATION = "/opt/site24x7/monagent/plugins"
    folder_destination = os.path.join(SITE24X7_LOCATION, this_plugin_name)
    file_destination = os.path.join(folder_destination, this_plugin_name + ".py")
    print("folder_destination: " + folder_destination)
    print("file_destination: " + file_destination)
    # create a folder if not exists
    if not os.path.exists(folder_destination):
        call(f"mkdir {folder_destination}", shell=True)

    # create a python file if not exists
    if not os.path.isfile(file_destination):
        call(f"touch {file_destination}", shell=True)
        open(file_destination, 'w', encoding="utf8").write(f"""#!/usr/bin/env python3
'''
   this file is generated using Jenkins, and it is a cron-task
'''
from site24x7_plugin_helper.connector.cache_client import CacheClient

CLIENT = CacheClient(
    "{cache_file_name}",
    date_created="{special_strftime()}",
    ignored_list=["query", "this_plugin_name"]
)

def metric_collector():
    data = {{}}
    try:
        CLIENT.set_metric_types()
        data.update(CLIENT.dict)
    except Exception as err:
        data["error"] = str(err)
    return data

if __name__ == "__main__":
    result = metric_collector()
    print(CLIENT.dumps(result))
""")
    else:
        # replace the file with new version
        pass
