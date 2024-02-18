# -*- coding: utf-8 -*-
"""myminapp"""

import unittest

from myminapp.test.command.testutil import TestUtil

class TestPsCharge(unittest.TestCase):

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
        dcnames = ['DTSU', 'Fritz', 'Bosch']
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

            # ------------------------------------------------------
            #  !!! This does powerstation charging in real world !!!
            # ------------------------------------------------------

            cmdinput = {}
            cmdinput['app'] = "app1"
            cmdinput['value'] = "cmax=50, smin=80"
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
