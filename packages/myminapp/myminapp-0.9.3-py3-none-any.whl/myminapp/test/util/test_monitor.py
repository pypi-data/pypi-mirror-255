# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0123

import unittest

from myminapp.lib.util.monitor import Monitor

class TestMonitor(unittest.TestCase):

    """Test class."""

    def test_util(self):
        """Performs a utility test.
        
        Args:
            None.

        Returns:
            None.
        """
        util = Monitor()
        try:

            util.open()

            name = "a_name"

            # ------
            # Insert
            # ------
            value = {}
            value["text_1"] = "data_1"
            value["text_2"] = "data_2"
            util.insert(name, value)
            print(f"Inserted: {name}, {value}")

            result = util.select("select * from monitor;")
            print(f"Selected: {result}")
            fields = result[0]
            self.assertEqual(fields[0], "name")
            self.assertEqual(fields[1], "value")
            key = result[1][0][0]
            self.assertEqual(key, "a_name")
            data = eval(result[1][0][1])
            self.assertIsInstance(data, dict)
            self.assertEqual(data.get("text_1"), "data_1")
            self.assertEqual(data.get("text_2"), "data_2")

            # ------
            # Update
            # ------
            value = {}
            value["text_1a"] = "data_1a"
            value["text_2a"] = "data_2a"
            util.update(name, value)
            print(f"Updated: {name}, {value}")

            result = util.select() # Select without statement
            print(f"Selected: {result}")
            key = result[1][0][0]
            self.assertEqual(key, "a_name")
            data = eval(result[1][0][1])
            self.assertIsInstance(data, dict)
            self.assertEqual(data.get("text_1a"), "data_1a")
            self.assertEqual(data.get("text_2a"), "data_2a")

        finally:
            if util is not None:
                util.close()

if __name__ == '__main__':
    unittest.main()
