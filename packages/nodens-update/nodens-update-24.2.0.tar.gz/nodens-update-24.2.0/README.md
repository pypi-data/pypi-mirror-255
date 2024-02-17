The purpose of this program - NodeNs Update - is to update a NodeNs sensor configuration via the MQTT gateway. The new configuration will be defined through the file: ```config-gateway.yaml```.

## Change log

v24.2.0. Added custom radar calibrations to the configuration update, using *RADAR_CAL*.

## Installation
NodeNs Update can be installed using pip:
```
pip install nodens.update
```

### Troubleshooting
**Installing PyYaml**. Pip sometimes has trouble installing the PyYaml package. If you experience this, it may be easier to install it manually:
```
pip install pyyaml
```

## Operation
NodeNs Update can be executed directly from the command line as follows:
```
python -m nodens.update
```

It can also be imported as a library into your own scripts:
```import nodens.update```

On execution, as a first step it will search for the configuration file ```config-update.yaml``` to define the MQTT broker and other basic settings. The program will first search for the config file in the User's (your) default config folder, and then in the folder you've executed the program from. If the config file is not found, it will create one based on a default configuration. [Click here for details of the Configuration](##Configuration).

If a Cloud service operation has been specified, the script will also search for relevant access tokens or certificates.

## Configuration
### Location of configuration file 
The program will search for the configuration file ```config-gateway.yaml``` in the following order:

1.  In the user config folder, e.g.
    - Windows: */Users/\<user>/AppData/Local/NodeNs/Gateway/*
    - Unix:  *~/.config/Gateway/*
2.  In the current working folder.
3.  In *<System documents folder>/NodeNs/*
4.  In *<System documents folder>/*
5.  Otherwise, a default config file will be created in the user folder, and the program will print its location. Feel free to edit it as necessary!

### Description of settings

**SENSOR**

*ROOT_ID* : MAC address of the root sensor.
*SENSOR_ID* : MAC address of the sensor to be updated.
*SENSOR_IP* : IP address of the MQTT broker. Default = 10.3.141.1
*SENSOR_PORT* : Port. 1883 : unsecured. 8883: secured (security keys must be provided).

**DATA_TRANSMIT**

*TRANSMIT_TIME* : How often sensor data is sent via Wi-Fi, in seconds. Default = 2.
*FULL_DATA_FLAG* : Flag to capture full-data for diagnostics. Set to 1 to transmit full diagnostics data via Wi-Fi, such as point clouds and micro-Dopplers. Default = 0.
*FULL_DATA_TIME* : Seconds between full-data captures (must be a multiple of TRANSMIT_TIME). Default = 2.

**RADAR**
*RADAR_SEND_FLAG* : Flag to send new radar configuration. Set to 1 to update the radar configuration. Default = 0.
*ROOM_X_MIN* / *ROOM_X_MAX*: Monitoring size of area (room or virtual zone) to scan. -X/+X is to the left/right respectively, in meters, from the point-of-view of the sensor. The origin is at (0,0,0).
*ROOM_Y_MIN* / *ROOM_Y_MAX*: As above. By default, sensor points along Y-axis. +Y is looking forward, from the point-of-view of the sensor. **Y must be +ve**. The origin is at (0,0,0).
*ROOM_Z_MIN* / *ROOM_Z_MAX*: As above. Z-axis is room height. -Z/+Z is to the down/up respectively, in meters, from the point-of-view of the sensor. The origin is at (0,0,0).
