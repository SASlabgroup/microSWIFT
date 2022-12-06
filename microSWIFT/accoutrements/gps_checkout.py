"""
Functions to test gps.py on the RPi board.
"""
import unittest
import gps
# import mock

class TestGPS(unittest.TestCase):
    """
    This class manages to test the GPS functions.
    """
    def test_smoke(self):
        """
        Smoke test to make sure the GPS initializes
        """
        gps.init(Config('./microSWIFT/config.txt'))
    
    def test_smoke_record(self):
        """
        Smoke test to make sure the gps record function works produces output
        """
        gps.record(Config('./microSWIFT/config.txt'))
       
   
    def test_init_expcetion(self):
        """
        One shot test to test if the function produces an expcetion in known
        bad data. The function should produce a log statement and a initialization result.
        """


    def test_record(self):
        """
        One shot test to test if the function produces correct output
        in known case. 
        """


    def test_edgecase1(self):
        """
        Edge case test to test if the function throws ValueError
        """


    def test_edgecase2(self):
        """
        Edge case test to test if the function throws ValueError
        """


