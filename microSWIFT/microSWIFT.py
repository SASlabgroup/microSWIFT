"""
The main operational script that runs on the microSWIFT V1 wave buoys.

This script sequences data collection, post-processing, and telemetry of
the microSWIFTs. Its core task is to schedule these events, ensuring
that the buoy is in the appropriate record or send window based on the
user-defined settings.

author(s): @edwinrainville, @alexdeklerk, @vivianacastillo, @jacobrdavis

Outline:
1. Load modules
2. Start main loop
3. Submit concurrent jobs to record GPS and record IMU separetely
4. End recording
5. Read-in GPS data from file
6. Process GPS data using the current GPSwaves algorithm (GPS velocity
   based algorithm)
7. Compute mean values of lat, lon and other characteristics
8. createTX file and pack payload data
9. Send SBD over telemetry

TODO:
    - update style
        * MAKE SURE IT IS CONSISTNENT WITH GROUP
        * what doc string style are we using?
        * single or double strings?
        * tabbing of function signatures?
    - docstrings
    - generateHeader function for each script? (i.e. --fun.py---)
    - alphabetize imports
    - log ideas: get_GPS_fs(), create a single function call log() which
      performs logger.info()
"""

import concurrent.futures
import os
import sys
import time

import numpy as np

from accoutrements import imu
from accoutrements import gps
from accoutrements import sbd
from datetime import datetime
from processing import imu_to_xyz, gps_waves, gps_to_uvz, uvza_waves
from utils import config
from utils import log
from utils import utils


####TODO: Update this block when EJ finishes the config integration ####
#Define Config file name and load file
CONFIG_FILENAME = r'/home/pi/microSWIFT/utils/Config.dat'
config = config.Config() # Create object and load file
loaded = config.loadFile(CONFIG_FILENAME)
if not loaded:
    print("Error loading config file")
    sys.exit(1)


# System Parameters
DATA_DIR = config.getString('System', 'dataDir')
FLOAT_ID = os.uname()[1]
SENSOR_TYPE = config.getInt('System', 'sensorType')
BAD_VALUE = config.getInt('System', 'badValue')
NUM_COEF = config.getInt('System', 'numCoef')
PORT = config.getInt('System', 'port')
PAYLOAD_TYPE = config.getInt('System', 'payloadType')
BURST_SECONDS = config.getInt('System', 'burst_seconds')
BURST_TIME = config.getInt('System', 'burst_time')
BURST_INT = config.getInt('System', 'burst_interval')


# GPS parameters
GPS_FS = config.getInt('GPS', 'gps_frequency') #TODO: currently not used, hardcoded at 4 Hz (see init_gps function)
# IMU parameters
IMU_FS = config.getFloat('IMU', 'imuFreq') #TODO: NOTE this has been changed to 12 from 12.5 (actual) to obtain proper # of pts in processing

#Compute number of bursts per hour
NUM_BURSTS = int(60 / BURST_INT)


#Generate lists of burst start and end times based on parameters from Config file
start_times = [BURST_TIME + i*BURST_INT for i in range(NUM_BURSTS)]
end_times = [start_times[i] + BURST_SECONDS/60 for i in range(NUM_BURSTS)]
########################################################################

# Initialize the logger to keep track of running tasks. These will print
# directly to the microSWIFT's log file. Then log the configuration.
logger = log.init()
log.header('', length = 50)
logger.info('Booted up')
logger.info('microSWIFT configuration:')
logger.info(f'float ID: {FLOAT_ID}, payload type: {PAYLOAD_TYPE}, sensor type: {SENSOR_TYPE}, ')
logger.info(f'burst seconds: {BURST_SECONDS}, burst interval: {BURST_INT}, burst time: {BURST_TIME}')

# TODO: 
# Define loop and wait counters. `loop_count` keeps track of the number
# of duty cycles and `wait_count` waiting to enter a record window.
loop_count = 1
wait_count = 0

# Initialize the telemetry stack if it does not exist yet. This is a
# text file that keeps track of the names of messages that have not been
# sent after a processing window. If messages are not sent, the
# message name will be stored and it will attempt to send at the next
# send window.
# TODO: change this to telemetry_stack.init()
logger.info('Initializing Telemetry Queue')
telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','a')
telemetryQueue.close()

# TODO: add this to checkout.py to make sure the stack is empty before it goes 
# out. Could be a function in telemetry_stack that gets called by checkout.py
telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
logger.info(f'Number of messages in queue: {len(telemetryQueue.readlines())}')
telemetryQueue.close
###

while True:
    current_min = datetime.utcnow().minute + datetime.utcnow().second/60
    duty_cycle_start_time = datetime.now()

    # Both IMU and GPS start as unititialized
    recording_complete = False

    # If the current time is within any record window (between start 
    # and end time) record the imu and gps data until the end of the
    # window. 
    for i in np.arange(len(start_times)):
        if current_min >= start_times[i] and current_min < end_times[i]:

            # Start time of loop iteration
            logger.info('----------- Iteration {} -----------'.format(loop_count))

            end_time = end_times[i]

            # Define next start time to enter into the sendSBD function:
            current_start = datetime.utcnow().replace(minute=start_times[i], second = 0, microsecond=0)
            next_start = current_start + datetime.timedelta(minutes=BURST_INT)

            # Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                record_gps_future = executor.submit(gps.record(), end_times[i])
                record_imu_future = executor.submit(imu.record(), end_times[i])

                # get results from Futures
                gps_file, gps_initialized = record_gps_future.result()
                IMUdataFilename, imu_initialized = record_imu_future.result()

            #exit out of loop once burst is finished
            recording_complete = True
            
            break

    if recording_complete is True:
        ## --------------- Data Processing Section ---------------------------------
        # Time processing section
        logger.info('Starting Processing')
        begin_processing_time = datetime.now()
        
        # #---TODO: delete
        # gps_initialized = True
        # imu_initialized = True
        # IMUdataFilename = '/home/pi/microSWIFT/data/microSWIFT057_IMU_17Aug2022_000146UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
        # gps_file = '/home/pi/microSWIFT/data/microSWIFT057_GPS_17Aug2022_000151UTC.dat'
        # #---TODO: delete
            
        if gps_initialized and imu_initialized: #gps_initialized == True and imu_initialized == True:
            logger.info('GPS and IMU initialized')

            # Compute u, v and z from raw GPS data
            GPS = gps.to_uvz(gps_file) # u, v, z, lat, lon = gps_to_uvz(gps_file)

            # Process raw IMU data
            IMU = imu_to_xyz(IMUdataFilename, IMU_FS) # ax, vx, px, ay, vy, py, az, vz, pz = imu_to_xyz(IMUdataFilename,IMU_FS)

            # Collate IMU and GPS onto a master time based on the IMU time
            logger.info('entering collateIMUandGPS.py')
            IMUcol,GPScol = collateIMUandGPS(IMU, GPS)
            logger.info('collateIMUandGPS.py executed')

            # UVZAwaves estimate; leave out first 120 seconds
            zeroPts = int(np.round(120*IMU_FS)) 
            logger.info(f'Zeroing out first 120 seconds ({zeroPts} pts)')
            Hs, Tp, Dp, E, f, a1, b1, a2, b2, check  = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], IMU_FS)
            logger.info('UVZAwaves.py executed, primary estimate (voltage==0)')

            # GPSwaves estimate (secondary estimate)
            Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], GPS_FS)
            logger.info('GPSwaves.py executed, secondary estimate (voltage==1)')

            # Unpack GPS variables for remaining code; use non-interpolated values
            u=GPS['u']; v=GPS['v']; z=GPS['z']; lat=GPS['lat']; lon=GPS['lon']

        elif gps_initialized and not imu_initialized: 
            
            # Compute u, v and z from raw GPS data
            u, v, z, lat, lon = gps_to_uvz(gps_file)

            # Compute Wave Statistics from GPSwaves algorithm
            Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = GPSwaves(u, v, z, GPS_FS)

        elif imu_initialized and not gps_initialized:
            #TODO: Process IMU data
            logger.info(f'GPS did not initialize but IMU did; would put IMU processing here but it is not yet functional... entering bad values ({BAD_VALUE})')
            u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=BAD_VALUE, spectralLen=NUM_COEF)

        else: # no IMU or GPS, enter bad values
            logger.info(f'Neither GPS or IMU initialized - entering bad values ({BAD_VALUE})')
            u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=BAD_VALUE, spectralLen=NUM_COEF)

        # check lengths of spectral quanities:
        if len(E)!=NUM_COEF or len(f)!=NUM_COEF:
            logger.info(f'WARNING: the length of E or f does not match the specified number of coefficients, {NUM_COEF}; (len(E)={len(E)}, len(f)={len(f)})')

        # Compute mean velocities, elevation, lat and lon
        u_mean = np.nanmean(u)
        v_mean = np.nanmean(v)
        z_mean = np.nanmean(z) 
    
        #Get last reported position
        last_lat = _get_last(BAD_VALUE, lat)
        last_lon = _get_last(BAD_VALUE, lon)

        # Temperature and Voltage recordings - will be added in later versions
        temp = 0.0
        salinity = 0.0
        volt = 0   #NOTE: primary estimate
        volt_2 = 1 #NOTE: secondary estimate (GPS if IMU and GPS are both initialized)

        # End Timing of recording
        logger.info('Processing section took {}'.format(datetime.now() - begin_processing_time))
            
        ## -------------- Telemetry Section ----------------------------------
        # Create TX file from processData.py output from combined wave products

        # Pack the data from the queue into the payload package
        logger.info('Creating TX file and packing payload data from primary estimate')
        TX_fname, payload_data = createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt)
    
        try: # GPSwaves estimate as secondary estimate
            logger.info('Creating TX file and packing payload data from secondary estimate')
            TX_fname_2, payload_data_2 = createTX(Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt_2)
        except:
            logger.info('No secondary estimate exists')

        # Read in the file names from the telemetry queue
        telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
        payload_filenames = telemetryQueue.readlines()
        telemetryQueue.close()
        payload_filenames_stripped = []
        for line in payload_filenames:
            payload_filenames_stripped.append(line.strip())

        # Append secondary estimate first (LIFO)
        try:
            logger.info(f'Adding TX file {TX_fname_2} to the telemetry queue')
            payload_filenames_stripped.append(TX_fname_2)
        except:
            logger.info('No secondary estimate exists to add to queue')

        # Append the primary estimate
        logger.info(f'Adding TX file {TX_fname} to the telemetry queue')
        payload_filenames_stripped.append(TX_fname)
        
        # Write all the filenames to the file including the newest file name
        telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
        for line in payload_filenames_stripped:
            telemetryQueue.write(line)
            telemetryQueue.write('\n')
        telemetryQueue.close()

        # Append the newest file name to the list
        payload_filenames_LIFO = list(np.flip(payload_filenames_stripped))
        logger.info('Number of Messages to send: {}'.format(len(payload_filenames_LIFO)))

        # Send as many messages from the queue as possible during the send window
        messages_sent = 0
        logger.info(payload_filenames_LIFO)
        for TX_file in payload_filenames_LIFO:
            # Check if we are still in the send window 
            if datetime.utcnow() < next_start:
                logger.info(f'Opening TX file from payload list: {TX_file}')
                
                with open(TX_file, mode='rb') as file: # b is important -> binary
                    payload_data = file.read()

                # read in the sensor type from the binary payload file
                payloadStartIdx = 0 # (no header) otherwise it is: = payload_data.index(b':') 
                sensor_type0 = ord(payload_data[payloadStartIdx+1:payloadStartIdx+2]) # sensor type is stored 1 byte after the header
                
                if sensor_type0 not in [50,51,52]:
                    logger.info(f'Failed to read sensor type properly; read sensor type as: {sensor_type0}')
                    logger.info(f'Trying to send as configured sensor type instead ({SENSOR_TYPE})')
                    send_sensor_type = SENSOR_TYPE
                else:
                    send_sensor_type = sensor_type0

                # send either payload type 50, 51, or 52
                if send_sensor_type == 50:
                    successful_send = send_microSWIFT_50(payload_data, next_start)
                elif send_sensor_type == 51:
                    successful_send = send_microSWIFT_51(payload_data, next_start)
                elif send_sensor_type == 52:
                    successful_send = send_microSWIFT_52(payload_data, next_start)
                else:
                    logger.info(f'Specified sensor type ({send_sensor_type}) is invalid or not currently supported')

                # Index up the messages sent value if successful send is true
                if successful_send == True:
                    messages_sent += 1
            else:
                # Exit the for loop if outside of the end time 
                break

        # Log the send statistics
        logger.info('Messages Sent: {}'.format(int(messages_sent)))
        messages_remaining = int(len(payload_filenames_stripped)) - messages_sent
        logger.info('Messages Remaining: {}'.format(messages_remaining))

        # Remove the sent messages from the queue by writing the remaining lines to the file
        if messages_sent > 0:
            del payload_filenames_stripped[-messages_sent:]
        telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
        for line in payload_filenames_stripped:
            telemetryQueue.write(line)
            telemetryQueue.write('\n')
        telemetryQueue.close()

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
            