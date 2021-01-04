#! /usr/bin/python3

#imports
import serial, sys, os
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time
import RPi.GPIO as GPIO
import pynmea2
import struct
import time
from time import sleep

#my imports
#import send_sbd_binary_data
#from rec_send_funcs import *
#import GPSwavesC
from config3 import Config


#load config file and get parameters
configFilename = sys.argv[1] #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	logger.info ('Error loading config file: "%s"' % configFilename)
	sys.exit(1)
	
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

#system parameters
dataDir = config.getString('System', 'dataDir')
floatID = config.getString('System', 'floatID') 
projectName = config.getString('System', 'projectName')
payLoadType = config.getInt('System', 'payLoadType')
badValue = config.getInt('System', 'badValue')
numCoef = config.getInt('System', 'numCoef')
Port = config.getInt('System', 'port')
payloadVersion = config.getInt('System', 'payloadVersion')
burst_seconds = config.getInt('System', 'burst_seconds')
burst_time = config.getInt('System', 'burst_time')
burst_int = config.getInt('System', 'burst_interval')

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

#temp and volt params 
#maxHoursTemp = config.getInt('Temp', 'maxHours')
#maxHoursVolt = config.getInt('Voltage', 'maxHours')

#Iridium parameters
#modemPort = config.getString('Iridium', 'port')
#modemBaud = config.getInt('Iridium', 'baud')
#modemGPIO = config.getInt('Iridium', 'modemGPIO')
#formatType = config.getInt('Iridium', 'formatType')
#callInt = config.getInt('Iridium', 'callInt')
#burst_num = config.getInt('Iridium', 'burstNum')

#hard coded parameters to change 
#IfHourlyCall = config.getString('Iridium', 'IfHourlyCall')
#IfHourlyCall = eval(IfHourlyCall) #boolean
#MakeCall = config.getString('Iridium', 'MakeCall') 
#MakeCall = eval(MakeCall) #boolean

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
		timeout=time.time() + gps_timeout
		while time.time() < timeout:
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
					logger.info('GPS quality= ' + str(gpgga.gps_qual))
					#check gps_qual value from GPGGS sentence. 0=invalid,1=GPS fix,2=DGPS fix
					if gpgga.gps_qual > 0:
						logger.info('GPS fix acquired')
						#get date and time from GPRMC sentence - GPRMC reported only once every 8 lines
						for i in range(8):
							newline=ser.readline().decode('utf-8')
							if 'GPRMC' in newline:
								try:
									gprmc=pynmea2.parse(newline)
									nmea_time=gprmc.timestamp
									nmea_date=gprmc.datestamp
									logger.info("nmea time: %s" %nmea_time)
									logger.info("nmea date: %s" %nmea_date)
									return ser, True, nmea_time, nmea_date		
								except Exception as e:
									logger.info(e)
									continue
							
						return ser, True, nmea_time, nmea_date
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
			t_end = time.time() + burst_seconds #get end time for burst
			ipos=0
			ivel=0
			while time.time() <= t_end or ipos < gps_samples or ivel < gps_samples:
				newline=ser.readline().decode()
				gps_out.write(newline)
				gps_out.flush()
		
				if "GPGGA" in newline:
					gpgga = pynmea2.parse(newline,check=True)   #grab gpgga sentence to return
					z[ipos] = gpgga.altitude
					lat[ipos] = gpgga.latitude
					lon[ipos] = gpgga.longitude
					ipos+=1
				elif "GPVTG" in newline:
					gpvtg = pynmea2.parse(newline,check=True)   #grab gpvtg sentence
					u[ivel] = gpvtg.spd_over_grnd_kmph*np.cos(gpvtg.true_track) #units are kmph
					v[ivel] = gpvtg.spd_over_grnd_kmph*np.sin(gpvtg.true_track) #units are kmph
					ivel+=1
				else: #if not GPGGA or GPVTG, continue to start of loop
					continue
			
				#if burst has ended but we are close to getting the right number of samples, continue for as short while
				if time.time() >= t_end and 0 < gps_samples-ipos <= 10:
					
					continue
				elif ipos == gps_samples and ivel == gps_samples:
					break
					
			logger.info('gps_samples ', gps_samples)	
			logger.info('number of GPGGA samples = ', ipos)
			logger.info('number of GPVTG samples = ', ivel)
						
		return u,v,z,lat,lon
	except Exception as e:
		logger.info(e)
		return u,v,z,lat,lon


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
def main():
	
	logger.info("---------------recordGPS.py------------------")
	logger.info(sys.version)
	
	#call function to initialize GPS
	ser, gps_initialized, time, date = init_gps()
	
	if gps_initialized:
		logger.info("GPS initialized")
		#set system time
		if time != '' and date != '':
			try:
				logger.info("setting system time from GPS: %s %s" %(date, time))
				os.system('sudo timedatectl set-timezone UTC')
				os.system('sudo date -s "%s %s"' %(date, time))
				os.system('sudo hwclock -w')
			except Exception as e:
				logger.info(e)
				logger.info('error setting system time')
		
		while True:
			#burst start conditions
			now=datetime.utcnow()
			if  now.minute == burst_time or now.minute % burst_int == 0 and now.second == 0:
				logger.info("starting burst")
				
				#create file name
				fname = dataDir + 'microSWIFT'+floatID + '_GPS_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
				logger.info("file name: %s" %fname)
				#call record_gps	
				u,v,z,lat,lon = record_gps(ser,fname)
			
				#GPS_waves_results = GPSwavesC.main_GPSwaves(gps_samples,u,v,z,gps_freq)
								
				#SigwaveHeight = GPS_waves_results[0]
				#logger.info ('WAVEHEIGHT: %f' %SigwaveHeight)
				
				#Peakwave_Period = GPS_waves_results[1]
				#Peakwave_dirT = GPS_waves_results[2]

				#WaveSpectra_Energy = np.squeeze(GPS_waves_results[3])
				#WaveSpectra_Energy = np.where(WaveSpectra_Energy>=18446744073709551615, 999.00000, WaveSpectra_Energy)
				#WaveSpectra_Freq = np.squeeze(GPS_waves_results[4])
				#WaveSpectra_Freq = np.where(WaveSpectra_Freq>=18446744073709551615, 999.00000, WaveSpectra_Freq)
				#WaveSpectra_a1 = np.squeeze(GPS_waves_results[5])
				#WaveSpectra_a1 = np.where(WaveSpectra_a1>=18446744073709551615, 999.00000, WaveSpectra_a1)
				#WaveSpectra_b1 = np.squeeze(GPS_waves_results[6])
				#WaveSpectra_b1 = np.where(WaveSpectra_b1>=18446744073709551615, 999.00000, WaveSpectra_b1)
				#WaveSpectra_a2 = np.squeeze(GPS_waves_results[7])
				#WaveSpectra_a2 = np.where(WaveSpectra_a2>=18446744073709551615, 999.00000, WaveSpectra_a2)
				#WaveSpectra_b2 = np.squeeze(GPS_waves_results[8])
				#WaveSpectra_b2 = np.where(WaveSpectra_b2>=18446744073709551615, 999.00000, WaveSpectra_b2)
				
				checkdata = np.full(numCoef,1)
				
				np.set_printoptions(formatter={'float_kind':'{:.5f}'.format})
				np.set_printoptions(formatter={'float_kind':'{:.2e}'.format})
			
				#uMean = getuvzMean(badValue,u)
				#vMean = getuvzMean(badValue,v)
				#zMean = getuvzMean(badValue,z)
				
				#dname = now.strftime('%d%b%Y')
				#tname = now.strftime('%H:%M:%S') 
				
				#fbinary = (dataDir + floatID + 'SWIFT' + '_' + projectName + '_' + dname + '_' + tname + '.sbd')
				#eventLog.info('[%.3f] - SBD file: %s' %(elapsedTime, fbinary ))
			
				if payLoadType == 50:
					payLoadSize = (16 + 7*42)*4
					#eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, payLoadType))
					#eventLog.info('[%.3f] - payLoadSize: %d' % (elapsedTime, payLoadSize))
				else:
					payLoadSize =  (5 + 7*42)*4
					#eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, payLoadType))
					#eventLog.info('[%.3f] - payLoadSize: %d' % (elapsedTime, payLoadSize))
		
				#try:
				#	fbinary = open(fbinary, 'wb')
					
				#except:
				#	logger.info ('[%.3f] - To write binary file is already open' % elapsedTime)
				
				#SigwaveHeight = round(SigwaveHeight,6)
				#Peakwave_Period = round(Peakwave_Period,6)
				#Peakwave_dirT = round(Peakwave_dirT,6)
				
				lat[0] = round(lat[0],6)
				lon[0] = round(lon[0],6)
				#uMean= round(uMean,6)
				#vMean= round(vMean,6)
				#zMean= round(zMean,6)
				
				#fbinary.write(struct.pack('<sbbhfff', 
				#						 str(payloadVersion),payLoadType,Port,
				#						 payLoadSize,SigwaveHeight,Peakwave_Period,Peakwave_dirT))
		 
				#fbinary.write(struct.pack('<42f', *WaveSpectra_Energy))
				#fbinary.write(struct.pack('<42f', *WaveSpectra_Freq))
				#fbinary.write(struct.pack('<42f', *WaveSpectra_a1))
				#fbinary.write(struct.pack('<42f', *WaveSpectra_b1))
				#fbinary.write(struct.pack('<42f', *WaveSpectra_a2))
				#fbinary.write(struct.pack('<42f', *WaveSpectra_b2))
				#fbinary.write(struct.pack('<42f', *checkdata))
				#fbinary.write(struct.pack('<f', lat[0]))
				#fbinary.write(struct.pack('<f', lon[0]))
				#fbinary.write(struct.pack('<f', temp))
				#fbinary.write(struct.pack('<f', volt))
				#fbinary.write(struct.pack('<f', uMean))
				#fbinary.write(struct.pack('<f', vMean))
				#fbinary.write(struct.pack('<f', zMean))
				#fbinary.write(struct.pack('<i', int(now.year)))
				#fbinary.write(struct.pack('<i', int(now.month)))
				#fbinary.write(struct.pack('<i', int(now.day)))
				#fbinary.write(struct.pack('<i', int(now.hour)))
				#fbinary.write(struct.pack('<i', int(now.minute)))
				#fbinary.write(struct.pack('<i', int(now.second)))
				#fbinary.flush()
				#fbinary.close()
			sleep(0.5)

				
	else:
		logger.info("GPS not init ialized, no data will be logged")
		
	sys.exit(0)

#run main function unless importing as a module
if __name__ == "__main__":
    main()





	


		
