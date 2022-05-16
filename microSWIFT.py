## microSWIFT.py 
"""
author: @EJ Rainville, @Alex de Klerk, @Viviana Castillo

Description: This script is the main operational script that runs on the microSWIFT. It is the scheduler that runs the recording of the GPS
and IMU as well as schedules the processing scripts after they are done recording.

Outline: 
1. Load modules
2. Start main loop 
3. Submit concurrent jobs to record GPS and record IMU separetely
4. End recording
5. Read-in GPS data from file
6. Process GPS data using the current GPSwaves algorithm (GPS velocity based algorithm)
7. Compute mean values of lat, lon and other characteristics
8. createTX file and pack payload data
9. Send SBD over telemetry

Stable version that does not include sendSBD yet - 08/09/21
Stable version that does include sendSBD - 08/20/21
Successfully merged all fixes/ bugs into microSWIFT.py-Centralized - 08/25/21


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
from GPS.GPSwaves import GPSwaves
from GPS.GPStoUVZ import GPStoUVZ

# Import IMU functions
from IMU.recordIMU import recordIMU

# Import SBD functions
from SBD.sendSBD import createTX
from SBD.sendSBD import sendSBD
from SBD.sendSBD import checkTX
from SBD.sendSBD import initModem
from SBD.sendSBD import send_microSWIFT_50
from SBD.sendSBD import send_microSWIFT_51

# Import Configuration functions
from utils.config3 import Config

def _get_uvzmean(badValue, pts):
	mean = badValue     #set values to 999 initially and fill if valid value
	index = np.where(pts != badValue)[0] #get index of non bad values
	pts=pts[index] #take subset of data without bad values in it
	
	if(len(index) > 0):
		mean = np.mean(pts)
   
	return mean

def _get_last(badValue, pts):
	for i in range(1, len(pts)): #loop over entire lat/lon array
		if pts[-i] != badValue: #count back from last point looking for a real position
			return pts[-i]
		
	return badValue #returns badValue if no real position exists

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
	# IMU parameters
	IMU_fs = config.getFloat('IMU', 'imuFreq')


	#Compute number of bursts per hour
	num_bursts = int(60 / burst_int)
	
	#Generate lists of burst start and end times based on parameters from Config file
	start_times = [burst_time + i*burst_int for i in range(num_bursts)]
	end_times = [start_times[i] + burst_seconds/60 for i in range(num_bursts)]

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
	logger.info('float ID: {0}, payload type: {1}, sensor type: {2}, '.format(floatID, payload_type, sensor_type))
	logger.info('burst seconds: {0}, burst interval: {1}, burst time: {2}'.format(burst_seconds, burst_int, burst_time))
	# logger.info('gps sample rate: {0}, call interval {1}, call time: {2}'.format(GPS_fs, call_int, call_time)) # Burst Int and burst time have not been defined yet

	# Define loop counter
	loop_count = 1
	wait_count = 0

	# Initialize the Telemetry Queue - create file and then close for thread protection
	# Note: 'a' opens the file in append mode so that previous data is not deleted
	telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','a')
	telemetryQueue.close()
	logger.info('Created Telemetry Queue')

	# --------------- Main Loop -------------------------
	while True:

		current_min = datetime.utcnow().minute + datetime.utcnow().second/60
		begin_script_time = datetime.now()

		## -------------- GPS and IMU Recording Section ---------------------------
		# Time recording section
		begin_recording_time = datetime.now()

		# Both IMU and GPS start as unititialized
		recording_complete = False

		for i in np.arange(len(start_times)):
			if current_min >= start_times[i] and current_min < end_times[i]: #Are we in a record window

				# Start time of loop iteration
				logger.info('----------- Iteration {} -----------'.format(loop_count))
				
				end_time = end_times[i]

				# Define next start time to enter into the sendSBD function:
				current_start = datetime.utcnow().replace(minute=start_times[i], second = 0, microsecond=0)
				next_start = current_start + timedelta(minutes=burst_int)
				
				# Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
				with concurrent.futures.ThreadPoolExecutor() as executor:
					# Submit Futures 
					recordGPS_future = executor.submit(recordGPS, end_times[i])
					recordIMU_future = executor.submit(recordIMU, end_times[i])

					# get results from Futures
					GPSdataFilename, gps_initialized = recordGPS_future.result()
					IMUdataFilename, imu_initialized = recordIMU_future.result()

				#exit out of loop once burst is finished
				recording_complete = True

				
				break

		if recording_complete == True: 
			## --------------- Data Processing Section ---------------------------------
			# Time processing section
			logger.info('Starting Processing')
			begin_processing_time = datetime.now()

			# Prioritize GPS processing
			if gps_initialized==True:

				# Run processGPS
				# Compute u, v and z from raw GPS data
				u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)

				# Compute Wave Statistics from GPSwaves algorithm
				Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = GPSwaves(u, v, z, GPS_fs)

			elif imu_initialized==True:
				
				# Process IMU data
				logger.info('GPS did not initialize but IMU did - Would put IMU processing here but it is not yet functional')
				# Bad Values of the GPS did not initialize - no imu processing in place yet
				u = 999
				v = 999
				z = 999
				lat = [999]
				lon = [999]
				Hs = 999
				Tp = 999
				Dp = 999
				E = 999 * np.ones(42)
				f = 999 * np.ones(42)
				a1 = 999 * np.ones(42)
				b1 = 999 * np.ones(42)
				a2 = 999 * np.ones(42) 
				b2 = 999 * np.ones(42)
				check = 999 * np.ones(42)

			
			else:
				logger.info('Neither GPS or IMU initialized - entering bad values')
				# Bad Values of the GPS did not initialize
				u = 999
				v = 999
				z = 999
				lat = 999
				lon = 999
				Hs = 999
				Tp = 999
				Dp = 999
				E = 999 * np.ones(42)
				f = 999 * np.ones(42)
				a1 = 999 * np.ones(42)
				b1 = 999 * np.ones(42)
				a2 = 999 * np.ones(42) 
				b2 = 999 * np.ones(42)
				check = 999 * np.ones(42)

			# Compute mean velocities, elevation, lat and lon
			u_mean = np.nanmean(u)
			v_mean = np.nanmean(v)
			z_mean = np.nanmean(z)
		
			#Get last reported position
			last_lat = _get_last(badValue, lat)
			last_lon = _get_last(badValue, lon)

			# Temperature and Voltage recordings - will be added in later versions
			temp = 0
			volt = 0

			# Print some values of interest
			logger.info('Hs = {}'.format(Hs))
			logger.info('Tp = {}'.format(Tp))
			logger.info('Dp = {}'.format(Dp))
			logger.info('u_mean = {}'.format(u_mean))
			logger.info('v_mean = {}'.format(v_mean))

			# End Timing of recording
			logger.info('Processing section took {}'.format(datetime.now() - begin_processing_time))
				
			## -------------- Telemetry Section ----------------------------------
			# Create TX file from processData.py output from combined wave products
			# Pack the data from the queue into the payload package
			logger.info('Creating TX file and packing payload data')
			TX_fname, payload_data = createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, last_lat, last_lon, temp, volt)

			# Append the telemetrry queue with the processed data
			logger.info('Adding TX filename to the telemetry queue')
			telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','a')
			telemetryQueue.write(TX_fname)
			telemetryQueue.write('\n')
			telemetryQueue.close()

			# Send as many payloads as possible from the queue in FIFO order
			telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r+')
			payload_files = telemetryQueue.readlines()
			logger.info('Number of Messages to send: {}'.format(len(payload_files)))

			# Send as many messages from the queue as possible
			messages_sent = 0
			for TX_file in payload_files:
				# Check if we are still in the send window 
				if datetime.utcnow() < next_start - timedelta(seconds=10):
					# Open the TX file for the payload 
					TX_filename = TX_file[:-1] # Remove the last character since a space is saved
					logger.info('Opening TX file from payload list')
					logger.info(TX_filename)
					with open(TX_filename, mode='rb') as file: # b is important -> binary
						payload_data = file.read()

					# send either payload type 50 or 51
					if sensor_type == 50:
						successful_send = send_microSWIFT_50(payload_data, next_start)
					elif sensor_type == 51:
						successful_send = send_microSWIFT_51(payload_data, next_start)
					# Index up the messages sent value if successful send is true
					if successful_send == True:
						messages_sent += 1
				else:
					# Exit this for loop if you are outside of the send window
					break

			# Close the Queue from read mode and report final send statistics
			telemetryQueue.close()
			logger.info('Messages Sent: {}'.format(int(messages_sent)))
			logger.info('Messages Remaining: {}'.format(int(len(payload_files)) - messages_sent))

			# Remove the sent messages from the queue

			# Increment up the loop counter
			loop_count += 1
			wait_count = 0

			# End Timing of entire Script
			logger.info('microSWIFT.py took {}'.format(datetime.now() - begin_script_time))
		
		else:
			sleep(1)
			wait_count += 1
			# Print waiting to log every 5 iterations
			if wait_count % 10 == 0:
				logger.info('Waiting to enter record window')
			continue
			