import pymongo
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def change_id_to_mongo_id(data):
    data['_id'] = data['id']
    del data['id']
    return data

def change_mongo_id_to_id(data):
    data['id'] = data['_id']
    del data['_id']
    return data


def persist_value(table, key, value):
    connection_string = config['db']['connection_string']  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client['caas'][table]
    value = change_id_to_mongo_id(value)
    client_table.replace_one({'_id':key},value,upsert=True)
    value = change_mongo_id_to_id(value)
    client.close()

def get_table_values(table, key):
    connection_string = config['db']['connection_string']  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client['caas'][table]
    data = client_table.find_one({'_id':key})
    data = change_mongo_id_to_id(data)
    client.close()
    return data

def delete_table_values(table,key):
    connection_string = config['db']['connection_string']  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client['caas'][table]
    client_table.delete_one({'_id':key})
    client.close()

def get_all_values_from_interim_jobs(table):
    connection_string = config['db']['connection_string']  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client['caas'][table]
    data = client_table.find({})
    all_ids = []
    for job in data:
        all_ids.append(job['_id'])
    return all_ids