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
import RPi.GPIO as GPIO

# Import microSWIFT specific information
from utils.config3 import Config
# import process_data

def recordGPS(configFilename):
    print('GPS recording')
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

    #setup GPIO and initialize
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    #GPIO.setup(modemGPIO,GPIO.OUT)
    GPIO.setup(gpsGPIO,GPIO.OUT)
    GPIO.output(gpsGPIO,GPIO.HIGH) #set GPS enable pin high to turn on and start acquiring signal

    #set up logging
    logDir = config.getString('Loggers', 'logDir')
    LOG_LEVEL = config.getString('Loggers', 'DefaultLogLevel')
    #format log messages (example: 2020-11-23 14:31:00,578, recordGPS - info - this is a log message)
    #NOTE: TIME IS SYSTEM TIME
    LOG_FORMAT = ('%(asctime)s, %(filename)s - [%(levelname)s] - %(message)s')
    #log file name (example: home/pi/microSWIFT/recordGPS_23Nov2020.log)
    LOG_FILE = (logDir + '/' + 'recordGPS' + '_' + datetime.strftime(datetime.now(), '%d%b%Y') + '.log')
    logger = getLogger('system_logger')
    logger.setLevel(LOG_LEVEL)
    logFileHandler = FileHandler(LOG_FILE)
    logFileHandler.setLevel(LOG_LEVEL)
    logFileHandler.setFormatter(Formatter(LOG_FORMAT))
    logger.addHandler(logFileHandler)

    logger.info("---------------recordGPS.py------------------")
    logger.info('python version {}'.format(sys.version))

    logger.info('microSWIFT configuration:')
    logger.info('float ID: {0}, payload type: {1}, sensors type: {2}, '.format(floatID, payload_type, sensor_type))
    logger.info('burst seconds: {0}, burst interval: {1}, burst time: {2}'.format(burst_seconds, burst_int, burst_time))
    logger.info('gps sample rate: {0}, call interval {1}, call time: {2}'.format(gps_freq, call_int, call_time))

    # Return the GPS filename to be read into the onboard processing
    return GPSdataFilename
    