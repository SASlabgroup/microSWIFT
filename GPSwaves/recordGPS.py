#! /usr/bin/python3

#imports



#my imports
from config3 import Config


#load config file and get parameters
configFilename = sys.argv[1] #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	print ('Error loading config file: "%s"' % configFilename)
	#LOG ERROR
	sys.exit(0)






#set up logging

#setup GPIO and initialize

#attempt to set time based on GPS -> turn on and wait 30 sec

#turn off GPS and modem via GPIO pins

#def record_serial

	#initialize empty numpy array and fill with bad values

	#open serial port

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

		

















	


		
