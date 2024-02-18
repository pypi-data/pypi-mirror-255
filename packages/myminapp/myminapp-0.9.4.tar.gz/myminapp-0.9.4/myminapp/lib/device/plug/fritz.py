# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0719

from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
# None

class Fritz:

    """
    This device class communicates with a FRITZ!Box via HTTP respectively
    TR-064.

    Requires: pip install fritzconnection

    Assuming that communication takes place exclusively in the local
    network, only HTTP, not HTTPS, is supported here.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Fritz' setup.
        
        Args:
            None.

        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        self.fritz = self.open_hub()

    # ==============
    # Public methods
    # ==============

    def open_hub(self):
        """Opens the home automation hub.
    
        Args:
            None.

        Returns:
            object: Instance of FritzHomeAutomation class.
        """
        fritz_conn = DEVICE_CLASS_CONNECTION_SPEC.get(self.name)
        if fritz_conn is None:
            raise Exception(self.helper.mtext(504, self.name))
        if fritz_conn.get("address") is None:
            raise Exception(self.helper.mtext(505, 'address', self.name))
        if fritz_conn.get("port") is None:
            raise Exception(self.helper.mtext(505, 'port', self.name))
        if fritz_conn.get("user") is None:
            raise Exception(self.helper.mtext(505, 'user', self.name))
        if fritz_conn.get("password") is None:
            raise Exception(self.helper.mtext(505, 'password', self.name))
        return FritzHomeAutomation(
            address = fritz_conn.get("address"),
            port = fritz_conn.get("port"),
            user = fritz_conn.get("user"),
            password = fritz_conn.get("password"),
            use_tls = False)

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
        return self.fritz.device_information()

    def get_info(self, devid:str):
        """Gets information about a specific home automation device.

        Args:
            devid (str): The device ID (here AIN, actor identifier number).
    
        Returns:
            dict: The information as key value pairs.
        """
        return self.fritz.get_device_information_by_identifier(devid)

    def set_switch(self, devid:str, state:str):
        """Switches a specific home automation device on or off.

        Args:
            devid (str): The device ID (here AIN, actor identifier number).
            state (str): ON or OFF.
    
        Returns:
           None.
        """
        if state == 'ON':
            self.fritz.set_switch(devid, on=True)
        elif state == 'OFF':
            self.fritz.set_switch(devid, on=False)
        else:
            raise Exception(self.helper.mtext(501, state))

    # ===============
    # Private methods
    # ===============
    # None
        