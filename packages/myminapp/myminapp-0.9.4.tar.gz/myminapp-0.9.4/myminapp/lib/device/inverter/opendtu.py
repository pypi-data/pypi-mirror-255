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
from requests.auth import HTTPBasicAuth

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========

# ---------------------------
# OpenDTU access via REST API
# ---------------------------
CHECK_TIMEOUT = 0.5 # Seconds
TIMEOUT = 1 # Seconds
PORT = 80 # Default port
URL_PREFIX = "http://--address-"
API_URL_PREFIX = f"http://--address-:{PORT}/api/"
GET_HEADERS = {"content-type": "application/json"}
POST_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

# --------------
# Type of limits
# --------------
NON_PERSISTENT_LIMIT_ABSOLUTE = int(0) # Maximum Watt
NON_PERSISTENT_LIMIT_RELATIVE = int(1) # Percent of persistent maximum
# -----------------------------------------------
# WARNING
# -----------------------------------------------
# Persistent limit should be set very rarely,
# because the inverter's EEPROM could be damaged
# ----------------------------------------------
PERSISTENT_LIMIT_ABSOLUTE = int(256) # Maximum Watt
PERSISTENT_LIMIT_RELATIVE = int(257) # Percent of persistent maximum

class OpenDTU:

    """
    This device class communicates with an OpenDTU hub via HTTP.

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
        """Class 'OpenDTU' setup.
        
        Args:
           None.

        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        opendtu_conn = DEVICE_CLASS_CONNECTION_SPEC.get(self.name)
        if opendtu_conn is None:
            raise Exception(self.helper.mtext(504, self.name))
        self.address = opendtu_conn.get("address")
        if self.address is None:
            raise Exception(self.helper.mtext(505, 'address', self.name))
        self.user = opendtu_conn.get("user")
        if self.user is None:
            raise Exception(self.helper.mtext(505, 'user', self.name))
        self.password = opendtu_conn.get("password")
        if self.password is None:
            raise Exception(self.helper.mtext(505, 'password', self.name))

    # ==============
    # Public methods
    # ==============

    def close(self):
        """Closes resources (formally only here).
        
        Args:
            None.

        Returns:
            None.
        """
        # Nothing to close here

    def get_info(self, devid:str):
        """Gets information about a specific home automation device.

        Args:
            devid (str): The device ID (here inverter's serial number).
    
        Returns:
           dict: The information as key value pairs.
        """
        check_url = URL_PREFIX.replace("--address-", self.address)
        url = API_URL_PREFIX.replace(
            "--address-", self.address) + "livedata/status"
        response = self.__GET(url, check_url)
        resp_json = json.loads(response.text)
        # ---------------------------------
        # Parse response for given inverter
        # ---------------------------------
        for inverter in resp_json['inverters']:
            inv_info = {}
            inv_serial = inverter["serial"]
            if devid != inv_serial:
                continue

            # -----------------------
            # Add general information
            # -----------------------
            inv_info["serial"] = inv_serial
            inv_info["name"] = inverter.get("name")
            inv_info["producing"] = inverter.get("producing")
            inv_info["limit_relative"] = inverter.get("limit_relative")
            inv_info["limit_absolute"] = inverter.get("limit_absolute")

            # ------------------------------
            # Translate 'reachable' to state
            # ------------------------------
            inv_info["state"] = "OFF"
            if inverter.get("reachable") is not None:
                test = inverter.get("reachable")
                if test is not None:
                    if test is True:
                        inv_info["state"] = "ON"

            # ----------------------------------------------
            # Get and add additional info from /limit/status
            # ----------------------------------------------
            limit_status = self.__get_limit_status(inv_serial)
            inv_info["limit_set_status"] = \
                limit_status.get("limit_set_status")
            inv_info["max_power"] = limit_status.get("max_power")

            # -------------------------------------
            # Add AC power supplied by the inverter
            # -------------------------------------
            if inv_info["state"] == "OFF":
                inv_info["power"] = 0.0
            else:
                inv_info["power"] = inverter['AC']['0']['Power']['v']

            # ---------------------------------------------------
            # Add DC power supplied by all solar panels connected
            # ---------------------------------------------------
            inv_info["power_dc"] = inverter['AC']['0']['Power DC']['v']

            # -------------------------------------------
            # Add energy for the day (Wh) and total (kWh)
            # -------------------------------------------
            inv_info["energy_day_wh"] = \
                inverter['AC']['0']['YieldDay']['v']
            inv_info["energy"] = \
                inverter['AC']['0']['YieldTotal']['v']

            # --------------------------------
            # Add DC data for each solar panel
            # --------------------------------
            unit_count = 0
            for panel in inverter['DC']:
                inv_info["unit_" + str(panel) + "_name"] = \
                    inverter['DC'][panel]["name"]["u"]
                inv_info["unit_" + str(panel) + "_power_dc_w"] = \
                    inverter['DC'][panel]["Power"]["v"]
                inv_info["unit_" + str(panel) + "_voltage_v"] = \
                    inverter['DC'][panel]["Voltage"]["v"]
                inv_info["unit_" + str(panel) + "_current_a"] = \
                    inverter['DC'][panel]["Current"]["v"]
                unit_count += 1
            inv_info["unit_count"] = unit_count

            return inv_info

    def set_limit_absolute(self, devid:str, limit:int):
        """Sets the non persistent absolute limit on an inverter.
         
        Args:
            devid (str): The device ID (here inverter's serial number).
            limit (int): The non persistent absolute limit value.
    
        Returns:
          object: Operation success information.
        """
        # ------------------------------------------------
        # Get the limit status and check if the set status
        # is OK. If not, raise an exception
        # ------------------------------------------------
        limit_status = self.__get_limit_status(devid)
        limit_set_status = limit_status["limit_set_status"]
        if limit_set_status.lower() != "ok":
            message = f"Limit cannot be set currently due to status " \
                      f"'{limit_set_status}'."
            raise Exception(message)
        # --------------------
        # Try to set the limit
        # --------------------
        payload = "data=" \
            "{\"serial\":\"%s\", \"limit_type\":%i, \"limit_value\":%i}" \
        % (devid, NON_PERSISTENT_LIMIT_ABSOLUTE, limit)
        check_url = API_URL_PREFIX.replace("--address-", self.address)
        url = API_URL_PREFIX.replace(
            "--address-", self.address) + "limit/config"
        response = self.__POST(url, check_url, payload)
        resp_json = json.loads(response.text)
        # -------------
        # Check success
        # -------------
        code = resp_json.get("code")
        if code is None or code != 1001:
            raise Exception(str(resp_json))
        # ---------------
        # Return response
        # ---------------
        return resp_json

    # ===============
    # Private methods
    # ===============

    def __get_limit_status(self, serial:str):
        """Gets information about the given inverter's limit status.
         
        Args:
            None.
    
        Returns:
           object: The information as key value pairs.
        """
        check_url = API_URL_PREFIX.replace("--address-", self.address)
        url = API_URL_PREFIX.replace(
            "--address-", self.address) + "limit/status"
        response = self.__GET(url, check_url)
        resp_json = json.loads(response.text)
        return resp_json[serial]

    def __GET(self, url:str, check_url:str):
        """Performs a GET request against the OpenDTU REST API.

        Args:
            url (str): The URL string.
            check_url (str): URL to check if service is reachable.

        Returns:
            Response: The response.
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
                        auth = HTTPBasicAuth(
                            self.user, self.password
                            ),
                        headers = GET_HEADERS,
                        timeout = TIMEOUT
                        )
        response.raise_for_status()
        return response

    def __POST(self, url:str, check_url:str, payload:dict):
        """Performs a POST request against a REST API.
        
        Args:
            url (str): The URL string.
            check_url (str): URL to check if service is reachable.
            payload (dict): The POST data.

        Returns:
            Response: The response.
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
        response = requests.post(url,
                        auth = HTTPBasicAuth(
                            self.user, self.password
                            ),
                        headers = POST_HEADERS,
                        timeout = TIMEOUT,
                        data = payload
                        )
        response.raise_for_status()
        return response
    