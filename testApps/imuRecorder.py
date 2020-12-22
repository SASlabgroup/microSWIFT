#! /usr/bin/python

########################################################################################
#
#Purpose: This app reads imu data and records it at an interval specified by the caller.
#The resulting file containing the entire data set is named by the date/time that the
#data was recorded.  
#
#Output: Records IMU data 
#
#Elapsed time (sec) 
#Roll (deg)
#Pitch (deg)
#Yaw (deg)
#
#Arguments: 
#[0] = App name 
#[1] = Directory where file is writen to 
#[2] = Total length of time to run (sec)
#[3] = Recording rate (Hz)

##########################################################################################

# standard imports 
import sys
import getopt
import RTIMU
import os.path
import time
import math

# my imports
utilsDir= "/home/pi/dev/utilities"
sys.path.insert(0, utilsDir)
from utils import currentTimeString
#==============================================================================
# specify what directory to save the written file in 
directory = sys.argv[1]
# gets the total requested run time from the caller 
totalRunTime=float(sys.argv[2])
# the rate of the interval-how many records to write per second 
# specified by the caller 
# get the requested rate in Hz (records/sec)
recordingRate=float(sys.argv[3])

# convert to time-between-recordings (sec)
recordingInterval=1./recordingRate
print("Interval: %.3f" % recordingInterval)

# call utilities to set date as file name 
SETTINGS_FILE = "RTIMULib"
print(("Using settings file " + SETTINGS_FILE + ".ini"))
# if the file does not exits, create it 
if not os.path.exists(SETTINGS_FILE + ".ini"):
    print("Settings file does not exist, will be created")

# read the file, store the data in s object 
s = RTIMU.Settings(SETTINGS_FILE)
# read the s object, store data in imu object 
imu = RTIMU.RTIMU(s)

# ???????
print(("IMU Name: " + imu.IMUName()))

# what is IMUInit?
if (not imu.IMUInit()):
    print("IMU Init Failed") 
    sys.exit(1)
else:
    print("IMU Init Succeeded")

# set fusion parameters
imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

# get the interval time (8ms)
poll_interval = imu.IMUGetPollInterval()

# turn int into float for sleep to read 
float_poll_interval = float(poll_interval)
# divide float to 1000 to turn ms to s, .008s
float_sec_poll_interval = (float_poll_interval/1000.0)

# print poll interval to 3 decimal places 
print(("SetPoll Interval: %.3dms\n" % float_sec_poll_interval))
 
# get the start time of the app to 3 decimal places  
tLastRecord=time.time() 
print(("Start Time: %.3f") % tLastRecord)

# grab start time of app in order to get the elapsed time, 
tStart = time.time()

# get the start time to use in replacement of sleep 
tLastRead = time.time()

# get the file name from currentTimeString functino
dataFile = str(currentTimeString())

# joing the directory path to save with file name 
path = os.path.join(directory, dataFile)

# open the file to write 
f = open(path + '.txt', 'w')

#================================================================================
# loop begins
#================================================================================
# loop through IMU data until specified time has elapsed 
while True: 
    # get the current time at this iteration 
    tNow = time.time()
    # get the elapsed time since the beginning of the app
    elapsedTime = tNow-tStart
    print("Elapsed time: %.3f" % elapsedTime)
    
    # the last read measurment 
    tSinceLastRead = tNow - tLastRead
    # pause time by .008s by comparing the current to the last read time
    if (tSinceLastRead) >=  float_sec_poll_interval:
        # get the IMU data
  	Imu = imu.IMURead()
	#x, y, z = imu.getFusionData()
  	#print("%f %f %f" % (x,y,z))
  	data = imu.getIMUData()
  	#print"-data is:";print type(data)
  	fusionPose = data["fusionPose"]
    #-------------------------------------------------------------------------------------------------
    # check for the time to record imu 
    #-------------------------------------------------------------------------------------------------
    # get the elapsed time by comparing the time right now and the time from the last recorded measurment  
    tSinceLastIMURecorded = tNow - tLastRecord
    print(("Time since last IMU recorded:%.3f") % (tSinceLastIMURecorded))
    # check that the command line duration has expired by comparing the time now to the start time
    if (tSinceLastIMURecorded) >= recordingInterval:
    # TIME TO RECORD 
        # convert IMU measurements from rad to deg 
        rollDeg = math.degrees(fusionPose[0])
        pitchDeg = math.degrees(fusionPose[1])
        yawDeg = math.degrees(fusionPose[2])
        # print the IMU measurements in degrees to 1 decimal place 
        print(("r: %.1f p: %.1f y: %.1f" % (rollDeg, pitchDeg, yawDeg)))
	
	# write timetaged IMU data to file 
	f.write("%.3f %f %.1f %.1f %.1f \n" % (elapsedTime, tNow, rollDeg, pitchDeg, yawDeg))
        #save the time of this recording 
        tLastRecord = tNow
    #-------------------------------------------------------------------------------------------------  
    # check that the requested total run time has expired
    #------------------------------------------------------------------------------------------------
    if (elapsedTime) >= totalRunTime:
        break 
#=============================================================================
# loop ends
#=============================================================================
print("Done!")
