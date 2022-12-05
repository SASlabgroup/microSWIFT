"""
Collection of functions to mock the functionality of the IMU module driver
package. Necessary to test various aspects of microSWIFT code if not being run
on a Raspberry Pi. This module is not meant to be a fully functional mock of
the IMU module driver, rather, it has the exact functionality required to
run microSWIFT code.
"""

class FXOS8700:
    """Class for the mock driver"""
    def __init__(self, i2c, accel_range):
        """
        """

        if i2c is False:
            raise Exception('i2c must be successfully called first')

        if accel_range != 0x00:
            raise ValueError('accel_range must be 0x00')

        return

    @property
    def accelerometer(self):
        """TODO: return random, but realistic values"""
        accel_x = 9
        accel_y = 8
        accel_z = 7

        return accel_x, accel_y, accel_z

    @property
    def magnetometer(self):
        """TODO: return random, but realistic values"""
        mag_x = 5
        mag_y = 4
        mag_z = 3

        return mag_x, mag_y, mag_z
