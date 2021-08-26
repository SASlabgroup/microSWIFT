#! /usr/bin/python3

## microSWIFT.py 
"""
authors: @EJRainville, @AlexdeKlerk and @VivianaCastillo

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
Stable version with sendSBD and recordGPS fixes added and merged into microSWIFT.py-Centralized branch - 08/25/21

"""

# Main import Statemennts
import concurrent.futures
import datetime
import numpy as np
import datetime
from logging import *
import sys, os

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
from SBD.sendSBD import sendSBD

# Import Configuration functions
from utils.config3 import Config

# Main body of microSWIFT.py
if __name__=="__main__":

    # ------------ Logging Characteristics ---------------
    # Define Config file name
    configFilename = r'utils/Config.dat'
    config = Config() # Create object and load file
    ok = config.loadFile( configFilename )
    if( not ok ):
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
    logger.info('Booted up at {}'.format(datetime.datetime.now()))

    #Output configuration parameters to log file
    logger.info('microSWIFT configuration:')
    logger.info('float ID: {0}, payload type: {1}, sensors type: {2}, '.format(floatID, payload_type, sensor_type))
    logger.info('burst seconds: {0}, burst interval: {1}, burst time: {2}'.format(burst_seconds, burst_int, burst_time))
    # logger.info('gps sample rate: {0}, call interval {1}, call time: {2}'.format(GPS_fs, call_int, call_time)) # Burst Int and burst time have not been defined yet

    # Define loop counter
    i = 1

    # --------------- Main Loop -------------------------
    while True:
        # Start time of loop iteration
        begin_script_time = datetime.datetime.now()
        logger.info('----------- Iteration {} -----------'.format(i))
        logger.info('At start of loop at {}'.format(begin_script_time))

        ## -------------- GPS and IMU Recording Section ---------------------------
        # Time recording section
        begin_recording_time = datetime.datetime.now()

        # Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit Futures 
            recordGPS_future = executor.submit(recordGPS, configFilename)
            recordIMU_future = executor.submit(recordIMU, configFilename)

            # get results from Futures
            GPSdataFilename, gps_intitialized = recordGPS_future.result()
            IMUdataFilename = recordIMU_future.result()

        # End Timing of recording
        logger.info('Recording section took {}'.format(datetime.datetime.now() - begin_recording_time))

        ## --------------- Data Processing Section ---------------------------------
        # Time processing section
        begin_processing_time = datetime.datetime.now()
        logger.info('Starting Processing')

        if gps_intitialized==True:

            # Run processGPS
            # Compute u, v and z from raw GPS data
            u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)

            # Compute Wave Statistics from GPSwaves algorithm
            Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, GPS_fs)

        else:
            # Bad Values of the GPS did not initialize
            u = 999
            v = 999
            z = 999
            lat = 999
            lon = 999

        # Compute mean velocities, elevation, lat and lon
        u_mean = np.nanmean(u)
        v_mean = np.nanmean(v)
        z_mean = np.nanmean(z)
        lat_mean = np.nanmean(lat)
        lon_mean = np.nanmean(lon)

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
        logger.info('Processing section took {}'.format(datetime.datetime.now() - begin_processing_time))
            
        ## -------------- Telemetry Section ----------------------------------
        # Create TX file from processData.py output from combined wave products
        logger.info('Creating TX file and packing payload data')
        TX_fname, payload_data = createTX(Hs, Tp, Dp, E, f, u_mean, v_mean, z_mean, lat_mean, lon_mean, temp, volt, configFilename)

        # Decode contents of TX file and print out as a check - will be removed in final versions
        # checkTX(TX_fname)

        # Initialize Iridium Modem
        logger.info('Intializing Modem now')
        ser, modem_initialized = initModem()

        # Send SBD over telemetry
        if modem_initialized == True:
            logger.info('entering sendSBD function now')
            sendSBD(ser, payload_data)
        else:
            logger.info('Modem did not initialize')

        # Increment up the loop counter
        i += 1

        # End Timing of entire Script
        logger.info('microSWIFT.py took {}'.format(datetime.datetime.now() - begin_script_time))
        logger.info('\n')