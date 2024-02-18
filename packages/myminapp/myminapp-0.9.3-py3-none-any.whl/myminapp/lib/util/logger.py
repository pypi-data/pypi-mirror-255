# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0718
#pylint: disable=W0719

import sys
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from myminapp.appdef import DATA_HOME
from myminapp.appdef import LOG_STDOUT
from myminapp.appdef import LOG_FILE
from myminapp.appdef import LOG_FILE_BACKUP_COUNT
from myminapp.appdef import LOG_FILE_MAX_BYTES
from myminapp.appdef import LOG_LEVEL
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
ERROR = "ERROR"
WARNING = "WARNING"
INFO = "INFO"
DEBUG = "DEBUG"

class Logger:

    """
    Use this utility class for logging.
        
    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self, logger_name:str):
        """Class 'Logger' setup.

        Args:
            logger_name (str): Name of the logger (e.g. app1, app2, ...).

        Returns:
            None.
        """
        self.helper = Helper()
        self.logger_name = logger_name.lower()
        self.log_file = DATA_HOME + "/log/" + self.logger_name + ".log"
        self.logger = None
        if logging.getLogger(self.logger_name).hasHandlers():
            self.logger = logging.getLogger(self.logger_name)
        else:
            self.logger = logging.getLogger(self.logger_name)
            self.logger.handlers.clear()
            if LOG_LEVEL == ERROR:
                self.logger.setLevel(logging.ERROR)
            elif LOG_LEVEL == WARNING:
                self.logger.setLevel(logging.WARNING)
            elif LOG_LEVEL == DEBUG:
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s')

            if LOG_STDOUT:
                stdout_handler = StreamHandler(sys.stdout)
                stdout_handler.setLevel(self.logger.level)
                stdout_handler.setFormatter(formatter)
                self.logger.addHandler(stdout_handler)

            if LOG_FILE:
                file_handler = RotatingFileHandler(self.log_file,
                                    maxBytes = LOG_FILE_MAX_BYTES,
                                    backupCount = LOG_FILE_BACKUP_COUNT,
                                    encoding = None, delay = False)
                file_handler.setLevel(self.logger.level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

            handler_list = []
            for handler in self.logger.handlers:
                handler_list.append(str(handler))
            self.write(900, self.helper.mtext(900, self.logger_name,
                                          str(handler_list)), "INFO")

    # ==============
    # Public methods
    # ==============

    def write(self, code:int, message:str, level:str):
        """Writes log data.

        Args:
            code (int): Message code.
            message (str:) Message to log.
            level (str): Message level (ERROR, WARNING, INFO, or DEBUG).
    
        Returns:
            None.
        """
        # ----------------------------------------
        # Set log message prefix plus message text
        # ----------------------------------------
        prefix = self.logger_name + " | " + str(code) + " |"
        log_message = f"{prefix} {message}"
        # --------------------------------
        # Log with the given message level
        # --------------------------------
        if level == ERROR:
            self.logger.error(log_message)
        elif level == WARNING:
            self.logger.warning(log_message)
        elif level == DEBUG:
            self.logger.debug(log_message)
        else:
            self.logger.info(log_message)

    def close(self):
        """Closes the logger.

        Args:
            None
   
        Returns:
            None.
        """
        if self.logger:
            try:
                self.write(901, self.helper.mtext(901, self.logger_name), "INFO")
                for handler in self.logger.handlers:
                    self.logger.removeHandler(handler)
                    handler.close()
            except Exception as error:
                print(self.helper.mtext(902, self.logger_name, error))

    # ===============
    # Private methods
    # ===============
    # None
                