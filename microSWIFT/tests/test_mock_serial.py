"""Unit tests for the mock serial"""
import unittest
from mocks import mock_serial

class Testserial(unittest.TestCase):
    """
    Test class for the mock serial.
    """
    def test_smoke(self):
        """
        Smoke test for the IMU.
        """
        gps_port = '/dev/ttyS0'
        start_baud = 9600
        timeout = 1
        mock_serial.Serial(gps_port, start_baud, timeout)
