# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0123
#pylint: disable=R0912
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0718
#pylint: disable=W0719

import time

from myminapp.appdef import DATA_HOME
from myminapp.lib.command.cmd import Cmd
from myminapp.lib.device.camera.numcam757 import Numcam757
from myminapp.lib.device.relay.relay5v import Relay5V
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
GPIO_POWER = 17
GPIO_DISPLAY = 18
PICTURE_PATH = DATA_HOME + "/temp/camera/"

class PsDischarge(Cmd):

    """
    This command class discharges a powerstation depending on its filling
    level.
     
    To get the filling level, device class 'Numcam757' is used to take a
    picture from the powerstation's display. Device class 'Relay5V' is used
    to activate the display light before the picture is taken, as described
    for Numcam757.

    Device class 'Relay5V' is used again to switch the power supply from
    the powerstation to the inverter.

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
        self.relay5v = None
        self.numcam757 = None
        self.helper = Helper()

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
        params = None   # Specifications as CSV list (e.g. minlevel=25,...)
        minlevel = None # Minimum filling level
        value = None    # Output value
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
            minlevel = kv_dict.get("minlevel")
            if minlevel is None:
                raise Exception(self.helper.mtext(204, self.name,
                                                   'minlevel=<int> in value'))
            if type(minlevel) is not int or minlevel < 5 or minlevel > 100:
                raise Exception(self.helper.mtext(215, 'minlevel', self.name,
                                                   str(minlevel)))
            schedule = cmdinput.get("schedule")
            # -------------------------
            # Relay5V for display light
            # -------------------------
            if self.relay5v is None:
                self.relay5v = Relay5V()
            try:
                self.relay5v.set_state(GPIO_DISPLAY, "ON")
                time.sleep(3)
                self.relay5v.set_state(GPIO_DISPLAY, "OFF")
            except Exception:
                try:
                    self.relay5v.close()
                except Exception:
                    pass # Ignore this special case
                self.relay5v = None
                raise
            # ---------
            # Numcam757
            # ---------
            num = -1
            if self.numcam757 is None:
                self.numcam757 = Numcam757()
                time.sleep(1)
            filename = app + "-" + "numcam757.bmp"
            file = PICTURE_PATH + filename
            try:
                num = self.numcam757.get_number(file)
            except Exception:
                try:
                    self.numcam757.close()
                except Exception:
                    pass # Ignore this special case
                self.numcam757 = None
                raise
            # ------------------------------------------------------
            # Raising this exception is not helpful, so skip this.
            # If it is not skipped, GPIO_POWER might be switched OFF
            # (see also final action below)
            # ------------------------------------------------------
            # if num == -1:
            #     raise Exception("Invalid picture capture.")
            # ------------------------------------
            # Relay5V for power supply to inverter
            # ------------------------------------
            if num >= minlevel:
                value = "ON"
            else:
                value = "OFF"
            try:
                self.relay5v.set_state(GPIO_POWER, value)
            except Exception:
                try:
                    self.relay5v.close()
                except Exception:
                    pass # Ignore this special case
                self.relay5v = None
                raise
            # --------------------------------------------------
            # If the command is scheduled, check whether this is
            # the final action within the scheduled time frame.
            # If so, switch power OFF as final task
            # --------------------------------------------------
            if schedule is not None and schedule.get("remaining_actions") == 0:
                self.relay5v.set_state(GPIO_POWER, "OFF")
                value = "OFF"

                if self.test:
                    print("TEST psdischarge: remaining_actions is 0 - " \
                          "final task performed.")

            # ---------------------
            # Set code, text, trace
            # ---------------------
            code = 0
            text = self.helper.mtext(0)
            trace = ""
            # -----------
            # Set dataset
            # -----------
            dataset["value"] = value + f" (level={num})"
            dataset["file"] = filename
            dataset["object"] = self.helper.file_to_blob(file)
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
        if self.numcam757:
            self.numcam757.close()
        if self.relay5v:
            self.relay5v.close()
