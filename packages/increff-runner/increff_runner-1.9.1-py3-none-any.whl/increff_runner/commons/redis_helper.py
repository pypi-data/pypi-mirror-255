import redis
import json
import configparser
global r

config = configparser.ConfigParser()
config.read('config.ini')

def create_connection():
    global r
    host = config['redis']['host']
    port = config['redis']['port']  # Default Redis SSL port
    username = config['redis']['username']
    password = config['redis']['password']  # Primary or secondary access key
    r = redis.StrictRedis(
        host=host, port=port, password=password, ssl=True, decode_responses=True
    )


def persist_value(table, key, value):
    global r
    create_connection()
    r.hset(table, key, json.dumps(value))
    r.connection_pool.disconnect()


def get_by_key(table, key):
    global r
    create_connection()
    value = r.get(f"{table}.{key}")
    r.connection_pool.disconnect()
    return json.loads(value)


def get_table_values(table, key):
    global r
    create_connection()
    value = r.hget(table, key)
    r.connection_pool.disconnect()
    return json.loads(value)

def add_to_set(table, value):
    global r
    create_connection()
    r.sadd(table, value)
    r.connection_pool.disconnect()


def remove_from_set(table, value):
    global r
    create_connection()
    r.srem(table, value)
    r.connection_pool.disconnect()


def get_all_values_from_set(table):
    global r
    create_connection()
    value = r.smembers(table)
    return value


# persist_value('algo_block','1.etl-lake-test',{
#     'app_id':'1',
#     'block-identifier':'etl-lake-test',
#     'repo_creds':{
#         'account_name':'stincreffmsproindev',
#         'file_system_name':'commons',
#         'storage_account_key':'hYeu5xvCGjPi7pCOhwtuvJOcnfpqBBN3QSl1hKMkh+l+WrZUvABZnltS18gf0N7qLLgBoDT53vrq+AStV6MbXA==',
#         'folder_path':'caas-test'
#     },
#     'repo_type':'data_lake',
#     'resource_type':'functions'
# })
