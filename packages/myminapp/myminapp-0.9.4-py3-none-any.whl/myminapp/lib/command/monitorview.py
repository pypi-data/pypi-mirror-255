# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.lib.command.cmd import Cmd
from myminapp.lib.util.monitor import Monitor

# =========
# Constants
# =========
# None

class MonitorView(Cmd):

    """
    This command class receives entries from the monitor.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class setup (calls superclass init with class name).
        
        Args:
            None

        Returns:
            None.
        """
        super().__init__(__class__.__name__)

    # ==============
    # Public methods
    # ==============

    #Overrides
    def exec(self, cmdinput:dict):
        """See superclass 'Cmd'."""

         # -------------------------------
        # Declare general local variables
        # -------------------------------
        code = -1       # Result code (0=OK, 1=error, 2=warning)
        text = ""       # Result text ('OK', or error text)
        trace = ""      # Result trace ('', or error trace)
        dataset = {}    # Result dataset
        datasets = []   # Result dataset list to be returned

        # ---------------------------------
        # Declare local variables as needed
        # ---------------------------------
        app = None          # Application instance name (app1, app2, ...)
        statement = None    # Query as a native select statement
        monitor = None      # Monitor

        try:
            # ------------------------------------------------------
            # Check and set app and other input parameters as needed
            # ------------------------------------------------------
            app = cmdinput.get('app')
            if app is None:
                raise Exception(self.helper.mtext(204, self.name, 'app'))
            statement = cmdinput.get('value') #May be None
            # ---------------------------------------------------------------
            # Get fields and entries from the given app's data storage entity
            # ---------------------------------------------------------------
            monitor = Monitor()
            monitor.open()
            fields, entries = monitor.select(statement)
             # -----------
            # Set dataset
            # -----------
            dataset["fields"] = fields
            dataset["entries"] = entries
            # ---------------------
            # Set code, text, trace
            # ---------------------
            code = 0
            text = self.helper.mtext(0)
            trace = ""
        # -----------------------------------------
        # Catch exception and set code, text, trace
        # -----------------------------------------
        except Exception as exception:
            code = 1
            text = self.helper.mtext(1, exception)
            trace = self.helper.tbline()
        # -------------
        # Do final work
        # -------------
        finally:
            if monitor:
                monitor.close()
            self.add_command_output(code, text, trace, dataset, datasets)
        # ---------------
        # Return datasets
        # ---------------
        return datasets

    #Overrides
    def close(self):
        """See superclass 'Cmd'."""
        # Formally only, nothing to close here.

    # ===============
    # Private methods
    # ===============
    # None
        