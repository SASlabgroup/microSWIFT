## recordIMU.py 
'''
author: @erainvil

'''

#standard imports 
import busio, board
import time, os, sys, math
from datetime import datetime
import numpy as np
import logging
from logging import *
from time import sleep

# Raspberry pi inputs
import RPi.GPIO as GPIO

# Configuration imports
from utils.config3 import Config

# IMU sensor imports
import IMU.adafruit_fxos8700_microSWIFT
import IMU.adafruit_fxas21002c_microSWIFT


def recordIMU(configFilename):
    ## --------- Define Initialize Functionn --------------
    def init_imu():
        #initialize fxos and fxas devices (required after turning off device)
        logger.info('power on IMU')
        GPIO.output(imu_gpio,GPIO.HIGH)
        i2c = busio.I2C(board.SCL, board.SDA)
        fxos = adafruit_fxos8700_microSWIFT.FXOS8700(i2c, accel_range=0x00)
        fxas = adafruit_fxas21002c_microSWIFT.FXAS21002C(i2c, gyro_range=500)
        
        return fxos, fxas

    ## ---------- Define Record Function -------------------


    ## ------------ Main Body of Function ------------------
    print('IMU recording...')

    # System and logging parameters
    config = Config() # Create object and load file
    ok = config.loadFile( configFilename )
    if( not ok ):
        sys.exit(0)

    #set up logging
    logDir = config.getString('Loggers', 'logDir')
    LOG_LEVEL = config.getString('Loggers', 'DefaultLogLevel')
    #format log messages (example: 2020-11-23 14:31:00,578, recordIMU - info - this is a log message)
    #NOTE: TIME IS SYSTEM TIME
    LOG_FORMAT = ('%(asctime)s, %(filename)s - [%(levelname)s] - %(message)s')
    #log file name (example: home/pi/microSWIFT/recordIMU_23Nov2020.log)
    LOG_FILE = (logDir + '/' + 'recordIMU' + '_' + datetime.strftime(datetime.now(), '%d%b%Y') + '.log')
    logger = getLogger('system_logger')
    logger.setLevel(LOG_LEVEL)
    logFileHandler = FileHandler(LOG_FILE)
    logFileHandler.setLevel(LOG_LEVEL)
    logFileHandler.setFormatter(Formatter(LOG_FORMAT))
    logger.addHandler(logFileHandler)

    #load parameters from Config.dat
    #system parameters 
    floatID = os.uname()[1]
    #floatID = config.getString('System', 'floatID')

    dataDir = config.getString('System', 'dataDir')
    burst_interval=config.getInt('System', 'burst_interval')
    burst_time=config.getInt('System', 'burst_time')
    burst_seconds=config.getInt('System', 'burst_seconds')

    bad = config.getInt('System', 'badValue')

    #IMU parameters
    imuFreq=config.getFloat('IMU', 'imuFreq')
    imu_samples = imuFreq*burst_seconds
    imu_gpio=config.getInt('IMU', 'imu_gpio')

    #initialize IMU GPIO pin as modem on/off control
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(imu_gpio,GPIO.OUT)
    #turn IMU on for script recognizes i2c address
    GPIO.output(imu_gpio,GPIO.HIGH)

    IMUdataFilename = 'IMUfname'
    return IMUdataFilename

