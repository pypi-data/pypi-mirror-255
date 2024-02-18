# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0200
#pylint: disable=R0912
#pylint: disable=R0913
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0718
#pylint: disable=W0719

from myminapp.appdef import DATA_HOME
from myminapp.appdef import FIELD_DEFSETS
from myminapp.appdef import PREFIX_FIELD_DEFSETS
from myminapp.appdef import LANG
from myminapp.lib.command.cmd import Cmd
from myminapp.lib.device.graphic.chart import Chart
from myminapp.lib.util.storage import Storage

# =========
# Constants
# =========
# None

class EPStats(Cmd):

    """
    This command class creates statistical data based on an entity like
    'state' or copies of it. Entity fields 'devname', 'devcat', and
    either 'energy' or 'power' are required, depending on the type.

    Device categories M, P, and I are supported.

    This class uses device class 'Chart' to create SVG chart files.

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
        eptype = None   # Type (energy, power, powerplus)
        entity = None   # Data storage entity (e.g. state)
        units = None    # Number of time units from year to minute (e.g. 3)
        tsfrom = None   # Timestamp from as integer (e.g. 202311, 20231125),
                        #  or a number followed by d, h, or m (e.g. 32h) for
                        #  days/hours/minutes
        tsto = None     # Timestamp to as integer (e.g. 202311, 202311251230),
                        #  or a number followed by d, h, or m (e.g. 7d) for
                        #  days/hours/minutes, or '*' for current time
        devname = None  # Device name(s) (e.g. * or EM or SOLAR, COOLER)
        devcat = None   # Device category (e.g. * or P)

        try:
            # ------------------------------------------------------
            # Check and set app and other input parameters as needed
            # ------------------------------------------------------
            app = cmdinput.get('app')
            if app is None:
                raise Exception(self.helper.mtext(204, self.name, 'app'))
            eptype = cmdinput.get('type')
            if eptype is None:
                raise Exception(self.helper.mtext(204, self.name, 'type'))
            if eptype != 'energy' and eptype != 'power' and \
                eptype != 'powerplus':
                raise Exception(self.helper.mtext(213, self.name, eptype))
            if eptype == 'powerplus' and \
                (cmdinput.get('devcat') is None or cmdinput.get('devcat') != 'M'):
                raise Exception(self.helper.mtext(214, 'M', self.name, eptype))
            entity = cmdinput.get('entity')
            if entity is None:
                raise Exception(self.helper.mtext(204, self.name, 'entity'))
            units = cmdinput.get('units')
            if units is None:
                raise Exception(self.helper.mtext(204, self.name, 'units'))
            tsfrom = cmdinput.get('from')
            if tsfrom is None:
                raise Exception(self.helper.mtext(204, self.name, 'from'))
            tsto = cmdinput.get('to')
            if tsto is None:
                raise Exception(self.helper.mtext(204, self.name, 'to'))
            if tsto == "*":
                tsto = self.helper.timestamp_iso2int(self.helper.timestamp())
            devname = cmdinput.get('devname')
            if devname is None:
                raise Exception(self.helper.mtext(204, self.name, 'devname'))
            if devname == "*":
                devname = None
            devname_list = None
            if devname is not None:
                devname_list = devname.strip().split(",")
            devcat = cmdinput.get('devcat')
            if devcat is not None and devcat == "*":
                devcat = None
            # -------------------
            # Complete timestamps
            # -------------------
            tsfrom, tsto = self.helper.complete_timestamps(tsfrom, tsto)
            # -------------------
            # Get data and charts
            # -------------------
            fields, entries, bar_charts, pie_charts, line_charts = \
                self.__get_data_and_charts(app, eptype, entity, units,
                                    tsfrom, tsto, devname_list, devcat)
            # -----------
            # Set dataset
            # -----------
            dataset["fields"] = fields
            dataset["entries"] = entries # Entries by time unit group
            dataset["charts"] = \
                bar_charts + "," + pie_charts + "," + line_charts
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

    def __get_data_and_charts(self, app:str, eptype:str, entity:str,
                                 units:int, tsfrom:int, tsto:int,
                                 devname_list:list, devcat):
        """Gets statistical data and charts.
    
        Args:
            app (str): Application instance name.
            eptype (str): Type energy or power/powerplus.
            entity (str): An entity name like state.
            units (int): Number of time units (t1, t2, ...).
            tsfrom (int): Timestamp from.
            tsto (int): Timestamp to.
            devname_list (list): Device name CSV list (A,B,...) or None.
            devcat (str): Device category or None.
            
        Returns:
            list: fields - Field name list.
            list: entries2 - Time unit related energy or average power data.
            str: bar_charts - CSV list of SVG file names.
            str: pie_charts - CSV list of SVG file names.
            str: line_charts - CSV list of SVG file names.
        """
        try:
            # -----------------------------
            # Open given app's data storage
            # -----------------------------
            storage = Storage(DATA_HOME + "/storage", app)
            storage.open()
            # -----------------------------------------------------
            # Specified device names, or all available device names
            # which can be found in the data storage entity
            # -----------------------------------------------------
            devnames = []
            statement = self.__get_stmt_devnames(entity,
                                            tsfrom, tsto, devname_list, devcat)
            fields, entries = \
                storage.read_by_native_statement(statement)
            for entry in entries:
                for value in entry:
                    devnames.append(value)
            # --------------------------------
            # No device name could be assigned
            # --------------------------------
            if len(devnames) == 0:
                raise Exception(self.helper.mtext(206))
            # ------------------
            # Chart title prefix
            # ------------------
            title_prefix = None
            if eptype == 'energy':
                title_prefix = \
                    FIELD_DEFSETS.get("energy").get(LANG).get("label")
            elif eptype == 'power':
                title_prefix = \
                    FIELD_DEFSETS.get("power").get(LANG).get("label") \
                    + " " \
                    + FIELD_DEFSETS.get("avg").get(LANG).get("label")
            elif eptype == 'powerplus':
                title_prefix = \
                    FIELD_DEFSETS.get("power").get(LANG).get("label") \
                    + " PLUS " \
                    + FIELD_DEFSETS.get("avg").get(LANG).get("label")
            else:
                title_prefix = ""
            # ----------------------------------------------------------------
            # Energy total or power average per device, bar charts, pie charts
            # ----------------------------------------------------------------
            entries1 = None
            bar_charts = None
            pie_charts = None
            statement = self.__get_stmt_total(
                eptype, entity, tsfrom, tsto, devname_list, devcat
                )
            fields, entries1 = storage.read_by_native_statement(
                statement
                )
            chart_labels, chart_data = self.__get_bar_chart_data(
                devnames, entries1
                )
            chart_title = self.__get_chart_title(
                "Chart 1: " + title_prefix, tsfrom, tsto
                )
            bar_charts = self.__get_charts(
                app, eptype, "bar", chart_title, chart_labels, chart_data
                )
            chart_title = self.__get_chart_title(
                "Chart 2: " + title_prefix, tsfrom, tsto
                )
            pie_charts = self.__get_charts(
                app, eptype, "pie", chart_title, chart_labels, chart_data
                )
            # -------------------------------------------------------
            # Energy or power average by time unit group, line charts
            # -------------------------------------------------------
            entries2 = None
            line_charts = None
            statement = self.__get_stmt_by_time_unit_group(
                eptype, entity, units, tsfrom, tsto, devname_list, devcat
                )
            fields, entries2 = storage.read_by_native_statement(
                statement
                )
            chart_labels, chart_data = self.__get_line_chart_data(
                units, devnames, entries2
                )
            chart_title = self.__get_chart_title(
                "Chart 3: " + title_prefix, tsfrom, tsto, units
                )
            line_charts = self.__get_charts(
                app, eptype, "line", chart_title, chart_labels, chart_data
                )
        # -------------
        # Do final work
        # -------------
        finally:
            if storage:
                storage.close()
        # ----------------------
        # Return data and charts
        # ----------------------
        return fields, entries2, bar_charts, pie_charts, line_charts

    def __get_stmt_devnames(self, entity:str,
                             tsfrom:int, tsto:int,
                             devname_list:list, devcat:str):
        """Gets a statement to receive device names.
    
        Args:
            eptype (str): Type energy or power/powerplus.
            entity (str): An entity name like state.
            tsfrom (int): Timestamp from.
            tsto (int): Timestamp to.
            devname_list (list): Device name CSV list (A,B,...) or None.
            devcat (str): Device category or None.
            
        Returns:
            str: Statement to get available device names.
        """
        stmt = []
        stmt.append("SELECT devname ")
        stmt.append(" FROM ")
        stmt.append(entity)
        stmt.append(" WHERE ")
        stmt.append(f"t0 >= {tsfrom} AND t0 <= {tsto}")
        if devname_list is not None:
            # ----------------------------------------
            # Enclose names in apostrophe using "'%s'"
            # ----------------------------------------
            stmt.append(" AND devname IN (")
            for i in range(0, len(devname_list)):
                if i > 0:
                    stmt.append(",")
                stmt.append(f"'{devname_list[i].strip()}'")
            stmt.append(")")
        if devcat is not None:
            stmt.append(f" AND devcat = '{devcat}'")
        else:
            stmt.append(" AND devcat IN ('M', 'P', 'I')")
        stmt.append(" GROUP BY 1 ORDER BY 1")
        stmt.append(";")
        return "".join(stmt)

    def __get_stmt_total(self, eptype:str, entity:str,
                                 tsfrom:int, tsto:int,
                                 devname_list:list, devcat):
        """Gets a statement for energy total or power average per device.
    
        Args:
            eptype (str): Type energy or power/powerplus.
            entity (str): An entity name like state.
            tsfrom (int): Timestamp from.
            tsto (int): Timestamp to.
            devname_list (list): Device name CSV list ('A','B',...) or None.
            devcat (str): Device category or None.
            
        Returns:
            str: Statement to get available entries.
        """
        stmt = []
        stmt.append("SELECT ")
        stmt.append("devname")
        stmt.append(",")
        stmt.append("devcat")
        stmt.append(",")
        stmt.append("COUNT(devname) AS 'count'")
        stmt.append(",")
        if eptype == 'energy':
            stmt.append("ROUND(MIN(energy), 3) AS 'min'")
            stmt.append(",")
            stmt.append("ROUND(MAX(energy), 3) AS 'max'")
            stmt.append(",")
            stmt.append("ROUND((MAX(energy)-MIN(energy)), 3) AS 'energy'")
        else:
            stmt.append("ROUND(MIN(ABS(power)), 1) AS 'min'")
            stmt.append(",")
            stmt.append("ROUND(MAX(ABS(power)), 1) AS 'max'")
            stmt.append(",")
            stmt.append("ROUND(AVG(ABS(power)), 1) AS 'power'")
        stmt.append(" FROM ")
        stmt.append(entity)
        stmt.append(" WHERE ")
        stmt.append(f"t0 >= {tsfrom} AND t0 <= {tsto}")
        if devname_list is not None:
            # ----------------------------------------
            # Enclose names in apostrophe using "'%s'"
            # ----------------------------------------
            stmt.append(" AND devname IN (")
            for i in range(0, len(devname_list)):
                if i > 0:
                    stmt.append(",")
                stmt.append(f"'{devname_list[i].strip()}'")
            stmt.append(")")
        if devcat is not None:
            stmt.append(" AND devcat = '")
            stmt.append(devcat)
            stmt.append("'")
        else:
            stmt.append(" AND devcat IN ('M', 'P', 'I')")
        if eptype == 'powerplus':
            stmt.append(" AND power > 0")
        stmt.append(" GROUP BY 1, 2 ORDER BY 1, 2")
        stmt.append(";")
        return "".join(stmt)

    def __get_stmt_by_time_unit_group(self, eptype:str, entity:str,
                                 units:int, tsfrom:int, tsto:int,
                                 devname_list:list, devcat:str):
        """Gets a statement for energy or power average by time unit group'.
    
        Args:
            eptype (str): Type energy or power/powerplus.
            units (int): Number of time units (t1, t2, ...).
            entity (str): An entity name like state.
            tsfrom (int): Timestamp from.
            tsto (int): Timestamp to.
            devname_list (list): Device name CSV list ('A','B',...) or None.
            devcat (str): Device category or None.
            
        Returns:
            str: Statement to get available entries.
        """
        stmt = []
        stmt.append("SELECT ")
        tn = []
        for i in range(0, units):
            if (i+1) == 5:
                tn.append("(t5/5)*5 AS 'm5'") # 5 minutes groups
            else:
                tn.append("t" + str(i+1))
        stmt.append(",".join(tn))
        group_count = units
        stmt.append(",")
        stmt.append("devname")
        group_count += 1
        stmt.append(",")
        stmt.append("devcat")
        group_count += 1
        stmt.append(",")
        stmt.append("COUNT(devname) AS 'count'")
        stmt.append(",")
        if eptype == 'energy':
            stmt.append("ROUND(MIN(energy), 3) AS 'min'")
            stmt.append(",")
            stmt.append("ROUND(MAX(energy), 3) AS 'max'")
            stmt.append(",")
            stmt.append("ROUND((MAX(energy)-MIN(energy)), 3) AS 'energy'")
        else:
            stmt.append("ROUND(MIN(ABS(power)), 1) AS 'min'")
            stmt.append(",")
            stmt.append("ROUND(MAX(ABS(power)), 1) AS 'max'")
            stmt.append(",")
            stmt.append("ROUND(AVG(ABS(power)), 1) AS 'power'")
        stmt.append(" FROM ")
        stmt.append(entity)
        stmt.append(" WHERE ")
        stmt.append(f"t0 >= {tsfrom} AND t0 <= {tsto}")
        if devname_list is not None:
            # ----------------------------------------
            # Enclose names in apostrophe using "'%s'"
            # ----------------------------------------
            stmt.append(" AND devname IN (")
            for i in range(0, len(devname_list)):
                if i > 0:
                    stmt.append(",")
                stmt.append(f"'{devname_list[i].strip()}'")
            stmt.append(")")
        if devcat is not None:
            stmt.append(" AND devcat = '")
            stmt.append(devcat)
            stmt.append("'")
        else:
            stmt.append(" AND devcat IN ('M', 'P', 'I')")
        if eptype == 'powerplus':
            stmt.append(" AND power > 0")
        stmt.append(" GROUP BY ")
        for i in range(0, group_count):
            if i > 0:
                stmt.append(",")
            stmt.append(str(i+1))
        stmt.append(" ORDER BY ")
        for i in range(0, (group_count)):
            if i > 0:
                stmt.append(",")
            stmt.append(str(i+1))
        stmt.append(";")
        return "".join(stmt)

    def __get_bar_chart_data(self, devnames:list, entries:list):
        """Gets data for bar charts.

        The entry field sequence is expected as follows:
            - devname
            - devcat
            - count
            - min (energy or power)
            - max (energy or power)
            - energy or power
   
        Args:
            devnames (list[str]): List of all involved device names.
            entries (list[tuple]): List of entries.
            
        Returns:
            dict: Chart labels, chart data.
        """
        chart_labels = []
        chart_data = {}
        # -----------------------------------------------------
        # Initialize chart data dictionary for each device name
        # -----------------------------------------------------
        for devname in devnames:
            values = []
            chart_data[devname] = values
        # --------------------------------------------
        # Set devname and value (energy) field indexes
        # --------------------------------------------
        devname_index = 0
        value_index = 5
        # ---------------
        # Process entries
        # ---------------
        for entry in entries:
            chart_labels.append(entry[devname_index])
            chart_data[entry[devname_index]] = entry[value_index]
        # ----------------------
        # Return labels and data
        # ----------------------
        return chart_labels, chart_data

    def __get_line_chart_data(self, units:int, devnames:list, entries:list):
        """Gets data for line charts.

        The entry field sequence is expected as follows:
            - units (time units t1, t2, ...)
            - devname
            - devcat
            - count
            - min (energy or power)
            - max (energy or power)
            - energy
   
        Args:
            units (str): Number of time units (t1, t2, ...)
            devnames (list[str]): List of all involved device names.
            entries (list[tuple]): List of entries.
            
        Returns:
            dict: Chart labels, chart data.
        """
        chart_labels = []
        chart_data = {}
        # -----------------------------------------------------
        # Initialize chart data dictionary for each device name
        # -----------------------------------------------------
        for devname in devnames:
            values = []
            chart_data[devname] = values
        # --------------------------------------------
        # Set devname and value (energy) field indexes
        # --------------------------------------------
        devname_index = units
        value_index = devname_index+5
        # ---------------
        # Process entries
        # ---------------
        last_label = ""
        for entry in entries:
            # -----------------------------------------
            # Set time unit group values as group label
            # -----------------------------------------
            time_values = []
            for i in range(0, units):
                value = entry[i]
                if value < 10:
                    time_values.append("0" + str(value))
                else:
                    time_values.append(str(value))
            label = self.helper.time_units_label(int("".join(time_values)))
            # --------------------------------------------------------------
            # On group label change, set all devnames' next value to None
            # as default. In this way, the value lists are consistent across
            # all devnames, whether or not there is a data entry in this
            # group for a particular devname
            # --------------------------------------------------------------
            if last_label != label:
                for devname in chart_data:
                    values = chart_data.get(devname)
                    values.append(None)
                chart_labels.append(label)
                last_label = label
            # ------------------------------------------------
            # Overwrite the last value of this entry's devname
            # ------------------------------------------------
            values = chart_data[entry[devname_index]]
            values[len(values)-1] = entry[value_index]
        # ----------------------
        # Return labels and data
        # ----------------------
        return chart_labels, chart_data

    def __get_charts(self, app:str, eptype:str,
                     chart_type:str, chart_title:str,
                     chart_labels:list, chart_data:dict):
        """Gets charts using device class 'Chart'.
    
        Args:
            app (str:) Application instance.
            eptype (str): Type 'energy' or 'power'/'powerplus'.
            chart_type (str): Chart type.
            chart_title (str): Chart title.
            chart_labels (list): Chart labels.
            chart_data (dict): Chart data.
            
        Returns:
            str: List of SVG chart files.
        """
        chart = None
        try:
            chart = Chart()
            if chart_type == "bar":
                return chart.create_bar_charts(app, eptype, chart_title,
                                        chart_labels, chart_data)
            elif chart_type == "pie":
                return chart.create_pie_charts(app, eptype, chart_title,
                                        chart_labels, chart_data)
            elif chart_type == "line":
                return chart.create_line_charts(app, eptype, chart_title,
                                        chart_labels, chart_data)
            else:
                raise Exception(self.helper.mtext(212, chart_type))
        finally:
            if chart:
                chart.close()

    def __get_chart_title(self, prefix:str, tsfrom:int, tsto:int,
                           units:int=None):
        """Gets a chart title'.
    
        Args:
            prefix (str): Title prefix.
            tsfrom (int): Timestamp from, e.g. 2023
            tsto (int): Timestamp to, e.g. 20230115
            units (int): Optional number of time units (t1, t2, ...)
            
        Returns:
            str: Chart title.
        """
        title = []
        title.append(prefix)
        if units is not None:
            title.append("/")
            if units == 5:
                title.append(
                 FIELD_DEFSETS.get("m5").get(LANG).get("label") # 5 minutes
                )
            else:
                title.append(
                 PREFIX_FIELD_DEFSETS.get(
                     "t" + str(units)).get(LANG).get("label")
                )
        title.append(" ")
        title.append(FIELD_DEFSETS.get("from").get(LANG).get("label"))
        title.append(" ")
        #title.append(self.helper.time_units_label(tsfrom))
        title.append(self.helper.timestamp_pretty(
            self.helper.timestamp_int2iso(tsfrom), LANG)
            )
        title.append(" ")
        title.append(FIELD_DEFSETS.get("to").get(LANG).get("label"))
        title.append(" ")
        #title.append(self.helper.time_units_label(tsto))
        title.append(self.helper.timestamp_pretty(
            self.helper.timestamp_int2iso(tsto), LANG)
            )
        return "".join(title)
    