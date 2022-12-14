"""Unit tests for the mock_adafruit_fxas21002c.py"""
import unittest
from mocks import mock_adafruit_fxas21002c
from mocks import mock_busio
from mocks import mock_board

class Testfxas(unittest.TestCase):
    """
    Test class for the mock fxas21002c driver.
    """
    def test_smoke(self):
        """
        Smoke test for the fxas driver.
        """
        i2c = mock_busio.I2C(mock_board.SCL, mock_board.SDA)
        fxas = mock_adafruit_fxas21002c.FXAS21002C(i2c, gyro_range=500)

    def test_gyro_smoke(self):
        """
        Smoke test for the fxas gyro.
        """
        i2c = mock_busio.I2C(mock_board.SCL, mock_board.SDA)
        fxas = mock_adafruit_fxas21002c.FXAS21002C(i2c, gyro_range=500)
        fxas.gyroscope
