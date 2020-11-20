#! /usr/bin/python3

#imports
import serial, io, sys, os
import numpy as np
from struct import *
import logging
from datetime import datetime
import time
import RPi.GPIO as GPIO
import pynmea2
import glob
import struct
from time import sleep

#my imports
import send_sbd_binary_data
from rec_send_funcs import *
import GPSwavesC
from config3 import Config


#load config file and get parameters
configFilename = sys.argv[1] #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	print ('Error loading config file: "%s"' % configFilename)
	#LOG ERROR
	sys.exit(0)

#system parameters
floatID = config.getString('System', 'floatID') 
projectName = config.getString('System', 'projectName')
payLoadType = config.getInt('System', 'payLoadType')
badValue = config.getInt('System', 'badValue')
numCoef = config.getInt('System', 'numCoef')
Port = config.getInt('System', 'port')
payloadVersion = config.getInt('System', 'payloadVersion')
#Log parameters
dataDir = config.getString('LogLocation', 'dataDir')
logDir = config.getString('LogLocation', 'logDir')

#GPS parameters 
gpsPort = config.getString('GPS', 'port')
baud = config.getInt('GPS', 'baud')
startBaud = config.getInt('GPS', 'startBaud')
GPSfrequency = config.getInt('GPS', 'GPSfrequency')
numSamplesConst = config.getInt('System', 'numSamplesConst')
gpsNumSamples = GPSfrequency*numSamplesConst
numLines = config.getInt('GPS', 'numLines')
gpsGpio = config.getInt('GPS', 'gpsGpio')
getFix = config.getInt('GPS', 'getFix') # min before rec gps

#temp and volt params 
maxHoursTemp = config.getInt('Temp', 'maxHours')
maxHoursVolt = config.getInt('Voltage', 'maxHours')

#Iridium parameters
modemPort = config.getString('Iridium', 'port')
modemBaud = config.getInt('Iridium', 'baud')
modemGpio = config.getInt('Iridium', 'iridiumGpio')
formatType = config.getInt('Iridium', 'formatType')
callInt = config.getInt('Iridium', 'callInt')
burst_num = config.getInt('Iridium', 'burstNum')


#hard coded parameters to change 
IfHourlyCall = config.getString('Iridium', 'IfHourlyCall')
IfHourlyCall = eval(IfHourlyCall) #boolean
MakeCall = config.getString('Iridium', 'MakeCall') 
MakeCall = eval(MakeCall) #boolean


#set up logging








#setup GPIO and initialize
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(modemGpio,GPIO.OUT)
GPIO.setup(gpsGpio,GPIO.OUT)

#attempt to set time based on GPS -> turn on and wait 30 sec

#turn off GPS and modem via GPIO pins


#try to open serial port, check for lines of data, make sure is set to 4hz rate and 115200 baud
try:
	#open serial port with expected baud rate 115200
	ser = serial.Serial(gpsPort,baud,timeout=1)
	print("GPS serial port open at %s baud" % (baud, gpsPort))
	#set interval to 250ms (4 Hz)
	ser.write('$PMTK220,250*29\r\n'.encode())
	print("setting GPS to 4 Hz rate")
except:
	print("unable to open GPS serial port, trying default baud rate 9600")
	try:
		#try default baud rate 9600
		ser = serial.Serial(gpsPort,9600,timeout=1)
		#set baud rate to 115200 and interval to 250ms (4 Hz)
		print("setting baud rate to 115200")
		ser.write('$PMTK251,115200*1F\r\n'.encode())
		print("setting GPS to 4 Hz rate")
		ser.write('$PMTK220,250*29\r\n'.encode())
	except:
		print("unable to open GPS serial port on 9600")
else:
	print("unable to open GPS serial port at %s and 9600 on port %s" % (baud, gpsPort))
	sys.exit(0)





#def record_serial

	#initialize empty numpy array and fill with bad values
	u = np.empty(gpsNumSamples)
    u.fill(badValue)
    v = np.empty(gpsNumSamples)
    v.fill(badValue)
    z = np.empty(gpsNumSamples)
    z.fill(badValue)
    lat = np.empty(gpsNumSamples)
    lat.fill(badValue)
    lon = np.empty(gpsNumSamples)
    lon.fill(badValue)
    
	#open serial port
	try:
        
        with serial.Serial('/dev/ttyS0',115200,timeout=.25) as pt, open(fname, 'a') as gpsOut: 
            ser = io.TextIOWrapper(io.BufferedRWPair(pt,pt,1), encoding='ascii',
                    errors='ignore', newline='\r', line_buffering=True)
            
            eventLog.info('[%.3f] - Open GPS port and file name: %s, %s' %  (elapsed, gpsPort,fname))

            #test for incoming data over serial port
            for i in range(1):
                newline = ser.readline()
                print('[%.3f] - New GPS output: %s' % (elapsedTime,newline))
                eventLog.info('[%.3f] - New GPS output' % elapsedTime)
                #sleep(1)   

            gpgga_stc = ''
            gpvtg_stc = ''
            ipos = 0
            ivel = 0


	#read some lines of data and log it
	
	#initialize some variables

	#If lines are not empty, enter loop
		#while counter is less than expected samples
			#read new line, write to file, flush
			#determine if line is GPGGA or GPVTG sentence
				#pass line to parse_nmea funtions in 'record_send_funcs.py'
				#get z,lat,lon from GPGGA or u,v from GPVTG
				
				#check if we have enough samples, and check if setTimeAtEnd flag is false
					#attempt to get and set time from GPRMC sentence

	#increment counter *should be incremented in while loop*

	#else print 'no serial data'

	#return u,v,z,lat,lon arrays

#def main
	
	#start time and elapsed time

	#initialize empty numpy arrays for u,v,z,lat,lon,temp,volt but do not fill with bad values

	#initialize numpy arrays for a1,b1,a2,b2,energy,freq

	#get burst interval

	#TimeBetweenBurst_call = busrtInt-callInt (??)

	#check if callInt is larger than burstInt and if so log an error message (??)

	#turn some switched off

	#while true
		#get time and set elapsed time

		

















	


		
