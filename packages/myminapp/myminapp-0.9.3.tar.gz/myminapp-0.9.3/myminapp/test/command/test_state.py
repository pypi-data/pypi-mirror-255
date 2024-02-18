# -*- coding: utf-8 -*-
"""myminapp"""

import unittest

from myminapp.test.command.testutil import TestUtil

class TestState(unittest.TestCase):

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
        dcnames = ['DTSU', 'Fritz']
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

            cmdinput = {}
            cmdinput['app'] = 'app1'
            cmdinput['devname'] = "SOLAR"
            cmdinput['devcat'] = "P"
            self.__perform_command(command, cmdinput)

            cmdinput = {}
            cmdinput['app'] = 'app1'
            cmdinput['devname'] = "EM"
            cmdinput['devcat'] = "M"
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
    