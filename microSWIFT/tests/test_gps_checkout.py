"""
Unit tests for the gps module
"""

import unittest
from accoutrements import gps_module
from utils import configuration

# from microSWIFT.utils import configuration
config = configuration.Config("./config.txt")

class TestGPS(unittest.TestCase):
    """
    Test class for the GPS.
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
        imu = imu_module.GPS(config)
        assert imu.imu_initialized == True
    
    def test_init2(self):
        """
        Test that imu is initialized
        """
        imu = imu_module.GPS('')
        assert imu.imu_initialized == False