"""
Test for the Config class for the microSWIFT.
"""

import unittest
import os

from microSWIFT.utils import configuration

class TestConfig(unittest.TestCase):
    """
    Unit testing class to test the Config class and methods.
    """
    def test_smoke(self):
        """
        Simple smoke test for the Config class to make sure you can
        make an instance of the class.
        """
        print(os.getcwd())
        configuration.Config('./microSWIFT/config.txt')

    def test_no_config_file(self):
        """
        Edge test to check that the __init__ method will raise a
        FileNotFoundError if no configuration file is found.
        """
        with self.assertRaises(FileNotFoundError):
            configuration.Config('')

    def test_duty_cycle_not_found(self):
        """
        Edge test to check that a ValueError is raised if there is no
        input for the duty cycle length.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_no_duty_cycle.txt')

    def test_duty_cycle_not_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for duty cycle length is not an integer.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_duty_cycle_not_int.txt')

    def test_record_window_length_not_found(self):
        """
        Edge test to check that a ValueError is raised if there is no
        input for the data record length.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_no_record_window.txt')

    def test_record_window_length_not_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for data record length is not a positive integer.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_record_window_not_int.txt')

    def test_record_window_length_too_long(self):
        """
        Edge test to check that a ValueError is raised if the user input
        for data record length is longer than the duty cycle.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_record_window_too_long.txt')

    def test_send_window_too_short(self):
        """
        Edge test to check that a warning is raised if the user input
        for data record length and the duty cycle leads to a send window
        less than 5 minutes.
        """
        with self.assertWarns(Warning):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_send_window_too_short.txt')

    def test_gps_sampling_freq_not_found(self):
        """
        Edge test to check that a ValueError is raised if there is no
        input for the gps sampling frequency.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_no_gps_freq.txt')

    def test_gps_sampling_freq_not_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for gps sampling frequency is not an integer.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_gps_freq_not_int.txt')

    def test_gps_sampling_freq_out_of_range(self):
        """
        Edge test to check that a ValueError is raised if the gps
        sampling frequency is out of the range of 1 - 4 Hz that can be
        supported by the hardware.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_gps_freq_out_of_range.txt')

    def test_imu_sampling_freq_not_found(self):
        """
        Edge test to check that a ValueError is raised if the imu
        sampling frequency is out of the range of 1 - 30 Hz that can be
        supported by the hardware.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_no_imu_freq.txt')

    def test_imu_sampling_freq_not_integer(self):
        """
        Edge test to check that a TypeError is raised if the user input
        for imu sampling frequency is not an integer.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_imu_freq_not_int.txt')

    def test_imu_sampling_freq_out_of_range(self):
        """
        Edge test to check that a ValueError is raised if the gps
        sampling frequency is out of the range of 1 - 4 Hz that can be
        supported by the hardware.
        """
        with self.assertRaises(ValueError):
            configuration.Config('./microSWIFT/tests/test_data/'
                                 'config_files/'
                                 'config_imu_freq_not_int.txt')
