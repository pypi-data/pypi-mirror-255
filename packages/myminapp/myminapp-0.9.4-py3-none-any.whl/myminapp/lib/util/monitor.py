# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0719

import sqlite3
import time

# =========
# Constants
# =========
RETRIES = 3
WAIT = 1.0

class Monitor():

    """
    This class implements a monitor using an SQLite in memory database.

    The databse is named 'monitordb' and can be shared by different threads
    in the same process.

    Note on sqlite3.OperationalError 'database table is locked': With
    multiple threads, this error can occur at least when updating tables,
    despite connection timeout setting. However, according to various
    test series, it apparently doesn't occur more than once. Therefore,
    up to 3 retries are performed for all access operations. This seems
    to work well as a workaround.
     
    For more information see myminapp manual.
    """

    # =============
    # Instantiation
    # =============

    def __init__(self):
        """Class 'Monitor' setup.
        
        Args:
            None.

        Returns:
            None.
        """
        self.test = False
        self.__conn = None

    # ==============
    # Public methods
    # ==============

    def open(self):
        """Opens the in memory database.

        Args:
            None.
        
        Returns:
            None
        """
        self.__create_conn()

    def close(self):
        """Closes the in memory database.
        
        Args:
            None.
        
        Returns:
            None
        """
        self.__close_conn()

    def insert(self, name:str, value:dict):
        """Adds an entry to the monitor table.

        Args:
            name (str): A monitor item, e.g. 'app1', 'schedule_1'.
            value (dict): Monitor data.
        
        Returns:
            None
        """
        count = 0
        while True:
            try:
                count += 1
                self.__insert(name, value)
                return
            except sqlite3.OperationalError as err:
                if self.test:
                    print(f"TEST Monitor.insert: " \
                          f"sqlite3 operational error #{count}: {err}")
                if count > RETRIES:
                    raise
                time.sleep(WAIT)

    def update(self, name:str, value:dict):
        """Updates an entry in the monitor table.

        Args:
            name (str): A monitor item, e.g. 'app1', 'schedule_1'.
            value (dict): Monitor data.
        
        Returns:
            None
        """
        count = 0
        while True:
            try:
                count += 1
                self.__update(name, value)
                return
            except sqlite3.OperationalError as err:
                if self.test:
                    print(f"TEST Monitor.update: " \
                          f"sqlite3 operational error #{count}: {err}")
                if count > RETRIES:
                    raise
                time.sleep(WAIT)

    def select(self, statement:str=None):
        """Selects entries as specified by the SQL statement.
        
        Args:
            statement (str): An optional SQL select statement.
        
        Returns:
            list[str], list[tuple]: The column names and the rows selected. 
        """
        if statement is None:
            statement = 'SELECT * from monitor;'
        count = 0
        while True:
            try:
                count += 1
                return self.__select(statement)
            except sqlite3.OperationalError as err:
                if self.test:
                    print(f"TEST Monitor.select: " \
                          f"sqlite3 operational error #{count}: {err}")
                if count > RETRIES:
                    raise
                time.sleep(WAIT)

    # ===============
    # Private methods
    # ===============

    def __create_conn(self):
        """Creates the database connection.
        
        Also creates database and monitor table if they do not already exist.
        
        Args:
            None
        
        Returns:
            None
        """
        sql = "CREATE TABLE IF NOT EXISTS monitor (name TEXT, value TEXT);"
        c = None
        try:
            self.__conn = sqlite3.connect(
                "file:monitordb?mode=memory&cache=shared",
                timeout=10.0
                )
            try:
                c = self.__conn.cursor()
                c.execute(sql)
                self.__conn.commit()
            finally:
                if c:
                    c.close()
        except Exception:
            self.__close_conn()
            raise

    def __close_conn(self):
        """Closes the database connection.

        Args:
            None
        
        Returns:
            None
        """
        if self.__conn:
            self.__conn.close()

    def __insert(self, name:str, value:dict):
        """Inserts a row into the monitor table.
   
        Args:
            name (str): A monitor item, e.g. 'app1', 'schedule_1'.
            value (dict): Monitor data with language-dependent text.
        
        Returns:
            None.
        """
        sql = "INSERT INTO monitor (name, value) VALUES (?,?);"
        c = None
        try:
            values = [name, str(value)]
            c = self.__conn.cursor()
            c.execute(sql, values)
            self.__conn.commit()
        finally:
            if c:
                c.close()

    def __update(self, name:str, value:dict):
        """Updates a row into the monitor table.
   
        Args:
            name (str): A monitor item, e.g. 'app1', 'schedule_1'.
            value (dict): Monitor data with language-dependent text.
        
        Returns:
            None.
        """
        sql = "UPDATE monitor SET (value) = ? WHERE name = ?;"
        c = None
        try:
            values = [str(value), name]
            c = self.__conn.cursor()
            c.execute(sql, values)
            self.__conn.commit()
        finally:
            if c:
                c.close()

    def __select(self, statement:str):
        """Selects rows from the monitor table as specified by the statement.

        Note: Selects rows without limit (fetchall).

        Args:
            statement (str): The SQL statement.
        
        Returns:
            list[str], list[tuple]: The field names and the entries selected. 
        """
        colnames = []
        sql = statement
        c = None
        try:
            # -------------------------------------------------
            # Ensure that this is a query and, as an additional
            # security measure, do NOT commit select statements
            # -------------------------------------------------
            test = statement.strip().lower()
            if not test.startswith("select"):
                raise Exception("Invalid query.")
            c = self.__conn.cursor()
            c.execute(sql)
            description = c.description
            for row in description:
                colnames.append(row[0])
            return colnames, c.fetchall()
        finally:
            if c:
                c.close()
