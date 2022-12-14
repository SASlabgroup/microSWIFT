"""
Collection of functions to mock the functionality of the standard Rpi.GPIO
package. Necessary to test various aspects of microSWIFT code if not being run
on a Raspberry Pi. This module is not meant to be a fully functional mock of
GPIO, rather, it has the exact functionality required to run microSWIFT code.
"""

# Constants defined in GPIO
BCM = 11
BOARD = 10
BOTH = 33
FALLING = 32
HARD_PWM = 43
HIGH = 1
I2C = 42
IN = 1
LOW = 0
OUT = 0
PUD_DOWN = 21
PUD_OFF = 20
PUD_UP = 22
RISING = 31
SERIAL = 40
SPI = 41
UNKNOWN = -1
SETUP = {}
WARNINGS = True

def setmode(pin_numbering_style):
    """
    Mock function for setmode.

    Parameters:
    ----------
    pin_numbering_style. For this project it should always be BCM

    Returns:
    -------
    none
    """
    if pin_numbering_style != BCM:
        raise ValueError('Setmode requires BCM')

def setup(pin_number, direction):
    """_summary_

    Parameters
    ----------
    pin_number : _type_
        _description_
    direction : _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    """
    if direction not in (IN, OUT):
        raise ValueError('Direction should be IN or OUT')
    if pin_number not in range(1,27):
        raise ValueError('Pin number not valid')
    SETUP[f'{pin_number}'] = direction

def output(pin_number, value):
    """
    Mock function for output

    Parameters:
    ----------
    pin_number: int 1-27

    Returns:
    -------
    none
    """
    if value not in (HIGH, LOW):
        raise ValueError('Value should be HIGH or LOW')
    if pin_number not in range(1,27):
        raise ValueError('Pin number not valid')
    if f'{pin_number}' not in SETUP.keys():
        raise Exception('Setup needs to be run first')

def setwarnings(boolean):
    """
    Sets the warnings for GPIO as on or off

    Parameters:
    ----------
    bool : True or False

    Returns:
    -------
    none
    """
    if boolean in (True, False):
        WARNINGS = boolean
    else:
        raise ValueError('must be True or False')
