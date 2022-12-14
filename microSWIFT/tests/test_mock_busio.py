"""Unit tests for the mock_busio.py"""
import unittest
from mocks import mock_busio
from mocks import mock_board

class Testbusio(unittest.TestCase):
    """
    Test class for the mock busio.
    """
    def test_smoke(self):
        """
        Smoke test for the fxos driver.
        """
        i2c = mock_busio.I2C(mock_board.SCL, mock_board.SDA)
