# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0200
#pylint: disable=R0912
#pylint: disable=W0622
#pylint: disable=W0718
#pylint: disable=W0719

import datetime
import sqlite3

from myminapp.appdef import FIELD_DEFSETS
from myminapp.appdef import PREFIX_FIELD_DEFSETS

# =========
# Constants
# =========
# None

class Storage():

    """
    Use this class to communicate with the data storage layer implemented
    with SQLite.
     
    The public methods of this class are abstracted to such an extent
    that the implementation of the data storage layer could be done in
    various ways. However, no implementation other than SQLite is planned
    for this project so far.

    For more information see myminapp manual.
    """

    # =============
    # Instantiation
    # =============

    def __init__(self, path:str, name:str):
        """Class 'Storage' setup.
        
        Args:
            path (str): Data storage path.
            name (str): Data storage name (like APP name), e.g. 'app1'.

        Returns:
            None.
        """
        self.path = path
        self.name = name
        if not self.name.endswith(".db"): # SQLite-specific:
            self.name = self.name + ".db" # Database file extension
        self.file = self.path + "/" + self.name
        self.__conn = None

    # ==============
    # Public methods
    # ==============

    def open(self):
        """Opens the data storage.
        
        Also creates the data storage if it does not already exist.
        
        Args:
            None.
        
        Returns:
            None
        """
        self.__create_conn()

    def close(self):
        """Closes the data storage.
        
        Args:
            None.
        
        Returns:
            None
        """
        self.__close_conn()

    def add(self, cmd:str, dataset:dict, ts:str=None):
        """Adds a data entry to the entity specified by cmd.

        Also creates the entity if it does not already exist.
   
        Args:
            cmd (str): The name of the command, identical to the entity name.
            data (dict): The full output dataset specified in COMMAND_DEFSETS,
                            with corresponding values in valid state.
            ts (str): Optional timestamp for consistent time values.
        
        Returns:
            int: Primary key generated automatically (last ID).
        """
        return self.__insert(cmd, dataset, ts)

    def update_by_native_statement(self, statement:str):
        """Executes the specified native statement without any checks.

        Note: DO NOT ALLOW THIS METHOD TO BE EXECUTED VIA COMMAND.

        Args:
            statement (str): The native statement.
        
        Returns:
            None.
        """
        return self.__update_by_statement(statement)

    def read_by_native_statement(self, statement:str):
        """Reads all entries as specified by the native statement.
        
        Args:
            statement (str): The native read statement (e.g. for SQLite).
        
        Returns:
            list[str], list[tuple]: The field names and the entries read.
        """
        return self.__select_by_statement(statement)

    def read_by_id(self, cmd:str, id:int):
        """Reads the entry with the given ID.

        Args:
            cmd (str): The name of the command, identical to the entity name.
            id (int): The unique ID.
        
        Returns:
            list[str], tuple: The field names and the entry read.
        """
        return self.__select_by_id(cmd, id)

    def get_field_list(self, cmd:str):
        """Gets a field list.

        Args:
            cmd (str): The name of the command, identical to the entity name.
        
        Returns:
            list: The field list.
        """
        return self.__get_column_list(cmd)

    # ===============
    # Private methods
    # ===============

    def __create_conn(self):
        """Creates the SQLite database connection.
        
        Also creates the database if it does not already exist.
        
        Args:
            None
        
        Returns:
            None
        """
        try:
            self.__conn = sqlite3.connect(self.file, timeout=10.0)
        except Exception:
            self.__close_conn()
            raise

    def __close_conn(self):
        """Closes the SQLite database connection.

        Args:
            None
        
        Returns:
            None
        """
        if self.__conn:
            self.__conn.close()

    def __create_table(self, cmd:str, dataset:dict):
        """Creates an SQLite table if it does not already exist.

        Args:
            cmd (str): The name of the command, identical to the table name.
            data (dict): The full output dataset specified in COMMAND_DEFSETS.
        
        Returns:
            None
        """
        sql = None
        c = None
        cols = []
        try:
            # ------------------------------
            # Set this prefix for all tables
            # ------------------------------
            name = "id"
            if PREFIX_FIELD_DEFSETS.get(name) is None:
                text = f"Missing configuration for prefix field '{name}'"
                raise Exception(text)
            cols.append("id INTEGER PRIMARY KEY")
            for i in range(0, 7):
                name = f"t{i}"
                if PREFIX_FIELD_DEFSETS.get(name) is None:
                    text = f"Missing configuration for prefix field '{name}'"
                    raise Exception(text)
                cols.append(f"{name} INTEGER NOT NULL")
            for name in dataset.keys():
                # ------------------------------------------------
                # Assign the field names to the entries defined in
                # FIELD_DEFSETS and determine the column formats
                # ------------------------------------------------
                defset = FIELD_DEFSETS.get(name)
                if defset is None:
                    text = f"Missing configuration for field '{name}'"
                    raise Exception(text)
                format = defset.get("storageformat")
                if format is None:
                    text = f"Missing key 'storageformat' for field '{name}'"
                    raise Exception(text)
                if format == "TEXT":
                    cols.append(f"{name} TEXT")
                elif format == "INTEGER":
                    cols.append(f"{name} INTEGER")
                elif format == "REAL":
                    cols.append(f"{name} REAL")
                elif format == "BLOB":
                    cols.append(f"{name} BLOB")
                else:
                    text = f"Unsupported storage format for field "\
                           f"'{name}': '{format}'"
                    raise Exception(text)
            # ------------------------------------------
            # Set and execute the create table statement
            # ------------------------------------------
            str_cols = ", ".join(cols)
            table_name = "'" + cmd + "'"
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({str_cols});"
            c = self.__conn.cursor()
            c.execute(sql)
            self.__conn.commit()
        finally:
            if c:
                c.close()

    def __insert(self, cmd:str, dataset:dict, ts:str=None):
        """Inserts a data row into a SQLite table.

        Also creates the table if it does not already exist.
   
        Args:
            cmd (str): The name of the command, identical to the table name.
            data (dict): The full output dataset specified in COMMAND_DEFSETS,
                            with corresponding values in valid state.
            ts (str): Optional timestamp for consistent time values.
        
        Returns:
            int: Primary key generated automatically (last ID).
        """
        sql = None
        c = None
        try:
            # ------------------------------------
            # Create the target table if necessary
            # ------------------------------------
            self.__create_table(cmd, dataset)
            # ------------------------
            # Prepare insert statement
            # ------------------------
            qmarks = []
            names = []
            values = []
            tn = self.__timestamp(ts)
            for i in range(0, len(tn)):
                qmarks.append("?")
                name = f"t{i}"
                names.append(name)
                values.append(tn[i])
            for name in dataset.keys():
                qmarks.append("?")
                names.append(name)
                if name == "info":
                    values.append(str(dataset.get(name)))
                else:
                    values.append(dataset.get(name))
            str_qmarks = ", ".join(qmarks)
            str_names = ", ".join(names)
            table_name = "'" + cmd + "'"
            sql = f"INSERT INTO {table_name} ({str_names}) "\
                  f"VALUES ({str_qmarks});"
            # ------------------------
            # Execute insert statement
            # ------------------------
            c = self.__conn.cursor()
            c.execute(sql, values)
            self.__conn.commit()
            return c.lastrowid
        finally:
            if c:
                c.close()

    def __update_by_statement(self, statement:str):
        """Executes the specified statement without any checks.

        Note: DO NOT ALLOW THIS METHOD TO BE EXECUTED VIA COMMAND.

        Args:
            statement (str): The SQL statement.
        
        Returns:
            None.
        """
        sql = statement
        c = None
        try:
            c = self.__conn.cursor()
            c.execute(sql)
            self.__conn.commit()
        finally:
            if c:
                c.close()


    def __select_by_statement(self, statement:str):
        """Selects rows as specified by the statement from an SQLite table.

        Note: Selects rows without limit (fetchall).

        Args:
            statement (str): The SQL statement.
        
        Returns:
            list[str], list[tuple]: The column names and the rows read. 
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

    def __select_by_id(self, cmd:str, id:int):
        """Selects the row with the given ID from an SQLite table.

        Args:
            cmd (str): The name of the command, identical to the table name.
            id (int): The ID (SQLite INTEGER PRIMARY KEY.
        
        Returns:
            str, tuple: The column list and the row read.
        """
        colnames = []
        sql = f"SELECT * from {cmd} where id = {id};"
        c = None
        try:
            c = self.__conn.cursor()
            c.execute(sql)
            description = c.description
            for row in description:
                colnames.append(row[0])
            return colnames, c.fetchone()
        finally:
            if c:
                c.close()

    def __get_column_list(self, cmd:str):
        """Gets a column list from an SQLite table.

        Args:
            cmd (str): The name of the command, identical to the table name.
        
        Returns:
            list: The column list.
        """
        colnames = []
        sql = f"SELECT * from {cmd} where id = 1;"
        c = None
        try:
            c = self.__conn.cursor()
            c.execute(sql)
            description = c.description
            for row in description:
                colnames.append(row[0])
            return colnames
        finally:
            if c:
                c.close()

    def __timestamp(self, ts:str=None):
        """Creates a numeric timestamp and fractions thereof.

        Creates an integer from an chronologically sortable, current and
        second-exact timestamp without timezone, formatted %Y%m%d%H%M%S,
        e.g. 20230928083015. Splits the timestamp into year, month, day,
        hour, minute, second.
        
        Args:
            ts (str): Optional timestamp for consistent time values.

        Returns:
            list[int]: The timestamp and its fractions.
        """
        if ts is not None:
            ts = ts.replace(" ", "").replace("-", "").replace(":", "")
        else:
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tn = []
        tn.append(int(ts))
        tn.append(int(ts[:4]))
        tn.append(int(ts[4:-8]))
        tn.append(int(ts[6:-6]))
        tn.append(int(ts[8:-4]))
        tn.append(int(ts[10:-2]))
        tn.append(int(ts[12:]))
        return tn
