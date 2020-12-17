#! /usr/bin/python3

#standard imports 
import busio, board
import time, os, sys, math
from datetime import datetime
import numpy as np
import logging
from logging import *

#third party imports
import RPi.GPIO as GPIO
import adafruit_fxos8700
import adafruit_fxas21002c

#my imports 
from config3 import Config
from utils import *

#initialize IMU GPIO pin as modem on/off control
GPIO.setmode(GPIO.BCM)
#---------------------------------------------------------------
configDat = sys.argv[1]
configFilename = configDat #Load config file/parameters needed

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


dataFile = str(currentTimeString()) #file name

#load parameters from Config.dat
#system parameters 
floatID = config.getString('System', 'floatID')
dataDir = config.getString('System', 'dataDir')
burst_interval=config.getInt('System', 'burst_interval')
burst_time=config.getInt('System', 'burst_time')
burst_seconds=config.getInt('System', 'burst_seconds')

bad = config.getInt('System', 'badValue')
projectName = config.getString('System', 'projectName')
numSamplesConst = config.getInt('System', 'numSamplesConst')

#iridium parameters
burstInterval = config.getInt('Iridium', 'burstInt')
burstNum = config.getInt('Iridium', 'burstNum')

#IMU parameters
imuFreq=config.getInt('IMU', 'imuFreq')
imuNumSamples = imuFreq*numSamplesConst
maxHours=config.getInt('IMU', 'maxHours')
imuGpio=config.getInt('IMU', 'imuGpio')
recRate = config.getInt('IMU', 'recRate')
recRate = 1./recRate





#turn imu on for script recognizes i2c address
GPIO.setup(imuGpio,GPIO.OUT)
GPIO.output(imuGpio,GPIO.HIGH)

i2c = busio.I2C(board.SCL, board.SDA)
fxos = adafruit_fxos8700.FXOS8700(i2c)
fxas = adafruit_fxas21002c.FXAS21002C(i2c)
sensor = adafruit_fxos8700.FXOS8700(i2c)
sensor2 = adafruit_fxas21002c.FXAS21002C(i2c)

# Optionally create the sensor with a different accelerometer range (the
# default is 2G, but you can use 4G or 8G values):
#sensor = adafruit_fxos8700.FXOS8700(i2c, accel_range=adafruit_fxos8700.ACCEL_RANGE_4G)
#sensor = adafruit_fxos8700.FXOS8700(i2c, accel_range=adafruit_fxos8700.ACCEL_RANGE_8G)
 
# Main loop will read the acceleration and magnetometer values every second
# and print them out.
imu = np.empty(imuNumSamples)
isample = 0


tStart = time.time()
#-------------------------------------------------------------------------------
#LOOP BEGINS
#-------------------------------------------------------------------------------
while True:
    now = datetime.utcnow()
    tNow = time.time()
    elapsedTime = tNow - tStart
    
    if now.minute % burstInterval == 0 and now.second == 0:
        eventLog.info('[%.3f] - Start new burst interval' % elapsedTime)
        
        #create new file for new burst interval 
        dname = now.strftime('%d%b%Y')
        tname = now.strftime('%H:%M:%S')
        fname = (dataDir + floatID +'_Imu_' + dname + '_' + tname +'UTC_burst_' +str(burstInterval) + '.dat')
        eventLog.info('[%.3f] - IMU file name: %s' % (elapsedTime,fname))
        fid=open(fname,'w')
        print('filename = ',fname)
        
        #turn imu on
        GPIO.output(imuGpio,GPIO.HIGH)
        eventLog.info('[%.3f] - IMU ON' % elapsedTime)

        for isample in range(imuNumSamples):
            time.sleep(recRate)
            tHere = time.time()
            elapsed = tHere - tStart
            fnow = datetime.utcnow()
            isample = isample + 1
            eventLog.info('[%.3f] - Num of samples: %d, Wanted samples: %d' % (elapsed,isample,imuNumSamples))

            accel_x, accel_y, accel_z = sensor.accelerometer
            mag_x, mag_y, mag_z = sensor.magnetometer
            gyro_x, gyro_y, gyro_z = sensor2.gyroscope
            roll = 180 * math.atan(accel_x/math.sqrt(accel_y*accel_y + accel_z*accel_z))/math.pi
            pitch = 180 * math.atan(accel_y/math.sqrt(accel_x*accel_x + accel_z*accel_z))/math.pi
            yaw = 180 * math.atan(accel_z/math.sqrt(accel_x*accel_x + accel_z*accel_z))/math.pi
            
            timestring = (str(fnow.year) + ',' + str(fnow.month) + ',' + str(fnow.day) +
                              ',' + str(fnow.hour) + ',' + str(fnow.minute) + ',' + str(fnow.second))
            fdname = fnow.strftime('%d%b%Y')
            ftname = fnow.strftime('%H:%M:%S')
            print('TIME ',fdname,ftname)
            fid.write('%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n' %(elapsed,accel_x,accel_y,accel_z,mag_x,mag_y,mag_z,gyro_x,gyro_y,gyro_z,roll,pitch,yaw))
            fid.flush()
            
        #turn imu off/ stop writing to file      
        fid.close()
        GPIO.output(imuGpio,GPIO.LOW)
        eventLog.info('[%.3f] - IMU OFF' % elapsedTime)
        eventLog.info('[%.3f] - End of burst interval' % elapsedTime)


    
    time.sleep(.50)
