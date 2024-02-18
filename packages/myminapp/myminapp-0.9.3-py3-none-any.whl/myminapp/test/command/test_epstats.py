# -*- coding: utf-8 -*-
"""myminapp"""

import unittest

from myminapp.test.command.testutil import TestUtil

TESTDB_NAME = "test_epstats"

class TestEPStats(unittest.TestCase):

    """Test class."""

    def test_command(self):
        """Performs a command test.
        
        Args:
            None.

        Returns:
            None.
        """
        # ----------------------------------------------
        # Check if required device classes are specified
        # ----------------------------------------------
        dcnames = ['Chart']
        if TestUtil().check_devspec(dcnames) is False:
            print(f"Skipping '{self.__class__.__name__}'.")
            return
        # --------------------
        # Get command instance
        # --------------------
        command = TestUtil().get_instance(
            self.__class__.__name__.lower().replace("test", "")
        )
        try:

            # -----------------------------------------------------------
            # Note
            # -----------------------------------------------------------
            # This test uses the pre-filled test database 'test_epstats'.
            # Charts (SVG files) can be found at /data/temp/chart.
            # -----------------------------------------------------------

            # ------
            # Energy
            # ------
            cmdinput = {}
            cmdinput["app"] = TESTDB_NAME
            cmdinput["type"] = "energy"
            cmdinput["entity"] = "state" # entity 'state' or copies of it
            cmdinput["units"] = 4
            cmdinput["from"] = '1d'
            cmdinput["to"] = 2024012511
            cmdinput["devname"] = "EM, TV, FRIDGE, DESKTOP, WASHER, SOLAR"
            self.__perform_command(command, cmdinput)

            # -----
            # Power
            # -----
            cmdinput = {}
            cmdinput["app"] = TESTDB_NAME
            cmdinput["type"] = "power"
            cmdinput["entity"] = "state" # entity 'state' or copies of it
            cmdinput["units"] = 4
            cmdinput["from"] = '1d'
            cmdinput["to"] = 2024012511
            cmdinput["devname"] = "EM, TV, FRIDGE, DESKTOP, WASHER, SOLAR"
            self.__perform_command(command, cmdinput)

            # ----------
            # Power PLUS
            # ----------
            cmdinput = {}
            cmdinput["app"] = TESTDB_NAME
            cmdinput["type"] = "powerplus"
            cmdinput["entity"] = "state" # entity 'state' or copies of it
            cmdinput["units"] = 5
            cmdinput["from"] = '1d'
            cmdinput["to"] = 2024012511
            cmdinput["devname"] = "EM"
            cmdinput["devcat"] = "M"
            self.__perform_command(command, cmdinput)

        finally:
            if command is not None:
                command.close()

    def __perform_command(self, command:object, cmdinput:str):
        """Performs the given command.
            
        Args:
            command (object): Instance of a specific command class.
            cmdinput (dict): Command input.

        Returns:
            None.
        """
        output = command.exec(cmdinput)
        print(f"Result {command.name}: {output}")
        code = output[0].get('code')
        self.assertEqual(code, 0)
        if code == 0:
            info = output[0].get('data').get('info')
            self.assertEqual(info, "OK")

if __name__ == '__main__':
    unittest.main()
