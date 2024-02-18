# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0914
#pylint: disable=W0718
#pylint: disable=W0719

import io
import os
import sys
import pydoc
from pathlib import Path

from myminapp.appdef import HOME
from myminapp.appdef import DATA_HOME
from myminapp.lib.command.cmd import Cmd

# =========
# Constants
# =========
ROOT_PATHNAME = "myminapp"

class TextDoc(Cmd):

    """
    This command class creates a docstring documentation as text files.

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
        try:
            # ------------------------------------------------------
            # Check and set app and other input parameters as needed
            # ------------------------------------------------------
            app = cmdinput.get('app')
            if app is None:
                raise Exception(self.helper.mtext(204, self.name, 'app'))
            # --------------------------------------------------------
            # Set the application path and the target path to write to
            # --------------------------------------------------------
            apppath = HOME
            docpath = DATA_HOME + f"/temp/textdoc/{ROOT_PATHNAME}/"
            # -----------------------------------
            # Create the target path if necessary
            # -----------------------------------
            if os.path.exists(docpath) is False:
                os.makedirs(docpath)
            # ------------------------------------------------------------
            # Suppress possible standard output from modules pydoc imports
            # ------------------------------------------------------------
            dummy = io.StringIO()
            sys.stdout = dummy
            # ---------------------------------------------------------
            # Create the text documentation for each application module
            # ---------------------------------------------------------
            for path in Path(apppath).rglob('*.py'):
                docdir = str(path.absolute())
                if docdir.endswith("__init__.py"):
                    continue
                modname_startpos = docdir.rindex(f"{ROOT_PATHNAME}/")
                docname_startpos = modname_startpos + len(f"{ROOT_PATHNAME}/")
                modname = docdir[modname_startpos:].replace(".py",
                                                    "").replace("/", ".")
                docname = docdir[docname_startpos:].replace(".py",
                                                    ".txt").replace("/", "_")
                # ---------------------
                # Let pydoc be creative
                # ---------------------
                doc = pydoc.render_doc(modname, renderer=pydoc.plaintext)
                # -------------
                # Write to file
                # -------------
                with open(docpath + docname, "w", encoding="utf-8") as file:
                    file.write(doc)
            # --------------------------
            # No data for a dataset here
            # --------------------------
            # ./.
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
            sys.stdout = sys.__stdout__ # Reset standard output
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
        