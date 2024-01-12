## microSWIFT.py 
"""
author: @edwinrainville, @alexdeklerk, @vivianacastillo, @jacobrdavis

Description: This script is the main operational script that runs on the microSWIFT. It is the 
scheduler that runs the recording of the GPS and IMU as well as schedules the processing scripts 
after they are done recording.

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

Log:
    - 08/09/21, @edwinrainville, @alexdeklerk, @vivianacastillo: Stable version that does not include sendSBD yet
    - 08/20/21, @edwinrainville, @alexdeklerk, @vivianacastillo: Stable version that does include sendSBD
         - 08/25/21, @edwinrainville, @alexdeklerk, @vivianacastillo: Successfully merged all fixes/ bugs into microSWIFT.py-Centralized
         - Sep 2021, @edwinrainville: DUNEX development
         - Jun 2022, @edwinrainville: telemetry queue
        - Aug 2022, @jacobrdavis: UVZAwaves
        - Aug 2022, @jacobrdavis: sensor_type_52, salinity placeholder
        - Aug 2022, @jacobrdavis: modified telemetry queue to check payload sensorType (to support multi-sensortype queues)
        
TODO:
        - telemetryQueue needs some way of knowing which SBD message it has. Possibly using len?
        - generateHeader function for each script? (i.e. --fun.py---)
"""

# Main import Statemennts
import concurrent.futures
import datetime
import pwd
import numpy as np
from datetime import datetime, timedelta
# from logging import *
import logging
import logging.handlers
import sys, os
from time import sleep
import struct

# Import GPS functions
from GPS.recordGPS import recordGPS
from GPS.GPStoUVZ import GPStoUVZ

# Import IMU functions
from IMU.recordIMU import recordIMU
from IMU.IMUtoXYZ import IMUtoXYZ 

# import functions to record health of rpi
from Health.recordHTH import recordHTH

# Import wave processing functions
from waves.UVZAwaves import UVZAwaves
from waves.GPSwaves import GPSwaves 

# Import SBD functions
from SBD.sendSBD import createTX
from SBD.sendSBD import sendSBD
from SBD.sendSBD import checkTX
from SBD.sendSBD import initModem_atStart
from SBD.sendSBD import send_microSWIFT_50
from SBD.sendSBD import send_microSWIFT_51
from SBD.sendSBD import send_microSWIFT_52
from SBD.sendSBD import send_health
from SBD.sendSBD import send_GPS
from SBD.sendSBD import send_location_and_health

# Import configuration and utility functions
from utils.config3 import Config
from utils.collateIMUandGPS import collateIMUandGPS
from utils.fillBadValues import fillBadValues

# RS start
from multiprocessing import Process, Queue
import threading

RS_filename=""

# here I am assuming that sending out the messages happens only occasionally,
# while updating the variables for the last value happens frequently
# with this implemenation, we just stop updating the variables while we
# send it out, causing that the variable might be slightly out of date, but
# we don't mingle different values together
#
# one lock would be sufficient, but possible future modifications might make
# two locks necessary
# moved to files in /dev/shm - assuming that's locked by the OS, above didn't work

#
# Because you'll want to define the logging configurations for listener and workers, the
# listener and worker process functions take a configurer parameter which is a callable
# for configuring logging for that process. These functions are also passed the queue,
# which they use for communication.
#
# In practice, you can configure the listener however you want, but note that in this
# simple example, the listener does not apply level or filter logic to received records.
# In practice, you would probably want to do this logic in the worker processes, to avoid
# sending events which would be filtered out between processes.
#
# The size of the rotated files is made small so you can see the results easily.
def listener_configurer():
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('mptest.log', 'a', 3000000, 10)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)

# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
# The worker configuration is done at the start of the worker process run.
# Note that on Windows you can't rely on fork semantics, so each process
# will run the logging configuration code when it starts.
def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.DEBUG)

# This is the worker process top-level loop, which just logs ten events with
# random intervening delays before terminating.
# The print messages are just so you know it's doing something!
def worker_process(queue, configurer):
    configurer(queue)
    name = multiprocessing.current_process().name
    print('Worker started: %s' % name)
    for i in range(10):
        time.sleep(random())
        logger = logging.getLogger(choice(LOGGERS))
        level = choice(LEVELS)
        message = choice(MESSAGES)
        logger.log(level, message)
    print('Worker finished: %s' % name)

# calc thread
def make_calculation(q, qs, lq, workc):
    workc(lq)
    logger = logging.getLogger(LOG_NAME)
    ## --------------- Data Processing Section ---------------------------------
    # Time processing section
    logger.info('Starting Processing, reniced to ' + str(os.nice(10)))
    ret=""
    while ret != "done":
        ret = q.get()
        
        gps_initialized = ret[0]
        imu_initialized = ret[1]
        GPSdataFilename = ret[2]
        IMUdataFilename = ret[3]

        logger.info("RS: got these filenames : " + GPSdataFilename + " and " + IMUdataFilename)
        # print("RS: got this array: ", ret)
        # print("RS: got these filenames : " + GPSdataFilename + " and " + IMUdataFilename)
        
        begin_processing_time = datetime.now()
        
        if gps_initialized and imu_initialized: #gps_initialized == True and imu_initialized == True:
            logger.info('GPS and IMU initialized')
            
            # Compute u, v and z from raw GPS data
            logger.info(f'entering GPStoUVZ.py: {GPSdataFilename}')
            GPS = GPStoUVZ(GPSdataFilename) # u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)
            logger.info('GPStoUVZ executed')
            
            # Process raw IMU data
            logger.info(f'entering IMUtoXYZ.py: {IMUdataFilename}')
            IMU = IMUtoXYZ(IMUdataFilename, IMU_fs) # ax, vx, px, ay, vy, py, az, vz, pz = IMUtoXYZ(IMUdataFilename,IMU_fs)
            logger.info('IMUtoXYZ.py executed')
            
            # Collate IMU and GPS onto a master time based on the IMU time
            logger.info('entering collateIMUandGPS.py')
            IMUcol,GPScol = collateIMUandGPS(IMU, GPS)
            logger.info('collateIMUandGPS.py executed')
            
            # UVZAwaves estimate; leave out first 120 seconds
            zeroPts = int(np.round(120*IMU_fs)) 
            logger.info(f'Zeroing out first 120 seconds ({zeroPts} pts)')
            Hs, Tp, Dp, E, f, a1, b1, a2, b2, check  = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], IMU_fs)
            logger.info('UVZAwaves.py executed, primary estimate (voltage==0)')
            
            # GPSwaves estimate (secondary estimate)
            Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], GPS_fs)
            logger.info('GPSwaves.py executed, secondary estimate (voltage==1)')
            
            # Unpack GPS variables for remaining code; use non-interpolated values
            u=GPS['u']; v=GPS['v']; z=GPS['z']; lat=GPS['lat']; lon=GPS['lon']
            
        elif gps_initialized and not imu_initialized: 
            
            # Compute u, v and z from raw GPS data
            u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)
        
            # Compute Wave Statistics from GPSwaves algorithm
            Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = GPSwaves(u, v, z, GPS_fs)
            
        elif imu_initialized and not gps_initialized:
            #TODO: Process IMU data
            logger.info(f'GPS did not initialize but IMU did; would put IMU processing here but it is not yet functional... entering bad values ({badValue})')
            u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=badValue, spectralLen=numCoef)
            
        else: # no IMU or GPS, enter bad values
            logger.info(f'Neither GPS or IMU initialized - entering bad values ({badValue})')
            u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=badValue, spectralLen=numCoef)
            
        # check lengths of spectral quanities:
        if len(E)!=numCoef or len(f)!=numCoef:
            logger.info(f'WARNING: the length of E or f does not match the specified number of coefficients, {numCoef}; (len(E)={len(E)}, len(f)={len(f)})')
        
        # Compute mean velocities, elevation, lat and lon
        u_mean = np.nanmean(u)
        v_mean = np.nanmean(v)
        z_mean = np.nanmean(z) 
        
        #Get last reported position
        last_lat = _get_last(badValue, lat)
        last_lon = _get_last(badValue, lon)
        
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
        TX_fname_2 = TX_fname
        try: # GPSwaves estimate as secondary estimate
            logger.info('Creating TX file and packing payload data from secondary estimate')
            TX_fname_2, payload_data_2 = createTX(Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt_2)
        except:
            logger.info('No secondary estimate exists')
        
        # # Read in the file names from the telemetry queue
        # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
        # payload_filenames = telemetryQueue.readlines()
        # telemetryQueue.close()
        # payload_filenames_stripped = []
        # for line in payload_filenames:
        #     payload_filenames_stripped.append(line.strip())
        
        # # Append secondary estimate first (LIFO)
        # try:
        #     logger.info(f'Adding TX file {TX_fname_2} to the telemetry queue')
        #     payload_filenames_stripped.append(TX_fname_2)
        # except:
        #     logger.info('No secondary estimate exists to add to queue')
        
        # # Append the primary estimate
        # logger.info(f'Adding TX file {TX_fname} to the telemetry queue')
        # payload_filenames_stripped.append(TX_fname)
        
        # # Write all the filenames to the file including the newest file name
        # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
        # for line in payload_filenames_stripped:
        #     telemetryQueue.write(line)
        #     telemetryQueue.write('\n')
        # telemetryQueue.close()
        
        # # Append the newest file name to the list
        # payload_filenames_LIFO = list(np.flip(payload_filenames_stripped))
        # logger.info('Number of Messages to send: {}'.format(len(payload_filenames_LIFO)))
        
        # RS TODO add filename to send thread
        # qs.put(["added", ret])
        qs.put(TX_fname)
        qs.put(TX_fname_2)
        
    qs.put("done")
    
# send thread

def add_2_send_queue(q, lq, workc):
    workc(lq)
    logger = logging.getLogger(LOG_NAME)
    ret=""
    while ret != "done":
        ret = q.get()
        # print("send :", ret)
        TX_file=ret.split(',')[0]
        radiostatus_filename=""
        if len(ret.split(',')) >=2:
            radiostatus_filename=ret.split(',')[1]
        # RS: create a dummy next_start, date now plus 20 minutes
        next_start = datetime.utcnow() + timedelta(minutes=20)
        # Send as many messages from the queue as possible during the send window
        messages_sent = 0
        # logger.info(payload_filenames_LIFO)
        # for TX_file in payload_filenames_LIFO:
        # Check if we are still in the send window 
        # if datetime.utcnow() < next_start:
        # RS: one file per send thread - and send independent of windows - send in background
        logger.info(f'Opening TX file from payload list: {TX_file}')
        
        # not as binary for time being !
        # with open(TX_file, mode='rb') as file: # b is important -> binary
        with open(TX_file, mode='r') as file: # b is important -> binary
            payload_data = file.read()
        
        # read in the sensor type from the binary payload file
        # coded in ascii as csv
        # payloadStartIdx = 0 # (no header) otherwise it is: = payload_data.index(b':') 
        # sensor_type0 = ord(payload_data[payloadStartIdx+1:payloadStartIdx+2]) # sensor type is stored 1 byte after the header
        sensor_type0 = -1
        if len(payload_data.split(','))>=2:
            sensor_type0 = int(payload_data.split(',')[1])
        if sensor_type0 not in [0, 1, 50,51,52]:
            logger.info(f'Failed to read sensor type properly; read sensor type as: {sensor_type0}')
            logger.info(f'Trying to send as configured sensor type instead ({sensor_type})')
            send_sensor_type = sensor_type
        else:
            send_sensor_type = sensor_type0
        
        # send either payload type 50, 51, or 52 - or 0, 1 RS new
        #  0 means health and contains info about radio link quality
        radio_status=""
        if send_sensor_type == 0:
            successful_send, radio_status = send_health(payload_data, next_start)
            
            logger.info(f'Will be writing radio {radio_status} status to file: {radiostatus_filename}')
            with open(radiostatus_filename, "a") as file:
                file.write(radio_status+"\n")
        elif send_sensor_type == 1:
            successful_send = send_GPS(payload_data, next_start)
        elif send_sensor_type == 50:
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
        #RS messages_remaining = int(len(payload_filenames_stripped)) - messages_sent
        #RS logger.info('Messages Remaining: {}'.format(messages_remaining))
        
        # # Remove the sent messages from the queue by writing the remaining lines to the file
        # if messages_sent > 0:
        #     del payload_filenames_stripped[-messages_sent:]
        # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
        # for line in payload_filenames_stripped:
        #     telemetryQueue.write(line)
        #     telemetryQueue.write('\n')
        # telemetryQueue.close()
        
        # Increment up the loop counter
        # loop_count += 1
        # wait_count = 0
        
        # End Timing of entire Script
        # logger.info('microSWIFT.py took {}'.format(datetime.now() - begin_script_time))


#RS end

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

def send2shor(queue_send, current_end, file_radiostatus):
    # wait 1 min to let other threads collect some data
    sleep(60)
    # send once in 5 mins
    now=datetime.utcnow()
    
    hn = os.uname().nodename
    nid=1
    if hn.startswith("buoy"):
        nid = int(hn[4:])
    
    logger = logging.getLogger(LOG_NAME)
    
    logger.info('-----------------------------------------')
    logger.info('--------------send2shore-----------------')
    logger.info('--------------send2shore-----------------' + str(nid))
    
    delay = 2*nid - now.second
    if delay < 0:
        delay = delay + 60
    logger.info('---send2shore---- configured delay of ' + str(delay))
    logger.info('--------------send2shore-----------------')
    logger.info('--------------send2shore-----------------')
    logger.info('--------------send2shore-----------------')
    
    sleep(delay)
        
    # enough time for one more transmission ?
    while now+timedelta(minutes=1) <= current_end:
        # Reading from file
        last_gps="none"
        last_hth="none"
        logger.info('---send2shore--- ready to send')
        with open("/dev/shm/GPS", "r") as file:
            last_gps=file.read()
        logger.info('---send2shore--- GPS : ' + last_gps)
        queue_send.put("/dev/shm/GPS")
        with open("/dev/shm/HTH", "r") as file:
            last_hth=file.read()
        logger.info('---send2shore--- HTH : ' + last_hth)
        queue_send.put("/dev/shm/HTH," + file_radiostatus)
        
        # send_location_and_health(last_gps,last_hth)
        logger.info('---send2shore--- good night')
        sleep(60-(datetime.utcnow()-now).total_seconds())
        logger.info('---send2shore--- good morning')
        now=datetime.utcnow()
    return True

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
    IMU_fs = config.getFloat('IMU', 'imuFreq') #TODO: NOTE this has been changed to 12 from 12.5 (actual) to obtain proper # of pts in processing
    
    #Compute number of bursts per hour
    num_bursts = int(60 / burst_int)
    
    #Generate lists of burst start and end times based on parameters from Config file
    start_times = [burst_time + i*burst_int for i in range(num_bursts)]
    end_times = [start_times[i] + burst_seconds/60 for i in range(num_bursts)]
    
    # RS start
    
    with open("/dev/shm/GPS", "w") as file:
        file.write("0,1,None")
    
    with open("/dev/shm/HTH", "w") as file:
        file.write("0,0,None")

    # Set-up logging based on config file parameters
    # logger = getLogger('microSWIFT')
    logDir = config.getString('Loggers', 'logDir')
    LOG_NAME = 'microSWIFT'
    LOG_LEVEL = config.getString('Loggers', 'DefaultLogLevel')
    LOG_FORMAT = ('%(asctime)s, %(name)s - [%(levelname)s] - %(message)s')
    LOG_FILE = (logDir  + LOG_NAME + '.log')
    # logger.setLevel(LOG_LEVEL)
    # logFileHandler = FileHandler(LOG_FILE)
    # logFileHandler.setLevel(LOG_LEVEL)
    # logFileHandler.setFormatter(Formatter(LOG_FORMAT))
    # logger.addHandler(logFileHandler)
    logqueue = Queue(-1)
    listener = Process(target=listener_process,
                       args=(logqueue, listener_configurer))
    listener.start()
    
    sendqueue = Queue()
    calcqueue = Queue()
    
    sp = Process(target=add_2_send_queue, args=(sendqueue, logqueue, worker_configurer))
    cp = Process(target=make_calculation, args=(calcqueue, sendqueue, logqueue, worker_configurer))
    sp.start()
    cp.start()
    
    worker_configurer(logqueue)
    logger = logging.getLogger(LOG_NAME)
    
    # RS end
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
    
    # Initialize the telemetry queue if it does not exist yet
    logger.info('Initializing Telemetry Queue')
    telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','a')
    telemetryQueue.close()
    
    # Report number of messages in current queue:
    telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
    logger.info(f'Number of messages in queue: {len(telemetryQueue.readlines())}')
    telemetryQueue.close
    
    initModem_atStart()
    
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
                
                RS_filename = dataDir + floatID + '_RS_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
                logger.info("radio status file name: {}".format(RS_filename))
                
                end_time = end_times[i]
                
                # Define next start time to enter into the sendSBD function:
                current_start = datetime.utcnow().replace(minute=start_times[i], second = 0, microsecond=0)
                current_end   = current_start + timedelta(seconds = burst_seconds)
                next_start = current_start + timedelta(minutes=burst_int)
                
                # Run recordGPS.py and recordIMU.py concurrently with asynchronous futures
                #TODO: uncomment
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Submit Futures 
                    recordGPS_future = executor.submit(recordGPS, end_times[i])
                    recordIMU_future = executor.submit(recordIMU, end_times[i])
                    recordHTH_future = executor.submit(recordHTH, current_end)
                    send2shor_future = executor.submit(send2shor, sendqueue, current_end, RS_filename)
                    
                    # get results from Futures
                    GPSdataFilename, gps_initialized = recordGPS_future.result()
                    IMUdataFilename, imu_initialized = recordIMU_future.result()
                    HTHdataFilename, hth_initialized = recordHTH_future.result()
                    send = send2shor_future.result()
                #TODO: uncomment 
                
                #exit out of loop once burst is finished
                recording_complete = True
                
                break
            
        # RS add one task to calc thread pool
            
        if recording_complete == True: 
            calcqueue.put([gps_initialized, imu_initialized, GPSdataFilename, IMUdataFilename])
                
                # if recording_complete == True: 
                #         ## --------------- Data Processing Section ---------------------------------
                #         # Time processing section
                #         logger.info('Starting Processing')
                #         begin_processing_time = datetime.now()
                        
                #         # #---TODO: delete
                #         # gps_initialized = True
                #         # imu_initialized = True
                #         # IMUdataFilename = '/home/pi/microSWIFT/data/microSWIFT057_IMU_17Aug2022_000146UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
                #         # GPSdataFilename = '/home/pi/microSWIFT/data/microSWIFT057_GPS_17Aug2022_000151UTC.dat'
                #         # #---TODO: delete
                                
                #         if gps_initialized and imu_initialized: #gps_initialized == True and imu_initialized == True:
                #                 logger.info('GPS and IMU initialized')

                #                 # Compute u, v and z from raw GPS data
                #                 logger.info(f'entering GPStoUVZ.py: {GPSdataFilename}')
                #                 GPS = GPStoUVZ(GPSdataFilename) # u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)
                #                 logger.info('GPStoUVZ executed')

                #                 # Process raw IMU data
                #                 logger.info(f'entering IMUtoXYZ.py: {IMUdataFilename}')
                #                 IMU = IMUtoXYZ(IMUdataFilename, IMU_fs) # ax, vx, px, ay, vy, py, az, vz, pz = IMUtoXYZ(IMUdataFilename,IMU_fs)
                #                 logger.info('IMUtoXYZ.py executed')

                #                 # Collate IMU and GPS onto a master time based on the IMU time
                #                 logger.info('entering collateIMUandGPS.py')
                #                 IMUcol,GPScol = collateIMUandGPS(IMU, GPS)
                #                 logger.info('collateIMUandGPS.py executed')

                #                 # UVZAwaves estimate; leave out first 120 seconds
                #                 zeroPts = int(np.round(120*IMU_fs)) 
                #                 logger.info(f'Zeroing out first 120 seconds ({zeroPts} pts)')
                #                 Hs, Tp, Dp, E, f, a1, b1, a2, b2, check  = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], IMU_fs)
                #                 logger.info('UVZAwaves.py executed, primary estimate (voltage==0)')

                #                 # GPSwaves estimate (secondary estimate)
                #                 Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], GPS_fs)
                #                 logger.info('GPSwaves.py executed, secondary estimate (voltage==1)')

                #                 # Unpack GPS variables for remaining code; use non-interpolated values
                #                 u=GPS['u']; v=GPS['v']; z=GPS['z']; lat=GPS['lat']; lon=GPS['lon']

                #         elif gps_initialized and not imu_initialized: 
                                
                #                 # Compute u, v and z from raw GPS data
                #                 u, v, z, lat, lon = GPStoUVZ(GPSdataFilename)

                #                 # Compute Wave Statistics from GPSwaves algorithm
                #                 Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = GPSwaves(u, v, z, GPS_fs)

                #         elif imu_initialized and not gps_initialized:
                #                 #TODO: Process IMU data
                #                 logger.info(f'GPS did not initialize but IMU did; would put IMU processing here but it is not yet functional... entering bad values ({badValue})')
                #                 u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=badValue, spectralLen=numCoef)

                #         else: # no IMU or GPS, enter bad values
                #                 logger.info(f'Neither GPS or IMU initialized - entering bad values ({badValue})')
                #                 u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=badValue, spectralLen=numCoef)

                #         # check lengths of spectral quanities:
                #         if len(E)!=numCoef or len(f)!=numCoef:
                #                 logger.info(f'WARNING: the length of E or f does not match the specified number of coefficients, {numCoef}; (len(E)={len(E)}, len(f)={len(f)})')

                #         # Compute mean velocities, elevation, lat and lon
                #         u_mean = np.nanmean(u)
                #         v_mean = np.nanmean(v)
                #         z_mean = np.nanmean(z) 
                
                #         #Get last reported position
                #         last_lat = _get_last(badValue, lat)
                #         last_lon = _get_last(badValue, lon)

                #         # Temperature and Voltage recordings - will be added in later versions
                #         temp = 0.0
                #         salinity = 0.0
                #         volt = 0   #NOTE: primary estimate
                #         volt_2 = 1 #NOTE: secondary estimate (GPS if IMU and GPS are both initialized)

                #         # End Timing of recording
                #         logger.info('Processing section took {}'.format(datetime.now() - begin_processing_time))
                                
                #         ## -------------- Telemetry Section ----------------------------------
                #         # Create TX file from processData.py output from combined wave products

                #         # Pack the data from the queue into the payload package
                #         logger.info('Creating TX file and packing payload data from primary estimate')
                #         TX_fname, payload_data = createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt)
                
                #         try: # GPSwaves estimate as secondary estimate
                #                 logger.info('Creating TX file and packing payload data from secondary estimate')
                #                 TX_fname_2, payload_data_2 = createTX(Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2, u_mean, v_mean, z_mean, last_lat, last_lon, temp, salinity, volt_2)
                #         except:
                #                 logger.info('No secondary estimate exists')

                #         # Read in the file names from the telemetry queue
                #         telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','r')
                #         payload_filenames = telemetryQueue.readlines()
                #         telemetryQueue.close()
                #         payload_filenames_stripped = []
                #         for line in payload_filenames:
                #                 payload_filenames_stripped.append(line.strip())

                #         # Append secondary estimate first (LIFO)
                #         try:
                #                 logger.info(f'Adding TX file {TX_fname_2} to the telemetry queue')
                #                 payload_filenames_stripped.append(TX_fname_2)
                #         except:
                #                 logger.info('No secondary estimate exists to add to queue')

                #         # Append the primary estimate
                #         logger.info(f'Adding TX file {TX_fname} to the telemetry queue')
                #         payload_filenames_stripped.append(TX_fname)
                        
                #         # Write all the filenames to the file including the newest file name
                #         telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
                #         for line in payload_filenames_stripped:
                #                 telemetryQueue.write(line)
                #                 telemetryQueue.write('\n')
                #         telemetryQueue.close()

                #         # Append the newest file name to the list
                #         payload_filenames_LIFO = list(np.flip(payload_filenames_stripped))
                #         logger.info('Number of Messages to send: {}'.format(len(payload_filenames_LIFO)))

                #         # Send as many messages from the queue as possible during the send window
                #         messages_sent = 0
                #         logger.info(payload_filenames_LIFO)
                #         for TX_file in payload_filenames_LIFO:
                #                 # Check if we are still in the send window 
                #                 if datetime.utcnow() < next_start:
                #                         logger.info(f'Opening TX file from payload list: {TX_file}')
                
                #                 # not as binary for time being !
                #                 # with open(TX_file, mode='rb') as file: # b is important -> binary
                #                 with open(TX_file, mode='r') as file: # b is important -> binary
                #                         payload_data = file.read()
                
                #                 # read in the sensor type from the binary payload file
                #                 # coded in ascii as csv
                #                 # payloadStartIdx = 0 # (no header) otherwise it is: = payload_data.index(b':') 
                #                 # sensor_type0 = ord(payload_data[payloadStartIdx+1:payloadStartIdx+2]) # sensor type is stored 1 byte after the header
                #                 sensor_type0 = int(payload_data.split(',')[1])
                #                 if sensor_type0 not in [50,51,52]:
                #                         logger.info(f'Failed to read sensor type properly; read sensor type as: {sensor_type0}')
                #                         logger.info(f'Trying to send as configured sensor type instead ({sensor_type})')
                #                         send_sensor_type = sensor_type
                #                 else:
                #                         send_sensor_type = sensor_type0
                
                #                 # send either payload type 50, 51, or 52
                #                 if send_sensor_type == 50:
                #                         successful_send = send_microSWIFT_50(payload_data, next_start)
                #                 elif send_sensor_type == 51:
                #                         successful_send = send_microSWIFT_51(payload_data, next_start)
                #                 elif send_sensor_type == 52:
                #                         successful_send = send_microSWIFT_52(payload_data, next_start)
                #                 else:
                #                         logger.info(f'Specified sensor type ({send_sensor_type}) is invalid or not currently supported')
                
                #                 # Index up the messages sent value if successful send is true
                #                 if successful_send == True:
                #                         messages_sent += 1
                #         else:
                #                 # Exit the for loop if outside of the end time 
                #                 break
                
                # # Log the send statistics
                # logger.info('Messages Sent: {}'.format(int(messages_sent)))
                # messages_remaining = int(len(payload_filenames_stripped)) - messages_sent
                # logger.info('Messages Remaining: {}'.format(messages_remaining))
                
                # # Remove the sent messages from the queue by writing the remaining lines to the file
                # if messages_sent > 0:
                #         del payload_filenames_stripped[-messages_sent:]
                # telemetryQueue = open('/home/pi/microSWIFT/SBD/telemetryQueue.txt','w')
                # for line in payload_filenames_stripped:
                #         telemetryQueue.write(line)
                #         telemetryQueue.write('\n')
                # telemetryQueue.close()
                
                # # Increment up the loop counter
            loop_count += 1
            wait_count = 0
                
                # # End Timing of entire Script
                # logger.info('microSWIFT.py took {}'.format(datetime.now() - begin_script_time))
                
        else:
            sleep(1)
            wait_count += 1
            # Print waiting to log every 5 iterations
            if wait_count % 10 == 0:
                logger.info('Waiting to enter record window')
                continue
                
    calcqueue.put("done")
