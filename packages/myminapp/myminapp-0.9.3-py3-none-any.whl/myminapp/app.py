# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0902
#pylint: disable=R0912
#pylint: disable=R0913
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0718
#pylint: disable=W0719

import os
import time
import importlib
from threading import Thread
from threading import Lock

from myminapp.appdef import DATA_HOME
from myminapp.appdef import COMMAND_DEFSETS
from myminapp.appdef import COMMAND_PRESETS
from myminapp.appdef import COMMAND_SCHEDSETS
from myminapp.lib.util.helper import Helper
from myminapp.lib.util.logger import Logger
from myminapp.lib.util.monitor import Monitor
from myminapp.lib.util.scheduler import Scheduler
from myminapp.lib.util.storage import Storage

class App():

    """
    This class provides the following features:

    - Perform commands and optionally store results
    - Instantiate, cache and close commands dynamically
    - Log messages
    - Perform schedule tasks
    
    For more information see myminapp manual.
    """

    # =========
    # Constants
    # =========
    # None

    # ============
    # Instantiaton
    # ============

    def __init__(self, appnum:int):
        """Class 'App' setup.
        
        Args:
            appnum (int): Application instance number (1, 2, ...).

        Returns:
            None.
        """
        if appnum is None:
            raise Exception("Missing application instance number.")
        if not isinstance(appnum, int):
            raise Exception(f"Invalid application instance number: "\
                            f"{str(appnum)}")
        self.appnum = appnum
        self.name = "app" + str(appnum)
        self.command_cache = {}
        self.command_count = 0
        self.command_calls = \
            {"total": 0, "oks": 0, "warnings": 0, "errors": 0, "invalids": 0}
        self.pid = os.getpid()
        self.helper = Helper()
        self.logger = Logger(self.name)
        self.schedulers = []
        self.scheduler_count = 0
        self.threadlock = Lock()
        self.scheduler_closed_count = 0
        self.scheduler_thread_state = 0
        self.status = {}
        self.status["class"] = self.__class__.__name__
        self.status["instance"] = id(self)
        self.status["name"] = self.name
        self.status["pid"] = self.pid
        self.status["started"] = self.helper.timestamp()
        self.status["schedulers"] = 0
        self.status["commands"] = 0
        self.status["command_calls"] = self.command_calls
        self.monitor = Monitor()
        self.monitor.open() # Open self.monitor to keep database in memory
        self.__monitor("insert", self.name, self.status)
        try:
            # ----------------
            # Start schedulers
            # ----------------
            for name in COMMAND_SCHEDSETS:
                schedset = COMMAND_SCHEDSETS.get(name)
                appnum_sched = schedset.get("appnum")
                if appnum_sched is not None and appnum_sched == appnum:
                    scheduler = Scheduler(name, schedset)
                    Thread(target=self.__run_scheduler, args=(scheduler,)).start()
                    self.scheduler_count += 1
                    time.sleep(1) # Wait a second
                    self.log(108, self.helper.mtext(108, str(scheduler)))
                    self.__monitor("insert", name, str(scheduler))
            # ----------------
            # Instance started
            # ----------------
            self.log(100, self.helper.mtext(100, self.name, self.pid))
            self.status.update({"schedulers": self.scheduler_count})
            self.__monitor("update", self.name, self.status)
        except Exception:
            self.close()
            raise

    # ==============
    # Public methods
    # ==============

    def log(self, code:int, message:str):
        """Logs a message.
         
        Args:
           code (int): The message code. 
           message (str): The message.
        
        Returns:
           None.
        """
        level = self.helper.mlevel(code)
        self.logger.write(code, message, level)

    def perform_command(self, data:dict, schedule:dict=None):
        """Performs a command.
         
        Args:
           data (dict): Command input data.
           schedule (dict): Optional schedule data.
        
        Returns:
           list: Command output data.
        """
        datasets = None
        ts_start = None
        ms_start = None
        ms_end = None
        cmd = None
        spec = None
        entry_index = 0
        entry_oks = 0
        entry_warnings = 0
        entry_errors = 0
        error = False
        error_text = None
        error_trace = None
        # -----------------------------------------------------------
        # Check if this instance is closed. If so, return immediately
        # -----------------------------------------------------------
        if self.name is None:
            print("App is closed.")
            return None
        try:
            # ----------------------------------------------
            # Set start time, get and check basic parameters
            # ----------------------------------------------
            ts_start = self.helper.timestamp()
            ms_start = int(time.time() * 1000)
            cmd = data.get("cmd")
            if cmd is None:
                raise Exception(self.helper.mtext(202))
            spec = COMMAND_DEFSETS.get(cmd)
            if spec is None:
                raise Exception(self.helper.mtext(203, cmd))
            input_params = spec.get("input")
            if input_params is None:
                raise Exception(self.helper.mtext(204, cmd, "input"))
            # ------------------------------------------------
            # Copy input parameters from data to command input
            # ------------------------------------------------
            cmdinput = {}
            for param in input_params:
                cmdinput[param] = data.get(param) # Might be None
            # ------------------------------------------
            # Add the name of this app instance to input
            # ------------------------------------------
            cmdinput["app"] = self.name
            # --------------------------------------
            # Add optional current schedule to input
            # --------------------------------------
            cmdinput["schedule"] = schedule
            # -------------------------------------------------
            # Get instance of command class and execute command
            # -------------------------------------------------
            datasets = self.__get_command(cmd).exec(cmdinput)
            # --------------------------------------------------------
            # Check result entry codes and add up the occurrences. Log
            # entry errors and warnings without raising an exception
            # --------------------------------------------------------
            for dataset in datasets:
                entry_index +=1
                code = dataset.get("code")
                text = dataset.get("text")
                trace = dataset.get("trace")
                if code == 0:
                    entry_oks+=1
                elif code == 1:
                    entry_errors+=1
                    self.log(221, self.helper.mtext(221,
                                        str(cmd), entry_index, text, trace))
                elif code == 2:
                    entry_warnings+=1
                    self.log(222, self.helper.mtext(222,
                                        str(cmd), entry_index, text, trace))
                elif code == 3:
                    self.log(223, self.helper.mtext(223,
                                        str(cmd), entry_index, text, trace))
                else:
                    raise Exception(132, self.helper.mtext(132,
                                        str(cmd), entry_index, code))
            # ---------------------------------------
            # Add valid data to storage if configured
            # ---------------------------------------
            if entry_oks > 0 and spec.get("storage") is True:
                self.__add_to_storage(cmd, datasets, schedule)
        # ----------------------------------------------------
        # Catch exception, set text and trace, then raise the
        # exception, and finally handle logging and monitoring
        # ----------------------------------------------------
        except Exception as exception:
            error = True
            error_text = exception
            error_trace = self.helper.tbline()
            raise
        finally:
            try:
                ms_end = int(time.time() * 1000)
                ms = ms_end-ms_start
                self.__publish_result_info(cmd, spec, data, ts_start, ms,
                        entry_index, entry_oks, entry_errors, entry_warnings,
                        error, error_text, error_trace)
            except Exception as exception:
                print(exception) # Probably a logging problem, so just print
                print(self.helper.tbline())
        # ---------------------------
        # Return datasets as response
        # ---------------------------
        return datasets

    def close(self):
        """Closes resources.

        Args:
            None.

        Returns:
            None.
        """
        self.__close_schedulers()
        self.__close_commands()
        self.__close_monitor()
        self.__close_logging()
        self.appnum = None
        self.name = None

    # ===============
    # Private methods
    # ===============

    def __add_to_storage(self, cmd, datasets, schedule):
        """Adds valid data to storage.

        Args:
           cmd (str): Command name alias storage entity name.
           datasets (list): List of datasets.
           schedule (dict): Optional schedule data.
                   
        Returns:
           None.
        """
        storage = None
        try:
            storage = Storage(DATA_HOME + "/storage", self.name)
            storage.open()
            for dataset in datasets:
                code = dataset.get("code")
                if code == 0:
                    if schedule is not None:
                        # -------------------------------------
                        # For consistent time values in storage
                        # -------------------------------------
                        storage.add(cmd, dataset.get("data"),
                                    schedule.get("last_timestamp"))
                    else:
                        storage.add(cmd, dataset.get("data"))
        finally:
            if storage:
                storage.close()

    def __publish_result_info(self, cmd, spec, data, ts_start, ms,
                        entry_index, entry_oks, entry_errors, entry_warnings,
                        error, error_text, error_trace):
        """Publishes result information via logging and monitoring.

        Args:
           cmd (str): Command name.
           spec (dict): Command specification.
           data (dict): Command input data.
           ts_start (str): Command execution start timestamp.
           ms (int): Command execution duration im milliseconds.
           entry_index (int): Number of entries -1.
           entry_oks (int): Number of entries with result code 0.
           entry_errors (int): Number of entries with result code 1.
           entry_warnings (int): Number of entries with result code 2.
           error (bool): Error flag.
           error_text (str): Error text.
           error_trace (str): Error trace.
                    
        Returns:
           None.
        """
        # -------
        # Logging
        # -------
        monitor_text = None
        if error is False:
            error_text = None
            error_trace = None
            monitor_text = "OK"
            self.log(130, self.helper.mtext(130, str(data), ms,
                entry_index, entry_oks, entry_errors, entry_warnings))
        else:
            data["error_text"] = error_text
            data["error_trace"] = error_trace
            monitor_text = error_text
            self.log(131, self.helper.mtext(131, str(data)))
        if spec is not None and spec.get("logging") is True:
            if error is False:
                self.log(200, self.helper.mtext(200, str(data), ms,
                entry_index, entry_oks, entry_errors, entry_warnings))
            else:
                self.log(201, self.helper.mtext(201, str(data)))
        # ----------
        # Monitoring
        # ----------
        monitor_entry_value = self.__monitor("select", cmd, None)
        monitor_entry_value.update({"invoked": ts_start,
                            "ms": ms,
                            "entries": entry_index,
                            "oks": entry_oks,
                            "errors": entry_errors,
                            "warnings": entry_warnings,
                            "text": monitor_text})
        self.__monitor("update", cmd, monitor_entry_value)
        self.command_calls["total"] += 1
        if entry_errors > 0:
            self.command_calls["errors"] += 1
        elif entry_warnings > 0:
            self.command_calls["warnings"] += 1
        elif entry_oks == entry_index:
            self.command_calls["oks"] += 1
        else:
            self.command_calls["invalids"] += 1
        self.__monitor("update", self.name, self.status)

    def __monitor(self, action:str, name:str, data):
        """Selects, inserts or updates a monitor entry thread safe.

        SQLite objects created in a thread can only be used in that same
        thread. So use a local monitor instance, not self.monitor.

        Args:
           action (str): Action 'select', 'insert', 'update'.
           name (str): Entry name.
           data (str or dict or None): Entry data.
        
        Returns:
           dict: If action is 'select' monitor entry value, else None.
        """
        monitor = None
        try:
            monitor = Monitor()
            monitor.open()
            if action == 'select':
                sql = f"SELECT value FROM monitor WHERE name = '{name}';"
                entry = monitor.select(sql)
                return self.helper.json2dict(entry[1][0][0])
            if isinstance(data, dict):
                entry_data = self.helper.dict2json(data)
            else:
                entry_data = str(data)
            if action == 'insert':
                monitor.insert(name, entry_data)
            else:
                monitor.update(name, entry_data)
            return None
        finally:
            if monitor:
                monitor.close()

    def __run_scheduler(self, scheduler:Scheduler):
        """To be called in an own thread to run the given scheduler.

        Scheduler thread states: 0=run, 1=terminate, 2=terminated.
         
        Args:
           Scheduler: Scheduler instance.
        
        Returns:
           None.
        """
        # ----------------------------------------------------
        # Perform scheduling tasks as long as status remains 0
        # ----------------------------------------------------
        while self.scheduler_thread_state == 0:
            time.sleep(3) # Wait 3 seconds
            if self.scheduler_thread_state != 0:
                break
            name = scheduler.name
            cmdpreset = scheduler.cmdpreset
            actnum = scheduler.get_action_number()
            # ---------------------
            # Refresh monitor entry
            # ---------------------
            self.__monitor("update", name, str(scheduler))
            if actnum > 0:
                # ---------------
                # Perform command
                # ---------------
                try:
                    data = COMMAND_PRESETS.get(cmdpreset)
                    # --------------------------------------------
                    # Get current schedule data from the scheduler
                    # --------------------------------------------
                    schedule = self.helper.json2dict(str(scheduler))
                    self.perform_command(data, schedule) # Pass schedule data
                    scheduler.confirm_action()
                    self.log(140, self.helper.mtext(140,
                                            name, cmdpreset, actnum))
                except Exception as exception:
                    scheduler.discard_action()
                    self.log(141, self.helper.mtext(141,
                                name, cmdpreset, actnum, str(exception)))
                    self.log(142, self.helper.mtext(142,
                                            name, cmdpreset, actnum))
            elif actnum < 0:
                # ------------------------------------------------------
                # An inverted (i.e. pending) action number was returned,
                # which should not occur. scheduler.reset_action() might
                # be called in this case, but that would ignore the
                # underlying problem...
                # -------------------------------------------------------
                self.log(143, self.helper.mtext(143, name, cmdpreset, actnum))
            else:
                # ----------------------------
                # Nothing to perform currently
                # ----------------------------
                pass
        # ------------------
        # Scheduler finished
        # ------------------
        scheduler = None
        with self.threadlock:
            self.scheduler_closed_count +=1

    def __get_command(self, command_name:str):
        """Gets a command instance by name.
         
        Args:
           command_name (str): The simple command name, e.g. 'state'.
        
        Returns:
           object: Instance of the command class specified by name.
        """
        defset = COMMAND_DEFSETS.get(command_name)
        if defset is None:
            raise Exception(self.helper.mtext(111, command_name))
        module_name = defset.get("module")
        class_name = defset.get("class")
        if module_name is None or class_name is None:
            raise Exception(self.helper.mtext(112, command_name))
        # ------------------------------
        # Try to get instance from cache
        # ------------------------------
        command_instance = self.command_cache.get(command_name)
        if command_instance is None:
            command_class = getattr(
                importlib.import_module(module_name), class_name
                )
            command_instance = command_class()
            # -------------------------
            # Put new instance to cache
            # -------------------------
            self.command_cache[command_name] = command_instance
            self.log(110, self.helper.mtext(110, command_name))
            self.command_count += 1
            self.status.update({"commands": self.command_count})
            self.__monitor("update", self.name, self.status)
            self.__monitor("insert", command_name,
                           {"class": class_name,
                            "instance": id(command_instance),
                            "name": command_name}
                            )
        return command_instance

    def __close_schedulers(self):
        """Closes schedulers if specified for this application instance.
         
        Args:
           None.
        
        Returns:
           None.
        """
        try:
            if self.scheduler_count == 0:
                return
            self.log(118, self.helper.mtext(118))
            self.scheduler_thread_state = 1 # Terminate
            time.sleep(5) # Wait 5 seconds
            with self.threadlock:
                if self.scheduler_closed_count == self.scheduler_count:
                    self.log(120, self.helper.mtext(120))
                else:
                    self.log(121, self.helper.mtext(121))
        except Exception:
            self.log(119, self.helper.mtext(119, self.helper.tbline()))

    def __close_commands(self):
        """Closes all cached command instances.
         
        Args:
           None.
        
        Returns:
           None.
        """
        try:
            # ---------------------------------------------
            # If there are no commands in the cache, return
            # ---------------------------------------------
            if len(self.command_cache) == 0:
                return
            # ---------------------
            # Close cached commands
            # ---------------------
            self.log(113, self.helper.mtext(113))
            for command_name in self.command_cache:
                command_instance = self.command_cache.get(command_name)
                if command_instance is not None:
                    try:
                        command_instance.close()
                        self.log(114, self.helper.mtext(114, command_name))
                    except Exception:
                        self.log(115, self.helper.mtext(115, command_name,
                                            self.helper.tbline()))
            self.command_cache = None
            self.log(117, self.helper.mtext(117))
        except Exception:
            self.log(116, self.helper.mtext(116, self.helper.tbline()))

    def __close_monitor(self):
        """Closes the monitor.
         
        Args:
           None.
        
        Returns:
           None.
        """
        if self.monitor:
            try:
                self.log(122, self.helper.mtext(122))
                self.monitor.close()
                self.monitor = None
                self.log(124, self.helper.mtext(124))
            except Exception:
                self.log(123, self.helper.mtext(123, self.helper.tbline()))

    def __close_logging(self):
        """Closes logging.
         
        Args:
           None.
        
        Returns:
           None.
        """
        if self.logger:
            self.logger.close()
            self.logger = None
