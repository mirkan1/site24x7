import sys
import os
import json
import argparse # use argparse to parse the arguments
from subprocess import call
from time import strftime
from dotenv import load_dotenv
from site24x7_plugin_helper.connector.database_client import DatabaseClient

# setting up the argument parser
parser = argparse.ArgumentParser(description='This is a helper script for Site24x7 plugins.')
parser.add_argument('--plugin',
    help='Unique plugin name that will be shown in site24x7 plugin list',
    required=True,
    type=str)
parser.add_argument('--query',
    help='MSSQL query to be executed',
    required=True,
    type=str)
parser.add_argument('--version',
    help="Which step of the plugin is this? (1, 2, 3, etc.)",
    required=False,
    type=int)
parser.add_argument('--server', help='Most of the time an IPv4 or IPv6', type=str)
parser.add_argument('--database', help='Database name belongs to the server', type=str)
parser.add_argument('--env', help='Path to .env file', default=None, type=str)
parser.add_argument('--username', help='Username for database connection', default=None, type=str)
parser.add_argument('--password', help='Password for database connection', default=None, type=str)
parser.add_argument('--db_driver', help="MSSQL driver's location",
    default="/usr/local/lib/python3.6/dist-packages/pyodbc/drivers/pyodbc.so", type=str)

# load the environment variables from file location if exists
if parser.parse_args().env:
    load_dotenv(dotenv_path=parser.parse_args().env)
# DEBUG
PASS_DATABASE_CONNECTION = True

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
    query = parser.parse_args().query or os.environ.get("QUERY")
    server = parser.parse_args().server or os.environ.get("SERVER")
    database = parser.parse_args().database or os.environ.get("DATABASE")
    username = parser.parse_args().username or os.environ.get("DATABASE_USERNAME")
    password = parser.parse_args().password or os.environ.get("DATABASE_PASSWORD")
    driver_location = parser.parse_args().password or os.environ.get("DATABASE_DRIVER_PATH")
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
    }
    if not PASS_DATABASE_CONNECTION:
        client = DatabaseClient(server, database, username, password, driver_location)
        cursor = client.cursor
        print("connnected")
        # existing query that returns all rows from the table for caching
        # 'EXEC [Ultramerchant].dbo.pr_membership_credit_billing_stats_24x7_monitor_sel'
        rows = client.fetchall(query)
        for i in enumerate(rows):
            key = rows[i][1]
            value = rows[i][2]
            cache[key] = value
    ## validate data before saving to cache
    # ww = connector.validatePluginData(cache)
    # save cache to file as this_plugin_name 
    cache_file_name = "/tmp/" + this_plugin_name.replace("/", "") + ".cache"
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
    author="Renas Mirkan Kilic",
    plugin_version="1",
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
    CLIENT.__setitem__("thisPluginName", "{this_plugin_name}")
    return data

if __name__ == "__main__":
    result = metric_collector()
    print(CLIENT.dumps(result))
""")
