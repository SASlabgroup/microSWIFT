#! usr/bin/python3

#This program takes in the results from recordGPS.py and uses Jim Thomson's GPSwaves processing 
#algorithm to produce wave statistics (Hs, PP, Dir, frequency spectra, energy spectra, and directional
#moments a1 b1 a2 b2).  It also get mean temperature from recordTemp.py, a battery voltage, and the 
#current time and date. Inputs are 1x2048 arrays of u, v, z, lat, lon from recordGPS.py, sampling
#rate (Hz), burst duration (seconds), bad value (999), and payload type (int).  Output is a binary file 
#that can be sent over Iridium telemetry as a series of 340 byte messages according to the microSWIFT
#payload telemetry type 50 (default)

#imports
import sys, os
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time
import struct
from time import sleep

#create modele level logger
logger = getLogger('system_logger.'+__name__)   

#my imports
<<<<<<< HEAD
#import send_sbd
#try:
#    import GPSwavesC
#except Exception as e:
#    logger.info('error importing GPSwavesC')
#    logger.info(e)
=======
from config3 import Config
import send_sbd
import GPSwaves
try:
    import GPSwavesC
except Exception as e:
    logger.info('error importing GPSwavesC')
    logger.info(e)
>>>>>>> parent of 92735f3 (Merge branch 'GPSwaves-python' into payload-type-51)
    
#load config file and get parameters
configFilename = sys.argv[1] #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    logger.info ('Error loading config file: "%s"' % configFilename)
    sys.exit(1)

dataDir = config.getString('System', 'dataDir')
floatID = os.uname()[1]
sensor_type = config.getInt('System', 'sensorType')
badValue = config.getInt('System', 'badValue')
port = config.getInt('System', 'port')
payload_type = config.getInt('System', 'payloadType')
burst_seconds = config.getInt('System', 'burst_seconds')        
gps_freq = config.getInt('GPS', 'GPS_frequency') #currently not used, hardcoded at 4 Hz (see init_gps function)


#inputs are u,v,z arrays, last lat/lon, sampling rate (Hz), burst duration (secs), 
#bad value, payload type, sensor type, and port number from recordGPS.py
def main(u,v,z,lat,lon):

    #check the number of u,v,z samples matches expected and 1 Hz minimum
    pts_expected = gps_freq * burst_seconds
    if len(z) >= pts_expected and gps_freq >= 1:          
        try:
            #note gps_freq is assumed to be 4Hz
            logger.info('running GPSwaves processing...')
            wavestats = GPSwavesC.main_GPSwaves(len(z),u,v,z,gps_freq)
            #Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves.GPSwaves(u,v,z,gps_freq)
            logger.info('done')    
                    
        except Exception as e:
            logger.info('error running GPSwaves processing')
            logger.info(e)
            sys.exit(1)
           
    else:
        logger.info('insufficient samples or sampling rate for wave processing')  
        logger.info('samples expected = %d, samples received = %d' % (pts_expected, len(z)))
        sys.exit(1)
        
        
    if payload_type != 7:
        logger.info('invalid payload type: {}'.format(payload_type))
        logger.info('exiting')
        sys.exit(1)
        
<<<<<<< HEAD
    if sensor_type != 50:
        logger.info('invalid sensor type: {}'.format(sensor_type))
        logger.info('exiting')
        sys.exit(1)
        
    #unpack wave processing results        
    #Hs = wavestats[0]
    #Tp = wavestats[1]
    #Dp = wavestats[2]
    #E = np.squeeze(wavestats[3])
    #E = np.where(E>=18446744073709551615, 999.00000, E)
    #f = np.squeeze(wavestats[4])
    #f = np.where(f>=18446744073709551615, 999.00000, f)
    #a1 = np.squeeze(wavestats[5])
    #a1 = np.where(a1>=18446744073709551615, 999.00000, a1)
    #b1 = np.squeeze(wavestats[6])
    #b1 = np.where(b1>=18446744073709551615, 999.00000, b1)
    #a2 = np.squeeze(wavestats[7])
    #a2 = np.where(a2>=18446744073709551615, 999.00000, a2)
    #b2 = np.squeeze(wavestats[8])
    #b2 = np.where(b2>=18446744073709551615, 999.00000, b2)
=======
    unpack wave processing results        
    Hs = wavestats[0]
    Tp = wavestats[1]
    Dp = wavestats[2]
    E = np.squeeze(wavestats[3])
    E = np.where(E>=18446744073709551615, 999.00000, E)
    f = np.squeeze(wavestats[4])
    f = np.where(f>=18446744073709551615, 999.00000, f)
    a1 = np.squeeze(wavestats[5])
    a1 = np.where(a1>=18446744073709551615, 999.00000, a1)
    b1 = np.squeeze(wavestats[6])
    b1 = np.where(b1>=18446744073709551615, 999.00000, b1)
    a2 = np.squeeze(wavestats[7])
    a2 = np.where(a2>=18446744073709551615, 999.00000, a2)
    b2 = np.squeeze(wavestats[8])
    b2 = np.where(b2>=18446744073709551615, 999.00000, b2)
>>>>>>> parent of 92735f3 (Merge branch 'GPSwaves-python' into payload-type-51)
    checkdata = np.full(42,1)
    
    np.set_printoptions(formatter={'float_kind':'{:.5f}'.format})
    np.set_printoptions(formatter={'float_kind':'{:.2e}'.format})
    #calculate mean value of good points only
    uMean = _getuvzMean(badValue,u)
    vMean = _getuvzMean(badValue,v)
    zMean = _getuvzMean(badValue,z)
    #get last good lattitude and longitude value from burst
    lat = _get_last(badValue, lat)
    lon = _get_last(badValue, lon)
    
    #file name for telemetry file (e.g. '/home/pi/microSWIFT/data/microSWIFT001_TX_01Jan2021_080000UTC.dat')
    now=datetime.utcnow()
    telem_file = dataDir + floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(now)
    logger.info('telemetry file = %s' % telem_file)

    with open(telem_file, 'wb') as file:
        logger.info('create telemetry file: {}'.format(telem_file))
        
        
        #payload size in bytes: 16 4-byte floats, 7 arrays of 42 4-byte floats, three 1-byte ints, and one 2-byte int   
        #payload_size = (16 + 7*42) * 4 + 5
    
        Hs = round(Hs,6)
        Tp = round(Tp,6)
        Dp = round(Dp,6)
        lat = round(lat,6)
        lon = round(lon,6)
        uMean = round(uMean,6)
        vMean = round(vMean,6)
        zMean = round(zMean,6)
        
        #ignore temp and voltage for now
        temp = 0.0
        volt = 0.0
        
        logger.info('Hs: {0} Tp: {1} Dp: {2} lat: {3} lon: {4} temp: {5} volt: {6} uMean: {7} vMean: {8} zMean: {9}'.format(
            Hs, Tp, Dp, lat, lon, temp, volt, uMean, vMean, zMean))

        if sensor_type == 50:

        #create formatted struct with all payload data
            now=datetime.now()
            payload_size = struct.calcsize('<sbbhfff42f42f42f42f42f42f42ffffffffiiiiii')
            payload_data = (struct.pack('<sbbhfff', str(payload_type).encode(),sensor_type,port, payload_size,Hs,Tp,Dp) + 
                            struct.pack('<42f', *E) +
                            struct.pack('<42f', *f) +
                            struct.pack('<42f', *a1) +
                            struct.pack('<42f', *b1) +
                            struct.pack('<42f', *a2) +
                            struct.pack('<42f', *b2) +
                            struct.pack('<42f', *checkdata) +
                            struct.pack('<f', lat) +
                            struct.pack('<f', lon) +
                            struct.pack('<f', temp) +
                            struct.pack('<f', volt) +
                            struct.pack('<f', uMean) +
                            struct.pack('<f', vMean) +
                            struct.pack('<f', zMean) +
                            struct.pack('<i', int(now.year)) +
                            struct.pack('<i', int(now.month)) +
                            struct.pack('<i', int(now.day)) +
                            struct.pack('<i', int(now.hour)) +
                            struct.pack('<i', int(now.minute)) +
                            struct.pack('<i', int(now.second)))
            
            #run send_sbd script to send telemetry file
            send_sbd.send_microSWIFT_50(payload_data)
            logger.info('data processing complete')
        
        elif sensor_type == 51:
            
            #compute fmin fmax and fstep
            fmin = np.min(f)
            fmax = np.max(f)
            fstep = (fmax - fmin)/41
            
            now=datetime.now()
            payload_size = struct.calcsize('<sbbhfff42fffffffffffiiiiii')
            payload_data = (struct.pack('<sbbhfff', str(payload_type).encode(),sensor_type,port, payload_size,Hs,Tp,Dp) + 
                            struct.pack('<42f', *E) +
                            struct.pack('<f', fmin) +
                            struct.pack('<f', fmax) +
                            struct.pack('<f', fstep) +
                            struct.pack('<f', lat) +
                            struct.pack('<f', lon) +
                            struct.pack('<f', temp) +
                            struct.pack('<f', volt) +
                            struct.pack('<f', uMean) +
                            struct.pack('<f', vMean) +
                            struct.pack('<f', zMean) +
                            struct.pack('<i', int(now.year)) +
                            struct.pack('<i', int(now.month)) +
                            struct.pack('<i', int(now.day)) +
                            struct.pack('<i', int(now.hour)) +
                            struct.pack('<i', int(now.minute)) +
                            struct.pack('<i', int(now.second)))
            
            #run send_sbd script to send telemetry file
            send_sbd.send_microSWIFT_51(payload_data)
            logger.info('data processing complete')
        
        else: 
            logger.info('invalid sensor type: {}'.format(sensor_type))
            logger.info('exiting')
            sys.exit(1)
        
        
        
        logger.info('writing data to file')
        file.write(payload_data)
        logger.info('done')
        file.flush()
        
    return payload_data

def _getuvzMean(badValue, pts):
    mean = badValue     #set values to 999 initially and fill if valid values
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

