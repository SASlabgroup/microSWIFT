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
        mock_serial.loaded
