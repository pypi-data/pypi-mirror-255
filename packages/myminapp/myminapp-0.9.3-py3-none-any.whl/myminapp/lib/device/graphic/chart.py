# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0103
#pylint: disable=R0913
#pylint: disable=W0719

import os
import pygal

from myminapp.appdef import DATA_HOME
from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
# None

class Chart:

    """
    This device class draws bar, line, and pie charts. 
     
    Requires: pip install pygal

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Chart' setup.
        
        Args:
            None.
                       
        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        # --------------------------------------------
        # Check device class connection spec pro forma
        # --------------------------------------------
        if DEVICE_CLASS_CONNECTION_SPEC.get(self.name) is None:
            raise Exception(self.helper.mtext(504, self.name))
        # -----------------------------------
        # Create the target path if necessary
        # -----------------------------------
        self.file_conn = DATA_HOME + "/temp/chart"
        if os.path.exists(self.file_conn) is False:
            os.makedirs(self.file_conn)

    # ==============
    # Public methods
    # ==============

    def create_bar_charts(self, app:str, cmd:str, title:str,
                          labels:list, data:dict):
        """Creates bar charts.

        Args:
            app (str): Calling application instance, used as file name prefix.
            cmd (str): Calling command, used as file name prefix.
            title (str): Chart title.
            labels (list): Chart labels.
            data (dict): Chart data.
           
        Returns:
            str: SVG charts as HTML code, enclosed in <div> </div>.
        """
        charts = None
        files = []
        # ------------
        # Bar chart #1
        # ------------
        bar_chart = pygal.Bar()
        bar_chart.title = title
        for name in labels:
            bar_chart.add(name, data.get(name), allow_interruptions=True,
                           rounded_bars=4)
        file = app + "-" + cmd + "-bar-chart.svg"
        bar_chart.render_to_file(self.file_conn + "/" + file)
        files.append(file)
        # ---------------------------------------------
        # Join file names to chart file list and return
        # ---------------------------------------------
        charts = ",".join(files)
        return charts

    def create_pie_charts(self, app:str, cmd:str, title:str,
                          labels:list, data:dict):
        """Creates pie charts.

        Args:
            app (str): Calling application instance, used as file name prefix.
            cmd (str): Calling command, used as file name prefix.
            title (str): Chart title.
            labels (list): Chart labels.
            data (dict): Chart data.
           
        Returns:
            str: SVG charts as HTML code, enclosed in <div> </div>.
        """
        charts = None
        files = []
        # ------------
        # Pie chart #1
        # ------------
        pie_chart = pygal.Pie(half_pie=False)
        pie_chart.title = title
        for name in labels:
            pie_chart.add(name, data.get(name), allow_interruptions=True)
        file = app + "-" + cmd + "-pie-chart.svg"
        pie_chart.render_to_file(self.file_conn + "/" + file)
        files.append(file)
        # ---------------------------------------------
        # Join file names to chart file list and return
        # ---------------------------------------------
        charts = ",".join(files)
        return charts

    def create_line_charts(self, app:str, cmd:str, title:str,
                           labels:list, data:dict):
        """Creates line charts.

        Args:
            app (str): Calling application instance, used as file name prefix.
            cmd (str): Calling command, used as file name prefix.
            title (str): Chart title.
            labels (list): Chart labels.
            data (dict): Chart data.
           
        Returns:
            str: SVG charts as HTML code, enclosed in <div> </div>.
        """
        SHOW_LABELS_MAX = 61
        charts = None
        files = []
        # -------------
        # Line chart #1
        # -------------
        if len(labels) > SHOW_LABELS_MAX:
            line_chart = pygal.Line(show_x_labels=False)
        else:
            line_chart = pygal.Line(show_x_labels=True)
        line_chart.title = title
        line_chart.x_labels = labels # Set labels in any case for tooltips
        line_chart.x_label_rotation = -90
        for name in data.keys():
            values = data.get(name)
            line_chart.add(name, values, allow_interruptions=True)
        file = app + "-" + cmd + "-line-chart.svg"
        line_chart.render_to_file(self.file_conn + "/" + file)
        files.append(file)
        # ---------------------------------------------
        # Join file names to chart file list and return
        # ---------------------------------------------
        charts = ",".join(files)
        return charts

    def close(self):
        """Closes resources (formally only here).
        
        Args:
            None.

        Returns:
            None.
        """
        # Nothing to close here

    # ===============
    # Private methods
    # ===============
    # None
        