# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.lib.command.cmd import Cmd

# =========
# Constants
# =========
# None

class HelloWorld(Cmd):

    """
    This command class just implements 'Hello World' for demonstration.

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
        app = None      # Application instance name (app1, app2, ...)
        param = None    # Input parameter
        value = None    # Output value

        try:

            # ------------------------------------------------------
            # Check and set app and other input parameters as needed
            # ------------------------------------------------------
            app = cmdinput.get('app')
            if app is None:
                raise Exception(self.helper.mtext(204, self.name, 'app'))
            param = cmdinput.get('value')
            if param is None:
                raise Exception(self.helper.mtext(204, self.name, 'value'))

            # --------------------------------------------------
            # If the command is scheduled, current schedule data
            # can be received, for example to get the number of
            # remaining actions within the scheduled time window
            # and to perform a final task with the last action
            # (i.e. when this command is invoked the last time)
            # --------------------------------------------------
            schedule = cmdinput.get('schedule')
            if schedule is not None:
                pass
                # print(f"schedule data: {schedule}")
                # remaining_actions = schedule.get("remaining_actions")
                # ...

            # -------------------------------------------------------------
            # Perform this command's task, preferably using private methods
            # -------------------------------------------------------------
            value = self.__get_hello_world_response(app, self.name, param)

            # -----------
            # Set dataset
            # -----------
            dataset["value"] = value

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

    def __get_hello_world_response(self, app:str, cmd:str, param:str):
        """Gets the value to be returned by this command.
             
        Args:
            app (str): Application instance name.
            cmd (str): This command's name.
            param (str): Input parameter.
    
        Returns:
           str: The response value.
        """
        return param + f" from {app}, {cmd}"
    