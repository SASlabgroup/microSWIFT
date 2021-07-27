## microSWIFT.py 
"""
author: @erainvil

Description: This script is the main operational script that runs on the microSWIFT. It is the scheduler that runs the recording of the GPS
and IMU as well as schedules the processing scripts after they are done recording. 


"""

# Main import Statemennts
from threading import Thread
from recordGPSTest import recordGPS
from GPSwaves.GPSwaves import GPSwaves

## ------------------- Test function section --------------------
# this will be removed and each function will live in its own file as we start to make these functions work
# def recordGPS():
#     print('GPS recording')

def recordIMU():
    print('IMU recording')

# processGPS data test functions
def GPStoUVZ(fname):
    print('reading in GPS data and converting to UVZ')
    u = v = z = lat = lon = [] 
    return u, v, z, lat, lon

# def GPSwaves(u,v,z,fs):
#     print('Computing bulk waves parameters from GPSwaves algorithm')
#     Hs = Tp = Dp = E = f = a1 = b1 = a2 = b2 = []
#     return Hs, Tp, Dp, E, f, a1, b1, a2, b2

# Telemetry test functions
def createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2):
    print('TX file created with the variables Hs, Tp, Dp, E, f, a1, b1, a2, b2')
    TX_fname = 'TX-file'
    return TX_fname

def sendSBD(TX_fname):
    print('Sending SBD...')
    print('Sent SBD...')


# Boot up as soon as power is turned on and get microSWIFT characteristics
    # Get microSWIFT number 
    # setup log files
GPS_fs = 4
IMU_fs = 4

## -------------- GPS and IMU Recording Section ---------------------------
# Run recordGPS.py and recordIMU.py concurrently
# Create threads to run concurrently 
threads = []
recordGPS_thread = Thread(target=recordGPS, args=[])
recordIMU_thread = Thread(target=recordIMU, args=[])

# Start each recording thread 
recordGPS_thread.start()
recordIMU_thread.start()

# Add each thread to the threads list
threads.append(recordGPS_thread)
threads.append(recordIMU_thread)

# Wait to continue main thread until all recording threads have finished by "joining"
for process in threads:
    process.join()

## --------------- Data Processing Section ---------------------------------
# Run processGPS
fname = 'name from recording section'

# Compute u, v and z from raw GPS data
u, v, z, lat, lon = GPStoUVZ(fname)

# Compute Wave Statistics from GPSwaves algorithm
Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, GPS_fs)


# Run processIMU
    # IMU data:
    # read in IMU data from file 
    # IMUtoXYZ(IMU data)
    # XYZwaves( XYZ from above )
    
## -------------- Telemetry Section ----------------------------------
# Create TX file from processData.py output from combined wave products
TX_fname = createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2)

# Send SBD over telemetry
sendSBD(TX_fname)

# Restart Recording



