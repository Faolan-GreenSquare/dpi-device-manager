import json, requests
import os
from datetime import datetime


end_point = os.environ['end_point']
bearer_token = os.environ['bearer_token']

#end_point = 'https://staging.farmdecisiontech.net.au'
#bearer_token = 'bad_token'
    

# Physical Device Links
physical_link_all = end_point + '/broker/api/physical/devices/?include_properties=false'
physical_link_notes = end_point + '/broker/api/physical/devices/notes/'
physical_link_uid = end_point + '/broker/api/physical/devices/'
physical_link_update = end_point + '/broker/api/physical/devices/'

# Logical Device Links
logical_link_all = end_point + '/broker/api/logical/devices/?include_properties=false'
logical_link_uid = end_point + '/broker/api/logical/devices/'
logical_link_insert = end_point + '/broker/api/logical/devices/'
logical_link_update = end_point + '/broker/api/logical/devices/'

# Mapping Device Links
physical_link_unmapped = end_point + '/broker/api/physical/devices/unmapped/'
physical_link_endmapping = end_point + '/broker/api/mappings/physical/end/'
logical_link_endmapping = end_point + '/broker/api/mappings/logical/end/'
mapping_link_all = end_point + '/broker/api/mappings/logical/all/'
mapping_link_current = end_point + '/broker/api/mappings/physical/current/'
mapping_link_insert = end_point + '/broker/api/mappings/'

# Other links
note_link_insert = end_point + '/broker/api/physical/devices/notes/'
delete_note_url = end_point + '/broker/api/physical/devices/notes/'
sources_link_all = end_point + '/broker/api/physical/sources/'

headers = {"Authorization": "Bearer " + bearer_token}

def get_sources():
    response = requests.get(sources_link_all, headers=headers)
    if response.status_code == 200:
        return response.json()    

def get_physical_devices():
    response = requests.get(physical_link_all, headers=headers)
    if response.status_code == 200:
        return response.json()

def get_physical_notes(uid):
    response = requests.get(physical_link_notes + str(uid), headers=headers)
    if response.status_code == 200:
        return response.json()

def get_logical_devices():
    response = requests.get(logical_link_all, headers=headers)
    if response.status_code == 200:
        return response.json()

def get_physical_unmapped():
    response = requests.get(physical_link_unmapped, headers=headers)
    if response.status_code == 200:
        return response.json()

def get_physical_device(uid):
    response = requests.get(physical_link_uid + str(uid), headers=headers)
    if response.status_code == 200:
        return response.json()

def get_logical_device(uid):
    response = requests.get(logical_link_uid + str(uid), headers=headers)
    if response.status_code == 200:
        return response.json()    

def get_device_mappings(uid):
    response = requests.get(mapping_link_all + str(uid), headers=headers)
    if response.status_code == 200:
        return response.json()    

def get_current_mappings(uid):
    response = requests.get(mapping_link_current + str(uid), headers=headers)
    if response.status_code == 200:
        return response.json()    
    
def update_physical_device(uid, name, location):
    device = get_physical_device(uid)
    device['name'] = name
    device['location'] = location
    response = requests.patch(physical_link_update, headers=headers, json=device)
    if response.status_code == 200:
        return response.json()

def update_logical_device(uid, name, location):
    device = get_logical_device(uid)
    device['name'] = name
    device['location'] = location
    response = requests.patch(logical_link_update, headers=headers, json=device)
    if response.status_code == 200:
        return response.json()

def end_logical_mapping(uid):
    url = logical_link_endmapping + uid
    requests.patch(url, headers=headers)

def end_physical_mapping(uid):
    url = physical_link_endmapping + uid
    requests.patch(url, headers=headers)

def create_logical_device(data):
    timeObject = datetime.now()
    logicalJson = {
        "uid": 0,
        "name": data['name'],
        "location": data['location'],
        "last_seen": str(timeObject),
        "properties": data['properties']
        }
    response = requests.post(logical_link_insert, json=logicalJson, headers=headers)
    logical_device = response.json()
    return logical_device['uid']

def delete_note(uid):
    baseUrl = delete_note_url + str(uid)
    response= requests.delete(baseUrl, headers=headers)
    return response.json()


def insert_device_mapping(physicalUid, logicalUid):
    logicalDevice = get_logical_device(logicalUid)
    physicalDevice = get_physical_device(physicalUid)
    timeObject = datetime.now()
    end_physical_mapping(physicalUid)
    mappingJson = {
        "pd": {
            "uid": physicalDevice['uid'],
            "source_name": physicalDevice['source_name'],
            "name": physicalDevice['name'],
            "location": physicalDevice['location'],
            "last_seen": physicalDevice['last_seen'],
            "source_ids": physicalDevice['source_ids'],
            "properties": physicalDevice['properties']
        },
        "ld": {
            "uid": logicalDevice['uid'],
            "name": logicalDevice['name'],
            "location": logicalDevice['location'],
            "last_seen": logicalDevice['last_seen'],
            "properties": logicalDevice['properties']
        },
        "start_time": str(timeObject),
        "end_time": str(timeObject)
    }
    response = requests.post(mapping_link_insert, json=mappingJson, headers=headers)
    return response.json()

def insert_note(noteText, uid):
    noteJson = {
        "note" : noteText
        }
    baseUrl = note_link_insert + uid
    response = requests.post(baseUrl, json=noteJson, headers=headers)
    return response.json()

def edit_note(noteText, uid):
    timeObject = datetime.now()
    noteJson = {
        "uid" : int(uid),
        "ts": str(timeObject),
        "note" : str(noteText)
        }
    baseUrl = note_link_insert
    response = requests.patch(baseUrl, json=noteJson, headers=headers)
    
    return response.json()

def format_json(data):
    return (json.dumps(data, indent=4, sort_keys=True))