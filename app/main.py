from flask import Flask, redirect, render_template, request

from utils.types import PhysicalDevice
from utils.api import *

app = Flask(__name__)
data = get_physical_devices()
debug_enabled = False


@app.route('/', methods=['GET', 'POST'])
def index():
    physicalDevices = []
    for i in range(len(data)):
        physicalDevices.append(PhysicalDevice(
            uid=data[i]['uid'],
            name=data[i]['name'],
            source_name=data[i]['source_name'],
            last_seen=data[i]['last_seen']
        ))
    return render_template('physical_device_table.html', title='Physical Devices', physicalDevices=physicalDevices)

@app.route('/physical-device/<int:uid>', methods=['GET', 'POST'])
def physical_device_form(uid):
    data = get_physical_device(uid)
    properties = format_json_property(data, 'properties')
    mappings = get_device_mappings(uid)
    mapping_formatted = format_json(mappings)
    deviceName = data['name']
    deviceLocation = data['location']
    deviceLastSeen = data['last_seen']
    title = 'Physical Device ' + str(uid) + ' - ' + str(deviceName)
    if request.method == 'POST':
        if request.form['create_mapping'] == 'Create Mapping':
            newLogicalDevice = create_logical_device(data)
            result = insert_device_mapping(uid, newLogicalDevice)
            return redirect('/physical-device/'+str(uid))
    elif request.method == 'GET':
        pass
    return render_template('physical_device_form.html',
                           title=title,
                           deviceLocation=deviceLocation,
                           deviceLastSeen=deviceLastSeen,
                           properties=properties,
                           mappings=mapping_formatted)

if __name__ == '__main__':
    app.run(debug=debug_enabled)