# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0912
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.appdef import NAME_DEVICE_MAP
from myminapp.lib.command.cmd import Cmd
from myminapp.lib.device.plug.fritz import Fritz
from myminapp.lib.device.plug.bosch import Bosch
from myminapp.lib.device.plug.nohub import Nohub
from myminapp.lib.device.inverter.opendtu import OpenDTU
from myminapp.lib.device.relay.relay5v import Relay5V

# =========
# Constants
# =========
# None

class Setting (Cmd):

    """
    This command class sets values, e.g. the switch state of a plug, an
    inverter limit, or a relay port, represented by corresponding device
    classes.
     
    Device categories P, I and R are supported.

    Annotation: The name 'set' was not used to avoid conflicts with
    reserved words, for example in SQLite.

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
        self.fritz = None
        self.bosch = None
        self.nohub = None
        self.opendtu = None
        self.relay5v = None

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
        devname = None  # Device name(s) (e.g. * or EM or SOLAR, COOLER)
        devcat = None   # Device category (e.g. * or P)
        devclass = None # Device class.
        devnames = []   # Device names to be processed.

        # --------------------------------------
        # Part 1 of 2: Perform preparatory tasks
        # --------------------------------------
        try:
            # ------------------------------------------------------
            # Check and set app and other input parameters as needed
            # ------------------------------------------------------
            app = cmdinput.get('app')
            if app is None:
                raise Exception(self.helper.mtext(204, self.name, 'app'))
            devname_in = cmdinput.get('devname')
            devcat_in = cmdinput.get('devcat')
            param_in = cmdinput.get('value')
            if devname_in is None:
                raise Exception(self.helper.mtext(204, self.name, 'devname'))
            if devcat_in is not None:
                if devcat_in not in ['*', 'P', 'I', 'R']:
                    raise Exception(self.helper.mtext(209, devname_in,
                                                           devcat_in))
            if param_in is None:
                raise Exception(self.helper.mtext(204, self.name, 'value'))
            if devname_in != "*":
                # -------------------------------------
                # Set given device name(s) and category
                # -------------------------------------
                devname_in_list = devname_in.strip().split(",")
                for devname_in in devname_in_list:
                    devname_in = devname_in.strip()
                    if NAME_DEVICE_MAP.get(devname_in) is not None:
                        devcat = NAME_DEVICE_MAP.get(devname_in).get("devcat")
                        if devcat is None:
                            raise Exception(self.helper.mtext(204, self.name,
                                                            'devcat'))
                        if devcat_in is not None and devcat_in != '*':
                            if devcat != devcat_in:
                                raise Exception(self.helper.mtext(209, devname_in,
                                                                devcat_in))
                        if devcat not in ['P', 'I', 'R']:
                            raise Exception(self.helper.mtext(209, devname_in,
                                                            devcat))
                        devnames.append(devname_in)
                    else:
                        raise Exception(self.helper.mtext(207, devname_in))
            else:
                # ----------------------------------------------
                # Set all device names with appropriate category
                # ----------------------------------------------
                for devname in NAME_DEVICE_MAP:
                    devcat = NAME_DEVICE_MAP.get(devname).get("devcat")
                    if devcat is None:
                        raise Exception(self.helper.mtext(204, self.name,
                                                        'devcat'))
                    if devcat not in ['P', 'I', 'R']:
                        continue
                    if devcat_in is not None and devcat_in != '*':
                        if devcat == devcat_in:
                            devnames.append(devname)
                    else:
                        devnames.append(devname)
            # --------------------------------
            # No device name could be assigned
            # --------------------------------
            if len(devnames) == 0:
                raise Exception(self.helper.mtext(206))
        # --------------------------------------------------------------------
        # Catch exception and set code, text, and trace - then return datasets
        # --------------------------------------------------------------------
        except Exception as exception:
            code = 1
            text = self.helper.mtext(1, exception)
            trace = self.helper.tbline()
            self.add_command_output(code, text, trace, dataset, datasets)
            return datasets

        # -----------------------------------------------------
        # Part 2/2: Iterate over device names and perform tasks
        # -----------------------------------------------------
        for devname in devnames:
            try:
                # --------------------------------
                # Initialize dataset for each pass
                # --------------------------------
                dataset = {}
                dataset["devname"] = devname

                # -------------------------------
                # Set devcat, devclass, and devid
                # -------------------------------
                devcat = NAME_DEVICE_MAP.get(devname).get("devcat")
                if devcat is None:
                    raise Exception(self.helper.mtext(204, self.name,
                                                        'devcat'))
                devclass = NAME_DEVICE_MAP.get(devname).get("devclass")
                if devclass is None:
                    raise Exception(self.helper.mtext(204, self.name,
                                                        'devclass'))
                devid = str(NAME_DEVICE_MAP.get(devname).get("devid"))
                if devid is None:
                    raise Exception(self.helper.mtext(204, self.name,
                                                        'devid'))

                # ----------------
                # Complete dataset
                # ----------------
                dataset["devcat"] = devcat
                dataset["value"] = param_in

                # ----------------
                # Initialize param
                # ----------------
                param = None

                # ---------------------------------
                # Device category 'P' - smart plugs
                # ---------------------------------
                if devcat == "P":
                    # -------------------------------
                    # Set param according to category
                    # -------------------------------
                    param = param_in.upper().strip()
                    if param not in ('ON', 'OFF'):
                        raise Exception(self.helper.mtext(502, devcat,
                                                            param_in))
                    # -----
                    # Fritz
                    # -----
                    if devclass == 'Fritz':
                        if self.fritz is None:
                            self.fritz = Fritz()
                        try:
                            self.fritz.set_switch(devid, param)
                        except Exception:
                            try:
                                self.fritz.close()
                            except Exception:
                                pass # Ignore this special case
                            self.fritz = None
                            raise
                    # -----
                    # Bosch
                    # -----
                    elif devclass == 'Bosch':
                        if self.bosch is None:
                            self.bosch = Bosch()
                        try:
                            self.bosch.set_switch(devid, param)
                        except Exception:
                            try:
                                self.bosch.close()
                            except Exception:
                                pass # Ignore this special case
                            self.bosch = None
                            raise
                    # -----
                    # Nohub
                    # -----
                    elif devclass == 'Nohub':
                        devbrand = \
                            NAME_DEVICE_MAP.get(devname).get("devbrand")
                        if devbrand is None:
                            raise Exception(
                            self.helper.mtext(204, self.name, 'devbrand'))
                        if self.nohub is None:
                            self.nohub = Nohub()
                        try:
                            self.nohub.set_switch(devid, devbrand, param)
                        except Exception:
                            try:
                                self.nohub.close()
                            except Exception:
                                pass # Ignore this special case
                            self.nohub = None
                            raise
                    # ------------------------
                    # Unsupported device class
                    # ------------------------
                    else:
                        raise Exception(self.helper.mtext(208, devclass))

                # -------------------------------------
                # Device category 'I' - micro inverters
                # -------------------------------------
                elif devcat == "I":
                    # -------------------------------
                    # Set param according to category
                    # -------------------------------
                    param = int(param_in)
                    if param < 0:
                        raise Exception(self.helper.mtext(502, devcat,
                                                            param_in))
                    # -------
                    # OpenDTU
                    # -------
                    if devclass == 'OpenDTU':
                        if self.opendtu is None:
                            self.opendtu = OpenDTU()
                        try:
                            self.opendtu.set_limit_absolute(devid, param)
                        except Exception:
                            try:
                                self.opendtu.close()
                            except Exception:
                                pass # Ignore this special case
                            self.opendtu = None
                            raise
                    # ------------------------
                    # Unsupported device class
                    # ------------------------
                    else:
                        raise Exception(self.helper.mtext(208, devclass))

                # ---------------------------
                # Device category 'R' - Relay
                # ---------------------------
                elif devcat == "R":
                    # -------------------------------
                    # Set param according to category
                    # -------------------------------
                    param = param_in.upper().strip()
                    if param != "ON" and param != "OFF":
                        raise Exception(self.helper.mtext(502, devcat,
                                                            param_in))
                    # -----
                    # Relay
                    # -----
                    if devclass == 'Relay5V':
                        if self.relay5v is None:
                            self.relay5v = Relay5V()
                        try:
                            self.relay5v.set_state(int(devid), param)
                        except Exception:
                            try:
                                self.relay5v.close()
                            except Exception:
                                pass # Ignore this special case
                            self.relay5v = None
                            raise

                    # ------------------------
                    # Unsupported device class
                    # ------------------------
                    else:
                        raise Exception(self.helper.mtext(208, devclass))

                # ---------------------------
                # Unsupported device category
                # ---------------------------
                else:
                    raise Exception(self.helper.mtext(209, devname, devcat))

                # ---------------------
                # Set code, text, trace
                # ---------------------
                code = 0
                text = self.helper.mtext(0)
                trace = ""
            # -----------------------------------------------------
            # Catch exception within loop and set code, text, trace
            # -----------------------------------------------------
            except Exception as exception:
                code = 1
                text = self.helper.mtext(1, exception)
                trace = self.helper.tbline()
            # -------------------------
            # Do final work within loop
            # -------------------------
            finally:
                self.add_command_output(code, text, trace, dataset, datasets)

        # ---------------
        # Return datasets
        # ---------------
        return datasets

    #Overrides
    def close(self):
        """See superclass 'Cmd'."""
        if self.fritz:
            self.fritz.close()
        if self.bosch:
            self.bosch.close()
        if self.nohub:
            self.nohub.close()
        if self.opendtu:
            self.opendtu.close()
        if self.relay5v:
            self.relay5v.close()
