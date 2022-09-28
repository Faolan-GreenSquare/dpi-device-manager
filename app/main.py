from flask import Flask, render_template, request
import folium

from utils.types import *
from utils.api import *

app = Flask(__name__)

debug_enabled = True

@app.route('/', methods=['GET', 'POST'])
def index():
    physicalDevices = []
    data = get_physical_devices()
    if data is None:
        return render_template('error_page.html')
    for i in range(len(data)):
        physicalDevices.append(PhysicalDevice(
            uid=data[i]['uid'],
            name=data[i]['name'],
            source_name=data[i]['source_name'],
            last_seen=formatTimeStamp(data[i]['last_seen'])
        ))
    return render_template('physical_device_table.html', title='Physical Devices', physicalDevices=physicalDevices)
    

@app.route('/physical-device/<int:uid>', methods=['GET'])
def physical_device_form(uid):
    pd_data = get_physical_device(uid)
    pd_data['location'] = formatLocationString(pd_data['location'])
    pd_data['last_seen'] = formatTimeStamp(pd_data['last_seen'])
    properties_formatted = format_json(pd_data['properties'])
    sources = get_sources()
    mappings = get_current_mappings(uid)
    notes = get_physical_notes(uid)
    currentDeviceMapping = []
    deviceNotes = []
    if mappings is not None:
        currentDeviceMapping.append(DeviceMapping(
            pd_uid=mappings['pd']['uid'],
            pd_name=mappings['pd']['name'],
            ld_uid=mappings['ld']['uid'],
            ld_name=mappings['ld']['name'],
            start_time=formatTimeStamp(mappings['start_time']),
            end_time=formatTimeStamp(mappings['end_time'])))
    if notes is not None:
        for i in range(len(notes)):
            deviceNotes.append(DeviceNote(
                note=notes[i]['note'],
                uid=notes[i]['uid'],
                ts=formatTimeStamp(notes[i]['ts'])
            )) 
    
    logicalDevices = []
    ld_data = get_logical_devices()
    for i in range(len(ld_data)):
        logicalDevices.append(LogicalDevice(
            uid=ld_data[i]['uid'],
            name=ld_data[i]['name'],
            location=formatLocationString(ld_data[i]['location']),
            last_seen=formatTimeStamp(ld_data[i]['last_seen'])
        ))

    title = 'Physical Device ' + str(uid) + ' - ' + str(pd_data['name'])
    return render_template('physical_device_form.html',
                           title=title,
                           pd_data=pd_data,
                           ld_data=ld_data,
                           sources=sources,
                           properties=properties_formatted,
                           currentMappings=currentDeviceMapping,
                           deviceNotes=deviceNotes)


@app.route('/logical-devices', methods=['GET'])
def logical_device_table():
    logicalDevices = []
    ld_data = get_logical_devices()
    for i in range(len(ld_data)):
        logicalDevices.append(LogicalDevice(
            uid=ld_data[i]['uid'],
            name=ld_data[i]['name'],
            location=formatLocationString(ld_data[i]['location']),
            last_seen=formatTimeStamp(ld_data[i]['last_seen'])
        ))
    return render_template('logical_device_table.html', title='Logical Devices', logicalDevices=logicalDevices)


@app.route('/logical-device/<int:uid>', methods=['GET'])
def logical_device_form(uid):
    ld_data = get_logical_device(uid)
    properties_formatted = format_json(ld_data['properties'])
    deviceName = ld_data['name']
    deviceLocation = formatLocationString(ld_data['location'])
    deviceLastSeen = formatTimeStamp(ld_data['last_seen'])
    title = 'Logical Device ' + str(uid) + ' - ' + str(deviceName)
    mappings = get_device_mappings(uid)
    deviceMappings = []
    if mappings is not None:
        for i in range(len(mappings)):
            deviceMappings.append(DeviceMapping(
                pd_uid=mappings[i]['pd']['uid'],
                pd_name=mappings[i]['pd']['name'],
                ld_uid=mappings[i]['ld']['uid'],
                ld_name=mappings[i]['ld']['name'],
                start_time=formatTimeStamp(mappings[i]['start_time']),
                end_time=formatTimeStamp(mappings[i]['end_time'])))
    
    physicalDevices = []
    data = get_physical_devices()
    for i in range(len(data)):
        physicalDevices.append(PhysicalDevice(
            uid=data[i]['uid'],
            name=data[i]['name'],
            source_name=data[i]['source_name'],
            last_seen=formatTimeStamp(data[i]['last_seen'])
        ))

    return render_template('logical_device_form.html',
                           title=title,
                           ld_data=ld_data,
                           pd_data=physicalDevices,
                           deviceLocation=deviceLocation,
                           deviceLastSeen=deviceLastSeen,
                           properties=properties_formatted,
                           deviceMappings=deviceMappings)


@app.route('/map', methods=['GET'])
def map():
    center_map = folium.Map(location=[-32.2400951991083, 148.6324743348766], title = 'PhysicalDeviceMap', zoom_start=10)
    #folium.Marker([-31.956194913619864, 115.85911692112582], popup="<i>Mt. Hood Meadows</i>", tooltip='click me').add_to(center_map)
    data = get_physical_devices()
    for i in range(len(data)):
        if (data[i]['location'] is not None):
            if(data[i]['source_name'] == "greenbrain"):
                color = 'green'
            elif(data[i]['source_name'] == "ttn"):
                color = 'red'
            else:
                color = 'blue'
            folium.Marker([data[i]['location']['lat'],data[i]['location']['long']],
            popup = data[i]['uid'],
            icon = folium.Icon(color=color, icon='cloud'),
            tooltip = data[i]['name']).add_to(center_map)
            
    return center_map._repr_html_()
    #center_map
    #return render_template('map.html')


@app.route('/create-mapping', methods=['GET'])
def CreateMapping():
    uid = request.args['uid']
    data = get_physical_device(uid)
    newLogicalDevice = create_logical_device(data)
    result = insert_device_mapping(uid, newLogicalDevice)
    return 'Success', 200

@app.route('/create-note/<noteText>/<uid>', methods=['GET'])
def CreateNote(noteText, uid):
    result = insert_note(noteText, uid)
    return 'Success', 200


@app.route('/delete-note/<noteUID>', methods=['DELETE'])
def DeleteNote(noteUID):
    result = delete_note(noteUID)
    return 'Success', 200


@app.route('/edit-note/<noteText>/<uid>', methods=['PATCH'])
def EditNote(noteText, uid):
    result = edit_note(noteText, uid)
    return 'Success', 200


@app.route('/update-physical-device', methods=['GET'])
def UpdatePhysicalDevice():
    if request.args['form_location'] != None and request.args['form_location'] != '' and request.args['form_location'] != 'None':
        location = request.args['form_location'].split(',')
        locationJson = {
            "lat": location[0].replace(' ', ''),
            "long": location[1].replace(' ', ''),
        }
    else:
        locationJson = None

    update_physical_device(request.args['form_uid'], request.args['form_name'], locationJson)
    return 'Success', 200


@app.route('/update-mappings', methods=['GET'])
def UpdateMappings():
    insert_device_mapping(request.args['physicalDevice_mapping'], request.args['logicalDevice_mapping'])
    return 'Success', 200


@app.route('/update-logical-device', methods=['GET'])
def UpdateLogicalDevice():
    if request.args['form_location'] != None and request.args['form_location'] != '' and request.args['form_location'] != 'None':
        location = request.args['form_location'].split(',')
        locationJson = {
            "lat": location[0].replace(' ', ''),
            "long": location[1].replace(' ', ''),
        }
    else:
        locationJson = None

    update_logical_device(request.args['form_uid'], request.args['form_name'], locationJson)
    return 'Success', 200

def formatTimeStamp(unformattedTime):
    if unformattedTime:
        formattedLastSeen = unformattedTime[0:19]
        formattedLastSeen = formattedLastSeen.replace('T', ' ')
        return formattedLastSeen

def formatLocationString(locationJson):
    if locationJson is not None:
        formattedLocation = str(locationJson['lat'])
        formattedLocation += ', '
        formattedLocation += str(locationJson['long'])
    else:
        formattedLocation = None
    return formattedLocation

if __name__ == '__main__':
    app.run(debug=debug_enabled, port='5000', host='0.0.0.0')
    #app.run(debug=True)