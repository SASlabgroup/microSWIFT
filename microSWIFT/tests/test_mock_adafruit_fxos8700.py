"""Unit tests for the mock_adafruit_fxos8700.py"""
import unittest
from mocks import mock_adafruit_fxos8700
from mocks import mock_busio
from mocks import mock_board

class Testfxos(unittest.TestCase):
    """
    Test class for the mock fxos8700 driver.
    """
    def test_smoke(self):
        """
        Smoke test for the fxos driver.
        """
        i2c = mock_busio.I2C(mock_board.SCL, mock_board.SDA)
        fxos = mock_adafruit_fxos8700.FXOS8700(i2c, accel_range=0x00)

    def test_accelerometer_smoke(self):
        """
        Smoke test for the fxos accelerometer.
        """
        i2c = mock_busio.I2C(mock_board.SCL, mock_board.SDA)
        fxos = mock_adafruit_fxos8700.FXOS8700(i2c, accel_range=0x00)
        fxos.accelerometer

    def test_magnetometer_smoke(self):
        """
        Smoke test for the fxos accelerometer.
        """
        i2c = mock_busio.I2C(mock_board.SCL, mock_board.SDA)
        fxos = mock_adafruit_fxos8700.FXOS8700(i2c, accel_range=0x00)
        fxos.magnetometer
