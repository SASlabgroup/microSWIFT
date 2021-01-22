#! usr/bin/python3

#imports
import serial, sys, os
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time
import RPi.GPIO as GPIO
import pynmea2
import struct
import time
from time import sleep

#my imports
import GPSwavesC


#inputs are u,v,z arrays, last lat/lon, sampling rate (Hz), and burst duration (secs) from recordGPS.py
def wavestats(u,v,z,lat,lon,fs=4,busrt_seconds=512):

    #check for # of u,v,z samples and sampling rate
    if len(z) >= fs*burst_seconds and fs >= 1:          
        try:
            #note gps_freq is assumed to be 4Hz
            wave_stats = GPSwavesC.main_GPSwaves(len(z),u,v,z,fs)    
                    
        except Exception as e:
            logger.info(e)
            logger.info('error running GPSwavesC processing')
    else:
        logger.info('insufficient samples for wave processing')  
        logger.info('samples expected = %d, samples received = %d' % (minpts))  
        
    #unpack wave processing results        
    SigwaveHeight = GPS_waves_results[0]
    Peakwave_Period = GPS_waves_results[1]
    Peakwave_dirT = GPS_waves_results[2]
    WaveSpectra_Energy = np.squeeze(GPS_waves_results[3])
    WaveSpectra_Energy = np.where(WaveSpectra_Energy>=18446744073709551615, 999.00000, WaveSpectra_Energy)
    WaveSpectra_Freq = np.squeeze(GPS_waves_results[4])
    WaveSpectra_Freq = np.where(WaveSpectra_Freq>=18446744073709551615, 999.00000, WaveSpectra_Freq)
    WaveSpectra_a1 = np.squeeze(GPS_waves_results[5])
    WaveSpectra_a1 = np.where(WaveSpectra_a1>=18446744073709551615, 999.00000, WaveSpectra_a1)
    WaveSpectra_b1 = np.squeeze(GPS_waves_results[6])
    WaveSpectra_b1 = np.where(WaveSpectra_b1>=18446744073709551615, 999.00000, WaveSpectra_b1)
    WaveSpectra_a2 = np.squeeze(GPS_waves_results[7])
    WaveSpectra_a2 = np.where(WaveSpectra_a2>=18446744073709551615, 999.00000, WaveSpectra_a2)
    WaveSpectra_b2 = np.squeeze(GPS_waves_results[8])
    WaveSpectra_b2 = np.where(WaveSpectra_b2>=18446744073709551615, 999.00000, WaveSpectra_b2)
    checkdata = np.full(numCoef,1)
    
    np.set_printoptions(formatter={'float_kind':'{:.5f}'.format})
    np.set_printoptions(formatter={'float_kind':'{:.2e}'.format})
    
#########################################
    uMean = getuvzMean(badValue,u)
    vMean = getuvzMean(badValue,v)
    zMean = getuvzMean(badValue,z)
#########################################    
    fbinary = dataDir+'microSWIFT'+floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
    logger.info('telemetry file = %s' % fbinary)

    if payLoadType == 50:
        payLoadSize = (16 + 7*42)*4
        logger.info('payload type = %d' % payLoadType)
        logger
    else:
        payLoadSize =  (5 + 7*42)*4
        #eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, payLoadType))
        #eventLog.info('[%.3f] - payLoadSize: %d' % (elapsedTime, payLoadSize))

    try:
        fbinary = open(fbinary, 'wb')
        
    except:
        logger.info ('[%.3f] - To write binary file is already open' % elapsedTime)
    
    SigwaveHeight = round(SigwaveHeight,6)
    Peakwave_Period = round(Peakwave_Period,6)
    Peakwave_dirT = round(Peakwave_dirT,6)
    
    lat[0] = round(lat[0],6)
    lon[0] = round(lon[0],6)
    uMean= round(uMean,6)
    vMean= round(vMean,6)
    zMean= round(zMean,6)
    
    fbinary.write(struct.pack('<sbbhfff', 
                             str(payloadVersion),payLoadType,Port,
                             payLoadSize,SigwaveHeight,Peakwave_Period,Peakwave_dirT))

    fbinary.write(struct.pack('<42f', *WaveSpectra_Energy))
    fbinary.write(struct.pack('<42f', *WaveSpectra_Freq))
    fbinary.write(struct.pack('<42f', *WaveSpectra_a1))
    fbinary.write(struct.pack('<42f', *WaveSpectra_b1))
    fbinary.write(struct.pack('<42f', *WaveSpectra_a2))
    fbinary.write(struct.pack('<42f', *WaveSpectra_b2))
    fbinary.write(struct.pack('<42f', *checkdata))
    fbinary.write(struct.pack('<f', lat[0]))
    fbinary.write(struct.pack('<f', lon[0]))
    fbinary.write(struct.pack('<f', temp))
    fbinary.write(struct.pack('<f', volt))
    fbinary.write(struct.pack('<f', uMean))
    fbinary.write(struct.pack('<f', vMean))
    fbinary.write(struct.pack('<f', zMean))
    fbinary.write(struct.pack('<i', int(now.year)))
    fbinary.write(struct.pack('<i', int(now.month)))
    fbinary.write(struct.pack('<i', int(now.day)))
    fbinary.write(struct.pack('<i', int(now.hour)))
    fbinary.write(struct.pack('<i', int(now.minute)))
    fbinary.write(struct.pack('<i', int(now.second)))
    fbinary.flush()
    fbinary.close()
sleep(0.5)

def getuvzMean(badValue,resultType):
    mean = badValue     #set values to 999 initially and fill if valid values  
    nan = float('nan')  #account for nan values
    idgood = np.where(resultType != badValue)[0]
    idgoodnan = np.where(resultType != nan)[0]
            
    if(len(idgood) > 0):
        mean = np.mean(resultType[idgood])
    elif(len(idgoodnan) > 0):
        mean = np.mean(resultType[idgoodnan])
        
    return mean
