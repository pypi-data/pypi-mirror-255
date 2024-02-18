# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0912
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0123
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.appdef import NAME_DEVICE_MAP
from myminapp.lib.command.cmd import Cmd
from myminapp.lib.device.meter.dtsu import DTSU
from myminapp.lib.device.plug.fritz import Fritz
from myminapp.lib.device.plug.bosch import Bosch
from myminapp.lib.device.plug.nohub import Nohub
from myminapp.lib.device.inverter.opendtu import OpenDTU
from myminapp.lib.device.relay.relay5v import Relay5V

# =========
# Constants
# =========
# None

class State(Cmd):

    """
    This command class determines and returns the state of energy meters,
    plugs, microinverters and relays, each represented by a device class
    of the corresponding category.

    Device categories M, P, I and R are supported.

    In order to map the status of various devices uniformly to the defined
    output dataset, method 'map_to_dataset()' is used.

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
        self.dtsu = None
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
            if devname_in is None:
                raise Exception(self.helper.mtext(204, self.name, 'devname'))
            if devcat_in is not None:
                if devcat_in not in ['*', 'M', 'P', 'I', 'R']:
                    raise Exception(self.helper.mtext(209, devname_in,
                                                           devcat_in))
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
                        if devcat not in ['M', 'P', 'I', 'R']:
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
                    if devcat not in ['M', 'P', 'I', 'R']:
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
        # ----------------------------------------------------------------
        # Catch exception and set code, text, trace - then return datasets
        # ----------------------------------------------------------------
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
                devcat = NAME_DEVICE_MAP.get(devname).get("devcat")
                dataset["devcat"] = devcat
                # ----------------------
                # Set devclass and devid
                # ----------------------
                devclass = NAME_DEVICE_MAP.get(devname).get("devclass")
                if devclass is None:
                    raise Exception(self.helper.mtext(204, self.name,
                                                        'devclass'))
                devid = NAME_DEVICE_MAP.get(devname).get("devid")
                if devid is None:
                    raise Exception(self.helper.mtext(204, self.name,
                                                        'devid'))
                # -----------------------------
                # Get specific data from device
                # -----------------------------
                devdata = self.__get_device_data(devname, devcat, devclass,
                                                  devid)
                # ---------------------------
                # Map specific result to dataset
                # ---------------------------
                self.__map_to_dataset(devclass, devdata, dataset)
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
        if self.dtsu:
            self.dtsu.close()
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

    # ===============
    # Private methods
    # ===============

    def __get_device_data(self, devname:str, devcat:str, devclass:str,
                           devid:str):
        """Gets data from a specific device.
             
        Args:
            devname (str): Device name.
            devcat (str): Device category.
            devclass (str): Device class.
            devid (str): Device ID.
    
        Returns:
           dict: Device data.
        """
        data = None
        # -----------------------------------
        # Device category 'M' - energy meters
        # -----------------------------------
        if devcat == "M":
            if devclass == 'DTSU':
                if self.dtsu is None:
                    self.dtsu = DTSU()
                data = {}
                try:
                    data["w_current"] = self.dtsu.get_w_current()
                    data["kwh_total"] = self.dtsu.get_kwh_total()
                except Exception:
                    try:
                        self.dtsu.close()
                    except Exception:
                        pass # Ignore this special case
                    self.dtsu = None
                    raise
            # ------------------------
            # Unsupported device class
            # ------------------------
            else:
                raise Exception(self.helper.mtext(208, devclass))
        # ---------------------------------
        # Device category 'P' - smart plugs
        # ---------------------------------
        elif devcat == "P":
            if devclass == 'Fritz':
                if self.fritz is None:
                    self.fritz = Fritz()
                try:
                    data = self.fritz.get_info(devid)
                except Exception:
                    try:
                        self.fritz.close()
                    except Exception:
                        pass # Ignore this special case
                    self.fritz = None
                    raise
            elif devclass == 'Bosch':
                if self.bosch is None:
                    self.bosch = Bosch()
                try:
                    data = self.bosch.get_info(devid)
                except Exception:
                    try:
                        self.bosch.close()
                    except Exception:
                        pass # Ignore this special case
                    self.bosch = None
                    raise
            elif devclass == 'Nohub':
                devbrand = NAME_DEVICE_MAP.get(devname).get("devbrand")
                if devbrand is None:
                    raise Exception(self.helper.mtext(204,
                                        self.name, 'devbrand'))
                if self.nohub is None:
                    self.nohub = Nohub()
                try:
                    data = self.nohub.get_info(devid, devbrand)
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
            if devclass == 'OpenDTU':
                if self.opendtu is None:
                    self.opendtu = OpenDTU()
                try:
                    data = self.opendtu.get_info(devid)
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
        # ----------------------------
        # Device category 'R' - relays
        # ----------------------------
        elif devcat == "R":
            if devclass == 'Relay5V':
                if self.relay5v is None:
                    self.relay5v = Relay5V()
                data = {}
                try:
                    data["state"] = self.relay5v.get_state(int(devid))
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
        # ------------------
        # Return device data
        # ------------------
        return data

    def __map_to_dataset(self, devclass:str, devdata:dict, dataset):
        """Maps data from a specific device to dataset.

        dataset_map specifies how the required device fields and values are
        to be mapped to the corresponding dataset fields. Use is made here
        of method 'eval()', which can dynamically process code.
                 
        Args:
            devclass (str): Device class.
            devdata (dict): Device data.
    
        Returns:
           None
        """
        dataset_map = {
            "DTSU": {
                "state": {"field": None, "code": "str('ON')"},
                "power": {"field": "w_current", "code": "round((value), 1)"},
                "energy": {"field": "kwh_total", "code": "round((value), 3)"},
                "tempc": {"field": None, "code": "None"}
                },
            "Fritz": {
                "state": {"field": "NewSwitchState", "code": "value"},
                "power": {"field": "NewMultimeterPower", "code": \
                           "round((value / 100), 1)"},
                "energy": {"field": "NewMultimeterEnergy", "code": \
                           "round((value / 1000), 3)"},
                "tempc": {"field": "NewTemperatureCelsius", "code": \
                         "round((value / 10), 1)"},
                },
            "Bosch": {
                "state": {"field": "state", "code": "value"},
                "power": {"field": "power", "code": "round((value), 1)"},
                "energy": {"field": "energy", "code": \
                           "round((value / 1000), 3)"},
                "tempc": {"field": None, "code": "None"}
                },
            "Nohub": {
                "state": {"field": "state", "code": "value"},
                "power": {"field": "power", "code": "round((value), 1)"},
                "energy": {"field": "energy", "code": "round((value / 1000), 3)"},
                "tempc": {"field": "tempc", "code": "round((value), 1)"}
                },
            "OpenDTU": {
                "state": {"field": "state", "code": "value"},
                "power": {"field": "power", "code": "round((value), 1)"},
                "energy": {"field": "energy", "code": "round((value), 3)"},
                "tempc": {"field": None, "code": "None"}
                },
            "Relay5V": {
                "state": {"field": "state", "code": "value"},
                "power": {"field": None, "code": "None"},
                "energy": {"field": None, "code": "None"},
                "tempc": {"field": None, "code": "None"}
                },
        }
        dmap = dataset_map.get(devclass)
        for name in dmap.keys():
            spec = dmap.get(name)
            field = spec.get("field")
            code = spec.get("code")
            value = None
            if field is None:
                value = eval(code) # Evaluate constant value
            else:
                try:
                    value = devdata[field]  # Get value from device data
                    value = eval(code)      # and evaluate that value
                except KeyError:
                    value = None
                except ValueError:
                    value = None
                except Exception:
                    value = None
            dataset[name] = value
            