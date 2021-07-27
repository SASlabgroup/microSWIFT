## recordGPS.py - centralized version

# Package imports
import serial, sys, os
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time as t
import pynmea2
import struct # do we need this twice?
from time import sleep

# Raspberry pi GPIO
# import RPi.GPIO as GPIO

# Import microSWIFT specific information
from utils.config3 import Config
# import process_data

def recordGPS(configFilename):
    print('GPS recording')
    print(configFilename)
    global GPSdataFilename
    GPSdataFilename = 'microSWIFT022_GPS_12Jul2021_202000UTC.dat'


    # load config file and get parameters
    config = Config() # Create object and load file
    ok = config.loadFile( configFilename )
    if( not ok ):
        logger.info ('Error loading config file: "%s"' % configFilename)
        sys.exit(1)
    
    #system parameters
    dataDir = config.getString('System', 'dataDir')
    floatID = os.uname()[1]
    #floatID = config.getString('System', 'floatID') 
    sensor_type = config.getInt('System', 'sensorType')
    badValue = config.getInt('System', 'badValue')
    numCoef = config.getInt('System', 'numCoef')
    port = config.getInt('System', 'port')
    payload_type = config.getInt('System', 'payloadType')
    burst_seconds = config.getInt('System', 'burst_seconds')
    burst_time = config.getInt('System', 'burst_time')
    burst_int = config.getInt('System', 'burst_interval')
    call_int = config.getInt('Iridium', 'call_interval')
    call_time = config.getInt('Iridium', 'call_time')


    #GPS parameters 
    gps_port = config.getString('GPS', 'port')
    baud = config.getInt('GPS', 'baud')
    startBaud = config.getInt('GPS', 'startBaud')
    gps_freq = config.getInt('GPS', 'GPS_frequency') #currently not used, hardcoded at 4 Hz (see init_gps function) 
    #numSamplesConst = config.getInt('System', 'numSamplesConst')
    gps_samples = gps_freq*burst_seconds
    gpsGPIO = config.getInt('GPS', 'gpsGPIO')
    gps_timeout = config.getInt('GPS','timeout')

    # #setup GPIO and initialize
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)
    # #GPIO.setup(modemGPIO,GPIO.OUT)
    # GPIO.setup(gpsGPIO,GPIO.OUT)
    # GPIO.output(gpsGPIO,GPIO.HIGH) #set GPS enable pin high to turn on and start acquiring signal

    return GPSdataFilename
    