## microSWIFT.py 
"""
author: @edwinrainville, @alexdeklerk, @vivianacastillo, @jacobrdavis

This is pared down version of microSWIFT.py that is used for evaluating IMU AHRS algorithms.

TODO:
	-
"""

# Main import Statemennts
import concurrent.futures
import datetime
import pwd
import numpy as np
from datetime import datetime, timedelta
from logging import *
import sys, os
from time import sleep
import struct

# Import GPS functions
from GPS.recordGPS import recordGPS
from GPS.GPStoUVZ import GPStoUVZ

# Import IMU functions
from IMU.recordIMU import recordIMU
# from IMU.IMUtoXYZ import IMUtoXYZ 

# Import wave processing functions
from waves.UVZAwaves import UVZAwaves
from waves.GPSwaves import GPSwaves 

# Import configuration and utility functions
from utils.config3 import Config
from utils.collateIMUandGPS import collateIMUandGPS
from utils.fillBadValues import fillBadValues

# Raspberry pi inputs
import RPi.GPIO as GPIO

# IMU sensor imports
import busio, board
import IMU.adafruit_fxos8700_microSWIFT
import IMU.adafruit_fxas21002c_microSWIFT

# Main body of microSWIFT.py
if __name__=="__main__":

	#Define Config file name and load file
	configFilename = r'/home/pi/microSWIFT/utils/Config.dat'
	config = Config() # Create object and load file
	ok = config.loadFile( configFilename )
	if( not ok ):
		print("Error loading config file")
		sys.exit(1)

	# System Parameters
	dataDir = config.getString('System', 'dataDir')
	floatID = os.uname()[1]
	sensor_type = config.getInt('System', 'sensorType')
	badValue = config.getInt('System', 'badValue')
	numCoef = config.getInt('System', 'numCoef')
	port = config.getInt('System', 'port')
	payload_type = config.getInt('System', 'payloadType')
	burst_seconds = config.getInt('System', 'burst_seconds')
	burst_time = config.getInt('System', 'burst_time')
	burst_int = config.getInt('System', 'burst_interval')
	
	# GPS parameters
	GPS_fs = config.getInt('GPS', 'gps_frequency') #currently not used, hardcoded at 4 Hz (see init_gps function)

	#IMU parameters
	imuFreq=config.getFloat('IMU', 'imuFreq')
	imu_gpio=config.getInt('IMU', 'imu_gpio')

	#initialize IMU GPIO pin as modem on/off control
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(imu_gpio,GPIO.OUT)
	#turn IMU on for script recognizes i2c address
	GPIO.output(imu_gpio,GPIO.HIGH)

	# Set-up logging based on config file parameters
	logger = getLogger('microSWIFT')
	logDir = config.getString('Loggers', 'logDir')
	LOG_LEVEL = config.getString('Loggers', 'DefaultLogLevel')
	LOG_FORMAT = ('%(asctime)s, %(name)s - [%(levelname)s] - %(message)s')
	LOG_FILE = (logDir  + logger.name + '.log')
	logger.setLevel(LOG_LEVEL)
	logFileHandler = FileHandler(LOG_FILE)
	logFileHandler.setLevel(LOG_LEVEL)
	logFileHandler.setFormatter(Formatter(LOG_FORMAT))
	logger.addHandler(logFileHandler)

	# Output Booted up time to log 
	logger.info('-----------------------------------------')
	logger.info('Booted up')

	#Output configuration parameters to log file
	logger.info('microSWIFT configuration:')
	logger.info(f'IMU rate: {imuFreq}')
	
	logger.info('initializing IMU')
	logger.info('power on IMU')

	GPIO.output(imu_gpio,GPIO.HIGH)
	i2c = busio.I2C(board.SCL, board.SDA)
	fxos = IMU.adafruit_fxos8700_microSWIFT.FXOS8700(i2c, accel_range=0x00)
	fxas = IMU.adafruit_fxas21002c_microSWIFT.FXAS21002C(i2c, gyro_range=500)

	acc = []
	mag = []
	gyo = []
	# --------------- Main Loop -------------------------
	while True:
		t = datetime.utcnow()
		n = 0 
		acc = np.empty((3,10))
		mag = np.empty((3,10))
		gyo = np.empty((3,10))

		while n <= 10:
			try:
				# t = datetime.utcnow()
				print(acc)
				acc[:,n] = fxos.accelerometer
				# acc.append(fxos.accelerometer)
				# mag.append(fxos.magnetometer)
				# gyo.append(fxas.gyroscope)
				n += 1
				# accel_x, accel_y, accel_z = fxos.accelerometer
				# mag_x, mag_y, mag_z = fxos.magnetometer
				# gyro_x, gyro_y, gyro_z = fxas.gyroscope

				sleep(1)
			except Exception as e:
				logger.info(e)
				logger.info('error reading IMU data')
		# print(acc)

		print(acc)
		# acc = np.array(acc).T


		# ax = round(sum(acc[0])/n,3)
		# ay = round(sum(acc[1])/n,3)
		# az = round(sum(acc[2])/n,3)

		# logger.info(f'{t} {ax} {ay} {az}')
		
		# # initialize fxos and fxas devices (required after turning off device)
    	

        # # Sleep to start recording at same time as GPS
        # sleep(5.1)
        
        # # return initialized values
        # imu_initialized = True

        # logger.info('IMU initialized')

        # ## --------------- Record IMU ----------------------
        # #create new file for to record IMU to 
        # logger.info('---------------recordIMU.py------------------')
        # IMUdataFilename = dataDir + floatID + '_IMU_'+'{:%d%b%Y_%H%M%SUTC.dat}'.format(datetime.utcnow())
        # logger.info('file name: {}'.format(IMUdataFilename))
        # logger.info('starting IMU burst at {}'.format(datetime.now()))
            
        # # Open the new IMU data file for logging
        # with open(IMUdataFilename, 'w',newline='\n') as imu_out:
        #     logger.info('open file for writing: {}'.format(IMUdataFilename))
        #     isample=0
        #     while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and isample < imu_samples:
        #         # Get values from IMU
        #         try:
        #             accel_x, accel_y, accel_z = fxos.accelerometer
        #             mag_x, mag_y, mag_z = fxos.magnetometer
        #             gyro_x, gyro_y, gyro_z = fxas.gyroscope
        #         except Exception as e:
        #             logger.info(e)
        #             logger.info('error reading IMU data')

        #         # Get current timestamp
        #         timestamp='{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())

        #         # Write data and timestamp to file
        #         imu_out.write('%s,%f,%f,%f,%f,%f,%f,%f,%f,%f\n' %(timestamp,accel_x,accel_y,accel_z,mag_x,mag_y,mag_z,gyro_x,gyro_y,gyro_z))
        #         imu_out.flush()
                
        #         # Index up number of samples
        #         isample = isample + 1

        #         # hard coded sleep to control recording rate. NOT ideal but works for now    
        #         sleep(0.065)
            
        #     # End of IMU sampling
        #     logger.info('end burst')
        #     logger.info('IMU samples {}'.format(isample)) 
        #     logger.info('IMU ending burst at: {}'.format(datetime.now()))

        #     # Turn IMU Off   
        #     GPIO.output(imu_gpio,GPIO.LOW)
        #     logger.info('power down IMU')














	# # Define loop counter
	# loop_count = 1
	# wait_count = 0

	# # --------------- Main Loop -------------------------
	# while True:

	# 	current_min = datetime.utcnow().minute + datetime.utcnow().second/60
	# 	begin_script_time = datetime.now()

	# 	## -------------- GPS and IMU Recording Section ---------------------------
	# 	# Time recording section
	# 	begin_recording_time = datetime.now()

	# 	# Both IMU and GPS start as unititialized
	# 	recording_complete = False

	# 	for i in np.arange(len(start_times)):
	# 		if current_min >= start_times[i] and current_min < end_times[i]: #Are we in a record window

	# 			# Start time of loop iteration
	# 			logger.info('----------- Iteration {} -----------'.format(loop_count))
				
	# 			end_time = end_times[i]

	# 			# Define next start time to enter into the sendSBD function:
	# 			current_start = datetime.utcnow().replace(minute=start_times[i], second = 0, microsecond=0)
	# 			next_start = current_start + timedelta(minutes=burst_int)
				
	# 			# Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
	# 			#TODO: uncomment
	# 			with concurrent.futures.ThreadPoolExecutor() as executor:
	# 				# Submit Futures 
	# 				recordGPS_future = executor.submit(recordGPS, end_times[i])
	# 				recordIMU_future = executor.submit(recordIMU, end_times[i])

	# 				# get results from Futures
	# 				GPSdataFilename, gps_initialized = recordGPS_future.result()
	# 				IMUdataFilename, imu_initialized = recordIMU_future.result()
	# 			#TODO: uncomment 

	# 			#exit out of loop once burst is finished
	# 			recording_complete = True
				
	# 			break

	# 	if recording_complete == True: 
	# 		## --------------- Data Processing Section ---------------------------------
	# 		# Time processing section
	# 		logger.info('Starting Processing')
	# 		begin_processing_time = datetime.now()
			
	# 		# #---TODO: delete
	# 		# gps_initialized = True
	# 		# imu_initialized = True
	# 		# IMUdataFilename = '/home/pi/microSWIFT/data/microSWIFT057_IMU_17Aug2022_000146UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
	# 		# GPSdataFilename = '/home/pi/microSWIFT/data/microSWIFT057_GPS_17Aug2022_000151UTC.dat'
	# 		# #---TODO: delete
				
	# 		if gps_initialized and imu_initialized: #gps_initialized == True and imu_initialized == True:
	# 			logger.info('GPS and IMU initialized')

	# 			# Compute u, v and z from raw GPS data
	# 			logger.info(f'entering GPStoUVZ.py: {GPSdataFilename}')
	# 			GPS = GPStoUVZ(GPSdataFilename) # u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)
	# 			logger.info('GPStoUVZ executed')

	# 			# Process raw IMU data
	# 			logger.info(f'entering IMUtoXYZ.py: {IMUdataFilename}')
	# 			IMU = IMUtoXYZ(IMUdataFilename, IMU_fs) # ax, vx, px, ay, vy, py, az, vz, pz = IMUtoXYZ(IMUdataFilename,IMU_fs)
	# 			logger.info('IMUtoXYZ.py executed')

	# 			# Collate IMU and GPS onto a master time based on the IMU time
	# 			logger.info('entering collateIMUandGPS.py')
	# 			IMUcol,GPScol = collateIMUandGPS(IMU, GPS)
	# 			logger.info('collateIMUandGPS.py executed')

	# 			# UVZAwaves estimate; leave out first 120 seconds
	# 			zeroPts = int(np.round(120*IMU_fs)) 
	# 			logger.info(f'Zeroing out first 120 seconds ({zeroPts} pts)')
	# 			Hs, Tp, Dp, E, f, a1, b1, a2, b2, check  = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], IMU_fs)
	# 			logger.info('UVZAwaves.py executed, primary estimate (voltage==0)')

	# 			# GPSwaves estimate (secondary estimate)
	# 			Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], GPS_fs)
	# 			logger.info('GPSwaves.py executed, secondary estimate (voltage==1)')

	# 			# Unpack GPS variables for remaining code; use non-interpolated values
	# 			u=GPS['u']; v=GPS['v']; z=GPS['z']; lat=GPS['lat']; lon=GPS['lon']

	# 		elif gps_initialized and not imu_initialized: 
				
	# 			# Compute u, v and z from raw GPS data
	# 			u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)

	# 			# Compute Wave Statistics from GPSwaves algorithm
	# 			Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = GPSwaves(u, v, z, GPS_fs)

	# 		elif imu_initialized and not gps_initialized:
	# 			#TODO: Process IMU data
	# 			logger.info(f'GPS did not initialize but IMU did; would put IMU processing here but it is not yet functional... entering bad values ({badValue})')
	# 			u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=badValue, spectralLen=numCoef)

	# 		else: # no IMU or GPS, enter bad values
	# 			logger.info(f'Neither GPS or IMU initialized - entering bad values ({badValue})')
	# 			u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=badValue, spectralLen=numCoef)

	# 		# check lengths of spectral quanities:
	# 		if len(E)!=numCoef or len(f)!=numCoef:
	# 			logger.info(f'WARNING: the length of E or f does not match the specified number of coefficients, {numCoef}; (len(E)={len(E)}, len(f)={len(f)})')

	# 		# Compute mean velocities, elevation, lat and lon
	# 		u_mean = np.nanmean(u)
	# 		v_mean = np.nanmean(v)
	# 		z_mean = np.nanmean(z) 
		
	# 		#Get last reported position
	# 		last_lat = _get_last(badValue, lat)
	# 		last_lon = _get_last(badValue, lon)

	# 		# Temperature and Voltage recordings - will be added in later versions
	# 		temp = 0.0
	# 		salinity = 0.0
	# 		volt = 0   #NOTE: primary estimate
	# 		volt_2 = 1 #NOTE: secondary estimate (GPS if IMU and GPS are both initialized)

	# 		# End Timing of recording
	# 		logger.info('Processing section took {}'.format(datetime.now() - begin_processing_time))
				
	# 		## -------------- Telemetry Section ----------------------------------
	# 		# Create TX file from processData.py output from combined wave products

	# 		# Pack the data from the queue into the payload package
	# 		logger.info('Creating TX file and packing payload data from primary estimate')
	# 		TX_fname, payload_data = createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt)
		
	# 		try: # GPSwaves estimate as secondary estimate
	# 			logger.info('Creating TX file and packing payload data from secondary estimate')
	# 			TX_fname_2, payload_data_2 = createTX(Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt_2)
	# 		except:
	# 			logger.info('No secondary estimate exists')

	# 		# Read in the file names from the telemetry queue
	# 		telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
	# 		payload_filenames = telemetryQueue.readlines()
	# 		telemetryQueue.close()
	# 		payload_filenames_stripped = []
	# 		for line in payload_filenames:
	# 			payload_filenames_stripped.append(line.strip())

	# 		# Append secondary estimate first (LIFO)
	# 		try:
	# 			logger.info(f'Adding TX file {TX_fname_2} to the telemetry queue')
	# 			payload_filenames_stripped.append(TX_fname_2)
	# 		except:
	# 			logger.info('No secondary estimate exists to add to queue')

	# 		# Append the primary estimate
	# 		logger.info(f'Adding TX file {TX_fname} to the telemetry queue')
	# 		payload_filenames_stripped.append(TX_fname)
			
	# 		# Write all the filenames to the file including the newest file name
	# 		telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
	# 		for line in payload_filenames_stripped:
	# 			telemetryQueue.write(line)
	# 			telemetryQueue.write('\n')
	# 		telemetryQueue.close()

	# 		# Append the newest file name to the list
	# 		payload_filenames_LIFO = list(np.flip(payload_filenames_stripped))
	# 		logger.info('Number of Messages to send: {}'.format(len(payload_filenames_LIFO)))

	# 		# Send as many messages from the queue as possible during the send window
	# 		messages_sent = 0
	# 		logger.info(payload_filenames_LIFO)
	# 		for TX_file in payload_filenames_LIFO:
	# 			# Check if we are still in the send window 
	# 			if datetime.utcnow() < next_start:
	# 				logger.info(f'Opening TX file from payload list: {TX_file}')
					
	# 				with open(TX_file, mode='rb') as file: # b is important -> binary
	# 					payload_data = file.read()

	# 				# read in the sensor type from the binary payload file
	# 				payloadStartIdx = 0 # (no header) otherwise it is: = payload_data.index(b':') 
	# 				sensor_type0 = ord(payload_data[payloadStartIdx+1:payloadStartIdx+2]) # sensor type is stored 1 byte after the header
					
	# 				if sensor_type0 not in [50,51,52]:
	# 					logger.info(f'Failed to read sensor type properly; read sensor type as: {sensor_type0}')
	# 					logger.info(f'Trying to send as configured sensor type instead ({sensor_type})')
	# 					send_sensor_type = sensor_type
	# 				else:
	# 					send_sensor_type = sensor_type0

	# 				# send either payload type 50, 51, or 52
	# 				if send_sensor_type == 50:
	# 					successful_send = send_microSWIFT_50(payload_data, next_start)
	# 				elif send_sensor_type == 51:
	# 					successful_send = send_microSWIFT_51(payload_data, next_start)
	# 				elif send_sensor_type == 52:
	# 					successful_send = send_microSWIFT_52(payload_data, next_start)
	# 				else:
	# 					logger.info(f'Specified sensor type ({send_sensor_type}) is invalid or not currently supported')

	# 				# Index up the messages sent value if successful send is true
	# 				if successful_send == True:
	# 					messages_sent += 1
	# 			else:
	# 				# Exit the for loop if outside of the end time 
	# 				break

	# 		# Log the send statistics
	# 		logger.info('Messages Sent: {}'.format(int(messages_sent)))
	# 		messages_remaining = int(len(payload_filenames_stripped)) - messages_sent
	# 		logger.info('Messages Remaining: {}'.format(messages_remaining))

	# 		# Remove the sent messages from the queue by writing the remaining lines to the file
	# 		if messages_sent > 0:
	# 			del payload_filenames_stripped[-messages_sent:]
	# 		telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
	# 		for line in payload_filenames_stripped:
	# 			telemetryQueue.write(line)
	# 			telemetryQueue.write('\n')
	# 		telemetryQueue.close()

	# 		# Increment up the loop counter
	# 		loop_count += 1
	# 		wait_count = 0

	# 		# End Timing of entire Script
	# 		logger.info('microSWIFT.py took {}'.format(datetime.now() - begin_script_time))
		
	# 	else:
	# 		sleep(1)
	# 		wait_count += 1
	# 		# Print waiting to log every 5 iterations
	# 		if wait_count % 10 == 0:
	# 			logger.info('Waiting to enter record window')
	# 		continue
			