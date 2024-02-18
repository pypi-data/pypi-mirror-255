# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0915

import json
import time
import unittest

from myminapp.lib.util.scheduler import Scheduler

class TestScheduler(unittest.TestCase):

    """Test class."""

    def test_util(self):
        """Performs a utility test.
        
        Args:
            None.

        Returns:
            None.
        """
        try:

            # -----------------------------------------------
            # Series of tests which illustrates the principle
            # -----------------------------------------------

            name = "schedule_test"

            schedset = {}
            schedset["cmdpreset"] = "testpreset"
            schedset["days"] = "*"
            schedset["time"] = None
            schedset["intervaldiff"] = 5
            util = Scheduler(name, schedset)
            print(" ")
            print(util)
            print(" ")

            actnum = util.get_action_number()
            print(f"Result get_action_number: {actnum}")
            self.assertEqual(actnum, 1)
            if actnum > 0:
                util.confirm_action()
                print("Action confirmed.")

            for _ in range(0, 4):
                time.sleep(4)
                actnum = util.get_action_number()
                print(f"Result get_action_number: {actnum}")
                self.assertIn(actnum, [0, 2, 3])
                if actnum > 0:
                    util.confirm_action()
                    print("Action confirmed.")

            time.sleep(6)
            actnum = util.get_action_number()
            print(f"Result get_action_number: {actnum}")
            self.assertEqual(actnum, 4)

            # -----------
            # Unconfirmed
            # -----------
            actnum = util.get_action_number()
            self.assertEqual(actnum, -4)
            print(f"Result get_action_number: {actnum}")

            util.discard_action()
            print("Action discarded.")

            time.sleep(6)
            actnum = util.get_action_number()
            print(f"Result get_action_number: {actnum}")
            self.assertEqual(actnum, 4)
            if actnum > 0:
                util.confirm_action()
                print("Action confirmed.")

            # -----
            # Reset
            # -----
            util.reset_actions()
            print("Actions reset.")

            time.sleep(2)

            actnum = util.get_action_number()
            print(f"Result get_action_number: {actnum}")
            self.assertEqual(actnum, 1)
            if actnum > 0:
                util.confirm_action()
                print("Action confirmed.")

            # -------------------------------------
            # Schedule state via 'to string' method
            # -------------------------------------
            state = json.loads(str(util))
            print(" ")
            print(f"State: {state}")
            print(" ")
            self.assertEqual(state.get("name"), name)
            self.assertEqual(state.get("cmdpreset"), schedset["cmdpreset"])
            self.assertEqual(state.get("time_from"), "00:00:00")
            self.assertEqual(state.get("time_to"), "23:59:59")
            self.assertEqual(state.get("interval_type"), "diff")
            self.assertEqual(state.get("interval_seconds"), 5)
            self.assertEqual(state.get("action_number"), 1)
            self.assertEqual(state.get("action_number_pending"), 0)

            # ----------------------------------------
            # More possible settings for further tests
            # ----------------------------------------

            # One time action on sunday (days 0 or 7)
            # ---------------------------------------
            schedset = {}
            schedset["cmdpreset"] = "testpreset"
            schedset["days"] = "0"
            schedset["time"] = "10:00:01"
            schedset["intervaldiff"] = None
            util = Scheduler(name, schedset)
            #print(util)
            #print(" ")

            # Daily ongoing action every 5 seconds between 10 and 12 a.m.
            # -----------------------------------------------------------
            schedset = {}
            schedset["cmdpreset"] = "testpreset"
            schedset["days"] = "*"
            schedset["time"] = "10:00:01-12:00:00"
            schedset["intervaldiff"] = 5
            util = Scheduler(name, schedset)
            #print(util)
            #print(" ")

            # Daily ongoing action every 60 seconds on Monday and Wednesday
            # -------------------------------------------------------------
            schedset = {}
            schedset["cmdpreset"] = "testpreset"
            schedset["days"] = "1,3"
            schedset["time"] = None
            schedset["intervaldiff"] = 60
            util = Scheduler(name, schedset)
            #print(util)
            #print(" ")

            # Dayly ongoing action every 5 minutes between 16 p.m. and 9 a.m.
            # ---------------------------------------------------------------
            schedset = {}
            schedset["cmdpreset"] = "testpreset"
            schedset["days"] = "*"
            schedset["time"] = "16:00:00-09:00:00"
            schedset["intervalunit"] = "m"
            util = Scheduler(name, schedset)
            #print(util)
            #print(" ")

            # Weekend ongoing action every hour between 1 and 3 a.m.
            # ------------------------------------------------------
            schedset = {}
            schedset["cmdpreset"] = "testpreset"
            schedset["days"] = "6,7"
            schedset["time"] = "01:00:00-03:00:00"
            schedset["intervalunit"] = "h"
            util = Scheduler(name, schedset)
            #print(util)
            #print(" ")

        finally:
            if util is not None:
                util.close()

if __name__ == '__main__':
    unittest.main()
