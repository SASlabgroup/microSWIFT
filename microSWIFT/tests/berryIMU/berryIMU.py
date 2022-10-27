#!/usr/bin/python
#
#	This program  reads the angles from the acceleromter, gyrscope
#	and mangnetometeron a BerryIMU connected to a Raspberry Pi.
#
#	Both the BerryIMUv1 and BerryIMUv2 are supported
#
#	BerryIMUv1 uses LSM9DS0 IMU
#	BerryIMUv2 uses LSM9DS1 IMU
#
#	This program includes a number of calculations to improve the 
#	values returned from BerryIMU. If this is new to you, it 
#	may be worthwhile first to look at berryIMU-simple.py, which 
#	has a much more simplified version of code which would be easier
#	to read.   
#
#	http://ozzmaker.com/

import time
import math
import IMU
import datetime
import os, sys

from config2 import Config
##########################################################################
#Load config file 
configDat =  sys.argv[1]
configFilename = configDat #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	sys.exit(0)
	
# If the IMU is upside down (Skull logo facing up), change this value to 1
IMU_UPSIDE_DOWN=config.getInt('IMU', 'upsidedown')


G_GAIN=config.getFloat('IMU', 'gGain') # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA=config.getFloat('IMU', 'AA') # Complementary filter constant

RAD_TO_DEG = 57.29578 # degrees()
M_PI = 3.14159265358979323846 #math.pi

recRate=config.getInt('IMU', 'recRate') 
runTime=config.getInt('IMU', 'runTime')  
recordingInterval=1./recRate
print ("Interval: %.3f" % recordingInterval)

now = datetime.datetime.now()
dname = now.strftime('%d%b%Y_')
tname = now.strftime('%H:%M:%S')

#LOG
dataDir=config.getString('LogLocation', 'dataDir')
floatID=config.getString('System', 'floatID')
projectName=config.getString('System', 'projectName')
projectName=config.getInt('IMU', 'runTime')
projectName=config.getInt('IMU', 'recRate')


imuData = (open((dataDir + floatID + '_Imu_' + dname + tname + '.txt'), 'w+')) 

################# Compass Calibration values ############
# Use calibrateBerryIMU.py to get calibration values 
# Calibrating the compass isnt mandatory, however a calibrated 
# compass will result in a more accurate heading value.

magXmin = -494 #-436 #32767
magYmin = -721 #32767
magZmin = -1526 #32767
magXmax = 2420 #-32767
magYmax = 2025 #-32767
magZmax = 1456 #-32767



'''
Here is an example:
magXmin =  -1748
magYmin =  -1025
magZmin =  -1876
magXmax =  959
magYmax =  1651
magZmax =  708
Dont use the above values, these are just an example.
'''



#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0


def kalmanFilterY ( accAngle, gyroRate, DT):
	y=0.0
	S=0.0

	global KFangleY
	global Q_angle
	global Q_gyro
	global y_bias
	global YP_00
	global YP_01
	global YP_10
	global YP_11

	KFangleY = KFangleY + DT * (gyroRate - y_bias)

	YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
	YP_01 = YP_01 + ( - DT * YP_11 )
	YP_10 = YP_10 + ( - DT * YP_11 )
	YP_11 = YP_11 + ( + Q_gyro * DT )

	y = accAngle - KFangleY
	S = YP_00 + R_angle
	K_0 = YP_00 / S
	K_1 = YP_10 / S
	
	KFangleY = KFangleY + ( K_0 * y )
	y_bias = y_bias + ( K_1 * y )
	
	YP_00 = YP_00 - ( K_0 * YP_00 )
	YP_01 = YP_01 - ( K_0 * YP_01 )
	YP_10 = YP_10 - ( K_1 * YP_00 )
	YP_11 = YP_11 - ( K_1 * YP_01 )
	
	return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
	x=0.0
	S=0.0

	global KFangleX
	global Q_angle
	global Q_gyro
	global x_bias
	global XP_00
	global XP_01
	global XP_10
	global XP_11


	KFangleX = KFangleX + DT * (gyroRate - x_bias)

	XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
	XP_01 = XP_01 + ( - DT * XP_11 )
	XP_10 = XP_10 + ( - DT * XP_11 )
	XP_11 = XP_11 + ( + Q_gyro * DT )

	x = accAngle - KFangleX
	S = XP_00 + R_angle
	K_0 = XP_00 / S
	K_1 = XP_10 / S
	
	KFangleX = KFangleX + ( K_0 * x )
	x_bias = x_bias + ( K_1 * x )
	
	XP_00 = XP_00 - ( K_0 * XP_00 )
	XP_01 = XP_01 - ( K_0 * XP_01 )
	XP_10 = XP_10 - ( K_1 * XP_00 )
	XP_11 = XP_11 - ( K_1 * XP_01 )
	
	return KFangleX


IMU.detectIMU()     #Detect if BerryIMUv1 or BerryIMUv2 is connected.
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
kalmanX = 0.0
kalmanY = 0.0

a = datetime.datetime.now()
tStart = time.time()
tLastRecord = 0
while True:
    tNow = time.time()
    elapsedTime = tNow - tStart
    print (elapsedTime)
    
    time.sleep(.25)
    #Read the accelerometer,gyroscope and magnetometer values
    ACCx = IMU.readACCx()
    ACCy = IMU.readACCy()
    ACCz = IMU.readACCz()
    GYRx = IMU.readGYRx()
    GYRy = IMU.readGYRy()
    GYRz = IMU.readGYRz()
    MAGx = IMU.readMAGx()
    MAGy = IMU.readMAGy()
    MAGz = IMU.readMAGz()
    

    #Apply compass calibration    
    MAGx -= (magXmin + magXmax) /2 
    MAGy -= (magYmin + magYmax) /2 
    MAGz -= (magZmin + magZmax) /2 
 
    
    ##Calculate loop Period(LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0)
    print ("Loop Time %5.2f " % ( LP ))


    #Convert Gyro raw to degrees per second
    rate_gyr_x =  GYRx * G_GAIN
    rate_gyr_y =  GYRy * G_GAIN
    rate_gyr_z =  GYRz * G_GAIN


    #Calculate the angles from the gyro. 
    gyroXangle+=rate_gyr_x*LP
    gyroYangle+=rate_gyr_y*LP
    gyroZangle+=rate_gyr_z*LP

    #Convert Accelerometer values to degrees

    if not IMU_UPSIDE_DOWN:
        # If the IMU is up the correct way (Skull logo facing down), use these calculations
        AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
        AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG
    else:
        #Us these four lines when the IMU is upside down. Skull logo is facing up
        AccXangle =  (math.atan2(-ACCy,-ACCz)*RAD_TO_DEG)
        AccYangle =  (math.atan2(-ACCz,-ACCx)+M_PI)*RAD_TO_DEG



    #Change the rotation value of the accelerometer to -/+ 180 and
    #move the Y axis '0' point to up.  This makes it easier to read.
    if AccYangle > 90:
        AccYangle -= 270.0
    else:
        AccYangle += 90.0



    #Complementary filter used to combine the accelerometer and gyro values.
    CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
    CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

    #Kalman filter used to combine the accelerometer and gyro values.
    kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
    kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)

    if IMU_UPSIDE_DOWN:
        MAGy = -MAGy      #If IMU is upside down, this is needed to get correct heading.
    #Calculate heading
    heading = 180 * math.atan2(MAGy,MAGx)/M_PI

    #Only have our heading between 0 and 360
    if heading < 0:
        heading += 360



    ####################################################################
    ###################Tilt compensated heading#########################
    ####################################################################
    #Normalize accelerometer raw values.
    if not IMU_UPSIDE_DOWN:        
        #Use these two lines when the IMU is up the right way. Skull logo is facing down
        accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
    else:
        #Us these four lines when the IMU is upside down. Skull logo is facing up
        accXnorm = -ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)

    #Calculate pitch and roll

    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm/math.cos(pitch))


    #Calculate the new tilt compensated values
    magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
 
    #The compass and accelerometer are orientated differently on the LSM9DS0 and LSM9DS1 and the Z axis on the compass
    #is also reversed. This needs to be taken into consideration when performing the calculations
    if(IMU.LSM9DS0):
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)   #LSM9DS0
    else:
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)+MAGz*math.sin(roll)*math.cos(pitch)   #LSM9DS1




	#Calculate tilt compensated heading
    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI

    if tiltCompensatedHeading < 0:
                tiltCompensatedHeading += 360

    ############################ END ##################################
    #tSinceLastRecord = tNow - tLastRecord
    #print (recordingInterval)
    time.sleep(recordingInterval)
    #tSinceLastRecorded = tNow - tLastRecord
        
    #if (tSinceLastRecorded >= recordingInterval):

    if 1:			#Change to '0' to stop showing the angles from the accelerometer
        print ("\t# ACCX Angle %5.2f ACCY Angle %5.2f #  \n" % (AccXangle, AccYangle)),

    if 1:			#Change to '0' to stop  showing the angles from the gyro
        print ("\t# GRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # \n" % (gyroXangle,gyroYangle,gyroZangle)),

    if 1:			#Change to '0' to stop  showing the angles from the complementary filter
        print ("\t# CFangleX Angle %5.2f   CFangleY Angle %5.2f # \n" % (CFangleX,CFangleY)),
        
    if 1:			#Change to '0' to stop  showing the heading
        print ("\t# HEADING %5.2f  tiltCompensatedHeading %5.2f # \n" % (heading,tiltCompensatedHeading)),
        
    if 1:			#Change to '0' to stop  showing the angles from the Kalman filter
        print ("\t# kalmanX %5.2f   kalmanY %5.2f # \n" % (kalmanX,kalmanY)),
    if 1:
        print ("\t# Pitch %.2f   Roll %.2f # \n" % (pitch,roll)),
    imuData.write("%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % (elapsedTime,
                                                                 AccXangle, AccYangle,
                                                                 gyroXangle,gyroYangle,gyroZangle,
                                                                 CFangleX,CFangleY,
                                                                 heading,tiltCompensatedHeading,
                                                                 kalmanX,kalmanY,
                                                                 pitch,roll))
    imuData.flush()
    #print a new line
    print ("")  
    if elapsedTime > runTime: 
        break




