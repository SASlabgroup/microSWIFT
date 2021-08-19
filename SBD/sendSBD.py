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

def get_response(ser,command, response='OK'):
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
        GPIO.output(modemGPIO,GPIO.HIGH) #power on GPIO enable pin
        sbdlogger.info('power on modem...')
        print('modem powered on')
        sleep(3)
        sbdlogger.info('done')
    except Exception as e:
        sbdlogger.info('error powering on modem')
        print('error powering on modem')
        sbdlogger.info(e)
        
    #open serial port
    sbdlogger.info('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    print('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    try:
        ser=serial.Serial(modemPort,modemBaud,timeout=timeout)
        sbdlogger.info('done')
    except serial.SerialException as e:
        sbdlogger.info('unable to open serial port: {}'.format(e))
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

def sendSBD(payload_data, configFilename):
    # Load in Configuration data
    config = Config() # Create object and load file
    ok = config.loadFile( configFilename )        
    burst_seconds = config.getInt('System', 'burst_seconds')   
    burst_time = config.getInt('System', 'burst_time')
    burst_int = config.getInt('System', 'burst_interval')
    call_int = config.getInt('Iridium', 'call_interval')
    call_time = config.getInt('Iridium', 'call_time')
        
    call_duration = burst_int*60-burst_seconds #time between burst end and burst start to make a call

    #Iridium parameters - fixed for now
    modemPort = '/dev/ttyUSB0' #config.getString('Iridium', 'port')
    modemBaud = 19200 #config.getInt('Iridium', 'baud')
    modemGPIO =  16 #config.getInt('Iridium', 'modemGPIO')
    formatType = 10 #config.getInt('Iridium', 'formatType')
    call_interval = 60 #config.getInt('Iridium', 'call_interval')
    call_time = 10 #config.getInt('Iridium', 'call_time')
    timeout=60 #some commands can take a long time to complete

    id = 0 #arbitrary message counter

    #set up GPIO pins for modem control
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(modemGPIO,GPIO.OUT)

    #logger = getLogger('system_logger.'+__name__)  
    sbdlogger = logging.getLogger('send_sbd.py')
    sbdlogger.setLevel(logging.INFO)

    #set up logging to file or sdout:
    LOG_FILE = ('/home/pi/microSWIFT/logs' + '/' + 'send_sbd' + '_' + datetime.strftime(datetime.now(), '%d%b%Y') + '.log')
    sbdFileHandler = FileHandler(LOG_FILE)
    sbdFileHandler.setLevel(logging.INFO)
    sbdFileHandler.setFormatter(Formatter('%(asctime)s, %(name)s - [%(levelname)s] - %(message)s'))
    sbdlogger.addHandler(sbdFileHandler)

    #Get signal quality using AT+CSQF command (see AT command reference).
    #Returns signal quality, default range is 0-5. Returns -1 for an error or no response
    #Example modem output: AT+CSQF +CSQF:0 OK    
    def sig_qual(ser, command='AT+CSQ'):
        ser.flushInput()
        ser.write((command+'\r').encode())
        sbdlogger.info('command = {} '.format(command))
        r=ser.read(23).decode()
        if 'CSQ:' in r:
            response=r[9:15]
            qual = r[14]
            sbdlogger.info('response = {}'.format(response))
            return int(qual) #return signal quality (0-5)
        elif 'ERROR' in r:
            sbdlogger.info('Response = ERROR')
            return -1
        elif r == '':
            sbdlogger.info('No response from modem')
            return -1
        else:
            sbdlogger.info('Unexpected response: {}'.format(r))  
            return -1

    # send binary message to modem buffer and transmits
    # returns true if trasmit command is sent, but does not mean a successful transmission
    # checksum is least significant 2 bytes of sum of message, with higher order byte sent first
    # returns false if anything goes wrong
    def transmit_bin(ser,msg):
        bytelen=len(msg)
        sbdlogger.info('payload bytes = {}'.format(bytelen))
                        
        #check signal quality and attempt to send until timeout reached
                
        try:
            sbdlogger.info('Command = AT+SBDWB')
            ser.flushInput()
            ser.write(('AT+SBDWB='+str(bytelen)+'\r').encode()) #command to write bytes, followed by number of bytes to write
            sleep(0.25)
        except serial.SerialException as e:
            sbdlogger.info('Serial error: {}'.format(e))
            return False
        except Exception as e:
            sbdlogger.info('Error: {}'.format(e))
            return False
        
        r = ser.read_until(b'READY') #block until READY message is received
        if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
            sbdlogger.info('response = READY')
            sbdlogger.info('passing message to modem buffer')
            ser.flushInput()
            ser.write(msg) #pass bytes to modem
            sleep(0.25)
            
            #The checksum is the least significant 2-bytes of the summation of the entire SBD message. 
            #The high order byte must be sent first. 
            checksum=sum(msg) #calculate checksum value
            byte1 = (checksum >> 8).to_bytes(1,'big') #bitwise operation shift 8 bits right to get firt byte of checksum and convert to bytes
            byte2 = (checksum & 0xFF).to_bytes(1,'big')#bitwise operation to get second byte of checksum, convet to bytes
            sbdlogger.info('passing checksum to modem buffer')
            ser.write(byte1) #first byte of 2-byte checksum 
            sleep(0.25)
            ser.write(byte2) #second byte of checksum
            sleep(0.25)
            
            r=ser.read(3).decode() #read response to get result code from SBDWB command (0-4)
            try:
                r=r[2] #result code of expected response
                sbdlogger.info('response = {}'.format(r))
                
                if r == '0': #response of zero = successful write, ready to send
                    sbdlogger.info('command = AT+SBDIX')
                    ser.flushInput()
                    ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                    sleep(5)
                    ser.read(11)
                    r=ser.readline().decode().strip('\r\n')  #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                    sbdlogger.info('response = {}'.format(r))
                    
                    if '+SBDIX: ' in r:
                        r=r.strip('+SBDIX:').split(', ')
                        #interpret response and check MO status code (0=success)
                        if int(r[0]) == 0:
                            sbdlogger.info('Message send success')
                            return True
                        else:
                            sbdlogger.info('Message send failure, status code = {}'.format(r[0]))
                            return False
                    else:
                        sbdlogger.info('Unexpected response from modem')
                        return False
                elif r == '1':
                    sbdlogger.info('SBD write timeout')
                    return False
                elif r == '2':
                    sbdlogger.info('SBD checksum does not match the checksum calculated by the modem')
                    return False
                elif r == '3':
                    sbdlogger.info('SBD message size is not correct')
                    return False
                else:
                    sbdlogger.info('Unexpected response from modem')
                    return False   
            except IndexError:
                sbdlogger.info('Unexpected response from modem')
                return False
        else:
            sbdlogger('did not receive READY message')
            return False

    # Final print statement that it sent
    print('Sent SBD...')