## microSWIFT.py 
"""
author: @erainvil

Description: This script is the main operational script that runs on the microSWIFT. It is the scheduler that runs the recording of the GPS
and IMU as well as schedules the processing scripts after they are done recording. 


"""

# Main import Statemennts
import concurrent.futures
import datetime
import numpy as np

# Import GPS functions
from GPS.recordGPS import recordGPS
from GPS.GPSwaves import GPSwaves
from GPS.GPStoUVZ import GPStoUVZ

# Import IMU functions
from IMU.recordIMU import recordIMU

# Import SBD functions
from SBD.sendSBD import createTX
from SBD.sendSBD import sendSBD

# Start running continuously while raspberry pi is on
while True:
    # Start time of loop iteration
    begin_script_time = datetime.datetime.now()
    print('Starting up')

    ## ------------- Boot up Characteristics --------------------------------
    # Define Config file name
    configFilename = r'utils/Config.dat' 

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

    # Compute mean velocities and elevation
    umean = np.mean(u)
    vmean = np.mean(v)
    zmean = np.mean(z)

    # Temperature and Voltage recordings - will be added in later versions
    temp = 0
    volt = 0

    # End Timing of recording
    print('Processing section took', datetime.datetime.now() - begin_processing_time)

    # Run processIMU
        # IMU data:
        # read in IMU data from file 
        # IMUtoXYZ(IMU data)
        # XYZwaves( XYZ from above )
        
    ## -------------- Telemetry Section ----------------------------------
    # Create TX file from processData.py output from combined wave products
    TX_fname = createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, umean, vmean, zmean, temp, volt, configFilename)

    # Send SBD over telemetry
    sendSBD(TX_fname)

    # End Timing of entire Script
    print('microSWIFT.py took', datetime.datetime.now() - begin_script_time)


