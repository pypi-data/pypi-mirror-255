# -*- coding: utf-8 -*-
"""myminapp"""

# -----------------------------------------------
# Disable specific pylint messages for this class
# -----------------------------------------------
#pylint: disable=W0719

from myminapp.appdef import DEVICE_CLASS_CONNECTION_SPEC
from myminapp.lib.util.helper import Helper

# =========
# Constants
# =========
# None

# ---------------------
# For Raspberry Pi only
# ---------------------
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as error:
    print(f"Probably not a Raspberry Pi environment: {error}.")

class Relay5V:

    """
    This device class communicates with GPIO ports on a SBC (Single Board
    Computer), in this case Raspberry Pi. A relay such as Elegoo DC 5V is
    required. For example, Raspberry'S GPIO 17 output may be used to
    control relay's input IN1.
    
    For more information see myminapp manual.
    """

    # ============
    # Instantiaton
    # ============

    def __init__(self):
        """Class 'Relay5V' setup.
        
        Args:
            None.
                       
        Returns:
            None.
        """
        self.name = __class__.__name__
        self.helper = Helper()
        self.gpio_pin = None
        self.init_gpio_conn()

    # ==============
    # Public methods
    # ==============

    def init_gpio_conn(self):
        """Initializes the relay GPIO connection.
        
        Args:
            None.
                       
        Returns:
            None.
        """
        # --------------------------------------------
        # Check device class connection spec pro forma
        # --------------------------------------------
        if DEVICE_CLASS_CONNECTION_SPEC.get(self.name) is None:
            raise Exception(self.helper.mtext(504, self.name))
        # -------------------
        # Set GPIO attributes
        # -------------------
        GPIO.setwarnings(False) # No warning "... channel in use ..."
        GPIO.setmode(GPIO.BCM) # GPIO numbers instead of board numbers

    def close(self):
        """Closes resources (formally only here).
        
        Args:
            None.

        Returns:
            None.
        """
        # Nothing to close here

    def get_state(self, gpio_pin:int):
        """Gets the relay state.

        Args:
            gpio_pin (int):  GPIO output pin number that is connected
             to the relay input port that is to be opened or closed.
    
        Returns:
           str: 'OFF' (relay OPEN, associated device OFF), or
                'ON' (relay CLOSED, associated device ON).
        """
        if self.gpio_pin is None or self.gpio_pin != gpio_pin:
            self.gpio_pin = gpio_pin
            GPIO.setup(self.gpio_pin, GPIO.OUT) # GPIO mode output
        gpio_state = GPIO.input(self.gpio_pin)
        if gpio_state == GPIO.LOW: # 0 is LOW, 1 is HIGH
            return "OFF"
        return "ON"

    def set_state(self, gpio_pin:int, state:str):
        """Sets the relay state.
         
        Args:
            gpio_pin (int):  GPIO output pin number that is connected
                to the relay input port that is to be opened or closed.
            state (str): 'OFF' (relay OPEN, associated device OFF), or
                         'ON' (relay CLOSED, associated device ON).
    
        Returns:
           None.
        """
        if self.gpio_pin is None or self.gpio_pin != gpio_pin:
            self.gpio_pin = gpio_pin
            GPIO.setup(self.gpio_pin, GPIO.OUT) # GPIO mode output
        if state == "OFF":
            # ---------------------------------
            # Relay OPEN, associated device OFF
            # ---------------------------------
            GPIO.output(self.gpio_pin, GPIO.LOW)
        elif state == "ON":
            # ----------------------------------
            # Relay CLOSED, associated device ON
            # ----------------------------------
            GPIO.output(self.gpio_pin, GPIO.HIGH)
        else:
            raise Exception(self.helper.mtext(501, state))

    # ===============
    # Private methods
    # ===============
    # None
