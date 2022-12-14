"""
Collection of functions to mock the functionality of the standard busio
package. Necessary to test various aspects of microSWIFT code if not being run
on a Raspberry Pi. This module is not meant to be a fully functional mock of
busio, rather, it has the exact functionality required to run microSWIFT code.
"""

from . import mock_board as board

def I2C(SCL, SDA):
    """
    Function for the mock I2C connection

    Parameters:
    ----------
    SCL, SDA. Should be ints that match these values for mock_board.py 

    Returns:
    -------
    True
    """
    if SCL != board.SCL:
        raise ValueError('Incorrect value for SCL')
    if SDA != board.SDA:
        raise ValueError('Incorrect value for SDA')
    return True
