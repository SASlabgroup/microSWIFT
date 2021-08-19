## Send Short Burst Data (SBD) Functions 
'''
author: @edwinrainville
All functions are heavily adapted from Viviano Castillo and Alex de Klerk.

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
    print(type(data))

def getResponse(ser,command, response='OK'):
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
                return True
            elif 'ERROR' in response:
                sbdlogger.info('response = ERROR')
                return False
    except serial.SerialException as e:
        sbdlogger.info('error: {}'.format(e))
        return False

def initModem():
    # Iridium parameters - fixed for now
    modemPort = '/dev/ttyUSB0' #config.getString('Iridium', 'port')
    modemBaud = 19200 #config.getInt('Iridium', 'baud')
    modemGPIO =  16 #config.getInt('Iridium', 'modemGPIO')
    formatType = 10 #config.getInt('Iridium', 'formatType')
    call_interval = 60 #config.getInt('Iridium', 'call_interval')
    call_time = 10 #config.getInt('Iridium', 'call_time')
    timeout=60 #some commands can take a long time to complete

    # logger = getLogger('system_logger.'+__name__)  
    sbdlogger = logging.getLogger('send_sbd.py')
    sbdlogger.setLevel(logging.INFO)

    try:
        GPIO.setup(modemGPIO, GPIO.OUT)
        GPIO.output(modemGPIO,GPIO.HIGH) #power on GPIO enable pin
        sbdlogger.info('power on modem...')
        print('modem powered on')
        sleep(3)
        sbdlogger.info('done')
    except Exception as e:
        sbdlogger.info('error powering on modem')
        print('error powering on modem')
        sbdlogger.info(e)
        print(e)
        
    #open serial port
    sbdlogger.info('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    print('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    try:
        ser=serial.Serial(modemPort,modemBaud,timeout=timeout)
        sbdlogger.info('done')
    except serial.SerialException as e:
        sbdlogger.info('unable to open serial port: {}'.format(e))
        print('unable to open serial port: {}'.format(e))
        return ser, False
        sys.exit(1)

    sbdlogger.info('command = AT')
    if get_response(ser,'AT'): #send AT command
        sbdlogger.info('command = AT&F')
        if get_response(ser,'AT&F'): #set default parameters with AT&F command 
            sbdlogger.info('command = AT&K=0')  
            if get_response(ser,'AT&K=0'): #important, disable flow control
                sbdlogger.info('modem initialized')
                print('modem initialized')
                return ser, True
    else:
        return ser, False

def sendSBD(ser, payload_data):
    ser.write(payload_data)
    # Final print statement that it sent
    print('Sent SBD successfully')