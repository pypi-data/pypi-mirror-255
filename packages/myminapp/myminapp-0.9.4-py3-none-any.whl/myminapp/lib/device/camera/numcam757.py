# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=C0103
#pylint: disable=C0200
#pylint: disable=R0914
#pylint: disable=W0105
#pylint: disable=W0719

import os
import time
import pygame
import pygame.camera
import pygame.transform

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
# None

class Numcam757:

    """
    This device class captures the filling level of an ANKER 757 power
    station from its display using a simple HD camera positioned in front
    of the display. The positioning must be accurate so that the digits
    are within the expected range of the captured image.

    On Linux, the video port is specified as follows: /dev/video<n>,
    e.g. /dev/video0. On Windows: <name>, e.g. HD Camera.
    
    Requires: pip install pygame

    Remark: To activate the display before capturing, a USB device
    connected to the power station might briefly be switched on and off
    using a relay.

    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Numcam757' setup.
        
        Args:
            None.
                       
        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        cam_conn = DEVICE_CLASS_CONNECTION_SPEC.get(self.name)
        if cam_conn is None:
            raise Exception(self.helper.mtext(504, self.name))
        self.port = cam_conn.get("port")
        if self.port is None:
            raise Exception(self.helper.mtext(505, 'port', self.name))
        self.cam = None

    # ==============
    # Public methods
    # ==============

    def get_image(self, file:str=None):
        """Gets a captured image.
        
        Args:
            file (str): Optional path and file name to save the image.
                        File extension must be '.bmp'

        Returns:
           bytearray: An image captured and transformed using pygame.
        """
        try:
           # ------------------
            # Initialize camera
            # -----------------
            pygame.camera.init()
            # ----------------------------------------------------
            # Get camera list and validate given camera descriptor
            # ----------------------------------------------------
            camlist = pygame.camera.list_cameras()
            exists = False
            for desc in camlist:
                if desc == self.port:
                    exists = True
                    break
            if exists is not True:
                raise Exception(f"Camera '{self.port}' is not in list '{camlist}'.")
            # ---------------------------------------------------------
            # Get camera object with lowset 16:9 HD resolution, which
            # obiously is 320x180 pixels for pygame, and color space
            # RGB (black and white seems not to be supported by pygame)
            # ---------------------------------------------------------
            self.cam = pygame.camera.Camera(self.port, (320, 180), "RGB")
            # ----------------------------------------------
            # Start camera, wait a second and then get image
            # ----------------------------------------------
            self.cam.start()
            time.sleep(1.0)
            img = self.cam.get_image()
            # -----------------------------------------
            # Get second image and transform mostly all
            # background pixels to black
            # -----------------------------------------
            img2 = img.copy()
            search_color = None
            threshold = (200, 200, 200, 0)
            set_color = (0, 0, 0, 0)
            inverse_set = True
            pygame.transform.threshold(
                img2, img, search_color = search_color,
                threshold = threshold, set_color = set_color,
                inverse_set = inverse_set)
            img = None
            # -------------------------------------------
            # Get third image and transform all remaining
            # non-black-pixels to pure white
            # -------------------------------------------
            img3 = img2.copy()
            set_color = (255, 255, 255, 0)
            inverse_set = False
            pygame.transform.threshold(
                img3, img2, search_color = search_color,
                threshold = threshold, set_color = set_color,
                inverse_set = inverse_set)
            img2 = None
            # ----------
            # Flip image
            # ----------
            img3a = pygame.transform.flip(img3, True, True)
            img3 = img3a.copy()
            # -----------------------------------
            # Optionally save image, return image
            # -----------------------------------
            if file is not None:
                # ------------------------
                # Extension must be '.bmp'
                # ------------------------
                if not file.endswith(".bmp"):
                    raise Exception("File extension must be '.bmp'")
                # -----------------------------------
                # Create the target path if necessary
                # -----------------------------------
                path = file[:file.rindex("/")]
                if os.path.exists(path) is False:
                    os.makedirs(path)
                # ----------
                # Save image
                # ----------
                pygame.image.save(img3, file)
            return pygame.image.tobytes(img3, "RGB")
        finally:
            # -----------
            # Stop camera
            # -----------
            if self.cam is not None:
                self.cam.stop()

    def get_number(self, file:str=None):
        """Gets the number recognized in an image received from get_image.
         
        Args:
            file (str): Optional path and file name to save the image.
                        File extension must be '.bmp'

        Returns:
           int: The number from the image or -1 if no number was recognized.
        """
        img = None
        img = self.get_image(file)
        ones = self.__get_digit(img, 'O')
        tens = self.__get_digit(img, 'T')
        if ones == -1:
            return -1
        elif ones == 0 and tens == 0:
            return 100
        elif tens == -1:
            return ones
        else:
            s = str(tens) + str(ones)
            return int(s)

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

    def __get_digit(self, img:bytearray, place:str):
        """Gets the digit from the image at the specified place.

        Args:
            img (bytearray): The image.
            place (str): The digit's place, T = tens, O = ones
    
        Returns:
            int: The digit or -1 if no digit was recognized.
        """
        ''''
        ----
        Note
        ----
        The image is 320 pixels wide and 180 pixels high.
        
        The places with tens and ones are examined, where 0 0 is interpreted
        as 100 and a single 0 as 0. The X ranges of the both places start
        approximately as follows:
            
        PT_X = 85  # Tens place X offset
        PO_X = 205 # Ones place X offset
        
        The Y ranges start as follows:
            
        PT_Y = 10 # Tens place Y offset
        PO_Y = 10 # Ones place Y offset
        
        A digit in a place consists of a mmaximum of 7 elements, A to G,
        as shown below using digit 8:
            
               ___________
          A    ___________ 
             
            | |          | |
          B | |        C | |
            | |          | |
            | |          | |
               ___________
          D    ___________ 
          
            | |          | |
          E | |        F | |
            | |          | |
            | |          | |
              ____________
          G   ____________          
           
        The middle X and Y positions of the elements are approximately:
                
        A_X = 50
        A_Y = 10
        B_X = 10
        B_Y = 50
        C_X = 90
        C_Y = 50
        D_X = 50
        D_Y = 85
        E_X = 10
        E_Y = 120
        F_X = 90
        F_Y = 120
        G_X = 50
        G_Y = 155
        
        To get a specific pixel's value, the corresponding place's X offset
        value has to be added to the element's X value, and the place's
        Y offset value to the element's Y value.
        
        The image is prepared to contain only the values 0 (black) and 255
        (white), where 255 represents a pixel within an element.
        
        However, the bytearray contains 3 bytes per pixel, so each line
        has a length of 960 and is compressed to 320 using the third byte
        per pixel only.
        '''
        #PT_X = 94  # Tens place X offset
        #PT_Y = 18  # Tens place Y offset
        #PO_X = 212 # Ones place X offset
        #PO_Y = 18  # Ones place Y offset
        PT_X = 85  # Tens place X offset
        PT_Y = 10  # Tens place Y offset
        PO_X = 205 # Ones place X offset
        PO_Y = 10  # Ones place Y offset
        X = [50, 10, 90, 50, 10, 90, 50]
        Y = [10, 50, 50, 85, 120, 120, 155]
        # -------------------------
        # Set image content as rows
        # -------------------------
        n1 = 0
        n2 = 0
        rows = {}
        row = []
        for _ in img:
            n1 += 1
            n2 += 1
            if n2 == 3:
                row.append(img[n1-1])
                n2 = 0
            if (n1 % 960) == 0:
                rn = int(n1/960)
                rows[rn] = row
                row = []
        # ----------------------
        # Set actual coordinates
        # ----------------------
        ofs_x = 0
        ofs_y = 0
        if place == 'T':
            ofs_x = PT_X
            ofs_y = PT_Y
        elif place == 'O':
            ofs_x = PO_X
            ofs_y = PO_Y
        else:
            raise Exception(f"Invalid place '{place}'.")
        x = []
        y = []
        for i in range(0, len(X)):
            x.append(ofs_x + X[i])
            y.append(ofs_y + Y[i])
        # ----------------
        # Set pixel values
        # ----------------
        values = []
        for i in range(0, len(x)):
            row = rows[y[i]]
            col = row[x[i]]
            values.append(col)
            #TEST
            #print(f"row#: {y[i]} col#: {x[i]}, value: {col}")
        # -------------------------------------------
        # Get digit by pixel value pattern and return
        # -------------------------------------------
        return self.__get_digit_by_pattern(values)

    def __get_digit_by_pattern(self, pattern:list):
        """ Gets a digit by pixel value pattern comparison.

        Args:
            pattern (list): The pixel values recognized with get_digit.

        Returns:
            int: The digit or -1 if no pattern matches.
        """
        # --------------------------------------------
        # 2D array with patterns for the digits 0 to 9
        # --------------------------------------------
        P = [
            [255, 255, 255, 0, 255, 255, 255],      #0
            [0, 0, 255, 0, 0, 255, 0],              #1
            [255, 0, 255, 255, 255, 0, 255],        #2
            [255, 0, 255, 255, 0, 255, 255],        #3
            [0, 255, 255, 255, 0, 255, 0],          #4
            [255, 255, 0, 255, 0, 255, 255],        #5
            [255, 255, 0, 255, 255, 255, 255],      #6
            [255, 0, 255, 0, 0, 255, 0],            #7
            [255, 255, 255, 255, 255, 255, 255],    #8
            [255, 255, 255, 255, 0, 255, 255]       #9
            ]
        s1 = str(pattern)

        #TEST print(f"pattern: {s1}")

        for i in range(0, len(P)):
            s2 = str(P[i])
            if s1 == s2:
                return i
        return -1
    