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
        imu_gps = gps_module.GPS(config)

    def test_init(self):
        """
        One shot test to test if the function produces correct 
        output in known case. Should return True.
        """
        gps = gps_module.GPS(config)
        assert gps.gps_initialized == True
    
    def test_init2(self):
        """
        One shot test to test if the function produces correct 
        output in known case. Should return False.
        """
        with self.assertRaises(ValueError):
            gps_module.GPS(' ')
