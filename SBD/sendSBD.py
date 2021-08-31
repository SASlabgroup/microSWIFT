## Send Short Burst Data (SBD) Functions 
'''
author: @edwinrainville
All functions are heavily adapted from Viviana Castillo and Alex de Klerk.

'''

# Import Statements
from datetime import datetime
import struct
from logging import *
import sys, os
from utils.config3 import Config
import numpy as np
import RPi.GPIO as GPIO
from time import sleep
from logging import getLogger
import serial

#Define Config file name and load file
configFilename = r'utils/Config.dat'
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    print("Error loading config file")
    sys.exit(1)

# Create the TX file named for the current time
logger = getLogger('microSWIFT.'+__name__)  


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
    
call_duration = burst_int*60-burst_seconds #time between burst end and burst start to make a call

# Iridium parameters
modemPort = config.getString('Iridium', 'port')
modemBaud = config.getInt('Iridium', 'baud')
modemGPIO = config.getInt('Iridium', 'modemGPIO')
timeout = config.getInt('Iridium', 'timeout')

#arbitrary message counter
id = 0


# Telemetry test functions
def createTX(Hs, Tp, Dp, E, f, u_mean, v_mean, z_mean, lat, lon,  temp, volt):

    #Create file name
    now=datetime.utcnow()
    TX_fname = dataDir + floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(now)
    logger.info('telemetry file = %s' %TX_fname)

    # Open the TX file and start to write to it
    with open(TX_fname, 'wb') as file:
      
        logger.info('create telemetry file: {}'.format(TX_fname))
        
        #payload size in bytes: 16 4-byte floats, 7 arrays of 42 4-byte floats, three 1-byte ints, and one 2-byte int   
        #payload_size = (16 + 7*42) * 4 + 5
        # Round the values each to 6 decimal places
        Hs = round(Hs,6)
        Tp = round(Tp,6)
        Dp = round(Dp,6)
        lat = round(lat,6)
        lon = round(lon,6)
        uMean = round(u_mean,6)
        vMean = round(v_mean,6)
        zMean = round(z_mean,6)
        
        # Log the data that will be sent    
        logger.info('Hs: {0} Tp: {1} Dp: {2} lat: {3} lon: {4} temp: {5} volt: {6} uMean: {7} vMean: {8} zMean: {9}'.format(
            Hs, Tp, Dp, lat, lon, temp, volt, uMean, vMean, zMean))

        # Compute fmin fmax and fstep
        fmin = np.min(f)
        fmax = np.max(f)
        fstep = (fmax - fmin)/f.shape
        
        # Build Structure of binary bits 
        now=datetime.now()
        payload_size = struct.calcsize('<sbbhfff42fffffffffffiiiiii')
        payload_data = (struct.pack('<s', str(payload_type).encode()) +
                        struct.pack('<b', sensor_type) +
                        struct.pack('<b', port) +
                        struct.pack('<h', payload_size) +
                        struct.pack('<f', Hs) +
                        struct.pack('<f', Tp) + 
                        struct.pack('<f', Dp) +
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

        # Write the binary packed data to a file 
        logger.info('writing data to file')
        file.write(payload_data)
        logger.info('done')
        file.flush()

    logger.info('TX file created with the variables Hs, Tp, Dp, E, fmin, fmax, fstep, lat, lon, temp, volt, umean, vmean, zmean and date')
    return TX_fname, payload_data

def checkTX(TX_fname):

    with open(TX_fname, mode='rb') as file: # b is important -> binary
        fileContent = file.read()
    data = struct.unpack('<sbbhfff42fffffffffffiiiiii', fileContent)
    logger.info('data = ', data)

def getResponse(ser,command, response='bad'):

    ser.flushInput()
    command=(command+'\r').encode()
    ser.write(command)
    sleep(1)
    try:
        while ser.in_waiting > 0:
            r=ser.readline().decode().strip('\r\n')
            if response in r:
                sbdlogger.info('response = {}'.format(r))
                logger.info('response = {}'.format(r))
                return True
            elif 'ERROR' in response:
                sbdlogger.info('response = ERROR')
                logger.info('response = ERROR')
                return False
    except serial.SerialException as e:
        sbdlogger.info('error: {}'.format(e))
        logger.info('error: {}'.format(e))
        return False

def initModem():

    # Turn on the pin to power on the modem
    try:
        GPIO.setup(modemGPIO, GPIO.OUT)
        GPIO.output(modemGPIO,GPIO.HIGH) #power on GPIO enable pin
        logger.info('modem powered on')
        sleep(3)
        sbdlogger.info('done')
    except Exception as e:
        logger.info('error powering on modem')
        logger.info(e)
        
    #open serial port
    logger.info('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    try:
        ser=serial.Serial(modemPort,modemBaud,timeout=timeout)
        logger.info('serial port opened successfully')
    except serial.SerialException as e:
        logger.info('unable to open serial port: {}'.format(e))
        return ser, False
    except Exception as e:
        logger.info('unable to open serial port')
        logger.info(e)
        return ser, False
    
    # If the try statement passed
    return ser, True

def sendSBD(ser, payload_data, next_start):
    import time
    from adafruit_rockblock import RockBlock
    
    # Setup loging 
    logger = getLogger('microSWIFT.'+__name__) 

    # Setup instance of RockBlock 
    rockblock = RockBlock(ser)

    # Send payload data through the RockBlock
    rockblock.data_out = payload_data
    logger.info('Talking to Satellite')
    retry = 0
    sent_status_val = 0 # any returned status value less than this means the message sent successfully.
    status = rockblock.satellite_transfer()
    now = datetime.utcnow().minute + datetime.utcnow().second/60
    while status[0] > sent_status_val and now < next_start:
        time.sleep(10)
        status = rockblock.satellite_transfer()
        logger.info('Retry number = {}'.format(retry))
        logger.info('status = {}'.format(status))
        now = datetime.utcnow().minute + datetime.utcnow().second/60
        retry += 1
    
    if status[0] == 0:
        # Final print statement that it sent
        logger.info('Sent SBD successfully')
    else:
        logger.info('Could not send SBD')
