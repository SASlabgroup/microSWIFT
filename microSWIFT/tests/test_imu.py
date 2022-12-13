"""Unit tests for the imu module"""
import unittest
from ..accoutrements import imu_module
from ..utils import configuration

# from microSWIFT.utils import configuration
config = configuration.Config("./microSWIFT/config.txt")

class TestImu(unittest.TestCase):
    """
    Test class for the IMU.
    """
    def test_smoke(self):
        """
        Smoke test for the IMU.
        """
        imu_test = imu_module.IMU(config)
