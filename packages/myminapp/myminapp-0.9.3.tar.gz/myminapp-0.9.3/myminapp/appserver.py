# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0103
#pylint: disable=R0912
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=R1702
#pylint: disable=R1705
#pylint: disable=W0622
#pylint: disable=W0718
#pylint: disable=W0719

import argparse
import os
import traceback
import urllib.parse
import base64
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from ssl import SSLContext
from ssl import PROTOCOL_TLS_SERVER

from myminapp.app import App
from myminapp.appdef import HOME
from myminapp.appdef import DATA_HOME
from myminapp.appdef import COMMAND_DEFSETS
from myminapp.appdef import COMMAND_PRESETS
from myminapp.appdef import FIELD_DEFSETS
from myminapp.appdef import PREFIX_FIELD_DEFSETS
from myminapp.appdef import LANG
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
CONTENT_TYPES = {
    '.ico': 'image/x-icon',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.bmp': 'image/bmp',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain; charset=utf-8',
    '.htm': 'text/html; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.svg': 'image/svg+xml; charset=utf-8'
}
WEB_INDICATOR = 'web='

class AppServer(BaseHTTPRequestHandler):

    """
    This class works as a handler for GET requests. It provides the
    following features:

        - Instantiate the App class
        - Receive GET requests (overrides do_GET)
        - Invoke the request method of the App instance
        - Receive, handle, and return the response
        - Route logging (overrides log_message)

    Requests can be sent from a browser or any other HTTP/HTTPS client.
    JSON format is specified for requests and responses.

    For more information see myminapp manual.
    """

    # ===============
    # Class variables
    # ===============
    app = None
    helper = None

    # ==============
    # Public methods
    # ==============

    #Overrides
    def do_GET(self):
        """See superclass."""
        # ------------------------------
        # Handle non-application request
        # ------------------------------
        content = None
        try:
            extension = (os.path.splitext(self.path))[1]
            if len(extension) > 0:
                if extension == ".pdf" and self.path.find("manual") > -1:
                    filename = HOME + "/doc/myminapp-manual-" + LANG + ".pdf"
                elif extension == ".bmp":
                    filename = DATA_HOME + "/temp/camera/" + self.path
                elif extension == ".svg":
                    filename = DATA_HOME + "/temp/chart" + self.path
                else:
                    filename = HOME + "/web" + self.path
                if os.path.exists(filename):
                    for ext in CONTENT_TYPES:
                        if ext == extension:
                            content_type = CONTENT_TYPES.get(ext)
                            if content_type.find("image/") > -1 or \
                                content_type.find("application/") > -1:
                                with open(filename, 'rb') as file:
                                    content = file.read()
                            else:
                                with open(filename, 'r', encoding="utf-8") \
                                    as file:
                                    data = file.read()
                                content = bytes(data + "\n", 'utf8')
                            self.send_response(200)
                            self.send_header('Content-type', content_type)
                            break
                else:
                    raise Exception("n/a")
        except Exception as exception:
            data = f"Bad request: '{self.path}' ({exception})"
            content = bytes(data + "\n", 'utf8')
            self.send_response(400)
            self.send_header('Content-type','text/plain; charset=utf-8')
        if content is not None:
            # ------------------------------------------------------------
            # Set content length and end headers, write content and return
            # ------------------------------------------------------------
            self.send_header('Content-length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        # -----------------------------------------------------------
        # Handle application request: Check rudimentary. If the check
        # fails, send code 400 plus error text, otherwise perform the
        # request. Send the response in JSON format with code 200 or
        # error text and code from the request
        # -----------------------------------------------------------
        error = False
        web_req = None
        req_json = None
        cmd = None
        resp = None
        try:
            query = urllib.parse.unquote_plus(self.path).strip()
            # ---------------------------------
            # Detect a web request by indicator
            # ---------------------------------
            index = query.find(WEB_INDICATOR)
            if index > -1:
                index += len(WEB_INDICATOR)
                web_req = query[index:].strip()
                if web_req.startswith("{"):
                    req_json = web_req
                    cmd = self.helper.json2dict(req_json).get("cmd")
                # -------------------
                # Perform web request
                # -------------------
                code, resp = self.__web_request(web_req, cmd, req_json)
                if code != 200:
                    error = True
                self.send_response(code)
            else:
                # ---------------
                # Perform request
                # ---------------
                index = query.find("{")
                if index < 0:
                    error = True
                    resp = f"Bad request: '{self.path}'"
                    self.send_response(400)
                else:
                    req_json = query[index:]
                    code, resp = self.__request(req_json)
                    if code != 200:
                        error = True
                    self.send_response(code)
        except Exception as exception:
            error = True
            if req_json is None:
                req_json = self.requestline
            resp = f"Bad request: '{req_json}' ({exception})"
            self.send_response(400)
        # -----------------------
        # Set response as message
        # -----------------------
        message = bytes(resp + "\n", 'utf8')
        # ------------
        # Send headers
        # ------------
        if error is True or web_req is not None:
            self.send_header('Content-type','text/plain; charset=utf-8')
        else:
            # -----------------------------------------------------------
            # Note: favicon.ico will not be displayed if JSON is returned
            # -----------------------------------------------------------
            ### self.send_header('Content-type','text/plain; charset=utf-8')
            self.send_header('Content-type','application/json; charset=utf-8')
        # ------------------------------------------------------------
        # Set content length and end headers, write message and return
        # ------------------------------------------------------------
        self.send_header('Content-length', str(len(message)))
        self.end_headers()
        self.wfile.write(message)
        return

    #Overrides
    def log_message(self, format, *args):
        """See superclass."""  
        if isinstance(args, tuple):
            line = format % tuple(args) + " from: " + self.address_string()
        else:
            line = "'" + str(args) + "' from: " + self.address_string()
        self.app.log(107, line)

    # ===============
    # Private methods
    # ===============

    def __request(self, req):
        """Handles a command request.
    
        Args:
            req (dict|str): Request as dictionary or in JSON format.

        Returns:
            int: Code (200, 500).
            dict|str: For code 200 response as input type, otherwise as str.
        """
        code = None
        resp = None
        try:
            if isinstance(req, str):
                resp = self.app.perform_command(self.helper.json2dict(req))
                code = 200
                return code, self.helper.dict2json(resp)
            else:
                resp = self.app.perform_command(req)
                code = 200
                return code, resp
        except Exception as exception:
            code = 500
            resp = str(exception)
            self.app.log(105, self.helper.mtext(105, self.helper.tbline()))
            return code, resp

    def __web_request(self, web_req, cmd, req_json:str):
        """Handles a web request.
    
        Args:
            web_req (str): Web request (preset or command).
            cmd (str): Command name for web command request.
            req_json (str): Original request in JSON format.

        Returns:
            int: Code (200, 500).
            str: Response in text format.
        """
        code = None
        resp = None
        try:
            if web_req.startswith("{"):
                return self.__get_web_data(cmd, req_json)
            else:
                return self.__get_web_preset(web_req)
        except Exception as exception:
            code = 500
            resp = str(exception)
            self.app.log(105, self.helper.mtext(105, self.helper.tbline()))
            return code, resp

    def __get_web_preset(self, web_req:str):
        """Gets a command preset list or a preset command.
    
        Args:
            web_req (str): The web request.

        Returns:
            int: Code.
            str: HTML option list or command (both text format).
        """
        ENT_0 = f"<!--lang={LANG}-->"
        ENT_1 = "<option value=\"command\" selected>...</option>"
        ENT_N = "<option value=\"%s\">%s</option>"
        if len(COMMAND_PRESETS) == 0:
            # ----------------------------------------------------
            # Should not occur, but COMMAND_PRESET could be empty.
            # In this case set HTTP code 404 with the 'No data'
            # message (message code 3)
            # ----------------------------------------------------
            text = self.helper.mtext(3)
            self.app.log(3, text)
            code = 404
            resp = text
        else:
            if web_req == "list":
                entries = []
                entries.append(ENT_0)
                entries.append(ENT_1)
                for name in COMMAND_PRESETS:
                    entries.append(ENT_N % (name, name))
                resp = "".join(entries)
                code = 200
            else:
                resp = COMMAND_PRESETS.get(web_req)
                if resp is None:
                    resp = f"Bad request: '{web_req}'"
                    code = 400
                else:
                    resp = self.helper.dict2json(resp)
                    code = 200
        return code, resp

    def __get_web_data(self, cmd:str, req_json:str ):
        """Gets data as a table.
    
        Args:
            cmd (str): Command name.
            req_json (str): The original request.

        Returns:
            int: Code.
            str: Data as HTML table (text format).
        """
        header = None
        data = None
        code, resp = self.__request(self.helper.json2dict(req_json))
        if code == 200:
            if len(resp) == 0:
                # ---------------------------------------------------
                # Should not occur, but request could return code 200
                # with an empty list. In this case set HTTP code 404
                # with the 'No data' message (message code 3)
                # ---------------------------------------------------
                text = self.helper.mtext(3)
                self.app.log(3, text)
                code = 404
                resp = text
            else:
                # ---------------------
                # Process response data
                # ---------------------
                fields = resp[0].get("data").get("fields")
                charts = resp[0].get("data").get("charts")
                sub_code, sub_resp = self.__get_web_table_header(
                                                    cmd, fields, charts)
                if sub_code != 200:
                    return sub_code, sub_resp
                else:
                    header = sub_resp
                entries = resp[0].get("data").get("entries")
                if entries is None:
                    entries = []
                    for entry in resp:
                        entries.append(entry.get("data"))
                sub_code, sub_resp = self.__get_web_table_data(entries)
                if sub_code != 200:
                    return sub_code, sub_resp
                else:
                    data = sub_resp
                code = 200
                resp = header + data
        return code, resp

    def __get_web_table_header(self, cmd:str, fields:list=None,
                                charts:str=None):
        """Gets a web table header from given field list or from defset.
    
        Args:
            cmd (str): Command name.
            fields (list): Optional given field name list.
            fields (list): Optional CSV list of chart file names.

        Returns:
            int: Code.
            str: Language specific web table header.
        """
        ROW = '<tr>%s</tr>'
        COL = '<th>%s</th>'
        CHART_BUTTON = '<input type="button" class="chart-button" ' + \
            'style=background-image:url("image-%schart.png"); ' + \
            'onclick="window.open(\'%s\', \'_blank\');">'
        code = None
        resp = None
        labels = None
        if fields is not None:
            # ------------------------
            # Use the given field list
            # ------------------------
            code, resp = self.__get_field_labels(fields)
            if code != 200:
                return code, resp
            else:
                labels = resp
        else:
            # ------------------------------------------
            # Use the defset output from COMMAND_DEFSETS
            # ------------------------------------------
            defset = COMMAND_DEFSETS.get(cmd)
            if defset is None:
                raise Exception(f"Undefined: {cmd}")
            output = defset.get("output")
            if output is None:
                raise Exception(f"Undefined: {cmd}, output")
            code, resp = self.__get_field_labels(output)
            if code != 200:
                return code, resp
            else:
                labels = resp
        if labels is None:
            code = 400
            resp = f"Bad request: {cmd}, labels"
            return code, resp
        else:
            cols = []
            for label in labels:
                cols.append(COL % (label))
            code = 200
            resp = ROW % ("".join(cols))
            # -------------------------------------------------------
            # If chart file names are given, add buttons to the last
            # header column to open charts of type line, bar, or pie.
            # The file names must contain 'line', 'bar', or 'pie'.
            # ------------------------------------------------------
            if charts is not None:
                names = charts.split(",")
                buttons = []
                for name in names:
                    if name.find("line") > -1:
                        buttons.append(CHART_BUTTON % ('line', name))
                    elif name.find("bar") > -1:
                        buttons.append(CHART_BUTTON % ('bar', name))
                    elif name.find("pie") > -1:
                        buttons.append(CHART_BUTTON % ('pie', name))
                    else:
                        pass # Currently unsupported
                resp = resp.replace('</th></tr>',
                                     "".join(buttons) + '</th></tr>')
            return code, resp

    def __get_web_table_data(self, entries):
        """Gets web table data from given entries.
    
        Args:
            entries (?): Data entries.

        Returns:
            int: Code.
            str: Web table data.
        """
        ROW = '<tr>%s</tr>'
        COL = '<td>%s</td>'
        #IMG = '<img src="%s" alt="%s" height=80></img>'
        IMG = '<img src="data:image/bmp;charset=utf-8;base64,%s" alt="%s" ' \
                'height=80></img>'
        code = None
        resp = None
        rows = []
        cols = []
        # --------------------------------------------------------
        # Determine the specific type and set the data accordingly
        # --------------------------------------------------------
        for entry in entries:
            if isinstance(entry, list) or isinstance(entry, tuple):
                for value in entry:
                    cols.append(self.__get_column_value(COL, IMG, value))
            elif isinstance(entry, dict):
                for field in entry.keys():
                    value = entry.get(field)
                    cols.append(self.__get_column_value(COL, IMG, value))
            else:
                value = str(entry)
                cols.append(self.__get_column_value(COL, IMG, value))
            # ----------------------------------
            # Append cols to row and row to rows
            # ----------------------------------
            rows.append(ROW % ("".join(cols)))
            cols = []
        resp = "".join(rows)
        # ---------------------
        # Return result as text
        # ---------------------
        code = 200
        return code, resp

    def __get_column_value(self, col:str, img:str, value:str):
        """Gets a formatted column value for a HTML table cell.
    
        Args:
            col (str): A column value frame.
            img (str): An image source data frame.
            value (str): The value.

        Returns:
            str: The formatted column value.
        """
        column = None
        if value is not None and isinstance(value, bytes):
            # --------------------------------
            # Assume binary object is an image
            # --------------------------------
            data = base64.b64encode(value)
            data = data.decode("UTF-8")
            column = col % (img % (data, len(data)))
        if column is None:
            column = col % (value)
        return column

    def __get_field_labels(self, fields:list):
        """Gets language specific field labels.
    
        Args:
            fields (list): A field name list.

        Returns:
            int: Code.
            str: Language specific field labels.
        """
        code = None
        resp = None
        labels = []
        for field in fields:
            defset = PREFIX_FIELD_DEFSETS.get(field)
            if defset is None:
                defset = FIELD_DEFSETS.get(field)
            if defset is None:
                labels.append(field) # Allow fields like 'min(power)'
            else:
                defset_lang = defset.get(LANG)
                if defset_lang is None:
                    raise Exception(f"Undefined: {field}, {LANG}")
                label = defset_lang.get("label")
                if label is None:
                    raise Exception(f"Undefined: {field}, {LANG}, label")
                labels.append(label)
        code = 200
        resp = labels
        return code, resp

# ====
# Main
# ====

def main():
    """Main method.
    
        Args:
            See documentation or code.

        Returns:
            None.
        """
    #appserver = None
    httpd = None
    try:
        # ----
        # Args
        # ----
        parser = argparse.ArgumentParser(
                    description="Appserver for myminapp")
        parser.add_argument('-appnum', type=int, default=1,
                help="application instance number, e.g. 1 (default), 2, ...")
        parser.add_argument('-host', type=str, default="127.0.0.1",
                help="host, e.g. 127.0.0.1 (default), 192.168.0.20, ...")
        parser.add_argument('-port', type=int, default=8081,
                help="port, e.g. 8081 (default), 4443, ...")
        parser.add_argument('-cert', type=str,
                help="path to cert.pem file for HTTPS")
        parser.add_argument('-key', type=str,
                help="path to key.pem file for HTTPS")
        args = parser.parse_args()
        appnum = args.appnum
        host = args.host
        port = args.port
        cert = args.cert
        key = args.key
        # ----------------
        # Setup and launch
        # ----------------
        pid = os.getpid()
        AppServer.app = App(appnum)
        AppServer.helper = Helper()
        httpd = HTTPServer((host, port), AppServer)
        if cert is not None and key is not None:
            context = SSLContext(PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert, key)
            httpd.socket = context.wrap_socket(
                sock = httpd.socket, server_side = True)
        text = f"host: {host}, port: {port}, pid: {pid}, appnum: {appnum}"
        AppServer.app.log(150, AppServer.helper.mtext(150, text))
        httpd.serve_forever()
    except KeyboardInterrupt:
        AppServer.app.log(151, AppServer.helper.mtext(151))
    except Exception:
        print(" ".join(str(traceback.format_exc()).split()))
    finally:
        try:
            if AppServer.app is not None:
                AppServer.app.close()
            if httpd is not None:
                httpd.server_close()
        except Exception:
            print(" ".join(str(traceback.format_exc()).split()))

if __name__ == '__main__':
    main()
