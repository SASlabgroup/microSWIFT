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
import subprocess

# Raspberry pi inputs
import RPi.GPIO as GPIO

# IMU sensor imports
from adafruit_lsm6ds import AccelRange
from adafruit_lsm6ds import GyroRange
from adafruit_lsm6ds import Rate
from adafruit_lsm6ds import AccelHPF
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL

# Configuration imports
from utils.config3 import Config
configFilename = r'/home/pi/microSWIFT/utils/Config.dat'

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
# RS May24 Start
# imuFreq=config.getFloat('IMU', 'IMU_Rate')
IMU_Rate=config.getString('IMU', 'imuRate')
IMU_accRg = config.getString('IMU', 'imuAccelRange')
IMU_gyrRg = config.getString('IMU', 'imuGyroRange')
IMU_accHPF = config.getString('IMU', 'imuAccelHPF')
# RS May24 End

# imu_samples = imuFreq*burst_seconds
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
        accel_gyro = LSM6DS(i2c)
        # RS May24 Start

        rs=512
        myRate=Rate.RATE_104_HZ
        if IMU_Rate == "RATE_SHUTDOWN":
            myRate=Rate.RATE_SHUTDOWN
            imuRate=0
        if IMU_Rate == "RATE_1_6_HZ":
            myRate=Rate.RATE_1_6_HZ
            imuRate=1.6
        if IMU_Rate == "RATE_12_5_HZ":
            myRate=Rate.RATE_12_5_HZ
            imuRate=12.5
        if IMU_Rate == "RATE_26_HZ":
            myRate=Rate.RATE_26_HZ
            imuRate=26
            rs=256
        if IMU_Rate == "RATE_52_HZ":
            myRate=Rate.RATE_52_HZ
            imuRate=52
            rs=128
        if IMU_Rate == "RATE_104_HZ":
            myRate=Rate.RATE_104_HZ
            imuRate=104
            rs=64
        if IMU_Rate == "RATE_208_HZ":
            myRate=Rate.RATE_208_HZ
            imuRate=208
            rs=32
        if IMU_Rate == "RATE_416_HZ":
            myRate=Rate.RATE_416_HZ
            imuRate=416
            rs=16
        if IMU_Rate == "RATE_833_HZ":
            myRate=Rate.RATE_833_HZ
            imuRate=833
            rs=8
        if IMU_Rate == "RATE_1_66K_HZ":
            myRate=Rate.RATE_1_66K_HZ
            imuRate=1660
            rs=4
        if IMU_Rate == "RATE_3_33K_HZ":
            myRate=Rate.RATE_3_33K_HZ
            imuRate=3330
            rs=2
        if IMU_Rate == "RATE_6_66K_HZ":
            myRate=Rate.RATE_6_66K_HZ
            imuRate=6660
            rs=1        
        # AccelRange
        myAccelRange=AccelRange.RANGE_8G
        #if IMU_accRg == "RANGE_2G":
        #    myAccelRange=AccelRange.RANGE_2G
        #if IMU_accRg == "RANGE_4G":
        #    myAccelRange=AccelRange.RANGE_4G
        #if IMU_accRg == "RANGE_8G":
        #    myAccelRange=AccelRange.RANGE_8G
        #if IMU_accRg == "RANGE_16G":
        #    myAccelRange=AccelRange.RANGE_16G
        
        myGyroRange=GyroRange.RANGE_2000_DPS
        #if IMU_gyrRg == "RANGE_125_DPS":
        #    myGyroRange=GyroRange.RANGE_125_DPS
        #if IMU_gyrRg == "RANGE_500_DPS":
        #    myGyroRange=GyroRange.RANGE_500_DPS
        #if IMU_gyrRg == "RANGE_1000_DPS":
        #    myGyroRange=GyroRange.RANGE_1000_DPS
        #if IMU_gyrRg == "RANGE_2000_DPS":
        #    myGyroRange=GyroRange.RANGE_2000_DPS
        
        #myAccelHPF=AccelHPF.SLOPE
        #if IMU_accHPF == "SLOPE":
        #    myAccelHPF=AccelHPF.SLOPE
        #if IMU_accHPF == "HPF_DIV100":
        #    myAccelHPF=AccelHPF.HPF_DIV100
        #if IMU_accHPF == "HPF_DIV9":
        #    myAccelHPF=AccelHPF.HPF_DIV9
        #if IMU_accHPF == "HPF_DIV400":
        #    myAccelHPF=AccelHPF.HPF_DIV400
        
        accel_gyro.accelerometer_range = myAccelRange
        accel_gyro.gyro_range = myGyroRange
        accel_gyro.accelerometer_data_rate = myRate
        accel_gyro.gyro_data_rate = myRate
        # accel_gyro.high_pass_filter = myAccelHPF
        # RS May24 mag = LIS3MDL(i2c)
        # RS May24 End
        
        # Sleep to start recording at same time as GPS
        sleep(5.1)
        
        # return initialized values
        imu_initialized = True

        #logger.info('IMU initialized : {}' % str(accel_gyro))
        logger.info('IMU initialized : %s' % str(accel_gyro.accelerometer_range))
        logger.info('IMU initialized : %s' % str(accel_gyro.gyro_range))
        logger.info('IMU initialized : %s' % str(accel_gyro.accelerometer_data_rate))
        logger.info('IMU initialized : %s' % str(accel_gyro.gyro_data_rate))
        logger.info('IMU initialized : %s' % str(accel_gyro.high_pass_filter))

        ## --------------- Record IMU ----------------------
        #create new file for to record IMU to 
        logger.info('---------------recordIMU.py------------------')
        IMUdataFilename = dataDir + floatID + '_IMU_'+'{:%d%b%Y_%H%M%SUTC.dat}'.format(datetime.utcnow())
        logger.info('file name: {}'.format(IMUdataFilename))
        logger.info('starting IMU burst at {}'.format(datetime.now()))
        
        # Open the new IMU data file for logging
        logger.info('open file for writing: {}'.format(IMUdataFilename))
        isample=0

        req_samples = imuRate*(60*(end_time -
                                   datetime.utcnow().minute) -
                               datetime.utcnow().second)
        if req_samples < 0:
            req_samples = 0
        
        result = subprocess.run(["/home/microswift/microswift/microSWIFT/cpp/minimu9-ahrs/minimu9-ms2",
                                 "--mode", "raw",
                                 "--sample",  str(int(req_samples)),
                                 "--output_file", str(IMUdataFilename),
                                 "--freq_int", str(myRate)],
                                capture_output = True, text = True)

        logger.info('output from minimu9: %s' % result.stdout.rsplit())
        ri=int(result.stdout.rsplit()[2])

        odr=(6667.+0.0015*float(ri)*6667.)/rs
        logger.info('converts to output data rate ODR of {}:'.format(odr))
        
        GPIO.output(imu_gpio,GPIO.LOW)
        logger.info('power down IMU')
        
        # Return IMUdataFilename to main microSWIFT.py
        return IMUdataFilename, imu_initialized
