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
SETUP = False

def setmode(pin_numbering_style):
    if pin_numbering_style != BCM:
        raise ValueError('Setmode requires BCM')

def setup(pin_number, direction):
    global SETUP
    if direction not in (IN, OUT):
        raise ValueError('Direction should be IN or OUT')
    if pin_number not in range(1,27):
        raise ValueError('Pin number not valid')
    SETUP = pin_number

def output(pin_number, value):
    if value not in (HIGH, LOW):
        raise ValueError('Value should be HIGH or LOW')
    if pin_number not in range(1,27):
        raise ValueError('Pin number not valid')
    if SETUP != pin_number:
        raise Exception('Setup needs to be run first')
