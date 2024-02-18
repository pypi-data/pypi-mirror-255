# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0911
#pylint: disable=R0912
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=R1716
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.lib.util.helper import DAYS
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========

TYPE_DIFF = "diff"
TYPE_UNIT = "unit"
DIFF_SECONDS_RANGE = [5, 43200]
UNIT_1_DAY = "d"
UNIT_1_DAY_SECONDS = 86400
UNIT_1_HOUR = "h"
UNIT_1_HOUR_SECONDS = 3600
UNIT_5_MINUTES = "m"
UNIT_5_MINUTES_SECONDS = 300
UNIT_VALUES = [UNIT_1_DAY, UNIT_1_HOUR, UNIT_5_MINUTES]
UNIT_START_LIMIT_SECOND = 8
UNIT_END_LIMIT_SECOND = 51

class Scheduler:

    """
    Use this utility class as scheduler.
    
    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self, name:str, schedset:dict):
        """Class 'Scheduler' setup.

        Args:
            name (str): Name of the schedule set.
            schedset (dict): The schedule set.

        Returns:
            None.
        """
        self.helper = Helper()
        self.test = False
        self.name = name                # Schedule set name
        self.cmdpreset = None           # Command preset name
        self.days = None                # Days of week
        self.time_from = None           # Start of time window
        self.time_to = None             # End of time window
        self.interval = None            # Time interval seconds or unit
        self.interval_type = None       # Time interval type
        self.interval_seconds = None    # Time interval seconds
        self.interval_unit = None       # Time interval unit
        self.interval_switch = False    # Time interval switch (default False)

        self.__set_params(schedset)     # Sets the preceding parameters

        self.time_from_timestamp = None # Time window start timestamp per day
        self.time_to_timestamp = None   # Time window end timestamp per day

        self.time_from_diff_secs = None # Seconds since time window start
        self.time_to_diff_secs = None   # Seconds until time window end
        self.remaining_actions = 0      # Remaining actions in time window

        self.action_number = 0          # Action number
        self.action_number_pending = 0  # Pending (unconfirmed) action number
        self.last_timestamp = None      # Timestamp of last pending action

    # ==============
    # Public methods
    # ==============

    def get_action_number(self):
        """Checks whether a planned action is to be performed at the moment.

        When an action is pending according to the schedule settings, a
        pending action number is set and returned. If the pending action
        is not confirmed with confirm_action(), this method will return the
        pending action number's inverted value, i.e. (number*-1).
                                 
        Args:
            None.
                    
        Returns:
            int: Pending action number > 0, its inverted value (*-1), or 0.
        """
        if self.action_number_pending > 0:
            return self.action_number_pending*-1 # Unconfirmed action
        if self.__is_action_pending():
            self.action_number_pending = self.action_number+1 # Increment
        return self.action_number_pending

    def confirm_action(self):
        """Confirms the currently pending action.

        If get_action_number() returned a number > 0, the corresponding action
        must be confirmed after it has been successfully performed. The action
        number then becomes the number of the pending action, and the number
        of the pending action becomes 0.
                             
        Args:
            None.
                    
        Returns:
            None.
        """
        if self.action_number_pending > 0:
            self.action_number = self.action_number_pending
            self.action_number_pending = 0

    def discard_action(self):
        """Confirms the currently pending action.

        This method resets the pending action number to 0 without checking the
        current status.
                         
        Args:
            None.
                    
        Returns:
            None.
        """
        self.action_number_pending = 0

    def reset_actions(self):
        """Resets the action number, pending action number and last timestamp.

        Args:
            None.
                    
        Returns:
            None.
        """
        self.action_number_pending = 0
        self.action_number = 0
        self.last_timestamp = None
        self.interval_switch = False

    def close(self):
        """Closes the data storage.
        
        Args:
            None.
        
        Returns:
            None
        """
        self.reset_actions()

    # =================
    # 'tostring' method
    # =================

    def __str__(self):
        """Creates a string representation of an instance of this class.

        Args:
            None.

        Returns:
            str: The string representation, JSON formatted.
        """
        s = {}
        s["class"] = self.__class__.__name__
        s["instance"] = id(self)
        s["name"] = self.name
        s["cmdpreset"] = self.cmdpreset
        s["days"] = self.days
        s["time_from"] = self.time_from
        s["time_to"] = self.time_to
        s["interval"] = self.interval
        s["interval_type"] = self.interval_type
        s["interval_seconds"] = self.interval_seconds
        s["interval_unit"] = self.interval_unit
        s["interval_switch"] = self.interval_switch
        s["time_from_timestamp"] = self.time_from_timestamp
        s["time_to_timestamp"] = self.time_to_timestamp
        s["time_from_diff"] = self.time_from_diff_secs
        s["time_to_diff"] = self.time_to_diff_secs
        s["remaining_actions"] = self.remaining_actions
        s["action_number"] = self.action_number
        s["action_number_pending"] = self.action_number_pending
        s["last_timestamp"] = self.last_timestamp
        return self.helper.dict2json(s)

    # ===============
    # Private methods
    # ===============

    def __set_params(self, schedset:dict):
        """Sets class instance params given with the schedule set.

        Args:
            schedset (dict): The schedule set.

        Returns:
            None.
        """
        cmdpreset = None
        days = []
        time_from = None
        time_to = None
        interval = None
        interval_type = None
        interval_seconds = None
        interval_unit = None
        try:
            # -------------------
            # Command preset name
            # -------------------
            value = schedset.get("cmdpreset")
            if value is None or len(value.strip()) == 0:
                raise Exception("Command preset name required.")
            cmdpreset = value
            # -------------------------------------
            # Day: "*" or number or CSV number list
            # -------------------------------------
            value = schedset.get("days")
            if value is None or len(value.strip()) == 0:
                raise Exception("At least one day number from range " \
                                "0 to 7, or '*' required.")
            else:
                value = value.strip()
            if value == '*':
                for i in range(1, 8): # Start at DAYS element 1
                    days.append(DAYS[i])
            else:
                daylist = value.split(",")
                if len(daylist) < 1:
                    raise Exception("At least one day number from range " \
                                "0 to 7, or '*' required.")
                if len(daylist) > 7:
                    raise Exception("A maximum of 7 day numbers from range " \
                                "0 to 7, or '*' required.")
                for day in daylist:
                    days.append(DAYS[int(day.strip())])
                if len(days) != len(daylist):
                    raise Exception("Invalid list of days.")
            # -------------------------------------------
            # Time: None or %H:%M:%S or %H:%M:%S-%H:%M:%S
            # -------------------------------------------
            value = schedset.get("time")
            if value is not None:
                times = value.split("-")
                time_from = times[0].strip()
                if len(times) > 1:
                    time_to = times[1].strip()
            if time_from is not None and len(time_from) != 8:
                raise Exception("Invalid time-from value.")
            if time_to is not None and len(time_to) != 8:
                raise Exception("Invalid time-to value.")
            # --------------------------------------
            # Interval: None or seconds or time unit
            # --------------------------------------
            value = schedset.get("intervaldiff")
            if value is not None:
                t = type(value)
                if t is int:
                    interval_type = TYPE_DIFF
                    interval_seconds = int(value)
                    interval = interval_seconds
                    if interval_seconds < DIFF_SECONDS_RANGE[0] or \
                        interval_seconds > DIFF_SECONDS_RANGE[1]:
                        raise Exception(f"Valid intervaldiff range: "\
                                        f"{str(DIFF_SECONDS_RANGE)} seconds.")
                else:
                    raise Exception(f"Invalid intervaldiff: '{str(value)}'")
            else:
                value = schedset.get("intervalunit")
                if value is not None:
                    t = type(value)
                    if t is str:
                        interval_type = TYPE_UNIT
                        interval_unit = value.strip()
                        interval = interval_unit
                        if interval_unit not in UNIT_VALUES:
                            raise Exception(f"Valid intervalunit values: "\
                                            f"{str(UNIT_VALUES)}")
                    else:
                        raise Exception(f"Invalid intervalunit: "\
                                        f"'{str(value)}'")

            # ------------
            # Plausibility
            # ------------
            if time_from is not None and time_to is None and interval is not None:
                raise Exception("Time-from without time-to requires "\
                                "interval None.")
            if time_from is not None and time_to is not None and interval is None:
                raise Exception("Time range requires interval value.")
            if time_to is not None and time_from is None:
                raise Exception("Time-to without time-from is invalid.")
            if time_from is None and interval is None:
                raise Exception("Neither time from nor interval is given.")
            # ----------------------
            # Set instance variables
            # ----------------------
            self.cmdpreset = cmdpreset
            self.days = days
            if time_from is not None:
                self.time_from = time_from
            else:
                self.time_from = "00:00:00" # Start of day
            if time_to is not None:
                self.time_to = time_to
            else:
                self.time_to = "23:59:59" # End of day
            self.interval = interval
            self.interval_type = interval_type
            self.interval_seconds = interval_seconds
            self.interval_unit = interval_unit
        # ---------------------------
        # Complete a raised exception
        # ---------------------------
        except Exception as exception:
            raise Exception(f"Invalid schedule setting at schedule set "\
                            f"'{self.name}': {exception}") from exception

    def __is_action_pending(self):
        """Checks if an action is pending according to the schedule settings.

        Args:
            None.

        Returns:
            bool: True if an action is pending, else False. 
        """
        # ---------------------
        # Date and time from/to
        # ---------------------
        date1 = self.helper.date()
        date2 = date1
        t1 = int(self.time_from.replace(":", ""))
        t2 = int(self.time_to.replace(":", ""))
        if t2 < t1:
            # ----------------------------
            # Time to is exceeding the day
            # ----------------------------
            t = int(self.helper.timestamp()[11:].replace(":", ""))
            if t2 < t:
                # -------------------
                # Time to is tomorrow
                # -------------------
                date2 = self.helper.date_shift(date2, 1)
            else:
                # ----------------------
                # Time from is yesterday
                # ----------------------
                date1 = self.helper.date_shift(date1, -1)
        # -----------------
        # Timestamp from/to
        # -----------------
        ts1 = date1 + " " + self.time_from
        ts2 = date2 + " " + self.time_to
        self.time_from_timestamp = ts1
        self.time_to_timestamp = ts2
        # -----------------------------------------------------------
        # Check if current day (respectively yesterday) is irrelevant
        # -----------------------------------------------------------
        day = self.helper.timestamp_pretty(ts1, "en").split(",")[0]
        if day not in self.days:
            return False # Day is not in schedule days, return False
        # -----------------------------------
        # Check if current time is irrelevant
        # -----------------------------------
        diff1 = self.helper.time_diff(ts1, "seconds")
        diff2 = self.helper.time_diff(ts2, "seconds")
        self.time_from_diff_secs = diff1
        self.time_to_diff_secs = diff2
        if diff1 < 0.0 or diff2 > 0.0:
            return False # Time is not in time window, return False
        # -----------------------------------------
        # Relevant day, current time in time window
        # -----------------------------------------
        if self.last_timestamp is None:
            # ----------------------------------------------------
            # If last timestamp is None, the first action after
            # scheduler initialization or action reset is pending.
            # So set last timestamp and return True, unless an
            # interval of type unit is set
            # ----------------------------------------------------
            if self.interval is None or self.interval_type != TYPE_UNIT:
                self.last_timestamp = self.helper.timestamp()
                self.__set_remaining_actions(abs(int(diff2)))
                return True # Action pending
        if self.interval is None:
            # ------------------------------------------------------
            # No interval means one-time-action per day, so check if
            # last timestamp is in the current time window. If so,
            # return False, else set last timestamp and return True
            # ------------------------------------------------------
            diff1 = self.helper.time_diff(ts1, "seconds", self.last_timestamp)
            diff2 = self.helper.time_diff(ts2, "seconds", self.last_timestamp)
            if diff1 >= 0.0 and diff2 <= 0.0:
                return False # In time window, action already performed
            self.last_timestamp = self.helper.timestamp()
            self.__set_remaining_actions(None)
            return True # Not in time window, action pending
        else:
            # --------------------------------------------------------
            # Interval means n-time-action. If it is time for the next
            # action, set last timestamp and return True, else False
            # --------------------------------------------------------
            if self.interval_type == TYPE_DIFF:
                if self.__is_time_for_interval_diff_action():
                    self.last_timestamp = self.helper.timestamp()
                    self.__set_remaining_actions(abs(int(diff2)))
                    return True # Action pending
            elif self.interval_type == TYPE_UNIT:
                if self.__is_time_for_interval_unit_action():
                    self.last_timestamp = self.helper.timestamp()
                    self.__set_remaining_actions(abs(int(diff2)))
                    return True # Action pending
            else:
                raise Exception(f"Invalid interval type: "\
                                f"'{self.interval_type}'")
            return False # Action currently not pending

    def __is_time_for_interval_diff_action(self):
        """Checks whether the current time indicates an action.

        Args:
            None.

        Returns:
            bool: True if it is time for action, else False.
        """
        diff = self.helper.time_diff(self.last_timestamp, "seconds")
        if diff >= 0.0 and diff >= self.interval_seconds:
            return True
        return False

    def __is_time_for_interval_unit_action(self):
        """Checks whether the current time indicates an action.

        Args:
            None.

        Returns:
            bool: True if it is time for action, else False.
        """
        # ---------------------
        # Current time elements
        # ---------------------
        ts = self.helper.timestamp()
        h = int(ts[11:-6])
        m = int(ts[14:-3])
        s = int(ts[17:])

        # -------------------
        # Handle unit one day
        # -------------------
        if self.interval_unit == UNIT_1_DAY:
            if self.interval_switch is False:
                if h == 0 and m == 0 and s < UNIT_START_LIMIT_SECOND:
                    self.interval_switch = True
                    return True
            else:
                if h == 23 and m == 59 and s > UNIT_END_LIMIT_SECOND:
                    self.interval_switch = False
                    return True
            return False

        # --------------------
        # Handle unit one hour
        # --------------------
        if self.interval_unit == UNIT_1_HOUR:
            if self.interval_switch is False:
                if m == 0 and s < UNIT_START_LIMIT_SECOND:
                    self.interval_switch = True
                    return True
            else:
                if m == 59 and s > UNIT_END_LIMIT_SECOND:
                    self.interval_switch = False
                    return True
            return False

        # ---------------------
        # Handle unit 5 minutes
        # ---------------------
        if self.interval_unit == UNIT_5_MINUTES:
            if self.interval_switch is False:
                if m > 0 and m < 5:
                    return False
                if m % 5 == 0 and s < UNIT_START_LIMIT_SECOND:
                    self.interval_switch = True
                    return True
            else:
                if m < 4:
                    return False
                if (m+1) % 5 == 0 and s > UNIT_END_LIMIT_SECOND:
                    self.interval_switch = False
                    return True
            return False

        # ----------------------------------------------------------
        # This step should never be reached, but return False anyway
        # ----------------------------------------------------------
        return False

    def __set_remaining_actions(self, time_to_diff:int):
        """Sets the number of remaining actions.

        Args:
            time_to_diff (int): Seconds until time window end.

        Returns:
            None.
        """
        remainder = 0
        remaining_actions = 0
        if self.interval_type is None:
            # ---------------
            # One time action
            # ---------------
            remaining_actions = 0
        elif self.interval_type == TYPE_DIFF:
            # ---------------------
            # Difference in seconds
            # ---------------------
            if time_to_diff <= 0:
                remaining_actions = 0
            elif time_to_diff < self.interval_seconds:
                remaining_actions = 0
            else:
                remaining_actions = int(time_to_diff / self.interval_seconds)
        else:
            # -----------------
            # Time unit seconds
            # -----------------
            unit_seconds = 0
            if self.interval_unit == UNIT_1_DAY:
                unit_seconds = UNIT_1_DAY_SECONDS
            elif self.interval_unit == UNIT_1_HOUR:
                unit_seconds = UNIT_1_HOUR_SECONDS
            else:
                unit_seconds = UNIT_5_MINUTES_SECONDS
            # -----------------------
            # 2 actions per time unit
            # -----------------------
            remaining_actions = int(time_to_diff / unit_seconds) * 2
            remainder = time_to_diff % unit_seconds
            if self.interval_switch is True:
                if remainder == 0:
                    remaining_actions -=1
                else:
                    remaining_actions +=1
        # --------------------------
        # Local to instance variable
        # --------------------------
        self.remaining_actions = remaining_actions

        if self.test:
            print(f"TEST Scheduler.set_remaining_actions " \
                  f"diff/type/unit/remainder//switch/actions: " \
                  f"{time_to_diff}/{self.interval_type}/{self.interval_unit}/" \
                  f"{remainder}/{self.interval_switch}/{remaining_actions}")
