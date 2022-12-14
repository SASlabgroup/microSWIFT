"""Unit tests for the mock board"""
import unittest
from mocks import mock_board

class Testboard(unittest.TestCase):
    """
    Test class for the mock board.
    """
    def test_smoke(self):
        """
        Smoke test for the IMU.
        """
        mock_board.SCL
        mock_board.SDA
