# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0103
#pylint: disable=W0719

import json
import requests

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========

PORT1 = 8444
PORT2 = 8443 # Currently not used
TIMEOUT = 5 # Seconds
HEADERS = {"content-type": "application/json", "api-version": "3.3"}
GET_SERVICES_AS_ARRAY = f"https://--address-:{PORT1}/smarthome/services"
PUT_POWER_SWITCH = f"https://--address-:{PORT1}/smarthome/devices/--devid-" \
                   f"/services/PowerSwitch/state"
PUT_POWER_SWITCH_ON = {'@type': "powerSwitchState", 'switchState': "ON"}
PUT_POWER_SWITCH_OFF = {'@type': "powerSwitchState", 'switchState': "OFF"}

class Bosch:

    """
    This device class communicates with a BOSCH Smart Home Controller II
    (SHC II) via HTTPS.

    Requires: pip install requests

    A session is not opened to preserve the statelessness typical of
    REST services.

    Before this class can be used, an API client must be registered at
    BOSCH SHC II, and, due to the mandatory HTTPS, certificate files
    must be created.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Bosch' setup.

        Args:
            None.

        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        self.init_hub_conn()

    # ==============
    # Public methods
    # ==============

    def init_hub_conn(self):
        """Initializes the home automation hub connection.

        Args:
            None.

        Returns:
            None.
        """
        bosch_conn = DEVICE_CLASS_CONNECTION_SPEC.get(self.name)
        if bosch_conn is None:
            raise Exception(self.helper.mtext(504, self.name))
        self.address = bosch_conn.get("address")
        if self.address is None:
            raise Exception(self.helper.mtext(505, 'address', self.name))
        self.certfile = bosch_conn.get("certfile")
        if self.certfile is None:
            raise Exception(self.helper.mtext(505, 'certfile', self.name))
        self.keyfile = bosch_conn.get("keyfile")
        if self.keyfile is None:
            raise Exception(self.helper.mtext(505, 'keyfile', self.name))
        self.cacertfile = bosch_conn.get("cacertfile")
        # ----------------------------------------------------------
        # CA/Server verification is optional here due to complex and
        # error-prone handling of CA certificate chain, server name,
        # etc. If no path to CA certificate is configured, urllib3
        # warnings might be disabled to avoid InsecureRequestWarning
        # ----------------------------------------------------------
        #if self.cacertfile is None:
        #    from urllib3 import disable_warnings
        #    disable_warnings()

    def close(self):
        """Closes resources (formally only here).
        
        Args:
            None.

        Returns:
            None.
        """
        # Nothing to close here

    def get_overall_info(self):
        """Gets information about all home automation devices.
 
        Args:
            None.
    
        Returns:
           list of dict: The information as key value pairs n times.
        """
        url = GET_SERVICES_AS_ARRAY.replace("--address-", self.address)
        response = self.__GET(url)
        return json.loads(response.text)

    def get_info(self, devid:str):
        """Gets information about a specific home automation device.

        Args:
            devid (str): The device ID.
    
        Returns:
            dict: The information as key value pairs.
        """
        # --------------------------------------------------------------
        # Get overall info and get specific information from the result.
        # This is much faster than explicit device requests
        # --------------------------------------------------------------
        data = self.get_overall_info()
        communication = None
        power = None
        energy = None
        state = None
        program = None
        for entity in data:

            entity_devid = entity.get("deviceId")
            if entity_devid != devid:
                continue

            value = entity.get("id")
            if value is not None:

                if value == "CommunicationQuality":
                    communication = entity['state']['quality']

                elif value == "PowerMeter":
                    power = entity['state']['powerConsumption']
                    energy = entity['state']['energyConsumption']

                elif value == "PowerSwitch":
                    state = entity['state']['switchState']

                elif value == "PowerSwitchProgram":
                    program = entity['state']['operationMode']

                else:
                    continue

        result = {}
        result["communication"] = communication
        result["state"] = state
        result["power"] = power
        result["energy"] = energy
        result["program"] = program
        return result

    def set_switch(self, devid:str, state:str):
        """Switches a specific home automation device on or off.

        Args:
            devid (str): The device ID.
            state (str): ON or OFF.
    
        Returns:
           Response: The response.
        """
        data = None
        if state == "ON":
            data = PUT_POWER_SWITCH_ON
        elif state == "OFF":
            data = PUT_POWER_SWITCH_OFF
        else:
            raise Exception(self.helper.mtext(501, state))
        url = PUT_POWER_SWITCH.replace("--address-", self.address)
        url = url.replace("--devid-", devid)
        return self.__PUT(url, data)

    # ===============
    # Private methods
    # ===============

    def __GET(self, url:str):
        """Performs a GET request against a REST API.
        
        Args:
            url (str): The URL string.

        Returns:
            Response: The response.
        """
        # --------------------------------------------------------------
        # CA/Server verification optional due to complex and error-prone
        # handling of CA certificate chain, server name, etc:
        # --------------------------------------------------------------
        verify_option = False
        if self.cacertfile is not None:
            verify_option = self.cacertfile
        # -------
        # Request
        # -------
        response = requests.get(url,
                                headers = HEADERS,
                                timeout = TIMEOUT,
                                cert = (self.certfile,
                                        self.keyfile),
                                verify = verify_option
                                )
        response.raise_for_status()
        return response

    def __PUT(self, url:str, data:dict):
        """Performs a PUT request against a REST API.

        Args:
            url (str): The URL string.
            data (dict): The PUT data.

        Returns:
            Response: The response.
        """
        # --------------------------------------------------------------
        # CA/Server verification optional due to complex and error-prone
        # handling of CA certificate chain, server name, etc:
        # --------------------------------------------------------------
        verify_option = False
        if self.cacertfile is not None:
            verify_option = self.cacertfile
        # -------
        # Request
        # -------
        response = requests.put(url,
                                headers = HEADERS,
                                json = data,
                                timeout = TIMEOUT,
                                cert = (self.certfile,
                                        self.keyfile),
                                verify = verify_option
                                )
        response.raise_for_status()
        return response
    