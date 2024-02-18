# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0103
#pylint: disable=C0200
#pylint: disable=W0718
#pylint: disable=W0719

import calendar
import datetime
import traceback
import json
import base64
from textwrap import wrap

from myminapp.lib.text.message import get_text
from myminapp.lib.text.message import ERROR
from myminapp.lib.text.message import WARNING
from myminapp.lib.text.message import INFO
from myminapp.lib.text.message import DEBUG
from myminapp.lib.text.message import ERROR_CODES
from myminapp.lib.text.message import WARNING_CODES
from myminapp.lib.text.message import DEBUG_CODES

# =========
# Constants
# =========

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
         "Saturday", "Sunday"] # 0 or 7 for Sunday
DAY_NAMES_DE = {
            "Monday": "Montag",
            "Tuesday": "Dienstag",
            "Wednesday": "Mittwoch",
            "Thursday": "Donnerstag",
            "Friday": "Freitag",
            "Saturday": "Samstag",
            "Sunday": "Sonntag"
            }

class Helper:

    """
    Use this utility class as helper for general purposes.
    
    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Helper' setup.

        Args:
            None.

        Returns:
            None.
        """

    # ==============
    # Public methods
    # ==============

    def mtext(self, code:int, *args):
        """Returns a text matching the given code and the configured language.

        This method is a wrapper for text.message.get_text.
                 
        Args:
            code (int): Message code.
            *args (tuple): Optional variable arguments.
        
        Returns:
            str: The message text or None if not found.
        """
        text = get_text(code, *args)
        return text

    def mlevel(self, code:int):
        """Returns the log level for the given message code.

        Args:
            code (int): Message code.

        Returns:
            str: Traceback in a single line.
        """
        if code in ERROR_CODES:
            return ERROR
        elif code in WARNING_CODES:
            return WARNING
        elif code in DEBUG_CODES:
            return DEBUG
        else:
            return INFO # Default

    def tbline(self):
        """Returns the traceback of the current error in a single line.

        Args:
            None.

        Returns:
            str: Traceback in a single line.
        """
        tb = traceback.format_exc()
        return " ".join(str(tb).split())

    def dict2json(self, data:dict):
        """Converts dictonary to JSON.

        Args:
            data (dict): Data as dictionary.

        Returns:
            str: Data in JSON format.
        """
        return json.dumps(data, ensure_ascii=False) # Keep utf-8

    def json2dict(self, data:str):
        """Converts JSON to dictonary.

        Args:
            data (str): Data in JSON format.

        Returns:
            dict: Data as dictionary.
        """
        return json.loads(data)

    def complete_timestamps(self, tsfrom, tsto):
        """Completes the given timestamps.

        Args:
            tsfrom (*): Timestamp from, e.g. 20231015, or a number of units
                            followed by 'd' or 'h' or 'm', e.g. 32m.
            tsto (*): Timstamp to, e.g. 2023101612, or a number of units
                            followed by 'd' or 'h' or 'm', e.g. 32m.

        Returns:
            int, int: The complete(d) timestamps.
        """
        ts1 = None
        ts2 = None
        number = None
        unit = None
        # --------------
        # Timestamp from
        # --------------
        number, unit = self.__timestamp_input_type(str(tsfrom))
        if unit is None:
            ts1 = self.complete_timestamp(number, False) # Timestamp from
            number, unit = self.__timestamp_input_type(str(tsto))
            if unit is not None:
                # -------------------------------------------
                # Time shift into the future for timestamp to
                # -------------------------------------------
                ts2 = self.timestamp_iso2int(self.time_shift(
                    self.timestamp_int2iso(ts1), unit, number
                    ))
        # ------------
        # Timestamp to
        # ------------
        number, unit = self.__timestamp_input_type(str(tsto))
        if unit is None:
            ts2 = self.complete_timestamp(number, True) # Timestamp to
            number, unit = self.__timestamp_input_type(str(tsfrom))
            if unit is not None:
                # --------------------------
                # Adjust future timestamp to
                # --------------------------
                if self.time_diff(self.timestamp_int2iso(ts2), "seconds") < 60:
                    ts = self.timestamp() # Current timestamp
                    if unit == "days":
                        ts = ts[:11] + "23:59:59" # Complete current day
                    elif unit == "hours":
                        ts = ts[:14] + "59:59" # Complete current hour
                    elif unit == "minutes":
                        ts = ts[:17] + "59" # Complete current minute
                    else:
                        pass
                    ts2 = self.timestamp_iso2int(ts)
                # -------------------------------------------
                # Time shift into the past for timestamp from
                # -------------------------------------------
                ts1 = self.timestamp_iso2int(self.time_shift(
                    self.timestamp_int2iso(ts2), unit, (number*-1)
                    ))
        # -----------------
        # Return timestamps
        # -----------------
        return ts1, ts2

    def complete_timestamp(self, timestamp:int, to:bool):
        """Completes the given timestamp according to the type from or to.

        Args:
            timestamp (int): Timestamp as int, e.g. 2023, 2023101510,
                                20231015102059. Year is mandatory.
            to (bool): False for timestamp from, True for timestamp to.

        Returns:
            int: The completed timestamp as number.
        """
        MIN_TIME_FROM = "000000"
        MAX_TIME_TO   = "235959"
        VALID_LENGTHS = [4, 6, 8, 10, 12, 14]
        ts = None
        s = str(timestamp).strip()
        t = []
        if len(s) not in VALID_LENGTHS:
            raise Exception(f"Invalid timestamp input: '{s}'")
        try:
            int(s)
        except ValueError as exception:
            raise Exception(f"Invalid timestamp input: '{s}'") from exception
        t.append(str(s))
        if len(s) < 14:
            if to is False:
                if len(s) == 4:
                    t.append("0101")
                    t.append(MIN_TIME_FROM)
                elif len(s) == 6:
                    t.append("01")
                    t.append(MIN_TIME_FROM)
                else:
                    t.append(MIN_TIME_FROM[(len(s)-8):])
            else:
                if len(s) == 4:
                    t.append("1231")
                    t.append(MAX_TIME_TO)
                elif len(s) == 6:
                    t.append(str(self.last_day_of_month(
                            int(s[:4]), int(s[4:])
                        )))
                    t.append(MAX_TIME_TO)
                else:
                    t.append(MAX_TIME_TO[(len(s)-8):])
        ts = "".join(t)
        # -----------------------------
        # Validate and return timestamp
        # -----------------------------
        if self.timestamp_valid(self.timestamp_int2iso(ts)) is True:
            return int(ts)
        raise Exception(f"Invalid timestamp input: '{s}'")

    def time_units_label(self, value:int):
        """Generates a label from a time unit value.
    
        Args:
            value (int): Time units value, e.g. 202310, 2023102001.
            
        Returns:
            str: Time units label.
        """
        sep = ["-", "-", " ", ":", ":"]
        s = [str(value)[:4]]
        sn = wrap(str(value)[4:], 2)
        for i in range(0, len(sn)):
            s.append(sep[i])
            s.append(sn[i])
        return "".join(s)

    def timestamp(self):
        """Creates an ISO-formatted timestamp without timezone.

        Args:
            None.

        Returns:
            str: Timestamp in format '%Y-%m-%d %H:%M:%S'.
        """
        return datetime.datetime.now().isoformat(' ', 'seconds')

    def timestamp_valid(self, timestamp):
        """Validates an ISO-formatted timestamp without timezone.

        Args:
            timestamp (str): Timestamp in format '%Y-%m-%d %H:%M:%S'.

        Returns:
            bool: True if valid, else False.
        """
        fmt = '%Y-%m-%d %H:%M:%S'
        try:
            datetime.datetime.strptime(timestamp, fmt)
            return True
        except Exception:
            return False

    def timestamp_int2iso(self, timestamp:int):
        """Creates an ISO-formatted timestamp from the given 14-digit number.

        Args:
            timestamp (int): Timestamp as integer, e.g. 20231115010101.

        Returns:
            str: Timestamp in format '%Y-%m-%d %H:%M:%S'.
        """
        s = str(timestamp)
        return f"{s[:4]}-{s[4:-8]}-{s[6:-6]} {s[8:-4]}:{s[10:-2]}:{s[12:]}"

    def timestamp_iso2int(self, timestamp:str):
        """Creates a 14-digit number from the given ISO-formatted timestamp.

        Args:
            timestamp (str): Timestamp in format '%Y-%m-%d %H:%M:%S'.

        Returns:
            int: Timestamp as 14-digit number.
        """
        s = timestamp.replace("-", "").replace(":", "").replace(" ", "")
        return int(s)

    def timestamp_pretty(self, timestamp:str, lang:str):
        """Creates a pretty timestamp representation.
        
        Creates a language specific partial textual timestamp representation.
        Does NOT make use of locale.setlocale to avoid system-wide effects.
        
        Args:
            timestamp (str): Timestamp formatted as with self.timestamp().
            lang (str): Language code (currently 'de' or 'en').

        Returns:
            str: The timestamp representation.
        """
        dtn = datetime.datetime.fromisoformat(timestamp)
        if lang == "de":
            tp = dtn.strftime("%A, %d.%m.%Y, %H:%M:%S")
            for name in DAY_NAMES_DE:
                tp = tp.replace(name, DAY_NAMES_DE.get(name))
        elif lang == "en":
            tp = dtn.strftime("%A, %b %d, %Y, %H:%M:%S")
        else:
            raise Exception("Unsupported language code.")
        return tp

    def date(self):
        """Creates an ISO-formatted date without timezone.
        
        Creates an ISO-formatted date without timezone, i.e. fmt = '%Y-%m-%d'
        
        Args:
            None.
    
        Returns:
            str: Date in format '%Y-%m-%d'.
        """
        return self.timestamp().split(" ")[0]

    def time_shift(self, timestamp:str, unit:str, shift:int):
        """Gets the given time unit plus or minus the given shift.

        Args:
            timestamp (int): Timestamp formatted as with self.timestamp().
            unit (str): Unit minutes, hours, days).
            shift (int): Number of units plus or minus, e.g. 1 or -1.
    
        Returns:
            str: The shifted date and time.
        """
        # --------------------------------------------------
        # Expected results, staying ahead of the unit limits
        # --------------------------------------------------
        # self.time_shift('2023-02-28 00:00:00', 'days', 1)
        #                         -> 2023-02-28 23:59:59
        # self.time_shift('2023-02-28 00:00:00', 'days', 2)
        #                         -> 2023-03-01 23:59:59
        # self.time_shift('2023-02-28 23:59:59', 'days', -1)
        #                         -> 2023-02-28 00:00:00
        # self.time_shift('2023-02-28 23:59:59', 'days', -2)
        #                         -> 2023-02-27 00:00:00
        # --------------------------------------------------
        secs = 0
        if unit == "days":
            secs = int(shift * 86400)
        elif unit == "hours":
            secs = int(shift * 3600)
        elif unit == "minutes":
            secs = int(shift * 60)
        else:
            raise Exception(f"Invalid time_shift time unit: {unit}")
        if shift > 0:
            secs -= 1 # Subtract 1 second to stay ahead of the unit limit
        elif shift < 0:
            secs += 1 # Add 1 second to stay ahead of the unit limit
        else:
            pass
        fmt = '%Y-%m-%d %H:%M:%S'
        d1 = datetime.datetime.strptime(timestamp, fmt)
        d2 = d1 + datetime.timedelta(seconds=secs)
        return str(d2)

    def date_shift(self, date:str, shift:int):
        """Gets the given date plus or minus the given shift.

        Args:
            date (str): Date string representation in format '%Y-%m-%d'.
            shift (int): Number of days plus or minus (e.g. 1 or -1).
    
        Returns:
            str: The shifted date.
        """
        # -----------------------------------------------
        # Expected results:
        # -----------------------------------------------
        # self.date_shift('2023-02-28', 1)  -> 2023-03-01
        # self.date_shift('2023-02-28', -1) -> 2023-02-27
        # -----------------------------------------------
        fmt = '%Y-%m-%d'
        d1 = datetime.datetime.strptime(date, fmt)
        d2 = d1 + datetime.timedelta(days=shift)
        return str(d2)[:10]

    def time_diff(self, timestamp:str, unit:str, timestamp2=None):
        """Gets the difference between given and current or given second time.

        Args:
            timestamp (str): Timestamp formatted as with self.timestamp().
            unit (str): Unit seconds, minutes, hours, days).
            timestamp2 (str): Optional given second timestamp to compare.
    
        Returns:
            float: The difference as float with one decimal place.
        """
        fmt = '%Y-%m-%d %H:%M:%S'
        d1 = datetime.datetime.strptime(timestamp, fmt)
        if timestamp2 is None:
            d2 = datetime.datetime.strptime(self.timestamp(), fmt)
        else:
            d2 = datetime.datetime.strptime(timestamp2, fmt)
        sec = (d2-d1).total_seconds()
        diff = 0.0
        if unit == "days":
            diff = sec / 86400.0
        elif unit == "hours":
            diff = sec / 3600.0
        elif unit == "minutes":
            diff = sec / 60.0
        else:
            diff = sec
        return round(diff, 1)

    def last_day_of_month(self, year:int, month:int):
        """Receives the last day of a month.

        Args:
            year (str): 4-digit year.
            month (str): Month.

        Returns:
            int: Last day of month.
        """
        return calendar.monthrange(int(year), int(month))[1]

    def file_to_blob(self, file:str):
        """Converts file content to a binary large object.

        Args:
            file (str): Absolute path and file name.

        Returns:
            object: The binary large object.
        """
        with open(file, 'rb') as f:
            blob = f.read()
        return blob

    def blob_to_file(self, blob:object, file:str):
        """Converts a binary large object to file content and saves the file.

        Args:
            blob (object): The binary large object.
            file (str): Absolute path and file name.

        Returns:
            None.
        """
        with open(file, 'wb') as f:
            f.write(blob)

    def str_to_base64(self, s:str):
        """Encodes string to Base64.
        
        Encodes the given string to UTF-8 bytes, encodes the bytes to
        Base64 bytes, and decodes the Base64 bytes to ASCII string.

        Args:
            s (str): The string to encode.

        Returns:
            str: The encoded Base64 string.
        """
        b = bytes(s, encoding='utf-8')
        return base64.b64encode(b).decode('ascii')

    def base64_to_str(self, s:str):
        """Decodes Base64 to string.
        
        Decodes the given Base64 ASCII string to bytes, and decodes
        the bytes to UTF-8 string.

        Args:
            s (str): The Base64 ASCII string to decode.

        Returns:
            str: The decoded Base64 ASCII string.
        """
        return base64.b64decode(s).decode('utf-8')

    def close(self):
        """Pro forma.

        Args:
            None.

        Returns:
            None
        """
        # Nothing to close here.

    # ===============
    # Private methods
    # ===============

    def __timestamp_input_type(self, tsinput:str):
        """Detects the type of timestamp input.

        Args:
            tsinput (str): Timestamp as int, e.g. 20231015, or a number of
                            units followed by 'd' or 'h' or 'm', e.g. 32m.

        Returns:
            int: The detected number.
            str: The detected unit type.
        """
        UNITS = ['d', 'h', 'm']
        UNIT_MAP = {
            'd': 'days',
            'h': 'hours',
            'm': 'minutes',
        }
        number = None
        unit = None
        s = str(tsinput).replace(" ", "").strip()
        for u in UNITS:
            p = s.find(u)
            if p > 0:
                number = int(s[:p])
                unit = UNIT_MAP.get(u)
                break
        if unit is None:
            number = int(s)
        return number, unit
    