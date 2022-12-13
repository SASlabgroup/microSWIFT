"""Unit tests for the imu module"""
import unittest
from accoutrements import imu_module
from utils import configuration

# from microSWIFT.utils import configuration
config = configuration.Config("./config.txt")

class TestImu(unittest.TestCase):
    """
    Test class for the IMU.
    """
    def test_smoke(self):
        """
        Smoke test for the IMU.
        """
        imu_test = imu_module.IMU(config)

    def test_init(self):
        """
        Test that imu is initialized
        """
        imu = imu_module.IMU(config)
        assert imu.imu_initialized == True
