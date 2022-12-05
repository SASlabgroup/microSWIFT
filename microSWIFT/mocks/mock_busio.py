"""
Collection of functions to mock the functionality of the standard busio
package. Necessary to test various aspects of microSWIFT code if not being run
on a Raspberry Pi. This module is not meant to be a fully functional mock of
busio, rather, it has the exact functionality required to run microSWIFT code.
"""

from . import mock_board as board

def I2C(SCL, SDA):
    if (SCL, SDA) not in (board.SCL, board.SDA):
        raise ValueError('Incorrect values for SCL and SDA')
    return True
