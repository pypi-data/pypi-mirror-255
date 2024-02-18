# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0912
#pylint: disable=R0913
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.appdef import COMMAND_DEFSETS
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
# None

class Cmd:

    """
    This class is the superclass for all command classes. It provides the
    following feature:

    - Set the standardized command output

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self, name:str):
        """Superclass 'Cmd' setup.
        
        Args:
            name (str): Name of the derived implementing command class.

        Returns:
            None.
        """
        self.name = name.lower()    # The derived command's class name
        self.helper = Helper()      # Helper class

    # ==============
    # Public methods
    # ==============

    #Override
    def exec(self, cmdinput:dict):
        """Executes a command.

        Override this method in the derived classes.
         
        Args:
            cmdinput (dict): Command input.
 
        Returns:
            list: Command results in self.datasets.
        """
        # --------------------------------------
        # To be implemented by the derived class
        # --------------------------------------

    #Override
    def close(self):
        """Closes resources if applicable (maybe formally only).

        Override this method in the derived classes.
        
        Args:
            None.
 
        Returns:
            None.
        """
        # --------------------------------------
        # To be implemented by the derived class
        # --------------------------------------

    def add_command_output(self, code:int, text:str, trace:str,
                                 dataset:dict, datasets:list):
        """Sets and adds standardized command result to datasets.

        Args:
            code (int): Result code (0=OK, 1=error, 2=warning).
            text (str): Result text ('OK', or error text).
            trace (str): Result trace ('', or error trace).
            dataset (dict): Result dataset.
            datasets (list): Result list to be returned by exec method.

        Returns:
            None.
        """
        result = {}
        output = {}
        try:
            # ----------------
            # Check parameters
            # ----------------
            if code is None:
                raise Exception("command parameter 'code' is None")
            if text is None:
                raise Exception("command parameter 'text' is None")
            if trace is None:
                raise Exception("command parameter 'trace' is None")
            if dataset is None:
                raise Exception("command parameter 'dataset' is None")
            # ------------------------------------------------
            # Try to get output specification for command name
            # ------------------------------------------------
            spec = COMMAND_DEFSETS.get(self.name)
            output_spec = None
            if spec is not None:
                output_spec = spec.get("output")
            if output_spec is None:
                raise Exception(self.helper.mtext(216, self.name))
            # ---------------------------------------------------------
            # Set values for specified fields from dataset as available
            # ---------------------------------------------------------
            for field in output_spec:
                if field in dataset:
                    output[field] = dataset.get(field)
                else:
                    output[field] = None
            # ---------------------------------------------------
            # If field info is defined and None, set text as info
            # ---------------------------------------------------
            if "info" in output_spec:
                info = output.get("info")
                if info is None:
                    output["info"] = text
            # ----------
            # Set result
            # ----------
            result["code"] = code
            result["text"] = text
            if len(trace) > 400:
                trace = trace[:400] + "..."
            result["trace"] = trace
            result["data"] = output
        except Exception as exception:
            # -----------------------
            # Set exception as result
            # -----------------------
            result = {}
            result["code"] = 1
            result["text"] = self.helper.mtext(201, self.name, exception)
            result["trace"] = self.helper.tbline()
            result["data"] = None
        finally:
            # ----------------------
            # Add result to datasets
            # ----------------------
            datasets.append(result)

    # ===============
    # Private methods
    # ===============
    # None
            