# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0902
#pylint: disable=R0912
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.appdef import NAME_DEVICE_MAP
from myminapp.lib.command.cmd import Cmd
from myminapp.lib.device.meter.dtsu import DTSU
from myminapp.lib.device.plug.fritz import Fritz
from myminapp.lib.device.plug.bosch import Bosch

# =========
# Constants
# =========
METER_DEVNAME = "EM"
SOLAR_DEVNAME = "SOLAR"
PLUG1_DEVNAME = "PS_IN1"
PLUG2_DEVNAME = "PS_IN2"
PLUG3_DEVNAME = "PS_IN3"
PLUG_POWER = 70

class PsCharge(Cmd):

    """
    This command class charges a powerstation via 3 power supply units
    depending on current total power consumption and current solar power.

    The power supply units are connected to switchable sockets ("plugs"),
    which are switched on or off here.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class setup (calls superclass init with class name).
        
        Args:
            None

        Returns:
            None.
        """
        super().__init__(__class__.__name__)
        self.test = False
        self.dtsu = None
        self.fritz = None
        self.bosch = None
        self.meter_devid = NAME_DEVICE_MAP.get(METER_DEVNAME).get("devid")
        self.solar_devid = NAME_DEVICE_MAP.get(SOLAR_DEVNAME).get("devid")
        self.plug1_devid = NAME_DEVICE_MAP.get(PLUG1_DEVNAME).get("devid")
        self.plug2_devid = NAME_DEVICE_MAP.get(PLUG2_DEVNAME).get("devid")
        self.plug3_devid = NAME_DEVICE_MAP.get(PLUG3_DEVNAME).get("devid")

    # ==============
    # Public methods
    # ==============

    #Overrides
    def exec(self, cmdinput:dict):
        """See superclass 'Cmd'."""

        # -------------------------------
        # Declare general local variables
        # -------------------------------
        code = -1       # Result code (0=OK, 1=error, 2=warning)
        text = ""       # Result text ('OK', or error text)
        trace = ""      # Result trace ('', or error trace)
        dataset = {}    # Result dataset
        datasets = []   # Result dataset list to be returned

        # ---------------------------------
        # Declare local variables as needed
        # ---------------------------------
        app = None      # Application instance name (app1, app2, ...)
        params = None   # Specifications as CSV list (e.g. cmax=-50,smin=100)
        cmax = None     # Consumption maximum watts
        ccur = None     # Consumpiton current watts
        smin = None     # Solar power minimum watts
        scur = None     # Solar power current watts
        p1 = None       # Plug #1 state
        p2 = None       # Plug #2 state
        p3 = None       # Plug #3 state
        schedule = None # Optional schedule data

        try:

            # ------------------------------------------------------
            # Check and set app and other input parameters as needed
            # ------------------------------------------------------
            app = cmdinput.get('app')
            if app is None:
                raise Exception(self.helper.mtext(204, self.name, 'app'))
            params = cmdinput.get('value')
            if params is None:
                raise Exception(self.helper.mtext(204, self.name, 'value'))
            kv_list = params.split(",")
            kv_dict = {}
            for kv in kv_list:
                kv = kv.split("=")
                kv_dict[kv[0].strip()] = int(kv[1].strip())
            cmax = kv_dict.get("cmax")
            smin = kv_dict.get("smin")
            if cmax is None:
                raise Exception(self.helper.mtext(204, self.name,
                                                   'cmax=<int> in value'))
            if smin is None:
                raise Exception(self.helper.mtext(204, self.name,
                                                   'smin=<int> in value'))
            schedule = cmdinput.get("schedule")

            # -----------------------------------
            # Get current values from the devices
            # -----------------------------------
            ccur, scur = self.__get_current_values()

            # -----------------------------------------------------------
            # Switch the plugs accordingly and get the state of each plug
            # -----------------------------------------------------------
            p1, p2, p3 = self.__switch_plugs(cmax, ccur, smin, scur, schedule)

            # ------------------------------
            # Set the result as output value
            # ------------------------------
            result = []
            result.append(f"cmax={cmax}")
            result.append(f"ccur={ccur}")
            result.append(f"smin={smin}")
            result.append(f"scur={scur}")
            result.append(f"p1={p1}")
            result.append(f"p2={p2}")
            result.append(f"p3={p3}")
            output_value = ",".join(result)

            # -----------
            # Set dataset
            # -----------
            dataset["value"] = output_value

            # ---------------------
            # Set code, text, trace
            # ---------------------
            code = 0
            text = self.helper.mtext(0)
            trace = ""

        # -----------------------------------------
        # Catch exception and set code, text, trace
        # -----------------------------------------
        except Exception as exception:
            code = 1
            text = self.helper.mtext(1, exception)
            trace = self.helper.tbline()

        # -------------
        # Do final work
        # -------------
        finally:
            self.add_command_output(code, text, trace, dataset, datasets)

        # ---------------
        # Return datasets
        # ---------------
        return datasets

    #Overrides
    def close(self):
        """See superclass 'Cmd'."""
        self.__close_devices()

    # ===============
    # Private methods
    # ===============

    def __close_devices(self):
        """Closes the devices.

        Args:
            None.
    
        Returns:
            None.
        """
        if self.dtsu:
            self.dtsu.close()
        if self.fritz:
            self.fritz.close()
        if self.bosch:
            self.bosch.close()

    def __get_current_values(self):
        """Gets current consumption and current solar power.

        Args:
            None.
            
        Returns:
            ccur (int): Consumpiton current watts
            scur (int): Solar power current watts
        """
        power = None
        info = None
        # ----
        # DTSU
        # ----
        if self.dtsu is None:
            self.dtsu = DTSU()
        try:
            power = self.dtsu.get_w_current() # Needs no devid
        except Exception:
            try:
                self.dtsu.close()
            except Exception:
                pass # Ignore this special case
            self.dtsu = None
            raise
        ccur = int(power)*-1 # Make negative value positive and vice versa
        # -----
        # Fritz
        # -----
        if self.fritz is None:
            self.fritz = Fritz()
        try:
            info = self.fritz.get_info(self.solar_devid)
        except Exception:
            try:
                self.fritz.close()
            except Exception:
                pass # Ignore this special case
            self.fritz = None
            raise
        power = info.get("NewMultimeterPower") # This value is always positve
        scur = int(power/100)
        return ccur, scur

    def __switch_plugs(self, cmax:int, ccur:int, smin:int, scur:int,
                       schedule:dict=None):
        """Switches plugs depending on consumption and solar power.

        Args:
            cmax (int): Consumption maximum watts
            ccur (int): Consumpiton current watts
            smin (int): Solar power minimum watts
            scur (int): Solar power current watts
            schedule (dict): Optional schedule data
            
        Returns:
            p1 (str): Plug #1 state ('ON' or 'OFF')
            p2 (str): Plug #2 state ('ON' or 'OFF')
            p3 (str): Plug #3 state ('ON' or 'OFF')
        """
        p1 = "OFF"
        p2 = "OFF"
        p3 = "OFF"
        # -----
        # Bosch
        # -----
        if self.bosch is None:
            self.bosch = Bosch()

        final_action = False
        if schedule is not None:
            if schedule.get("remaining_actions") == 0:
                final_action = True

        if self.test:
            print(f"TEST ccur, cmax, scur, smin, final_action: " \
                  f"{ccur}, {cmax}, {scur}, {smin}, {final_action}")

        try:

            if final_action is True:
                self.bosch.set_switch(self.plug3_devid, "OFF")
                p3 = "OFF"
                self.bosch.set_switch(self.plug2_devid, "OFF")
                p2 = "OFF"
                self.bosch.set_switch(self.plug1_devid, "OFF")
                p1 = "OFF"
            else:
                # ---------------------
                # Get plug switch state
                # ---------------------
                p1 = self.bosch.get_info(self.plug1_devid).get("state")
                p2 = self.bosch.get_info(self.plug2_devid).get("state")
                p3 = self.bosch.get_info(self.plug3_devid).get("state")
                # ----------------------------------------------------------
                # Switch one plug per call only for the following reasons:
                # - Too many switching operations on the plugs and on the
                #   power station should be avoided
                # - The call interval should ensure accurate device values
                #   between the switching operations (device latency)
                # - The impact of short-term fluctuations in consumption
                #   and solar feed-in should be minimized
                # ----------------------------------------------------------
                if ccur > cmax or scur < smin:
                    # ----------------------------------
                    # Switch OFF from plug #3 to plug #1
                    # ----------------------------------
                    if p3 == "ON":
                        self.bosch.set_switch(self.plug3_devid, "OFF")
                        p3 = "OFF"
                    elif p2 == "ON":
                        self.bosch.set_switch(self.plug2_devid, "OFF")
                        p2 = "OFF"
                    elif p1 == "ON":
                        self.bosch.set_switch(self.plug1_devid, "OFF")
                        p1 = "OFF"
                    else:
                        pass
                elif (ccur + PLUG_POWER) <= cmax and scur >= smin:
                    # ---------------------------------
                    # Switch ON from plug #1 to plug #3
                    # ---------------------------------
                    if p1 == "OFF":
                        self.bosch.set_switch(self.plug1_devid, "ON")
                        p1 = "ON"
                    elif p2 == "OFF":
                        self.bosch.set_switch(self.plug2_devid, "ON")
                        p2 = "ON"
                    elif p3 == "OFF":
                        self.bosch.set_switch(self.plug3_devid, "ON")
                        p3 = "ON"
                    else:
                        pass
                else:
                    pass

            if self.test:
                print(f"TEST p1, p2, p3: {p1}, {p2}, {p3}")

        except Exception:
            try:
                self.bosch.close()
            except Exception:
                pass # Ignore this special case
            self.bosch = None
            raise
        return p1, p2, p3
    