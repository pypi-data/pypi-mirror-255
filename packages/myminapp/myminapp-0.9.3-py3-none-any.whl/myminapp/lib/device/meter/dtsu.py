# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0719

import time
import minimalmodbus

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
RETRIES = 3
WAIT = 1.5
TOTAL_KWH_DIFF = 0.0025 # Total kWh at DTSU value change (informative)

class DTSU:

    """
    This device class communicates via Modbus RTU with a Chint energy
    meter named 'DTSU666' that operates as Modbus slave.

    Requires: pip install minimalmodbus

    This class wraps the following minimalmodbus/DTSU requests:
        
        - read_float(4137, ...) -> get_kwh_total
        - read_float(8211, ...) -> get_w_current
    
    It is assumed that the energy meter is connected to a serial port
    via USB adapter. On Linux, the serial port is specified as follows:
    /dev/ttyUSB<n>, e.g. /dev/ttyUSB0. On Windows: COM<n>, e.g. COM3.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'DTSU' setup.
        
        Args:
            None

        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        self.test = False
        self.dtsu = self.open_device()

    # ==============
    # Public methods
    # ==============

    def open_device(self):
        """Opens the device.

        Args:
            None.

        Returns:
            object: Instance of minimalmodbus Instrument class.
        """
        # ---------------------------------
        # DTSU specific minimalmodbus setup
        # ---------------------------------
        dtsu_conn = DEVICE_CLASS_CONNECTION_SPEC.get(self.name)
        if dtsu_conn is None:
            raise Exception(self.helper.mtext(504, self.name))
        if dtsu_conn.get("port") is None:
            raise Exception(self.helper.mtext(505, 'port', self.name))
        if dtsu_conn.get("address") is None:
            raise Exception(self.helper.mtext(505, 'address', self.name))
        dtsu = minimalmodbus.Instrument(
                                dtsu_conn.get("port"),
                                dtsu_conn.get("address")
                                )
        # Default DTSU settings
        dtsu.serial.mode = minimalmodbus.MODE_RTU
        dtsu.serial.baudrate = 9600
        dtsu.serial.parity = minimalmodbus.serial.PARITY_NONE
        dtsu.serial.stopbits = 1
        # Additional settings
        dtsu.serial.bytesize = 8
        dtsu.serial.timeout = 0.5
        dtsu.clear_buffers_before_each_transaction = False
        dtsu.close_port_after_each_call = False
        # ---------------
        # Return instance
        # ---------------
        return dtsu

    def get_kwh_total(self):
        """Gets the total kilowatt hours from the device.
        
        Args:
            None.

        Returns:
           float: The total kWh rounded to 4 decimal places.
        """
        count = 0
        while True:
            try:
                count += 1
                return self.__get_kwh_total()
            except IOError as err:
                if self.test:
                    print(f"TEST DTSU.get_kwh_total: " \
                          f"IO error #{count}: {err}")
                if count > RETRIES:
                    raise
                time.sleep(WAIT)

    def get_w_current(self):
        """Gets the current watts from the device.
        
        Args:
            None.

        Returns:
           float: The current W rounded to 4 decimal places.
        """
        count = 0
        while True:
            try:
                count += 1
                return self.__get_w_current()
            except IOError as err:
                if self.test:
                    print(f"TEST DTSU.get_w_current: " \
                          f"IO error #{count}: {err}")
                if count > RETRIES:
                    raise
                time.sleep(WAIT)

    def close(self):
        """Closes the device.

        Args:
            None.

        Returns:
            None.
        """
        if self.dtsu:
            self.dtsu.serial.close()

    # ===============
    # Private methods
    # ===============

    def __get_kwh_total(self):
        """Gets the total kilowatt hours from the device.
        
        Args:
            None.

        Returns:
           float: The total kWh rounded to 4 decimal places.
        """
        return round(abs(
            self.dtsu.read_float(4137, 4, 2, minimalmodbus.BYTEORDER_BIG)
            ), 4)

    def __get_w_current(self):
        """Gets the current watts from the device.
        
        Args:
            None.

        Returns:
           float: The current W rounded to 4 decimal places.
        """
        return round((
            self.dtsu.read_float(8211, 4, 2, minimalmodbus.BYTEORDER_BIG)
            * 0.1), 4)
            