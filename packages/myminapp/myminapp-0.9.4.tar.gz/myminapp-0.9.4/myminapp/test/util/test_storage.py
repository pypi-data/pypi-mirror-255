# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=R0914
#pylint: disable=R0915
#pylint: disable=W0123

import os
import unittest

from myminapp.appdef import DATA_HOME
from myminapp.lib.util.storage import Storage

TESTDB_NAME = "test_storage"

class TestStorage(unittest.TestCase):

    """Test class."""

    def test_util(self):
        """Performs a utility test.
        
        Args:
            None.

        Returns:
            None.
        """
        util = Storage(DATA_HOME + "/storage", TESTDB_NAME)
        try:

            # -------------------------------------------
            # Remove probably existing test database file
            # -------------------------------------------
            testdb = DATA_HOME + "/storage/" + TESTDB_NAME + ".db"
            if os.path.exists(testdb):
                os.remove(testdb)

            # ------------
            # Open storage
            # ------------
            util.open()

            # ---
            # Add
            # ---
            cmd = "state"
            data = {}
            data["devname"] = "SOLAR"
            data["devcat"] = "P"
            data["state"] = "ON"
            data["power"] = "15.1"
            data["energy"] = "250.123"
            data["tempc"] = "15.0"
            data["info"] = '{"code": 0, "text": "OK"}'
            last_id = util.add(cmd, data)
            print(f"add result (last id): {last_id}")
            self.assertGreaterEqual(last_id, 1)

            # ------------------------
            # Read by native statement
            # ------------------------
            result = util.read_by_native_statement(f"select * from {cmd};")
            print(f"read result: {result}")
            data = result[1][0]
            first_id = data[0]
            self.assertEqual(first_id, 1)
            info_set = eval(data[len(data)-1])
            self.assertIsInstance(info_set, dict)
            self.assertEqual(info_set.get("code"), 0)
            self.assertEqual(info_set.get("text"), "OK")

            # ----------
            # Read by ID
            # ----------
            fields, r = util.read_by_id(cmd, 1)
            print(f"read_by_id result: {fields}, {r}")
            self.assertEqual(r[0], 1)

            # ----------
            # Field list
            # ----------
            result = util.get_field_list(cmd)
            print(f"get_field_list_result: {result}")
            self.assertEqual(result[0], "id")
            self.assertEqual(result[1], "t0")
            self.assertEqual(result[2], "t1")
            self.assertEqual(result[3], "t2")
            self.assertEqual(result[4], "t3")
            self.assertEqual(result[5], "t4")
            self.assertEqual(result[6], "t5")
            self.assertEqual(result[7], "t6")
            self.assertEqual(result[8], "devname")
            self.assertEqual(result[9], "devcat")
            self.assertEqual(result[10], "state")
            self.assertEqual(result[11], "power")
            self.assertEqual(result[12], "energy")
            self.assertEqual(result[13], "tempc")
            self.assertEqual(result[14], "info")

            # -------------------
            # Read BLOB from file
            # -------------------
            filename = "test-numcam757.bmp"
            file = DATA_HOME + "/temp/camera/" + filename
            blob = None
            with open(file, 'rb') as f:
                blob = f.read()
            blob_size = len(blob)
            self.assertEqual(blob_size, 172854)
            print(f"BLOB size: {blob_size}")

            # ---------------------
            # Write BLOB to storage
            # ---------------------
            cmd = "psdischarge"
            data = {}
            data["value"] = "OK (level=42)"
            data["file"] = filename
            data["object"] = blob
            last_id = util.add(cmd, data)
            print(f"add result (last id): {last_id}")

            # ----------------------
            # Read BLOB from storage
            # ----------------------
            fields, result = util.read_by_id(cmd, last_id)
            blob_size = len(result[len(result)-1])
            self.assertEqual(blob_size, 172854)
            print(f"read_by_id results (with BLOB size): {fields}, "\
                  f"{blob_size}")

            # ------------------
            # Write BLOB to file
            # ------------------
            blob2 = result[len(result)-1]
            filename = "test-numcam757-2.bmp"
            file = DATA_HOME + "/temp/camera/" + filename
            with open(file, 'wb') as f:
                f.write(blob2)

        finally:
            if util is not None:
                util.close()

if __name__ == '__main__':
    unittest.main()
