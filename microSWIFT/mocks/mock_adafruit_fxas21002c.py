"""
Collection of functions to mock the functionality of the IMU module driver
package. Necessary to test various aspects of microSWIFT code if not being run
on a Raspberry Pi. This module is not meant to be a fully functional mock of
the IMU module driver, rather, it has the exact functionality required to
run microSWIFT code.
"""

class FXAS21002C:
    """
    TODO: Class short description.

    TODO: Class long description.

    Attributes
    ----------
    attribute1 : type
        Description.
    attribute2 : type
        Description.

    Methods
    -------
    method1(argument1, argument2)
        Description.
    method2(argument1, argument2)
        Description.

    """

    def __init__(self, i2c, gyro_range):
        """
        TODO:
        """

        if i2c is False:
            raise Exception('i2c must be successfully called first')

        if gyro_range != 500:
            raise ValueError('gyro_range must be 500')

        return

    @property
    def gyroscope(self):
        """TODO: return random, but realistic values"""
        gyro_x = 0
        gyro_y = 1
        gyro_z = 2

        return gyro_x, gyro_y, gyro_z
