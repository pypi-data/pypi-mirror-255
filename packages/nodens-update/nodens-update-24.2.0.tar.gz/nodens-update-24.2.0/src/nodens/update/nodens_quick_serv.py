#!/usr/bin/python3
#print('nodens step0')

# Copyright NodeNs Medical Ltd. Author: Khalid Rajab, khalid@nodens.eu
# Captures multi-topic sensor MQTT data and publishes to GCP

# TODO: Command API
# TODO: Separate API script

import os
from datetime import datetime as dt
from os.path import dirname, join as pjoin
import numpy as np
import paho.mqtt.client as mqtt
import json
import base64
from pathlib import Path
import logging
import csv
import nodens.update as nodens
from nodens.update import nodens_fns as ndns_fns
from nodens.update import nodens_mesh as ndns_mesh


global heartbeat


######## ~~~~~~~~~~~~~~~~~~~~~~ ###############


# MQTT Message callback function - quick version without processing#
def on_message_quick(client, userdata, msg):

    global heartbeat

    #getting data from mqtt
    mqttDataN = (msg.payload)
    mqttData = json.loads(mqttDataN)

    
    if 'addr' in mqttData:
        # try:
        sen_idx = nodens.si.check(mqttData)

        # Check if command is received
        if mqttData['data'][0:3] == "CMD":
            logging.debug("Command verified: {}".format(mqttData['data']))
        else:
            # Parse data
            data = base64.b64decode(mqttData['data'])
            str_data = str(data[0])
            for i in range(7):
                str_data = str_data + str(data[i+1])
            # Check if full data packet received
            if str_data == '21436587':
                pass
            # Otherwise process occupancy info
            else:
                if mqttData['type'] == 'bytes':

                    if 'Sensor Information' in mqttData:
                        logging.debug("\nSensor information: {} for Device: {}\n". format(mqttData['Sensor Information'], mqttData['addr']))

                        # Check for sensor version
                        temp = mqttData['Sensor Information']
                        
                        if temp[0:7] == 'VERSION':
                            ndns_fns.sv.parse(temp[9:])

                        elif temp[0:6] == 'CONFIG':
                            ndns_fns.rcp.receive_config(temp[8:])

                        elif temp[0:3] == 'MSG':
                            ndns_mesh.MESH.status.receive_msg(temp, mqttData['timestamp'])
                            ndns_mesh.MESH.status.receive_info(temp, mqttData['timestamp'])
                            if ndns_mesh.MESH.status.last_msg.find("NEW CONFIG!") >= 0:
                                msg = ndns_mesh.MESH.status.last_msg
                                i0 = msg.find("X=")
                                i1 = msg[i0:].find(",")
                                i2 = msg[i0:].find(")")

                                nodens.rcp.ROOM_X_MIN = (msg[i0+3:i0+i1])
                                nodens.rcp.ROOM_X_MAX = (msg[i0+i1+1:i0+i2])

                                i0 = (msg.find("Y="))
                                i1 = (msg[i0:].find(","))
                                i2 = msg[i0:].find(")")

                                nodens.cp.ROOM_Y_MIN = (msg[i0+3:i0+i1])
                                nodens.cp.ROOM_Y_MAX = (msg[i0+i1+1:i0+i2])

                        else:
                            ndns_mesh.MESH.status.receive_info(temp, mqttData['timestamp'])
                
                elif mqttData['type'] == 'heartbeat':
                    heartbeat += "."
                    heartbeat = "\r" + heartbeat
                    #print(heartbeat, end='')
                else:
                    logging.warning("Another type: {}".format(mqttData))

    

