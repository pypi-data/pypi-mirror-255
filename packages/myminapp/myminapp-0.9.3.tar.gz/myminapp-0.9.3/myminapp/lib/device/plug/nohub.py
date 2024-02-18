# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0103
#pylint: disable=W0105
#pylint: disable=W0719

import json
import requests

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========

CHECK_TIMEOUT = 0.5 # Seconds
TIMEOUT = 1 # Seconds
HEADERS = {"content-type": "application/json"}

# ---------------
# SHELLY contants
# ---------------
SHELLY_PLUG_PREFIX = "http://--address-"
SHELLY_PLUG_STATUS = "/rpc/Switch.GetStatus?id=0"
SHELLY_PLUG_SWITCH_ON = "/rpc/Switch.Set?id=0&on=true"
SHELLY_PLUG_SWITCH_OFF = "/rpc/Switch.Set?id=0&on=false"

# More brands...
# ------------
# ... contants
# ------------
#...

class Nohub:

    """
    This device class communicates with devices like Shelly plugs via
    HTTP without a hub.

    Requires: pip install requests

    Assuming that communication takes place exclusively in the local
    network, only HTTP, not HTTPS, is supported here.

    A session is not opened to preserve the statelessness typical of
    REST services.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Nohub' setup.
        
        Args:
            None.

        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        self.init_nohub_conn()

    # ==============
    # Public methods
    # ==============

    def init_nohub_conn(self):
        """Initializes the home automation 'nohub' connection.

        Args:
            None.

        Returns:
            None.
        """
        # -----------------
        # Set configuration
        # -----------------
        self.nohub_conn = DEVICE_CLASS_CONNECTION_SPEC.get("Nohub")
        if self.nohub_conn is None:
            raise Exception(self.helper.mtext(504, self.name))

    def close(self):
        """Closes resources (formally only here).
        
        Args:
            None.

        Returns:
            None.
        """
        # Nothing to close here

    def get_info(self, devid:str, devbrand:str):
        """Gets information about a specific home automation device.
        
        Args:
            devid (str): The device ID.
            devbrand (str): The device brand.
    
        Returns:
            dict: The information as key value pairs.
        """
        url = None
        check_url = None
        # ------
        # Shelly
        # ------
        if devbrand == "Shelly":
            result = {}
            url = SHELLY_PLUG_PREFIX.replace("--address-", devid)
            check_url = url
            url = url + SHELLY_PLUG_STATUS
            # -----------------------------------------------
            # Get device info, then parse result specifically
            # -----------------------------------------------
            response = self.__GET(url, check_url)
            data = json.loads(response.text)
            result.update(self.__shelly_parse_info(data))
            return result
        # -----
        # Other
        # -----
        elif devbrand == "Xyz":
            # Implement as needed
            raise Exception(self.helper.mtext(503,
                                              __class__.__name__, devbrand))
        # -----------------
        # Unsupported brand
        # -----------------
        else:
            raise Exception(self.helper.mtext(503,
                                              __class__.__name__, devbrand))

    def set_switch(self, devid:str, devbrand:str, state:str):
        """Switches a specific home automation device on or off.

        Args:
            devid (str): The device ID.
            devbrand (str): The device brand.
            state (str): 'ON' or 'OFF'.
    
        Returns:
           None.
        """
        url = None
        check_url = None
        # -------
        # Shelly
        # -------
        if devbrand == "Shelly":
            url = SHELLY_PLUG_PREFIX.replace("--address-", devid)
            check_url = url
            if state == "ON":
                url = url + SHELLY_PLUG_SWITCH_ON
            elif state == "OFF":
                url = url + SHELLY_PLUG_SWITCH_OFF
            else:
                raise Exception(self.helper.mtext(501, state))
        # -----
        # Other
        # -----
        elif devbrand == "Xyz":
            # Implement as needed
            raise Exception(self.helper.mtext(503,
                                              __class__.__name__, devbrand))
        # -----------------
        # Unsupported brand
        # -----------------
        else:
            raise Exception(self.helper.mtext(503,
                                              __class__.__name__, devbrand))
        # ----------
        # Set switch
        # ----------
        response = self.__GET(url, check_url)
        data = json.loads(response.text)
        return data

    # ===============
    # Private methods
    # ===============

    def __GET(self, url:str, check_url:str):
        """Performs a GET request against a REST or REST like API.
 
        Args:
            url (str): The URL string.
            check_url (str): URL to check if service is reachable.

        Returns:
            object: The response.
        """
        # -------------------------
        # Check if URL is reachable
        # -------------------------
        try:
            requests.get(check_url, timeout = CHECK_TIMEOUT)
        except requests.exceptions.ConnectionError as exception:
            raise Exception(f"URL {check_url} is not reachable.") from exception
        # ---------------
        # Perform request
        # ---------------
        response = requests.get(url,
                        headers = HEADERS,
                        timeout = TIMEOUT
                        )
        response.raise_for_status()
        return response

    def __shelly_parse_info(self, data:dict):
        """Parses Shelly device information data.

        Args:
            data (dict): Response data.
    
        Returns:
            dict: The information as key value pairs.
        """
        result = {}

        try:
            value = data["output"]
            if value is True:
                result["state"] = "ON"
            else:
                result["state"] = "OFF"
        except KeyError:
            pass

        try:
            value = data["apower"]
            result["power"] = float(value)
        except KeyError:
            pass

        try:
            value = data["aenergy"]["total"]
            result["energy"] = float(value)
        except KeyError:
            pass

        try:
            value = data["temperature"]["tC"]
            result["tempc"] = float(value)
        except KeyError:
            pass

        return result

    '''
    def __<other>_parse_info(self, data:dict):
        """Parses <other> device information data.

        # Implement accordingly...

        Args:
            data (dict): Response data.
    
        Returns:
            dict: The information as key value pairs.
        """
    '''