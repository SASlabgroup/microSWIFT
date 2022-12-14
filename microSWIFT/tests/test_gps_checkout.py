"""
This is the test for the gps class methods from gps_module
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
        Smoke test to make sure the function runs
        """
        imu_test = imu_module.IMU(config)

    def test_init(self):
        """
        One shot test to test if the function produces correct 
        output in known case. Should return True.
        """
        imu = imu_module.GPS(config)
        assert imu.imu_initialized == True
    
    def test_init2(self):
        """
        One shot test to test if the function produces correct 
        output in known case. Should return False.
        """
        imu = imu_module.GPS(' ')
        assert imu.imu_initialized == False