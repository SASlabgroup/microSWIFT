## recordIMU.py 
'''
authors: @EJRainville, @AlexdeKlerk, @Viviana Castillo

Description: This function initializes and records IMU data
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

# IMU sensor imports
import IMU.adafruit_fxos8700_microSWIFT
import IMU.adafruit_fxas21002c_microSWIFT

# Configuration imports
from utils.config3 import Config
configFilename = r'utils/Config.dat'

# System and logging parameters
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    sys.exit(0)

# Set up module level logger
logger = getLogger('microSWIFT.'+__name__)  

#system parameters 
floatID = os.uname()[1]
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


def recordIMU(end_time):
    # IMU is not Initialzied at first
    imu_initialized = False

    # Loop if the imu did not initialize and it is still within a recording block
    while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and imu_initialized==False:
        
        ## --------------- Initialize IMU -----------------
        logger.info('initializing IMU')

        # initialize fxos and fxas devices (required after turning off device)
        logger.info('power on IMU')
        GPIO.output(imu_gpio,GPIO.HIGH)
        i2c = busio.I2C(board.SCL, board.SDA)
        fxos = IMU.adafruit_fxos8700_microSWIFT.FXOS8700(i2c, accel_range=0x00)
        fxas = IMU.adafruit_fxas21002c_microSWIFT.FXAS21002C(i2c, gyro_range=500)

        # Sleep to start recording at same time as GPS
        sleep(5.1)
        
        # return initialized values
        imu_initialized = True

        logger.info('IMU initialized')

        ## --------------- Record IMU ----------------------
        #create new file for to record IMU to 
        logger.info('---------------recordIMU.py------------------')
        IMUdataFilename = dataDir + floatID + '_IMU_'+'{:%d%b%Y_%H%M%SUTC.dat}'.format(datetime.utcnow())
        logger.info('file name: {}'.format(IMUdataFilename))
        logger.info('starting IMU burst at {}'.format(datetime.now()))
            
        # Open the new IMU data file for logging
        with open(IMUdataFilename, 'w',newline='\n') as imu_out:
            logger.info('open file for writing: {}'.format(IMUdataFilename))
            isample=0
            while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time or isample < imu_samples:
                # Get values from IMU
                try:
                    accel_x, accel_y, accel_z = fxos.accelerometer
                    mag_x, mag_y, mag_z = fxos.magnetometer
                    gyro_x, gyro_y, gyro_z = fxas.gyroscope
                except Exception as e:
                    logger.info(e)
                    logger.info('error reading IMU data')

                # Get current timestamp
                timestamp='{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())

                # Write data and timestamp to file
                imu_out.write('%s,%f,%f,%f,%f,%f,%f,%f,%f,%f\n' %(timestamp,accel_x,accel_y,accel_z,mag_x,mag_y,mag_z,gyro_x,gyro_y,gyro_z))
                imu_out.flush()
                
                # Index up number of samples
                isample = isample + 1

                # hard coded sleep to control recording rate. NOT ideal but works for now    
                sleep(0.065)
            
            # End of IMU sampling
            logger.info('end burst')
            logger.info('IMU samples {}'.format(isample)) 
            logger.info('IMU ending burst at: {}'.format(datetime.now()))

            # Turn IMU Off   
            GPIO.output(imu_gpio,GPIO.LOW)
            logger.info('power down IMU')

        # Return IMUdataFilename to main microSWIFT.py
        return IMUdataFilename, imu_initialized