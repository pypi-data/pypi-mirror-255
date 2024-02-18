# -*- coding: utf-8 -*-
"""myminapp"""

import unittest

from myminapp.test.command.testutil import TestUtil

TESTDB_NAME = "test_epstats"

class TestSelection(unittest.TestCase):

    """Test class."""

    def test_command(self):
        """Performs a command test.
        
        Args:
            None.

        Returns:
            None.
        """
        command = TestUtil().get_instance(
            self.__class__.__name__.lower().replace("test", "")
        )
        try:

            # ----------------------------------------------------------
            # This test uses the pre-filled test database 'test_epstats'
            # ----------------------------------------------------------

            cmdinput = {}
            cmdinput["app"] = TESTDB_NAME
            cmdinput["value"] = "SELECT * FROM state WHERE devcat = 'P' AND power > 1900.0"
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

if __name__ == '__main__':
    unittest.main()
