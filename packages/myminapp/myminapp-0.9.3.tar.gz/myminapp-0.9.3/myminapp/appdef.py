# -*- coding: utf-8 -*-
"""
myminapp

This file is used for definition and configuration within myminapp.

For more information see myminapp manual.
"""

import os

# -----------------------------------------------------------------------
# HOME
# -----------------------------------------------------------------------
# HOME is the myminapp application directory, i.e. the location where
# this file is located, for example 'home/u1/myminapp'.
#
# The directory is automatically determined here and set as HOME. Please
# do not change this setting (and don't use 'os.getcwd()'):
#
# HOME = os.path.dirname(os.path.abspath(__file__))
# -----------------------------------------------------------------------
HOME = os.path.dirname(os.path.abspath(__file__))
print(f"myminapp.appdef HOME     : '{HOME}'")

# -----------------------------------------------------------------------
# DATA_HOME
# -----------------------------------------------------------------------
# DATA_HOME is the directory where all application data is located,
# for example under 'home/u1/myminapp/data'.
# -----------------------------------------------------------------------
DATA_HOME = HOME + "/data"
print(f"myminapp.appdef DATA_HOME: '{DATA_HOME}'")

# -----------------------------------------------------------------------
# LOG_STDOUT, _FILE, _FILE_MAX_BYTES, _FILE_BACKUP_COUNT, _LEVEL
# -----------------------------------------------------------------------
# LOG_STDOUT = True: The logging target is standard out.
#
# LOG_FILE = True: The logging target are files in DATA_HOME/log.
#
# LOG_FILE_MAX_BYTES specifies the maximum log file size in bytes. If
# the size is reached, the file is saved in up to LOG_FILE_BACKUP_COUNT
# backups.
#
# With LOG_LEVEL the following log levels can be specified:
#
# ERROR, WARNING, INFO, DEBUG.
#
# Example with a maximum size of 500 KB, 5 backups and log level INFO:
#
# LOG_STDOUT = False
# LOG_FILE = True
# LOG_FILE_MAX_BYTES = 500*1000
# LOG_FILE_BACKUP_COUNT = 5
# LOG_LEVEL = 'INFO'
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
LOG_STDOUT = True
LOG_FILE = True
LOG_FILE_MAX_BYTES = 500*1000
LOG_FILE_BACKUP_COUNT = 5
LOG_LEVEL = 'INFO'

# -----------------------------------------------------------------------
# LANG
# -----------------------------------------------------------------------
# Language code for message texts and data field labels. Currently are
# supported English (en) and German (de). Example for German:
#
# LANG = 'de'
# -----------------------------------------------------------------------
LANG = 'de'

# -----------------------------------------------------------------------
# FIELD_DEFSETS
# -----------------------------------------------------------------------
# In this section field defintion sets are specified, each respresenting
# a specific data field. These fields are used for data exchange across
# all application layers, as well as for data storage.
#
# See COMMAND_DEFSETS for how the fields are used to specify the input
# and output field structures of the commands.
#
# Add new field definition sets as needed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
FIELD_DEFSETS = {
    "devname": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Name", "desc": "Unique device name / name list"},
        "de": {"label": "Name",
                "desc": "Eindeutiger Device-Name / Namensliste"}
    },
    "devcat": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Category", "desc":"Device category"},
        "de": {"label": "Kategorie", "desc":"Device-Kategorie"}
    },
    "devid": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "ID", "desc": "Unique device ID"},
        "de": {"label": "ID", "desc": "Eindeutige Device-ID"}
    },
    "state": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "State", "desc":"Switching state or another status"},
        "de": {"label": "Zustand", "desc":"Schaltzustand oder anderer Status"}
    },
    "power": {
        "format": "float", "storageformat": "REAL",
        "en": {"label": "Power W", "desc":"Power in watts"},
        "de": {"label": "Leistung W", "desc":"Leistung in Watt"}
    },
    "energy": {
        "format": "float", "storageformat": "REAL",
        "en": {"label": "Energy kWh", "desc":"Energy in kilowatt hours"},
        "de": {"label": "Energie kWh", "desc":"Energie in Kilowattstunden"}
    },
    "tempc": {
        "format": "float", "storageformat": "REAL",
        "en": {"label": "°C", "desc": "Temperature Celsius"},
        "de": {"label": "°C", "desc": "Temperatur Celsius"}
    },
    "name": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Name", "desc": "Variable for various purposes"},
        "de": {"label": "Name", "desc": "Variable für diverse Zwecke"}
    },
    "value": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Value", "desc": "Variable for various purposes"},
        "de": {"label": "Wert", "desc": "Variable für diverse Zwecke"}
    },
    "file": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "File", "desc": "Filename"},
        "de": {"label": "Datei", "desc": "Dateiname"}
    },
    "object": {
        "format": "bytes", "storageformat": "BLOB",
        "en": {"label": "Object", "desc": "Binary object"},
        "de": {"label": "Objekt", "desc": "Binäres Objekt"}
    },
    "type": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Type", "desc": "Variable type"},
        "de": {"label": "Typ", "desc": "Variabler Typ"}
    },
    "from": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "from", "desc": "Timestamp from"},
        "de": {"label": "von", "desc": "Zeitstempel von"}
    },
    "to": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "to", "desc": "Timestamp to"},
        "de": {"label": "bis", "desc": "Zeitstempel bis"}
    },
    "count": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Count", "desc": "Count per group"},
        "de": {"label": "Anzahl", "desc": "Anzahl pro Gruppe"}
    },
    "min": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Min", "desc": "Minimum"},
        "de": {"label": "Min.", "desc": "Minimum"}
    },
    "max": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Max", "desc": "Maximum"},
        "de": {"label": "Max.", "desc": "Maximum"}
    },
    "avg": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Average", "desc": "Average"},
        "de": {"label": "Durchschnitt", "desc": "Durchschnitt"}
    },
    "m5": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "5 minutes", "desc": "5 minutes"},
        "de": {"label": "5 Minuten", "desc": "5 Minuten"}
    },
    "entity": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Entity", "desc": "Data storage entity"},
        "de": {"label": "Entität", "desc": "Datenspeicher-Entität"}
    },
    "fields": {
        "format": "list", "storageformat": "TEXT",
        "en": {"label": "Fields", "desc": "Entity field names"},
        "de": {"label": "Felder", "desc": "Eintitäten-Feldnamen"}
    },
    "entries": {
        "format": "list", "storageformat": "TEXT",
        "en": {"label": "Entries", "desc": "Entity entries"},
        "de": {"label": "Einträge", "desc": "Eintitäten-Einträge"}
    },
    "units": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Units", "desc": "Number of (time-)units"},
        "de": {"label": "Einheiten", "desc": "Anzahl (Zeit-)Einheiten"}
    },
    "charts": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Charts", "desc": "Chart file names"},
        "de": {"label": "Charts", "desc": "Chart-Dateinamen"}
    },
    "info": {
        "format": "str", "storageformat": "TEXT",
        "en": {"label": "Info", "desc":"Additional information"},
        "de": {"label": "Info", "desc":"Zusätzliche Informationen"}
    }
}

# -----------------------------------------------------------------------
# PREFIX_FIELD_DEFSETS
# -----------------------------------------------------------------------
# In this section prefix field defintion sets are specified. These fields
# form a prefix that is automatically placed in front of each entry in
# the data storage entities.
#
# These prefix field definition sets should not be changed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
PREFIX_FIELD_DEFSETS = {
    "id": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "ID", "desc": "Entity primary key"},
        "de": {"label": "ID", "desc": "Entitäts-Primärschlüssel"}
    },
    "t0": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Timestamp", "desc": "Entry timestamp"},
        "de": {"label": "Zeitstempel", "desc": "Eintrags-Zeitstempel"}
    },
    "t1": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Year", "desc": "Entry year"},
        "de": {"label": "Jahr", "desc": "Eintrags-Jahr"}
    },
    "t2": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Month", "desc": "Entry month"},
        "de": {"label": "Monat", "desc": "Eintrags-Monat"}
    },
    "t3": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Day", "desc": "Entry day"},
        "de": {"label": "Tag", "desc": "Eintrags-Tag"}
    },
    "t4": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Hour", "desc": "Entry hour"},
        "de": {"label": "Stunde", "desc": "Eintrags-Stunde"}
    },
    "t5": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Minute", "desc": "Entry minute"},
        "de": {"label": "Minute", "desc": "Eintrags-Minute"}
    },
    "t6": {
        "format": "int", "storageformat": "INTEGER",
        "en": {"label": "Second", "desc": "Entry second"},
        "de": {"label": "Sekunde", "desc": "Eintrags-Sekunde"}
    }
}

# -----------------------------------------------------------------------
# COMMAND_DEFSETS
# -----------------------------------------------------------------------
# In this section command defintion sets are specified, each
# respresenting a class that implements a specific command. These sets
# are used to instantiate and call commands dynamically, taking into
# account the described input and output field structures.
#
# See FIELD_DEFSETS for how the fields are defined.
#
# Add new command definition sets as needed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
COMMAND_DEFSETS = {
    "helloworld": {
        "module": "myminapp.lib.command.helloworld", "class": "HelloWorld",
        "input": ["value"],
        "output": ["value", "info"],
        "storage": True, "logging": False
    },
    "monitorview": {
        "module": "myminapp.lib.command.monitorview", "class": "MonitorView",
        "input": ["value"],
        "output": ["fields", "entries", "info"],
        "storage": False, "logging": False
    },
    "setting": {
        "module": "myminapp.lib.command.setting", "class": "Setting",
        "input": ["devname", "devcat", "value"],
        "output": ["devname", "devcat", "value", "info"],
        "storage": True, "logging": False
    },
    "state": {
        "module": "myminapp.lib.command.state", "class": "State",
        "input": ["devname", "devcat"],
        "output": ["devname", "devcat", "state", "power", "energy", "tempc",
                    "info"],
        "storage": True, "logging": False
    },
    "pscharge": {
        "module": "myminapp.lib.command.pscharge", "class": "PsCharge",
        "input": ["value"],
        "output": ["value", "info"],
        "storage": True, "logging": False
    },
    "psdischarge": {
        "module": "myminapp.lib.command.psdischarge", "class": "PsDischarge",
        "input": ["value"],
        "output": ["value", "file", "object", "info"],
        "storage": True, "logging": False
    },
    "epstats": {
        "module": "myminapp.lib.command.epstats", "class": "EPStats",
        "input": ["type", "entity", "units", "from", "to", "devname",
                   "devcat"],
        "output": ["fields", "entries", "charts", "info"],
        "storage": False, "logging": False
    },
    "selection": {
        "module": "myminapp.lib.command.selection", "class": "Selection",
        "input": ["value"],
        "output": ["fields", "entries", "info"],
        "storage": False, "logging": False
    },
    "textdoc": {
        "module": "myminapp.lib.command.textdoc", "class": "TextDoc",
        "input": [],
        "output": ["info"],
        "storage": False, "logging": False
    }
}

# -----------------------------------------------------------------------
# NAME_DEVICE_MAP
# -----------------------------------------------------------------------
# In this section, unique names are mapped to device-related parameters.
#
# Parameters:
#
#   - devclass: Name of the device class that represents one or more
#                         physical or virtual device(s)
#   - devcat: Device category ('C' camera, 'G' graphic, 'I' inverter,
#                         'M': energy meter, 'P': smart plug, 'R' relay)
#   - devid: Device ID (physical ID, IP address, GPIO pin, or None,
#                         depending on the device class)
#   - devbrand: Device brand (e.g. Shelly, ..., or None,
#                         depending on the device class)
#
# Device IDs must be adjusted as needed.
#
# Add new map entries as needed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
NAME_DEVICE_MAP = {

    "EM": {"devclass": "DTSU", "devcat": "M", "devid": "EM1"},

    "SOLAR": {"devclass": "Fritz", "devcat": "P", "devid": "11657 0000000"},

    "DESKTOP": {"devclass": "Fritz", "devcat": "P", "devid": "11630 0000000"},

    "FRIDGE": {"devclass": "Fritz", "devcat": "P", "devid": "11657 0000000"},

    "TV": {"devclass": "Fritz", "devcat": "P", "devid": "11630 0000000"},

    "WASHER": {"devclass": "Fritz", "devcat": "P", "devid": "11657 0000000"},

    "PS_IN1": {"devclass": "Bosch", "devcat": "P",
                "devid": "hdm:ZigBee:aaaaaaaaaaaaaaaa"},

    "PS_IN2": {"devclass": "Bosch", "devcat": "P",
                "devid": "hdm:ZigBee:aaaaaaaaaaaaaaaa"},

    "PS_IN3": {"devclass": "Bosch", "devcat": "P",
                "devid": "hdm:ZigBee:aaaaaaaaaaaaaaaa"},

    "PS_OUT": {"devclass": "Bosch", "devcat": "P",
                "devid": "hdm:ZigBee:aaaaaaaaaaaaaaaa"},

    "PLUG": {"devclass": "Bosch", "devcat": "P",
              "devid": "hdm:ZigBee:aaaaaaaaaaaaaaaa"},

    "COOLER": {"devclass": "Nohub", "devcat": "P",
                "devid": "192.168.178.37", "devbrand": "Shelly"},

    "HEATER1": {"devclass": "Nohub", "devcat": "P",
                "devid": "192.168.178.28", "devbrand": "Shelly"},

    "HEATER2": {"devclass": "Nohub", "devcat": "P",
                 "devid": "192.168.178.32", "devbrand": "Shelly"},

    "HM300": {"devclass": "OpenDTU", "devcat": "I", "devid": "000000000000"},
    "HM600": {"devclass": "OpenDTU", "devcat": "I", "devid": "000000000000"},

    "RELAY1": {"devclass": "Relay5V", "devcat": "R", "devid": "17"},
    "RELAY2": {"devclass": "Relay5V", "devcat": "R", "devid": "18"},

    "CAM757": {"devclass": "Numcam757", "devcat": "C"},

    "CHART": {"devclass": "Chart", "devcat": "G"}
}

# -----------------------------------------------------------------------
# DEVICE_CLASS_CONNECTION_SPEC
# -----------------------------------------------------------------------
# This section specifies connection parameters for device classes.
#
# Connection types:
#
#   - 'file' File system
#   - 'gpio' GPIO, typically on a SBC like Raspberry Pi
#   - 'hub' Local network via hub, e.g. with a FRITZ!Box
#   - 'nohub' Local network direct, e.g. with a Shelly plug
#   - 'serial' Serial port, e.g. with a Chint Modbus energy meter
#   - 'video' Video port
#
# Parameters depending on the connection type.
#
# Commented-out specifications can be uncommented if the respective
# device is applicable in this installation.
#
# Address, port, and login information must be adjusted as needed.
#
# Add new specifications as needed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
DEVICE_CLASS_CONNECTION_SPEC = {

    #"DTSU": {"conntype": "serial", "address": 68, "port": "/dev/ttyUSB0"},

    #"Fritz": {"conntype": "hub", "address": "192.168.178.1", "port": 49000,
    #           "user": "fritzuser", "password": "aaaaaaaaaa"},

    #"Bosch": {"conntype": "hub", "address": "192.168.178.27",
    #           "certfile": DATA_HOME + "/cert/bosch/br-shccert.pem",
    #           "keyfile": DATA_HOME + "/cert/bosch/br-shckey.pem"},

    #"OpenDTU": {"conntype": "hub", "address": "192.168.178.29",
    #             "user": "admin", "password": "aaaaaaaaaaaa"},

    #"Nohub": {"conntype": "nohub"},

    #"Relay5V": {"conntype": "gpio"},

    #"Numcam757": {"conntype": "video", "port": "/dev/video0"},

    #"Chart": {"conntype": "file"}
}

# -----------------------------------------------------------------------
# COMMAND_PRESETS
# -----------------------------------------------------------------------
# In this section command presets are specified. They are used in the
# web frontend and for scheduling (see COMMAND_SCHEDSETS).
#
# Commented-out presets can be uncommented if the respective command is
# applicable in this installation.
#
# Add new command presets as needed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
COMMAND_PRESETS = {

    "helloworld": {"cmd": "helloworld", "value": "Hello World"},

    "select": {"cmd": "selection", "value": "SELECT * FROM helloworld;"},

    "monitor_1": {"cmd": "monitorview"},

    "monitor_2": {"cmd": "monitorview", "value": 
                  "SELECT * FROM monitor WHERE name LIKE '%hello%';"},

    "textdoc": {"cmd": "textdoc"},

    #"state": {"cmd": "state", "devname": "*"},

    #"state_1": {"cmd": "state", "devname": "EM"},

    #"state_2": {"cmd": "state", "devname": "SOLAR, DESKTOP, FRIDGE, TV, "\
    #            "WASHER"},

    #"state_3": {"cmd": "state", "devname": "PS_IN1, PS_IN2, PS_IN3, "\
    #            "PS_OUT, PLUG"},

    #"state_4": {"cmd": "state", "devname": "COOLER, HEATER1, HEATER2"},

    #"state_5": {"cmd": "state", "devname": "*", "devcat": "I"},

    #"state_6": {"cmd": "state", "devname": "*", "devcat": "R"},

    #"ps_in1_ON": {"cmd": "setting", "devname": "PS_IN1", "value": "ON"},
    #"ps_in1_OFF": {"cmd": "setting", "devname": "PS_IN1", "value": "OFF"},

    #"ps_in2_ON": {"cmd": "setting", "devname": "PS_IN2", "value": "ON"},
    #"ps_in2_OFF": {"cmd": "setting", "devname": "PS_IN2", "value": "OFF"},

    #"ps_in3_ON": {"cmd": "setting", "devname": "PS_IN3", "value": "ON"},
    #"ps_in3_OFF": {"cmd": "setting", "devname": "PS_IN3", "value": "OFF"},

    #"ps_out_ON": {"cmd": "setting", "devname": "PS_OUT", "value": "ON"},
    #"ps_out_OFF": {"cmd": "setting", "devname": "PS_OUT", "value": "OFF"},

    #"plug_ON": {"cmd": "setting", "devname": "PLUG", "value": "ON"},
    #"plug_OFF": {"cmd": "setting", "devname": "PLUG", "value": "OFF"},

    #"cooler_ON": {"cmd": "setting", "devname": "COOLER", "value": "ON"},
    #"cooler_OFF": {"cmd": "setting", "devname": "COOLER", "value": "OFF"},

    #"heater1_ON": {"cmd": "setting", "devname": "HEATER1", "value": "ON"},
    #"heater1_OFF": {"cmd": "setting", "devname": "HEATER1", "value": "OFF"},

    #"heater2_ON": {"cmd": "setting", "devname": "HEATER2", "value": "ON"},
    #"heater2_OFF": {"cmd": "setting", "devname": "HEATER2", "value": "OFF"},

    #"relay1_ON": {"cmd": "setting", "devname": "RELAY1", "value": "ON"},
    #"relay1_OFF": {"cmd": "setting", "devname": "RELAY1", "value": "OFF"},

    #"relay2_ON": {"cmd": "setting", "devname": "RELAY2", "value": "ON"},
    #"relay2_OFF": {"cmd": "setting", "devname": "RELAY2", "value": "OFF"},

    #"epstats_energy": {"cmd": "epstats", "type": "energy",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "*"},

    #"epstats_power": {"cmd": "epstats", "type": "power",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "*"},

    #"epstats_1_energy": {"cmd": "epstats", "type": "energy",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "EM"},

    #"epstats_1_power": {"cmd": "epstats", "type": "power",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "EM"},

    #"epstats_1_powerplus": {"cmd": "epstats", "type": "powerplus",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "EM", "devcat": "M"},

    #"epstats_2_energy": {"cmd": "epstats", "type": "energy",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "SOLAR, DESKTOP, FRIDGE, TV, WASHER"},

    #"epstats_2_power": {"cmd": "epstats", "type": "power",
    #                    "entity": "state",
    #                    "units": 4, "from": "5d", "to": "*",
    #                    "devname": "SOLAR, DESKTOP, FRIDGE, TV, WASHER"},

    #"epstats_3_energy": {"cmd": "epstats", "type": "energy",
    #                    "entity": "state",
    #                    "units": 5, "from": "8h", "to": "*",
    #                    "devname": "PS_IN1, PS_IN2, PS_IN3, PS_OUT, PLUG"},

    #"epstats_3_power": {"cmd": "epstats", "type": "power",
    #                    "entity": "state",
    #                    "units": 5, "from": "8h", "to": "*",
    #                    "devname": "PS_IN1, PS_IN2, PS_IN3, PS_OUT, PLUG"},

    #"epstats_4_energy": {"cmd": "epstats", "type": "energy",
    #                    "entity": "state",
    #                    "units": 3, "from": "202402", "to": "20240205",
    #                    "devname": "COOLER, HEATER1, HEATER2, HM300, HM600"},

    #"epstats_4_power": {"cmd": "epstats", "type": "power",
    #                    "entity": "state",
    #                    "units": 3, "from": "202402", "to": "20240205",
    #                    "devname": "COOLER, HEATER1, HEATER2, HM300, HM600"},

    #"select_1": {"cmd": "selection", "value": "SELECT * FROM state " \
    #             "WHERE id = 1;"},

    #"select_2": {"cmd": "selection", "value": "SELECT t1, t2, devname, " \
    #             "ROUND((max(energy) - min(energy)), 3) AS 'energy' " \
    #              "FROM state GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;"},

    #"pscharge_1": {"cmd": "pscharge", "value": "cmax=50, smin=100"},

    #"psdischarge_1": {"cmd": "psdischarge", "value": "minlevel=25"}
}

# -----------------------------------------------------------------------
# COMMAND_SCHEDSETS
# -----------------------------------------------------------------------
# In this section command schedule sets are specified. These sets refer
# to COMMAND_PRESETS by parameter 'cmdpreset'. If a schedule set is
# specified and appnum is the number of a running application instance,
# that instance performs the referred command at the appropriate times.
#
# Commented-out schedule sets can be uncommented if the respective
# command preset and command are applicable in this installation.
#
# Add new schedule sets as needed.
#
# For more information see myminapp manual.
# -----------------------------------------------------------------------
COMMAND_SCHEDSETS = {

    #"schedule_1": {"cmdpreset": "helloworld", "days": "*",
    #               "intervaldiff": 15, "appnum": 1},

    #"schedule_1a": {"cmdpreset": "helloworld", "days": "*",
    #                "time": "10:00:00-18:30:00",
    #                "intervalunit": 'm', "appnum": 1},

    #"schedule_1b": {"cmdpreset": "helloworld", "days": "1,2,4",
    #                "time": "12:59:01", "appnum": 1},

    #"schedule_1c": {"cmdpreset": "helloworld", "days": "*",
    #                "time": "10:00:01-01:00:00",
    #                "intervaldiff": 10, "appnum": 1},

    #"schedule_11": {"cmdpreset": "state_1", "days": "*",
    #                "intervalunit": 'm', "appnum": 1},

    #"schedule_12": {"cmdpreset": "state_2", "days": "*",
    #                "intervalunit": 'm', "appnum": 1},

    #"schedule_12a": {"cmdpreset": "state_2", "days": "*",
    #                 "time": "10:00:00-03:00:00",
    #                 "intervaldiff": 30, "appnum": 1},

    #"schedule_13": {"cmdpreset": "state_3", "days": "*",
    #                "intervalunit": 'h', "appnum": 1},

    #"schedule_14": {"cmdpreset": "state_4", "days": "*",
    #                "intervalunit": 'd', "appnum": 1},

    #"schedule_15": {"cmdpreset": "pscharge_1", "days": "*",
    #                "time": "08:00:00-18:00:00",
    #                "intervaldiff": 60, "appnum": 1},

    #"schedule_16": {"cmdpreset": "psdischarge_1", "days": "*",
    #                "time": "19:00:00-02:00:00",
    #                "intervaldiff": 1800, "appnum": 1}
}
