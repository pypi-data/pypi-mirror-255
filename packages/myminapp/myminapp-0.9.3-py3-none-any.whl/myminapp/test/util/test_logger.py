# -*- coding: utf-8 -*-
"""myminapp"""

import unittest

from myminapp.lib.util.logger import Logger

class TestLogger(unittest.TestCase):

    """Test class."""

    def test_util(self):
        """Performs a utility test.
        
        Args:
            None.

        Returns:
            None.
        """
        util = Logger('test')
        try:

            util.write(88, "Hello from logger test", 'INFO')
            util.write(88, "Hello again from logger test", 'INFO')

        finally:
            if util is not None:
                util.close()

if __name__ == '__main__':
    unittest.main()
