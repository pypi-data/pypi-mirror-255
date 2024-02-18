# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0718
#pylint: disable=W1401

import unittest

from myminapp.lib.util.helper import Helper

class TestHelper(unittest.TestCase):

    """Test class."""

    def test_util(self):
        """Performs a utility test.
        
        Args:
            None.

        Returns:
            None.
        """
        util = Helper()
        try:

            # ------------------------
            # Message without variable
            # ------------------------
            result = util.mtext(0)
            print(f"Result mtext: {result}")
            self.assertEqual(result, "OK")

            # ---------------------
            # Message with variable
            # ---------------------
            result = util.mtext(104, 'Test')
            print(f"Result mtext: {result}")
            self.assertEqual(result, "Info: Test")

            # ---------------------------------------------------
            # Traceback line of exception due to division by zero
            # ---------------------------------------------------
            result = None
            try:
                _ = 1/0 # Division by zero
            except ZeroDivisionError:
                result = util.tbline()
                print(f"Result of division by zero: {util.tbline()}")
            self.assertIn("ZeroDivisionError", result)

            # ----------
            # Log levels
            # ----------
            loglevel = util.mlevel(0)
            print(f"Result mlevel log level message code 0: {loglevel}")
            self.assertEqual(loglevel, "INFO")

            loglevel = util.mlevel(1)
            print(f"Result mlevel log level message code 1: {loglevel}")
            self.assertEqual(loglevel, "ERROR")

            loglevel = util.mlevel(2)
            print(f"Result mlevel log level message code 2: {loglevel}")
            self.assertEqual(loglevel, "WARNING")

            loglevel = util.mlevel(200)
            print(f"Result mlevel log level message code 200: {loglevel}")
            self.assertEqual(loglevel, "INFO")

            loglevel = util.mlevel(201)
            print(f"Result mlevel log level message code 201: {loglevel}")
            self.assertEqual(loglevel, "ERROR")

            # ---------------
            # JSON conversion
            # ---------------
            data = {'name1': 'value1', 'name2': 'value2'}
            self.assertIsInstance(data, dict)

            to_json = util.dict2json(data)
            print(f"Result dict2json for {data}: {to_json}")
            self.assertIsInstance(to_json, str)

            to_dict = util.json2dict(to_json)
            print(f"Result json2dict for {to_json}: {to_dict}")
            self.assertIsInstance(to_dict, dict)

            self.assertEqual(data, to_dict)

            # ------------------------
            # Base64 encoding/decoding
            # ------------------------
            s = 'ABCabc123#äöü*%$§"ß\/ _+-~'
            base64 = 'QUJDYWJjMTIzI8Okw7bDvColJMKnIsOfXC8gXystfg=='

            to_base64 = util.str_to_base64(s)

            print(f"Result str_to_base64 for {s}: {to_base64}")
            self.assertEqual(to_base64, base64)

            to_str = util.base64_to_str(to_base64)
            print(f"Result base64_to_str for {to_base64}: {to_str}")
            self.assertEqual(to_str, s)

            # ----------------
            # Timestamp pretty
            # ----------------
            ts = "2023-12-01 15:01:23"

            tsp = util.timestamp_pretty(ts, "de")
            print(f"Result timestamp pretty for {ts} (de): {tsp}")
            self.assertEqual(tsp, "Freitag, 01.12.2023, 15:01:23")

            tsp = util.timestamp_pretty(ts, "en")
            print(f"Result timestamp pretty for {ts} (en): {tsp}")
            self.assertEqual(tsp, "Friday, Dec 01, 2023, 15:01:23")

            # ----------------
            # Time units label
            # ----------------
            label = util.time_units_label(2023)
            print(f"Result time units label 2023: {label}")
            self.assertEqual(label, "2023")

            label = util.time_units_label(202305)
            print(f"Result time units label 202305: {label}")
            self.assertEqual(label, "2023-05")

            label = util.time_units_label(2023051201)
            print(f"Result time units label 2023051201: {label}")
            self.assertEqual(label, "2023-05-12 01")

            label = util.time_units_label(20230512010203)
            print(f"Result time units label 20230512010203: {label}")
            self.assertEqual(label, "2023-05-12 01:02:03")

            # ---------------
            # Timestamp valid
            # ---------------
            b = util.timestamp_valid("2023-11-15 00:00:00")
            print(f"Result timestamp valid 2023-11-15 00:00:00: {b}")
            self.assertTrue(b)

            b = util.timestamp_valid("2023-13-15 00:00:00")
            print(f"Result timestamp valid 2023-13-15 00:00:00: {b}")
            self.assertFalse(b)

            b = util.timestamp_valid("2023-02-29 00:00:00")
            print(f"Result timestamp valid 2023-02-29 00:00:00: {b}")
            self.assertFalse(b)

            b = util.timestamp_valid("2023-11-15 23:59:59")
            print(f"Result timestamp valid 2023-11-15 23:59:59: {b}")
            self.assertTrue(b)

            b = util.timestamp_valid("2023-11-15 24:59:59")
            print(f"Result timestamp valid 2023-11-15 24:59:59: {b}")
            self.assertFalse(b)

            # ---------
            # Time diff
            # ---------
            t = util.time_diff("2023-11-22 08:00:00", "seconds",
                                     "2023-11-22 09:00:00")
            print(f"Result time diff 2023-11-22 08:00:00, seconds, "\
                                    f"2023-11-22 09:00:00: {t}")
            self.assertEqual(t, 3600.0)

            t = util.time_diff("2023-11-22 08:00:00", "seconds",
                                     "2023-11-22 07:00:00")
            print(f"Result time diff 2023-11-22 08:00:00, seconds, "\
                                    f"2023-11-22 07:00:00: {t}")
            self.assertEqual(t, -3600.0)

            t = util.time_diff("2023-11-22 23:00:00", "seconds",
                                     "2023-11-23 01:00:00")
            print(f"Result time diff 2023-11-22 23:00:00, seconds, "\
                                    f"2023-11-23 01:00:00: {t}")
            self.assertEqual(t, 7200.0)

            t = util.time_diff("2023-11-23 00:30:00", "seconds",
                                     "2023-11-23 00:10:00")
            print(f"Result time diff 2023-11-23 00:30:00, seconds, "\
                                    f"2023-11-23 00:10:00: {t}")
            self.assertEqual(t, -1200.0)

            t = util.time_diff("2023-11-23 00:30:00", "seconds",
                                     "2023-11-23 00:40:00")
            print(f"Result time diff 2023-11-23 00:30:00, seconds, "\
                                    f"2023-11-23 00:40:00: {t}")
            self.assertEqual(t, 600.0)

            # ----------
            # Time shift
            # ----------

            # --------------------------------------------------------------
            # Note:
            # --------------------------------------------------------------
            # Method time_shift adjusts to stay ahead of unit limits:
            #
            # if shift > 0:
            #  secs -= 1 # Subtract 1 second to stay ahead of the unit limit
            # elif shift < 0:
            #  secs += 1 # Add 1 second to stay ahead of the unit limit
            #
            # For more information see myminapp manual, appendix, chapter
            # 'Recording data for statistical purposes'.
            #
            # So results such as the following are correct:
            #
            # d = util.time_shift("2023-11-15 00:00:00", "minutes", -1)
            # self.assertEqual(d, "2023-11-14 23:59:01")
            #
            # d = util.time_shift("2023-11-15 00:00:00", "minutes", 1)
            # self.assertEqual(d, "2023-11-15 00:00:59")
            # --------------------------------------------------------------

            # minutes, hours, days minus
            # --------------------------

            d = util.time_shift("2023-11-15 00:00:00", "minutes", -1)
            print(f"Result time shift 2023-11-15 00:00:00 m -1  : {d}")
            self.assertEqual(d, "2023-11-14 23:59:01")

            d = util.time_shift("2023-11-15 00:00:01", "minutes", -1)
            print(f"Result time shift 2023-11-15 00:00:01 m -1  : {d}")
            self.assertEqual(d, "2023-11-14 23:59:02")

            d = util.time_shift("2023-11-15 00:00:59", "minutes", -1)
            print(f"Result time shift 2023-11-15 00:00:59 m -1  : {d}")
            self.assertEqual(d, "2023-11-15 00:00:00")

            d = util.time_shift("2023-11-15 00:00:00", "minutes", -30)
            print(f"Result time shift 2023-11-15 00:00:00 m -30 : {d}")
            self.assertEqual(d, "2023-11-14 23:30:01")

            d = util.time_shift("2023-11-15 00:00:00", "minutes", -60)
            print(f"Result time shift 2023-11-15 00:00:00 m -60 : {d}")
            self.assertEqual(d, "2023-11-14 23:00:01")

            d = util.time_shift("2023-11-15 00:00:00", "minutes", -61)
            print(f"Result time shift 2023-11-15 00:00:00 m -61 : {d}")
            self.assertEqual(d, "2023-11-14 22:59:01")

            d = util.time_shift("2023-11-15 00:01:00", "minutes", -61)
            print(f"Result time shift 2023-11-15 00:01:00 m -61 : {d}")
            self.assertEqual(d, "2023-11-14 23:00:01")

            d = util.time_shift("2023-11-15 00:00:00", "hours", -1)
            print(f"Result time shift 2023-11-15 00:00:00 h -1  : {d}")
            self.assertEqual(d, "2023-11-14 23:00:01")

            d = util.time_shift("2023-11-15 00:00:00", "days", -1)
            print(f"Result time shift 2023-11-15 00:00:00 d -1  : {d}")
            self.assertEqual(d, "2023-11-14 00:00:01")

            d = util.time_shift("2023-11-15 00:00:00", "days", -360)
            print(f"Result time shift 2023-11-15 00:00:00 d -360: {d}")
            self.assertEqual(d, "2022-11-20 00:00:01")

            d = util.time_shift("2023-02-28 23:59:59", "days", -1)
            print(f"Result time shift 2023-02-28 23:59:59 d -1  : {d}")
            self.assertEqual(d, "2023-02-28 00:00:00")

            d = util.time_shift("2023-02-28 23:59:59", "days", -2)
            print(f"Result time shift 2023-02-28 23:59:59 d -2  : {d}")
            self.assertEqual(d, "2023-02-27 00:00:00")

            # minutes, hours, days plus
            # -------------------------

            d = util.time_shift("2023-11-15 00:00:00", "minutes", 1)
            print(f"Result time shift 2023-11-15 00:00:00 m +1  : {d}")
            self.assertEqual(d, "2023-11-15 00:00:59")

            d = util.time_shift("2023-11-15 00:00:01", "minutes", 1)
            print(f"Result time shift 2023-11-15 00:00:01 m +1  : {d}")
            self.assertEqual(d, "2023-11-15 00:01:00")

            d = util.time_shift("2023-11-15 00:00:59", "minutes", 1)
            print(f"Result time shift 2023-11-15 00:00:59 m +1  : {d}")
            self.assertEqual(d, "2023-11-15 00:01:58")

            d = util.time_shift("2023-11-15 00:00:00", "minutes", 30)
            print(f"Result time shift 2023-11-15 00:00:00 m +30 : {d}")
            self.assertEqual(d, "2023-11-15 00:29:59")

            d = util.time_shift("2023-11-15 00:00:00", "minutes", 60)
            print(f"Result time shift 2023-11-15 00:00:00 m +60 : {d}")
            self.assertEqual(d, "2023-11-15 00:59:59")

            d = util.time_shift("2023-11-15 00:00:00", "minutes", 61)
            print(f"Result time shift 2023-11-15 00:00:00 m +61 : {d}")
            self.assertEqual(d, "2023-11-15 01:00:59")

            d = util.time_shift("2023-11-15 00:01:00", "minutes", 61)
            print(f"Result time shift 2023-11-15 00:01:00 m +61 : {d}")
            self.assertEqual(d, "2023-11-15 01:01:59")

            d = util.time_shift("2023-11-15 00:00:00", "hours", 1)
            print(f"Result time shift 2023-11-15 00:00:00 h +1  : {d}")
            self.assertEqual(d, "2023-11-15 00:59:59")

            d = util.time_shift("2023-11-15 00:00:00", "days", 1)
            print(f"Result time shift 2023-11-15 00:00:00 d +1  : {d}")
            self.assertEqual(d, "2023-11-15 23:59:59")

            d = util.time_shift("2023-11-15 00:00:00", "days", 360)
            print(f"Result time shift 2023-11-15 00:00:00 d +360: {d}")
            self.assertEqual(d, "2024-11-08 23:59:59")

            d = util.time_shift("2023-02-28 00:00:00", "days", 1)
            print(f"Result time shift 2023-02-28 00:00:00 d +1  : {d}")
            self.assertEqual(d, "2023-02-28 23:59:59")

            d = util.time_shift("2023-02-28 00:00:00", "days", 2)
            print(f"Result time shift 2023-02-28 00:00:00 d +2  : {d}")
            self.assertEqual(d, "2023-03-01 23:59:59")

            # ----------------------
            # Int to ISO, ISO to int
            # ----------------------
            ts = util.timestamp_int2iso(20230102030405)
            print(f"Result timestamp_int2iso 20230102030405: {ts}")
            self.assertEqual(ts, "2023-01-02 03:04:05")

            ts = util.timestamp_iso2int("2023-01-02 03:04:05")
            print(f"Result timestamp_iso2int 2023-01-02 03:04:05: {ts}")
            self.assertEqual(ts, 20230102030405)

            # -----------------
            # Last day of month
            # -----------------
            ldm = util.last_day_of_month(2023, 1)
            print(f"Result last day of month 2023, 1: {ldm}")
            self.assertEqual(ldm, 31)

            # -------------------
            # Complete timestamps
            # -------------------

            # From and to given explicitly
            # ----------------------------

            ts1, ts2 = util.complete_timestamps(2023, 2023)
            print(f"Result complete timestamps 2023, 2023: {ts1}, {ts2}")
            self.assertEqual(ts1, 20230101000000)
            self.assertEqual(ts2, 20231231235959)

            ts1, ts2 = util.complete_timestamps(20231015, 202310)
            print(f"Result complete timestamps 20231015, 202310: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231015000000)
            self.assertEqual(ts2, 20231031235959)

            ts1, ts2 = util.complete_timestamps(202310, 20231015)
            print(f"Result complete timestamps 202310, 20231015: " \
                  f"{ts1}, {ts2}")
            self.assertEqual(ts1, 20231001000000)
            self.assertEqual(ts2, 20231015235959)

            ts1, ts2 = util.complete_timestamps(2023101500, 2023101500)
            print(f"Result complete timestamps 2023101500, 2023101500: " \
                  f"{ts1}, {ts2}")
            self.assertEqual(ts1, 20231015000000)
            self.assertEqual(ts2, 20231015005959)

            # From given explicitly, to as d (days), h (hours), m (months)
            # ------------------------------------------------------------

            ts1, ts2 = util.complete_timestamps(2023, '10d')
            print(f"Result complete timestamps 2023, '10d': {ts1}, {ts2}")
            self.assertEqual(ts1, 20230101000000)
            self.assertEqual(ts2, 20230110235959)

            ts1, ts2 = util.complete_timestamps(20231115, '10d')
            print(f"Result complete timestamps 20231115, '10d': {ts1}, {ts2}")
            self.assertEqual(ts1, 20231115000000)
            self.assertEqual(ts2, 20231124235959)

            ts1, ts2 = util.complete_timestamps(20231115, '240h')
            print(f"Result complete timestamps 20231115, '240h': {ts1}, {ts2}")
            self.assertEqual(ts1, 20231115000000)
            self.assertEqual(ts2, 20231124235959)

            ts1, ts2 = util.complete_timestamps(20231115, '14400m')
            print(f"Result complete timestamps 20231115, '14400m': {ts1}, {ts2}")
            self.assertEqual(ts1, 20231115000000)
            self.assertEqual(ts2, 20231124235959)

            ts1, ts2 = util.complete_timestamps(20231115, '14399m')
            print(f"Result complete timestamps 20231115, '14399m': {ts1}, {ts2}")
            self.assertEqual(ts1, 20231115000000)
            self.assertEqual(ts2, 20231124235859)

            ts1, ts2 = util.complete_timestamps(20231115, '14401m')
            print(f"Result complete timestamps 20231115, '14401m': {ts1}, {ts2}")
            self.assertEqual(ts1, 20231115000000)
            self.assertEqual(ts2, 20231125000059)

            # From given as d (days), h (hours), m (months), to explicitly
            # ------------------------------------------------------------

            ts1, ts2 = util.complete_timestamps('10d', '2023')
            print(f"Result complete timestamps '10d', 2023: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231222000000)
            self.assertEqual(ts2, 20231231235959)

            ts1, ts2 = util.complete_timestamps('10d', '20231115')
            print(f"Result complete timestamps '10d', 20231115: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231106000000)
            self.assertEqual(ts2, 20231115235959)

            ts1, ts2 = util.complete_timestamps('240h', '20231115')
            print(f"Result complete timestamps '240h', 20231115: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231106000000)
            self.assertEqual(ts2, 20231115235959)

            ts1, ts2 = util.complete_timestamps('14400m', '20231115')
            print(f"Result complete timestamps '14400m', 20231115: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231106000000)
            self.assertEqual(ts2, 20231115235959)

            ts1, ts2 = util.complete_timestamps('14399m', '20231115')
            print(f"Result complete timestamps '14399m', 20231115: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231106000100)
            self.assertEqual(ts2, 20231115235959)

            ts1, ts2 = util.complete_timestamps('14401m', '20231115')
            print(f"Result complete timestamps '14401m', 20231115: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231105235900)
            self.assertEqual(ts2, 20231115235959)

            ts1, ts2 = util.complete_timestamps('5d', '2023')
            print(f"Result complete timestamps '5d', 2023: {ts1}, {ts2}")
            self.assertEqual(ts1, 20231227000000)
            self.assertEqual(ts2, 20231231235959)

            # Invalid timestamp
            # -----------------
            result = None
            try:
                ts1, ts2 = util.complete_timestamps('10d', '20230231')
            except Exception as exception:
                result = str(exception).lower()
                print(f"Result invalid timestamp '10d', 20230231: {result}")
            self.assertIn("invalid timestamp", result)

            # Invalid unit input (integer with suffix 's')
            # --------------------------------------------
            result = None
            try:
                ts1, ts2 = util.complete_timestamps('10s', '2023')
            except Exception as exception:
                result = str(exception).lower()
                print(f"Result invalid unit '10s', 2023: {result}")
            self.assertIn("invalid literal", result)

        finally:
            if util is not None:
                util.close()

if __name__ == '__main__':
    unittest.main()
