#!flask/bin/python
from flask import Flask, request, jsonify
import subprocess
import re
from sets import Set
import json
import os.path

Implements = ['VolumeDriver']
IgnoreHeaders = True
commonMountPoint = '/imaginary/mount/point'

Volumes = {
	'vol-1' : {'DeviceId' : 'null',
		   'PartitionName' : 'null',
                   'MntPt' : commonMountPoint, 
		   'Hosts' : ['id1', 'id2']},
	'vol-2' : {'DeviceId' : 'null',
		   'PartitionName' : 'null',
                   'MntPt' : commonMountPoint, 
		   'Hosts' : ['id1', 'id2']}
}

app = Flask(__name__)

@app.route('/Plugin.Activate', methods=['POST'])
def plugin_activate():
	return jsonify({'Implements': ['VolumeDriver']})

@app.route('/VolumeDriver.Create', methods=['POST'])
def volume_create():
	err = ''
	inputData = request.get_json(force=IgnoreHeaders)
	try:
		volumeName = inputData['Name']
		volumeCreateOptions = inputData['Opts']
		print("Volume Name: {0}".format(volumeName)) 
		print("Volume Create Options: {0}".format(volumeCreateOptions))
		if Volumes.has_key(volumeName):
			raise Exception("Volume exists with name:" + volumeName)
				
		Volumes[volumeName] = {'DeviceId' : volumeCreateOptions['device_id'], 'MntPt' : '', 'Hosts' : []}
		
		print("Volume created successfully: ", Volumes[volumeName])
	except Exception as e:
		err = str(e)
	finally:
		output = {'Err':err}
		return jsonify(output)

@app.route('/VolumeDriver.Remove', methods=['POST'])
def volume_remove():
	err = ''
	try:
		inputData = request.get_json(force=IgnoreHeaders)
		volumeName = inputData['Name']
		print "Volume Name:", volumeName
		Volumes.pop(volumeName)		
	except Exception as e:
		err = str(e)
	finally:	
		output = {'Err':err}
		return jsonify(output)

@app.route('/VolumeDriver.Mount', methods=['POST'])
def volume_mount():		
	inputData = request.get_json(force=IgnoreHeaders)	
	volumeName = inputData['Name']
	mountId = inputData['ID']
	print "Volume Name:", Volumes[volumeName]
	print "Mount Id:", mountId		
	Volumes[volumeName]['MntPt'] = commonMountPoint
	Volumes[volumeName]['Hosts'].append(mountId) 		
	output = {'Mountpoint':commonMountPoint, 'Err':''}
	return jsonify(output)

@app.route('/VolumeDriver.Path', methods=['POST'])
def volume_path():
	inputData = request.get_json(force=IgnoreHeaders)	
	mountPoint = commonMountPoint
	err = ''
	if inputData:
		volumeName = inputData['Name']
		if volumeName:
			print "Volume Name:", volumeName			
			mountPoint = Volumes[volumeName]['MntPt']
		else:
			err = 'Volume not found'
	else:
		err = 'No input data'
	# refactor
	output = {'Mountpoint':commonMountPoint, 'Err':err}
	return jsonify(output)

@app.route('/VolumeDriver.Unmount', methods=['POST'])
def volume_unmount():
	inputData = request.get_json(force=IgnoreHeaders)
	volumeName = inputData['Name']
	mountId = inputData['ID']
	print "Volume Name:", volumeName
	print "Mount Id:", mountId
	Volumes[volumeName]['Hosts'].remove(mountId)
	Volumes[volumeName]['MntPt'] = ''		
	output = {'Err':''}
	return jsonify(output)

@app.route('/VolumeDriver.List', methods=['POST'])
def volume_list():
	volumeList = []
	for volumeName in Volumes.keys():
		volumeList.append({'Name' : volumeName, 'Mountpoint' : Volumes[volumeName]['MntPt']})
	print "No of volumes found:", len(volumeList)
	output = {'Volumes' : volumeList, 'Err':''}
	return jsonify(output)

@app.route('/VolumeDriver.Get', methods=['POST'])
def volume_get():
	inputData = request.get_json(force=IgnoreHeaders)	
	volumeDetails = {}
	if inputData:
		volumeName = inputData['Name']
		print "Volume Name:", volumeName		
		volumeDetails = {'Name' : volumeName, 'Mountpoint' : Volumes[volumeName]['MntPt'], 'Status' : {}
	output = {'Volume' : volumeDetails, 'Err' : ''}
	return jsonify(output)	

@app.route('/VolumeDriver.Capabilities', methods=['POST'])
def volume_capabilities():
	output = {"Capabilities" : {"Scope" : "Global"}}
	return jsonify(output)

if __name__ == '__main__':	
	print(Volumes)
	app.run(host='0.0.0.0', debug=True)
