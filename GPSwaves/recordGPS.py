#! /usr/bin/python3

#imports
import serial, sys, os
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time as t
import RPi.GPIO as GPIO
import pynmea2
import struct
from time import sleep

#my imports
from config3 import Config
import process_data


#load config file and get parameters
configFilename = sys.argv[1] #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	logger.info ('Error loading config file: "%s"' % configFilename)
	sys.exit(1)
	
#system parameters
dataDir = config.getString('System', 'dataDir')
floatID = config.getString('System', 'floatID') 
projectName = config.getString('System', 'projectName')
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
numLines = config.getInt('GPS', 'numLines')
gpsGPIO = config.getInt('GPS', 'gpsGPIO')
getFix = config.getInt('GPS', 'getFix') # min before rec gps
gps_timeout = config.getInt('GPS','timeout')

#setup GPIO and initialize
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#GPIO.setup(modemGPIO,GPIO.OUT)
GPIO.setup(gpsGPIO,GPIO.OUT)
GPIO.output(gpsGPIO,GPIO.HIGH) #set GPS enable pin high to turn on and start acquiring signal

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
def init_gps():
	nmea_time=''
	nmea_date=''
	#set GPS enable pin high to turn on and start acquiring signal
	GPIO.output(gpsGPIO,GPIO.HIGH)
	
	logger.info('initializing GPS')
	try:
		#start with GPS default baud whether it is right or not
		logger.info("try GPS serial port at 9600")
		ser=serial.Serial(gps_port,startBaud,timeout=1)
		try:
			#set device baud rate to 115200
			logger.info("setting baud rate to 115200 $PMTK251,115200*1F\r\n")
			ser.write('$PMTK251,115200*1F\r\n'.encode())
			sleep(1)
			#switch ser port to 115200
			ser.baudrate=baud
			logger.info("switching to %s on port %s" % (baud, gps_port))
			#set output sentence to GPGGA and GPVTG, plus GPRMC once every 4 positions (See GlobalTop PMTK command packet PDF)
			logger.info('setting NMEA output sentence $PMTK314,0,4,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n')
			ser.write('$PMTK314,0,4,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n'.encode())
			sleep(1)
			#set interval to 250ms (4 Hz)
			logger.info("setting GPS to 4 Hz rate $PMTK220,250*29\r\n")
			ser.write("$PMTK220,250*29\r\n".encode())
			sleep(1)
		except Exception as e:
			return ser, False, nmea_time, nmea_date
			logger.info("error setting up serial port")
			logger.info(e)
	except Exception as e:
		return ser, False, nmea_time, nmea_date
		logger.info("error opening serial port")
		logger.info(e)
					
	#read lines from GPS serial port and wait for fix
	try:
		#loop until timeout dictated by gps_timeout value (seconds)
		timeout=t.time() + gps_timeout
		while t.time() < timeout:
			ser.flushInput()
			ser.read_until('\n'.encode())
			newline=ser.readline().decode('utf-8')
			logger.info(newline)
			if not 'GPGGA' in newline:
				newline=ser.readline().decode('utf-8')
				if 'GPGGA' in newline:
					logger.info('found GPGGA sentence')
					logger.info(newline)
					gpgga=pynmea2.parse(newline,check=True)
					logger.info('GPS quality= %d' % gpgga.gps_qual)
					#check gps_qual value from GPGGS sentence. 0=invalid,1=GPS fix,2=DGPS fix
					if gpgga.gps_qual > 0:
						logger.info('GPS fix acquired')
						#get date and time from GPRMC sentence - GPRMC reported only once every 8 lines
						for i in range(8):
							newline=ser.readline().decode('utf-8')
							if 'GPRMC' in newline:
								logger.info('found GPRMC sentence')
								try:
									gprmc=pynmea2.parse(newline)
									nmea_time=gprmc.timestamp
									nmea_date=gprmc.datestamp
									logger.info("nmea time: %s" %nmea_time)
									logger.info("nmea date: %s" %nmea_date)
									
									#set system time
									try:
										logger.info("setting system time from GPS: %s %s" %(nmea_date, nmea_time))
										os.system('sudo timedatectl set-timezone UTC')
										os.system('sudo date -s "%s %s"' %(nmea_date, nmea_time))
										os.system('sudo hwclock -w')
										
										logger.info("GPS initialized")
										return ser, True, nmea_time, nmea_date
									except Exception as e:
										logger.info(e)
										logger.info('error setting system time')
										continue	
								except Exception as e:
									logger.info(e)
									logger.info('error parsing nmea sentence')
									continue
						#return False if gps fix but time not set	
						return ser, False, nmea_time, nmea_date
			sleep(1)
		#return False if loop is allowed to timeout
		return ser, False, nmea_time, nmea_date
	except Exception as e:
		logger.info(e)
		return ser, False, nmea_time, nmea_date
	
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
def record_gps(ser,fname):

	#initialize empty numpy array and fill with bad values
	u = np.empty(gps_samples)
	u.fill(badValue)
	v = np.empty(gps_samples)
	v.fill(badValue)
	z = np.empty(gps_samples)
	z.fill(badValue)
	lat = np.empty(gps_samples)
	lat.fill(badValue)
	lon = np.empty(gps_samples)
	lon.fill(badValue)
	
	try:
		ser.flushInput()
		with open(fname, 'w',newline='\n') as gps_out:
			
			logger.info('open file for writing: %s' %fname)
			t_end = t.time() + burst_seconds #get end time for burst
			ipos=0
			ivel=0
			while t.time() <= t_end or ipos < gps_samples or ivel < gps_samples:
				newline=ser.readline().decode()
				gps_out.write(newline)
				gps_out.flush()
		
				if "GPGGA" in newline:
					gpgga = pynmea2.parse(newline,check=True)   #grab gpgga sentence and parse
					#check to see if we have lost GPS fix, and if so, continue to loop start. a badValue will remain at this index
					if gpgga.gps_qual < 1:
						logger.info('lost GPS fix, sample not recorded. Waiting 10 seconds')
						sleep(10)
						ipos+=1
						continue
					z[ipos] = gpgga.altitude
					lat[ipos] = gpgga.latitude
					lon[ipos] = gpgga.longitude
					ipos+=1
				elif "GPVTG" in newline:
					if gpgga.gps_qual < 1:
						continue
					gpvtg = pynmea2.parse(newline,check=True)   #grab gpvtg sentence
					u[ivel] = gpvtg.spd_over_grnd_kmph*np.cos(gpvtg.true_track) #units are kmph
					v[ivel] = gpvtg.spd_over_grnd_kmph*np.sin(gpvtg.true_track) #units are kmph
					ivel+=1
				else: #if not GPGGA or GPVTG, continue to start of loop
					continue
			
				#if burst has ended but we are close to getting the right number of samples, continue for as short while
				if t.time() >= t_end and 0 < gps_samples-ipos <= 10:
					
					continue
				elif ipos == gps_samples and ivel == gps_samples:
					break
				
		badpts = len(np.where(z == 999)) #index of bad values if lost GPS fix. Should be same for u and v
	
		logger.info('number of GPGGA samples = %s' %ipos)
		logger.info('number of GPVTG samples = %s' %ivel)
		logger.info('number of bad samples %d' %badpts)
						
		return u,v,z,lat,lon
	except Exception as e:
		logger.info(e, exc_info=True)
		return u,v,z,lat,lon


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
#set up logging, initialize GPS, and record data unless importing as a module
if __name__ == "__main__":
	
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
	#call function to initialize GPS
	ser, gps_initialized, time, date = init_gps()
	
	if gps_initialized:
		logger.info('waiting for burst start')
		while True:
			#burst start conditions
			now=datetime.utcnow()
			if now.minute % burst_int == 0 and now.second == 0:
				
				logger.info("starting burst")
				#create file name
				fname = dataDir + 'microSWIFT'+floatID + '_GPS_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
				logger.info("file name: %s" %fname)
				#call record_gps	
				u,v,z,lat,lon = record_gps(ser,fname)
				
				
				#check if burst completed with 2048 poi
				try:
					if os.path.isfile(fname) and os.path.getsize(fname) > 0:
						#call data processing script
						logger.info('starting to process data')
						process_data.main(u,v,z,lat,lon,gps_freq,burst_seconds,badValue,payload_type,sensor_type,port,dataDir,floatID)
					else:
						logger.info('data file does not exist or does not contain enough data for processing')	
					
				except OSError as e:
					logger.info(e)
					sys.exit(1)
					
	else:
		logger.info("GPS not initialized, exiting")
		sys.exit(1)
		
 





	


		
