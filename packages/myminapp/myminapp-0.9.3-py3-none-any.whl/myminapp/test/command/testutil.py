# -*- coding: utf-8 -*-
"""myminapp"""

import importlib

from myminapp.appdef import COMMAND_DEFSETS
from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC

class TestUtil:

    """
    This class provides additional methods for command testing.

    For more information see myminapp manual.
    """

    def __init__(self):
        """Setup.
        
        Args:
            None.

        Returns:
            None.
        """

    def get_instance(self, name:str):
        """Gets dynamically an instance of the command to test.
        
        Args:
            name (str): Command name as defined in COMMAND_DEFSETS.

        Returns:
            object: The command instance.
        """
        #spec = self.appdef.COMMAND_DEFSETS.get(name)
        spec = COMMAND_DEFSETS.get(name)
        mname = spec.get('module')
        cname = spec.get('class')
        command_class = getattr(importlib.import_module(mname), cname)
        return command_class()

    def check_devspec(self, names:list):
        """Checks if specifications for required device classes are present.
        
        Args:
            names (list): List of device class names.

        Returns:
            bool: True if the specifications are present, else False.
        """
        check = True
        for name in names:
            #if self.appdef.DEVICE_CLASS_CONNECTION_SPEC.get(name) is None:
            if DEVICE_CLASS_CONNECTION_SPEC.get(name) is None:
                check = False
                print(f"Specification for device class '{name}' "\
                       "not found in appdef.DEVICE_CLASS_CONNECTION_SPEC.")
        return check
    