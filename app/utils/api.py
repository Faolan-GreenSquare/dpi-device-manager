import json
import requests
from datetime import datetime

physical_link_all = 'https://staging.farmdecisiontech.net.au/broker/api/physical/devices/?include_properties=false'
physical_link_uid = 'https://staging.farmdecisiontech.net.au/broker/api/physical/devices/'
logical_link_insert = 'https://staging.farmdecisiontech.net.au/broker/api/logical/devices/'
mapping_link_all = 'https://staging.farmdecisiontech.net.au/broker/api/mappings/logical/all/'
mapping_link_current = 'https://staging.farmdecisiontech.net.au/broker/api/mappings/physical/current/'
mapping_link_insert = 'https://staging.farmdecisiontech.net.au/broker/api/mappings/'
headers = {"Authorization": "Bearer bad_token"}

def get_physical_devices():
    response = requests.get(physical_link_all, headers=headers)
    return response.json()

def get_physical_device(uid):
    response = requests.get(physical_link_uid + str(uid), headers=headers)
    return response.json()

def get_device_mappings(uid):
    response = requests.get(mapping_link_current + str(uid), headers=headers)
    return response.json()

def create_logical_device(data):
    timeObject = datetime.now()
    print(timeObject)
    print(timeObject.tzname())

    logicalJson = {
        "uid": 0,
        "name": data['name'],
        "location": data['location'],
        "last_seen": str(timeObject),
        "properties": {}
        }
    response = requests.post(logical_link_insert, json=logicalJson, headers=headers)
    logical_device = response.json()
    return logical_device['uid']

def insert_device_mapping(physicalUid, logicalUid):
    mappingJson = {
        "pd": {
            "uid": physicalUid,
            "source_name": "string",
            "name": "string",
            "location": {
            "lat": 0,
            "long": 0
            },
            "last_seen": "2022-05-18T09:50:01.928Z",
            "source_ids": {},
            "properties": {}
        },
        "ld": {
            "uid": logicalUid,
            "name": "string",
            "location": {
            "lat": 0,
            "long": 0
            },
            "last_seen": "2022-05-18T09:50:01.928Z",
            "properties": {}
        },
        "start_time": "2022-05-18T09:50:01.928Z",
        "end_time": "2022-05-18T09:50:01.928Z"
        }
    response = requests.post(mapping_link_insert, json=mappingJson, headers=headers)
    return response.json()

def format_json(data):
    return (json.dumps(data, indent=4, sort_keys=True))

def format_json_property(data, property):
    return (json.dumps(data[property], indent=4, sort_keys=True))