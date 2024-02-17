# __init__.py

from importlib import resources
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
import yaml
from nodens.update import nodens_fns
import os
from platformdirs import user_config_dir, user_documents_dir, user_log_dir
from pathlib import Path
import logging

global APPNAME
global APPAUTHOR
global CWD

# Logging level
logging.basicConfig(level=logging.DEBUG)

# Some information
__title__ = "nodens-update"
__version__ = "24.2.0"
__author__ = "Khalid Z Rajab"
__author_email__ = "khalid@nodens.eu"
__copyright__ = "Copyright (c) 2024 " + __author__
__license__ = "MIT"

APPNAME = "Update"
APPAUTHOR = "NodeNs"
CWD = os.getcwd() + '/'

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
log_file = user_log_dir(APPNAME, APPAUTHOR)+'/nodens_update.log'
Path(user_log_dir(APPNAME, APPAUTHOR)).mkdir(parents=True, exist_ok=True)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(log_file)

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

logger.info("Log location: {}".format(os.path.realpath(log_file)))

# Read parameters from the config file
def read_yaml(file_path):
    with open(file_path, "r") as yaml_file:
        return yaml.safe_load(yaml_file)
    
# Write parameters to config file
def write_yaml(file_path, data):
    with open(file_path, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False, sort_keys=False)

class config_program:
    def __init__(self):
        ## ~~~~~~~ DEFAULT CONFIGURATION ~~~~~~~ ##
                
        # Sensor config #
        self.SENSOR_ROOT = '807d3abc9ba0'
        self.SENSOR_TARGET = self.SENSOR_ROOT
        self.SENSOR_IP = '10.3.141.1'
        self.SENSOR_PORT = 1883
        self.SENSOR_TOPIC = 'mesh/' + self.SENSOR_ROOT + '/toDevice'

        # Data transmit config #
        self.SCAN_TIME = 60 # Seconds between scans
        self.FULL_DATA_FLAG = 0 # 1 = Capture full-data for diagnostics
        self.FULL_DATA_TIME = 60 # Seconds between full-data captures

        # Radar config #
        self.RADAR_SEND_FLAG = 0 # 1 = Send radar config
        # Note: Sensor located at origin (X,Y) = (0,0). Z-axis is room height. By default, sensor points along Y-axis.
        self.ROOM_X = "-5, 5"
        self.ROOM_Y = "0.25, 9"
        self.ROOM_Z = "0, 2"
        room_x = self.ROOM_X.split(",")
        room_y = self.ROOM_Y.split(",")
        room_z = self.ROOM_Z.split(",")
        # Static monitoring area
        mon_x = [float(room_x[0]) + 0.5, float(room_x[1]) - 0.5]
        mon_y = [0.5, float(room_y[1]) - 0.5]
        mon_z = [0, 2]
        self.MONITOR_X = str(mon_x[0]) + "," + str(mon_x[1])
        self.MONITOR_Y = str(mon_y[0]) + "," + str(mon_y[1])
        self.MONITOR_Z = str(mon_z[0]) + "," + str(mon_z[1])
        self.RADAR_CAL = "0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0"
        # Notes on sensor orientation. 
        # Default: (Yaw,Pitch) = (0,0) which points along the Y-axis.
        # Units: degrees.
        # Yaw: rotation around Z-axis (side-to-side). Clockwise is +ve.
        # Pitch: rotation around X-axis (up-down). Upwards is +ve.
        self.SENSOR_YAW = 0
        self.SENSOR_PITCH = 0
        self.SENSITIVITY = 1
        self.OCC_SENSITIVITY = 1

        # Entry config #
        self.ENTRY_FLAG = 0
        self.ENTRY_X = []
        self.ENTRY_Y = []

        # In future: replace resources.read_text with: files(package).joinpath(resource).read_text(encoding=encoding)
        print("CWD: {}. APPAUTHOR: {}. platformdir: {}".format(CWD, APPAUTHOR, user_config_dir(APPNAME, APPAUTHOR)))
        if os.path.exists(user_config_dir(APPNAME, APPAUTHOR)+"/config-update.yaml"):
            yaml_file = user_config_dir(APPNAME, APPAUTHOR)+"/config-update.yaml"
            self.read_config(yaml_file)
            
            logging.info("Config file found: {}".format(yaml_file))
        elif os.path.exists(CWD+"config-update.yaml"):
            yaml_file = CWD+"config-update.yaml"
            self.read_config(yaml_file)

            logging.info("Config file found: {}".format(yaml_file))          
        else:
            yaml_file = user_config_dir(APPNAME, APPAUTHOR)+"/config-update.yaml"
            logging.warning("NO CONFIG FILE FOUND. DEFAULT PARAMETERS USED. CONFIG SAVED: {}".format(yaml_file))

            # Write new yaml config file
            Path(user_config_dir(APPNAME, APPAUTHOR)).mkdir(parents=True, exist_ok=True)
            make_config = {
                "SENSOR": {
                    "ROOT_ID": self.SENSOR_ROOT,
                    "SENSOR_ID": self.SENSOR_TARGET,
                    "SENSOR_IP": self.SENSOR_IP,
                    "SENSOR_PORT": self.SENSOR_PORT,
                },
                "DATA_TRANSMIT": {
                    "TRANSMIT_TIME": self.SCAN_TIME,
                    "FULL_DATA_FLAG": self.FULL_DATA_FLAG,
                    "FULL_DATA_TIME": self.FULL_DATA_TIME,
                },
                "RADAR": {
                    "RADAR_SEND_FLAG": self.RADAR_SEND_FLAG,
                    "ROOM_X": self.ROOM_X,
                    "ROOM_Y": self.ROOM_Y,
                    "ROOM_Z": self.ROOM_Z,
                    "MONITOR_X": self.MONITOR_X,
                    "MONITOR_Y": self.MONITOR_Y,
                    "MONITOR_Z": self.MONITOR_Z,
                    "RADAR_CAL": self.RADAR_CAL,
                    "SENSOR_YAW": self.SENSOR_YAW,
                    "SENSOR_PITCH": self.SENSOR_PITCH,
                    "SENSITIVITY": self.SENSITIVITY,
                    "OCC_SENSITIVITY": self.OCC_SENSITIVITY,
                },
                "ENTRYWAYS": {
                    "ENTRY_FLAG": self.ENTRY_FLAG,
                    "ENTRY_X": self.ENTRY_X,
                    "ENTRY_Y": self.ENTRY_Y,
                }
            }

            # Write config to yaml
            write_yaml(yaml_file, make_config)

    def read_config(self, file):
        # Read configs from yaml file
        _cfg = read_yaml(file)

        # SENSOR config #
        self.SENSOR_ROOT = str(_cfg["SENSOR"]["ROOT_ID"])
        self.SENSOR_TARGET = str(_cfg["SENSOR"]["SENSOR_ID"])
        self.SENSOR_IP = str(_cfg["SENSOR"]["SENSOR_IP"])
        self.SENSOR_PORT = int(_cfg["SENSOR"]["SENSOR_PORT"])
        self.SENSOR_TOPIC = 'mesh/' + self.SENSOR_ROOT + '/toDevice'

        # Data transmit config #
        self.SCAN_TIME = float(_cfg["DATA_TRANSMIT"]["TRANSMIT_TIME"])
        self.FULL_DATA_FLAG = int(_cfg["DATA_TRANSMIT"]["FULL_DATA_FLAG"])
        self.FULL_DATA_TIME = float(_cfg["DATA_TRANSMIT"]["FULL_DATA_TIME"])

        # Radar config #
        self.RADAR_SEND_FLAG = int(_cfg["RADAR"]["RADAR_SEND_FLAG"])
        self.ROOM_X = (_cfg["RADAR"]["ROOM_X"])
        self.ROOM_Y = (_cfg["RADAR"]["ROOM_Y"])
        self.ROOM_Z = (_cfg["RADAR"]["ROOM_Z"])
        self.MONITOR_X = (_cfg["RADAR"]["MONITOR_X"])
        self.MONITOR_Y = (_cfg["RADAR"]["MONITOR_Y"])
        self.MONITOR_Z = (_cfg["RADAR"]["MONITOR_Z"])
        if "RADAR_CAL" in _cfg["RADAR"]:
            self.RADAR_CAL = str(_cfg["RADAR"]["RADAR_CAL"])
        self.SENSOR_YAW = float(_cfg["RADAR"]["SENSOR_YAW"])
        self.SENSOR_PITCH = float(_cfg["RADAR"]["SENSOR_PITCH"])
        self.SENSITIVITY = (_cfg["RADAR"]["SENSITIVITY"])
        self.OCC_SENSITIVITY = (_cfg["RADAR"]["OCC_SENSITIVITY"])

        # Entryways config#
        if "ENTRYWAYS" in _cfg:
            self.ENTRY_FLAG = int(_cfg["ENTRYWAYS"]["ENTRY_FLAG"])
            self.ENTRY_X = (_cfg["ENTRYWAYS"]["ENTRY_X"])
            self.ENTRY_Y = (_cfg["ENTRYWAYS"]["ENTRY_Y"])

cp = config_program()

# Initialisations #
si = nodens_fns.si                  # Sensor info
ew = nodens_fns.EntryWays()         # Entryway monitors
oh = nodens_fns.OccupantHist()      # Occupant history
sm = nodens_fns.SensorMesh()        # Sensor Mesh state
