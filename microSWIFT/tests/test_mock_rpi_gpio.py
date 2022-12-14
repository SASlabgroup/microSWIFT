"""Unit tests for the mock rpi_gpio.py"""
import unittest
from mocks import mock_rpi_gpio as GPIO

class Testgpio(unittest.TestCase):
    """
    Test class for the mock gpio module.
    """
    def test_setmode_smoke(self):
        """
        Smoke test for setmode.
        """
        GPIO.setmode(GPIO.BCM)

    def test_setup_smoke(self):
        """
        Smoke test for setup.
        """
        GPIO.setup(20,GPIO.OUT)

    def test_output_smoke(self):
        """
        Smoke test for output.
        """
        GPIO.setup(20,GPIO.OUT)
        GPIO.output(20,GPIO.HIGH)

    def test_setwarnings_smoke(self):
        """
        Smoke test for setwarnings.
        """
        GPIO.setwarnings(True)
