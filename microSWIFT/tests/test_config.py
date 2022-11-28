"""
Test for the Config class for the microSWIFT.
"""
# Import core packages
import unittest

# Import 3rd party packages
import numpy as np

# Import modules
from utils import config

class TestConfig(unittest.TestCase):
    """
    Unit testing class to test the Config class and methods.
    """
    def test_smoke(self):
        """
        Simple smoke test for the Config class to make sure you can
        make an instance of the class. 
        """
        self.assertEqual(1, 0)

    def test_no_config_file(self):
        """
        Edge test to check that the __init__ method will raise a 
        FileNotFoundError if no configuration file is found.
        """       
        self.assertEqual(1, 0)

    def test_duty_cycle_not_found(self):
        """
        Edge test to check that a ValueError is raised if there is no
        input for the duty cycle length.
        """
        self.assertEqual(1, 0)

    def test_duty_cycle_not_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for duty cycle length is not an integer.
        """
        self.assertEqual(1, 0)

    def test_data_record_length_not_found(self):
        """
        Edge test to check that a ValueError is raised if there is no
        input for the data record length.
        """
        self.assertEqual(1, 0)

    def test_data_record_length_not_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for data record length is not a positive integer.
        """
        self.assertEqual(1, 0)

    def test_data_record_length_too_long(self):
        """
        Edge test to check that a ValueError is raised if the user input
        for data record length is longer than the duty cycle. 
        """
        self.assertEqual(1, 0)

    def test_send_window_too_short(self):
        """
        Edge test to check that a warning is raised if the user input
        for data record length and the duty cycle leads to a send window
        less than 5 minutes. 
        """
        self.assertEqual(1, 0)

    def test_gps_sampling_freq_not_found(self):
        """
        Edge test to check that a ValueError is raised if there is no
        input for the gps sampling frequency.
        """
        self.assertEqual(1, 0)

    def test_gps_sampling_freq_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for gps sampling frequency is not an integer.
        """
        self.assertEqual(1, 0)

    def test_gps_sampling_freq_out_of_range(self):
        """
        Edge test to check that a ValueError is raised if the gps
        sampling frequency is out of the range of 1 - 4 Hz that can be
        supported by the hardware.
        """
        self.assertEqual(1, 0)

    def test_imu_sampling_freq_not_found(self):
        """
        Edge test to check that a ValueError is raised if the imu
        sampling frequency is out of the range of 1 - 30 Hz that can be
        supported by the hardware.
        """
        self.assertEqual(1, 0)

    def test_imu_sampling_freq_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for imu sampling frequency is not an integer.
        """
        self.assertEqual(1, 0)

    def test_gps_sampling_freq_out_of_range(self):
        """
        Edge test to check that a ValueError is raised if the gps
        sampling frequency is out of the range of 1 - 4 Hz that can be
        supported by the hardware.
        """
        self.assertEqual(1, 0)
