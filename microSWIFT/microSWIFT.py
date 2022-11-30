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
6. Process GPS data using the current gps_waves algorithm (GPS velocity
   based algorithm)
7. Compute mean values of lat, lon and other characteristics
8. createTX file and pack payload data
9. Send SBD over telemetry

TODO:
    - generateHeader function for each script? (i.e. --fun.py---)
"""

import concurrent.futures
import os
import sys
import time

import numpy as np

from .accoutrements import imu
from .accoutrements import gps
from .accoutrements import sbd
from .accoutrements import telemetry_stack
from datetime import datetime
from .processing.gps_waves import gps_waves
from .processing.uvza_waves import uvza_waves
from .processing.collate_imu_and_gps import collate_imu_and_gps
from .utils import config
from .utils import log
from .utils import utils


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


WAVE_PROCESSING_TYPE = 'gps_waves'
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
#TODO: init queue
telemetry_stack.init()
logger.info(f'Number of messages in queue: {telemetry_stack.get_length()}')

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

            # Start time of loop iteration #TODO: use utility here
            logger.info('----------- Iteration {} -----------'.format(loop_count))

            end_time = end_times[i]

            # Define next start time to enter into the sendSBD function:
            current_start = datetime.utcnow().replace(minute=start_times[i], second = 0, microsecond=0)
            next_start = current_start + datetime.timedelta(minutes=BURST_INT)

            # Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                record_gps_future = executor.submit(gps.record, end_times[i])
                record_imu_future = executor.submit(imu.record, end_times[i])

                # get results from Futures
                gps_file, gps_initialized = record_gps_future.result()
                imu_file, imu_initialized = record_imu_future.result()

            #exit out of loop once burst is finished
            recording_complete = True
            
            break

    if recording_complete is True:
        # TODO: this entire section requires clean up and organization,
        # including allowing the user to specify which type of processing 
        # they want to use. We should consider storing the imu and gps 
        # variables as attributes or properties in a gps class? Or just
        # omit the dictionary structure (sorry, I did that). It is a lot 
        # of variables to keep track of and pass around...

        # Time processing section
        logger.info('Starting Processing')
        begin_processing_time = datetime.now()
    
        
        # TODO: fix this comment:
        #  Compute u, v and z from raw GPS data
        # Process raw IMU data
        # Collate IMU and GPS onto a master time based on the IMU time
        # uvza_waves estimate; leave out first 120 seconds
        # gps_waves estimate (secondary estimate)

        if WAVE_PROCESSING_TYPE == 'gps_waves' and gps_initialized:
            gps_vars = gps.to_uvz(gps_file)
            Hs, Tp, Dp, E, f, a1, b1, a2, b2, check \
                                                    = gps_waves(gps_vars['u'],
                                                                gps_vars['v'],
                                                                gps_vars['z'],
                                                                GPS_FS)

            logger.info('gps_waves.py executed')

        elif WAVE_PROCESSING_TYPE == 'uvza_waves' and gps_initialized \
                                                        and imu_initialized:
            gps_vars = gps.to_uvz(gps_file)
            imu_vars =imu.to_xyz(imu_file, IMU_FS)
            imu_collated, gps_collated = collate_imu_and_gps(imu_vars, gps_vars)

            ZERO_POINTS = int(np.round(120*IMU_FS))
            Hs, Tp, Dp, E, f, a1, b1, a2, b2, check  \
                                = uvza_waves(gps_collated['u'][ZERO_POINTS:],
                                             gps_collated['v'][ZERO_POINTS:],
                                             imu_collated['pz'][ZERO_POINTS:],
                                             imu_collated['az'][ZERO_POINTS:],
                                             IMU_FS)
            logger.info('uvza_waves.py executed.')

        else:
            logger.info(('A wave solution cannot be created; either the'
                f' specified processing type (={WAVE_PROCESSING_TYPE}) is'
                f' invalid, or either or both of the sensors failed to'
                f' initialize (GPS initialized={gps_initialized}, IMU'
                f' initialized={imu_initialized}). Entering bad values for'
                f' the wave products (={BAD_VALUE}).'))
            u, v, z, lat, lon, Hs, Tp, Dp, E, f, a1, b1, a2, b2, check \
                                = utils.fill_bad_values(badVal=BAD_VALUE,
                                                        spectralLen=NUM_COEF)

        # check lengths of spectral quanities:
        if len(E)!=NUM_COEF or len(f)!=NUM_COEF:
            logger.info(('WARNING: the length of E or f does not match the'
                         f' specified number of coefficients, {NUM_COEF};'
                         f' (len(E)={len(E)}, len(f)={len(f)})'))

        # Extract the remaining variables. This solution is not great 
        # but can be sorted out later.
        u=gps_vars['u']
        v=gps_vars['v']
        z=gps_vars['z']
        lat=gps_vars['lat']
        lon=gps_vars['lon']

        # Compute mean velocities, elevation, lat and lon
        u_mean = np.nanmean(u)
        v_mean = np.nanmean(v)
        z_mean = np.nanmean(z) 
    
        #Get last reported position
        last_lat = utils.get_last(BAD_VALUE, lat)
        last_lon = utils.get_last(BAD_VALUE, lon)

        # Temperature and Voltage recordings - will be added in later versions
        voltage = 0
        temperature = 0.0
        salinity = 0.0
  
        # End Timing of recording
        logger.info('Processing section took {}'.format(datetime.now() - begin_processing_time))
            
        ## -------------- Telemetry Section ----------------------------------
        # Create TX file from processData.py output from combined wave products

        # Pack the data from the queue into the payload package
        logger.info('Creating TX file and packing payload data from primary estimate')
        tx_filename, payload_data = sbd.createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, last_lat, last_lon, temperature, salinity, voltage)
    
        ################################################################
        #### TODO: add this chunk to a telemetry stack (formerly queue) module
        #### called telemetry_stack.py and reduce the following to telemetry_stack.add(),
        
        # # Read in the file names from the telemetry queue
        # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
        # payload_filenames = telemetryQueue.readlines()
        # telemetryQueue.close()
        # payload_filenames_stripped = []
        # for line in payload_filenames:
        #     payload_filenames_stripped.append(line.strip())

        # # Append the primary estimate
        # logger.info(f'Adding TX file {tx_filename} to the telemetry queue')
        # payload_filenames_stripped.append(tx_filename)
        
        # # Write all the filenames to the file including the newest file name
        # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
        # for line in payload_filenames_stripped:
        #     telemetryQueue.write(line)
        #     telemetryQueue.write('\n')
        # telemetryQueue.close()

        # Append the newest file name to the list 
        payload_filenames = telemetry_stack.push(tx_filename)
        # payload_filenames = telemetry_stack.get_filenames()
        # payload_filenames.append(tx_filename)

        ################################################################
        #### TODO: add these to a telemetry stack module and reduce
        #### to telemetry_stack.get_last() or simlar. This can be called
        #### after each successful send. Or we can have a method that gets
        #### the whole stack list and just incorporate it as is.

        # payload_filenames_LIFO = list(np.flip(payload_filenames))

        logger.info('Number of Messages to send: {}'.format(len(payload_filenames)))

        # Send as many messages from the queue as possible during the send window
        messages_sent = 0
        for TX_file in list(np.flip(payload_filenames)):

            # Check if we are still in the send window
            if datetime.utcnow() < next_start:
                logger.info(f'Opening TX file from payload list: {TX_file}')
                
                with open(TX_file, mode='rb') as file: # b is important -> binary
                    payload_data = file.read() # TODO: payload_data would be returned by .get_last(), see comment above
        ################################################################

                # Read in the sensor type from the binary payload file.
                # This check is neccessary for a stack with multiple
                # sensor types in it.
                PAYLOAD_START_INDEX = 0 # (no header) otherwise it is: = payload_data.index(b':') 
                SENSOR_TYPE_FROM_PAYLOAD = ord(payload_data[PAYLOAD_START_INDEX+1:PAYLOAD_START_INDEX+2]) # sensor type is stored 1 byte after the header
                
                if SENSOR_TYPE_FROM_PAYLOAD not in [50,51,52]: #TODO: make this list a constant 
                    logger.info(f'Failed to read sensor type properly; read sensor type as: {SENSOR_TYPE_FROM_PAYLOAD}')
                    logger.info(f'Trying to send as configured sensor type instead ({SENSOR_TYPE})')
                    send_sensor_type = SENSOR_TYPE
                else:
                    send_sensor_type = SENSOR_TYPE_FROM_PAYLOAD

                # send either payload type 50, 51, or 52
                if send_sensor_type == 50:
                    successful_send = sbd.send_microSWIFT_50(payload_data, next_start)
                elif send_sensor_type == 51:
                    successful_send = sbd.send_microSWIFT_51(payload_data, next_start)
                elif send_sensor_type == 52:
                    successful_send = sbd.send_microSWIFT_52(payload_data, next_start)
                else:
                    logger.info(f'Specified sensor type ({send_sensor_type}) is invalid or not currently supported')

                # Index up the messages sent value if successful send is true
                if successful_send is True:
                    del payload_filenames[-1]
                    messages_sent += 1
            else:
                # Exit the for loop if outside of the end time
                break

        # Log the send statistics
        logger.info('Messages Sent: {}'.format(int(messages_sent)))
        messages_remaining = int(len(payload_filenames)) - messages_sent
        logger.info('Messages Remaining: {}'.format(messages_remaining))

        ################################################################
        #### TODO: add these to a telemetry stack module and reduce
        #### to telemetry_stack.remove() or similar? It might be better 
        #### to call this method in the loop above such that the order
        #### is more clear.

        # Remove the sent messages from the queue by writing the remaining lines to the file
        #TODO: this was moved to be inside the loop for clarity
        # if messages_sent > 0:
        #     del payload_filenames_stripped[-messages_sent:]


        # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
        # for line in payload_filenames_stripped:
        #     telemetryQueue.write(line)
        #     telemetryQueue.write('\n')
        # telemetryQueue.close()
        telemetry_stack.write(payload_filenames)
        ################################################################

        # Increment up the loop counter
        loop_count += 1
        wait_count = 0

        # End Timing of entire Script
        logger.info('microSWIFT.py took {}'.format(datetime.now() - begin_processing_time))
    
    else:
        time.sleep(1)
        wait_count += 1
        # Print waiting to log every 5 iterations
        if wait_count % 10 == 0:
            logger.info('Waiting to enter record window')
        continue
            