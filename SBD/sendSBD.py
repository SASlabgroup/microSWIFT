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
import logging
import serial

# Telemetry test functions
def createTX(Hs, Tp, Dp, E, f, u_mean, v_mean, z_mean, lat, lon,  temp, volt, configFilename):
    #load config file and get parameters
    config = Config() # Create object and load file
    ok = config.loadFile( configFilename )
    dataDir = config.getString('System', 'dataDir')
    floatID = os.uname()[1]

    # Create the TX file named for the current time
    logger = getLogger('system_logger.'+__name__)   
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
        
        # System configurations
        sensor_type = config.getInt('System', 'sensorType')
        payload_type = config.getInt('System', 'payloadType')
        port = config.getInt('System', 'port')
        
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

    print('TX file created with the variables Hs, Tp, Dp, E, fmin, fmax, fstep, lat, lon, temp, volt, umean, vmean, zmean and date')
    print(TX_fname)
    return TX_fname, payload_data

def checkTX(TX_fname):
    with open(TX_fname, mode='rb') as file: # b is important -> binary
        fileContent = file.read()
    data = struct.unpack('<sbbhfff42fffffffffffiiiiii', fileContent)
    print('data = ', data)

def getResponse(ser,command, response='bad'):
    # logger = getLogger('system_logger.'+__name__)  
    sbdlogger = logging.getLogger('send_sbd.py')
    sbdlogger.setLevel(logging.INFO)

    ser.flushInput()
    command=(command+'\r').encode()
    ser.write(command)
    sleep(1)
    try:
        while ser.in_waiting > 0:
            r=ser.readline().decode().strip('\r\n')
            if response in r:
                sbdlogger.info('response = {}'.format(r))
                print('response = {}'.format(r))
                return True
            elif 'ERROR' in response:
                sbdlogger.info('response = ERROR')
                print('response = ERROR')
                return False
    except serial.SerialException as e:
        sbdlogger.info('error: {}'.format(e))
        print('error: {}'.format(e))
        return False

def initModem():
    # Iridium parameters - fixed for now
    modemPort = '/dev/ttyUSB0'
    modemBaud = 19200
    modemGPIO =  16 
    timeout=60

    # Turn on the pin to power on the modem
    try:
        GPIO.setup(modemGPIO, GPIO.OUT)
        GPIO.output(modemGPIO,GPIO.HIGH) #power on GPIO enable pin
        print('modem powered on')
        sleep(3)
    except Exception as e:
        print('error powering on modem')
        print(e)
        
    #open serial port
    print('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    try:
        ser=serial.Serial(modemPort,modemBaud,timeout=timeout)
        print('serial port opened successfully')
    except serial.SerialException as e:
        print('unable to open serial port: {}'.format(e))
        return ser, False
    
    # If the try statement passed
    return ser, True

def sendSBD(ser, payload_data):
    import time
    from adafruit_rockblock import RockBlock

    # Setup instance of RockBlock 
    rockblock = RockBlock(ser)

    # Send payload data through the RockBlock
    rockblock.data_out = payload_data
    print('Talking to Satellite')
    retry = 0
    max_retry = 10
    sent_status_val = 4 # any returned status value less than this means the message sent successfully.
    status = rockblock.satellite_transfer()
    while status[0] > sent_status_val and retry < max_retry:
        time.sleep(10)
        status = rockblock.satellite_transfer()
        print('Retry number = ', retry)
        print('status = ', status)
        retry += 1
    
    if status[0] <= 4:
        # Final print statement that it sent
        print('Sent SBD successfully')
    else:
        print('Could not send SBD')
