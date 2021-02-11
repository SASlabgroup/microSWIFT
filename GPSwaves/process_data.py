#! usr/bin/python3

#This program takes in the results from recordGPS.py and uses Jim Thomson's GPSwaves processing 
#algorithm to produce wave statistics (Hs, PP, Dir, frequency spectra, energy spectra, and directional
#moments a1 b1 a2 b2).  It also get mean temperature from recordTemp.py, a battery voltage, and the 
#current time and date. Inputs are 1x2048 arrays of u, v, z, lat, lon from recordGPS.py, sampling
#rate (Hz), burst duration (seconds), bad value (999), and payload type (int).  Output is a binary file 
#that can be sent over Iridium telemetry as a series of 340 byte messages according to the microSWIFT
#payload telemetry type 50 (default)

#imports
import sys
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time
import struct
from time import sleep

#my imports
import send_sbd
try:
    import GPSwavesC
except Exception as e:
    logger.info('error importing GPSwavesC')
    logger.info(e)
    
#inputs are u,v,z arrays, last lat/lon, sampling rate (Hz), and burst duration (secs) from recordGPS.py
def main(u,v,z,lat,lon,fs=4,burst_seconds=512,badValue,payloadType=50):

    #check the number of u,v,z samples matches expected and 1 Hz minimum
    pts_expected
    if len(z) >= pts_expected and fs >= 1:          
        try:
            #note gps_freq is assumed to be 4Hz
            wavestats = GPSwavesC.main_GPSwaves(len(z),u,v,z,fs)    
                    
        except Exception as e:
            logger.info('error running GPSwavesC processing')
            logger.info(e)
            sys.exit(1)
           
    else:
        logger.info('insufficient samples or sampling rate for wave processing')  
        logger.info('samples expected = %d, samples received = %d' % (pts_expected, len(z)))
        sys.exit(1)
        
    #unpack wave processing results        
    hs = wavestats[0]
    pp = wavestats[1]
    dir = wavestats[2]
    WaveSpectra_Energy = np.squeeze(wavestats[3])
    WaveSpectra_Energy = np.where(WaveSpectra_Energy>=18446744073709551615, 999.00000, WaveSpectra_Energy)
    WaveSpectra_Freq = np.squeeze(wavestats[4])
    WaveSpectra_Freq = np.where(WaveSpectra_Freq>=18446744073709551615, 999.00000, WaveSpectra_Freq)
    WaveSpectra_a1 = np.squeeze(wavestats[5])
    WaveSpectra_a1 = np.where(WaveSpectra_a1>=18446744073709551615, 999.00000, WaveSpectra_a1)
    WaveSpectra_b1 = np.squeeze(wavestats[6])
    WaveSpectra_b1 = np.where(WaveSpectra_b1>=18446744073709551615, 999.00000, WaveSpectra_b1)
    WaveSpectra_a2 = np.squeeze(wavestats[7])
    WaveSpectra_a2 = np.where(WaveSpectra_a2>=18446744073709551615, 999.00000, WaveSpectra_a2)
    WaveSpectra_b2 = np.squeeze(wavestats[8])
    WaveSpectra_b2 = np.where(WaveSpectra_b2>=18446744073709551615, 999.00000, WaveSpectra_b2)
    checkdata = np.full(numCoef,1)
    
    np.set_printoptions(formatter={'float_kind':'{:.5f}'.format})
    np.set_printoptions(formatter={'float_kind':'{:.2e}'.format})
    #calculate mean value of good points only
    uMean = _getuvzMean(badValue,u)
    vMean = _getuvzMean(badValue,v)
    zMean = _getuvzMean(badValue,z)
    #get last good lattitude and longitude value from burst
    lat = _get_last(lat)
    lon = _get_last(lon)
    
    #file name for telemetry file (e.g. '/home/pi/microSWIFT/data/microSWIFT001_TX_01Jan2021_080000UTC.dat')
    now=datetime.utcnow()
    telem_file = dataDir+'microSWIFT'+floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(now)
    logger.info('telemetry file = %s' % telem_file)

    with open(telem_file, 'wb') as f:

        if payloadType == 50:
            payloadSize = (16 + 7*42)*4
            logger.info('payload type = %d' % payloadType)
            logger.info('payload size = %d' %payloadSize)
        elif payloadType == 7:
            payloadSize =  (5 + 7*42)*4
            logger.info('payload type = %d' % payloadType)
            logger.info('payloadSize: %d' % (payloadSize))
        else:
            logger.info('invalid payload type %d' % payloadType)
            sys.exit(1)
    
        hs = round(hs,6)
        pp = round(pp,6)
        dir = round(dir,6)
        lat = round(lat,6)
        lon = round(lon,6)
        uMean = round(uMean,6)
        vMean = round(vMean,6)
        zMean = round(zMean,6)
        
        #ignore temp and voltage for now
        temp = 0.0
        volt = 0.0
        
        f.write(struct.pack('<sbbhfff', str(payloadVersion),payloadType,Port, payloadSize,hs,pp,dir))
    
        f.write(struct.pack('<42f', *WaveSpectra_Energy))
        f.write(struct.pack('<42f', *WaveSpectra_Freq))
        f.write(struct.pack('<42f', *WaveSpectra_a1))
        f.write(struct.pack('<42f', *WaveSpectra_b1))
        f.write(struct.pack('<42f', *WaveSpectra_a2))
        f.write(struct.pack('<42f', *WaveSpectra_b2))
        f.write(struct.pack('<42f', *checkdata))
        f.write(struct.pack('<f', lat))
        f.write(struct.pack('<f', lon))
        f.write(struct.pack('<f', temp))
        f.write(struct.pack('<f', volt))
        f.write(struct.pack('<f', uMean))
        f.write(struct.pack('<f', vMean))
        f.write(struct.pack('<f', zMean))
        f.write(struct.pack('<i', int(now.year)))
        f.write(struct.pack('<i', int(now.month)))
        f.write(struct.pack('<i', int(now.day)))
        f.write(struct.pack('<i', int(now.hour)))
        f.write(struct.pack('<i', int(now.minute)))
        f.write(struct.pack('<i', int(now.second)))
        f.flush()
    
    #run send_sbd script to send telemetry file
    send_sbd(telem_file)    
    
    return telem_file

def _getuvzMean(badValue, pts):
    mean = badValue     #set values to 999 initially and fill if valid values
    index = np.where(pts != badValue)[0] #get index of non bad values
    pts=pts[index] #take subset of data without bad values in it
    
    if(len(index) > 0):
        mean = np.mean(pts)
 
    return mean

def _get_last(badValue,a):
    for i in range(1, len(a)): #loop over entire lat/lon array
        if a[-i] != badValue: #count back from last point looking for a real position
            return a[-i]
        
    return [a-i] #returns badValue if no real position exists
    
if __name__== '__main__':
    
    telem_file = main()
    
    
    
    
    

