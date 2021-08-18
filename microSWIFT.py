## microSWIFT.py 
"""
author: @edwinrainville
		adapted heavily from previous functions and scripts written by Alex de Klerk and Vivano Castillo

Description: This script is the main operational script that runs on the microSWIFT. It is the scheduler that runs the recording of the GPS
and IMU as well as schedules the processing scripts after they are done recording.

Outline: 
1. Load modules
2. Start main loop 
3. Submit concurrent jobs to recordGPS and recordIMU separetely
4. End recording
5. Read-in GPS data from file
6. Process GPS data using the current GPSwaves algorithm
7. Compute mean values of lat, lon and other characteristics
8. createTX file and pack payload data
9. Send SBD over telemetry

Stable version that does not include sendSBD yet - 08/09/21


"""

# Main import Statemennts
import concurrent.futures
import datetime
import numpy as np
from utils.config3 import Config

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

# Start running continuously while raspberry pi is on
print('Starting up at ', datetime.datetime.now())
while True:
    # Start time of loop iteration
    begin_script_time = datetime.datetime.now()
    print('At start of loop')

    ## ------------- Boot up Characteristics --------------------------------
    # Define Config file name
    configFilename = r'./utils/Config.dat' 

    # Boot up as soon as power is turned on and get microSWIFT characteristics
        # Get microSWIFT number 
        # setup log files
    GPS_fs = 4 # need to get from config file
    IMU_fs = 4

    ## -------------- GPS and IMU Recording Section ---------------------------
    # Time recording section
    begin_recording_time = datetime.datetime.now()

    # Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit Futures 
        recordGPS_future = executor.submit(recordGPS, configFilename)
        recordIMU_future = executor.submit(recordIMU, configFilename)

        # get results from Futures
        GPSdataFilename = recordGPS_future.result()
        IMUdataFilename = recordIMU_future.result()

    # End Timing of recording
    print('Recording section took', datetime.datetime.now() - begin_recording_time)

    ## --------------- Data Processing Section ---------------------------------
    # Time processing section
    begin_processing_time = datetime.datetime.now()

    # Run processGPS
    # Compute u, v and z from raw GPS data
    u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)

    # Compute Wave Statistics from GPSwaves algorithm
    Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, GPS_fs)

    # Compute mean velocities, elevation, lat and lon
    u_mean = np.mean(u)
    v_mean = np.mean(v)
    z_mean = np.mean(z)
    lat_mean = np.mean(lat)
    lon_mean = np.mean(lon)

    # Temperature and Voltage recordings - will be added in later versions
    temp = 0
    volt = 0

    # End Timing of recording
    print('Processing section took', datetime.datetime.now() - begin_processing_time)
        
    ## -------------- Telemetry Section ----------------------------------
    # Create TX file from processData.py output from combined wave products
    TX_fname, payload_data = createTX(Hs, Tp, Dp, E, f, u_mean, v_mean, z_mean, lat_mean, lon_mean, temp, volt, configFilename)

    # Decode contents of TX file and print out as a check - will be removed in final versions
    checkTX(TX_fname)

    # Send SBD over telemetry
    # sendSBD(payload_data, configFilename)

    # End Timing of entire Script
    print('microSWIFT.py took', datetime.datetime.now() - begin_script_time)


