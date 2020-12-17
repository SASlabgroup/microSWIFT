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
imu_samples = imuFreq*burst_seconds
maxHours=config.getInt('IMU', 'maxHours')
imu_gpio=config.getInt('IMU', 'imu_gpio')
recRate = config.getInt('IMU', 'recRate')
recRate = 1./recRate


#initialize IMU GPIO pin as modem on/off control
GPIO.setmode(GPIO.BCM)
GPIO.setup(imu_gpio,GPIO.OUT)
#turn IMU on for script recognizes i2c address
GPIO.output(imu_gpio,GPIO.HIGH)

i2c = busio.I2C(board.SCL, board.SDA)
fxos = adafruit_fxos8700.FXOS8700(i2c)
fxas = adafruit_fxas21002c.FXAS21002C(i2c)

# Optionally create the sensor with a different accelerometer range (the
# default is 2G, but you can use 4G or 8G values):
#sensor = adafruit_fxos8700.FXOS8700(i2c, accel_range=adafruit_fxos8700.ACCEL_RANGE_4G)
#sensor = adafruit_fxos8700.FXOS8700(i2c, accel_range=adafruit_fxos8700.ACCEL_RANGE_8G)
 
# Main loop will read the acceleration and magnetometer values every second
# and print them out.
imu = np.empty(imu_samples)
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
        
        
        logger.info('[%.3f] - Start new burst interval' % elapsedTime)
        
        #create new file for new burst interval 
        fname = dataDir + 'microSWIFT'+ floatID + '_IMU_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
        print('filename = ',fname)
        logger.info("file name: %s" %fname)
        logger.info('[%.3f] - IMU file name: %s' % (elapsedTime,fname))
        fid=open(fname,'w')
        
        #turn imu on
        GPIO.output(imu_gpio,GPIO.HIGH)
        logger.info('[%.3f] - IMU ON' % elapsedTime)
        
        
        with open(fname, 'w',newline='\n') as imu_out:
        
            t_end = time.time() + burst_seconds #get end time for burst
            isample=0
            while time.time() <= t_end or ipos < imu_samples:
        
                accel_x, accel_y, accel_z = fxos.accelerometer
                mag_x, mag_y, mag_z = fxos.magnetometer
                gyro_x, gyro_y, gyro_z = fxas.gyroscope
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
        
        
        
                if time.time() >= t_end and 0 < imu_samples-isample <= 10:
                        
                        continue
                    elif ipos == imu_samples and ivel == imu_samples:
                        break
        
        
                isample = isample + 1

                for isample in range(imu_samples):
                time.sleep(recRate)
                tHere = time.time()
                elapsed = tHere - tStart
                fnow = datetime.utcnow()
                
                logger.info('[%.3f] - Num of samples: %d, Wanted samples: %d' % (elapsed,isample,imu_samples))
    
                
                
            #turn imu off/ stop writing to file      
            GPIO.output(imu_gpio,GPIO.LOW)
            logger.info('[%.3f] - IMU OFF' % elapsedTime)
            logger.info('[%.3f] - End of burst interval' % elapsedTime)


    
    time.sleep(.50)
