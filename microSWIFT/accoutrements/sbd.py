## Send Short Burst Data (SBD) Functions 
'''
author: @edwinrainville
All functions are heavily adapted from Viviana Castillo and Alex de Klerk.

Log:
    - Aug 2022, @jacobrdavis: sensor_type_52, send_microSWIFT_52()

TODO:
    - lookup table for status codes 
    - pull out into functions?
    - combine repeated code for send_microSWIFT_50,51,52
'''

# Import Statements
from datetime import datetime
import struct
from logging import *
import sys, os
from utils.config3 import Config
import numpy as np
import RPi.GPIO as GPIO
import time as t
import serial

####TODO: Update this block when EJ finishes the config integration ####
#Define Config file name and load file
CONFIG_FILENAME = r'/home/pi/microSWIFT/utils/Config.dat'
config = Config() # Create object and load file
ok = config.loadFile( CONFIG_FILENAME )
if( not ok ):
    print("Error loading config file")
    sys.exit(1)

# Create the TX file named for the current time
logger = getLogger('microSWIFT.'+__name__)  

# System Parameters
DATA_DIR = config.getString('System', 'dataDir')
FLOAT_ID = os.uname()[1]
SENSOR_TYPE = config.getInt('System', 'sensorType')
BAD_VALUE = config.getInt('System', 'badValue')
NUM_COEF = config.getInt('System', 'numCoef')
PORT = config.getInt('System', 'port')
PAYLOAD_TYPE = config.getInt('System', 'payloadType')
BURST_SECONDS = config.getInt('System', 'burst_seconds')
BURST_TIME = config.getInt('System', 'burst_time')
BURST_INT = config.getInt('System', 'burst_interval')
CALL_DURATION = BURST_INT*60-BURST_SECONDS #time between burst end and burst start to make a call

# Iridium parameters
MODEM_PORT = config.getString('Iridium', 'port')
MODEM_BAUD_RATE = config.getInt('Iridium', 'baud')
MODEM_GPIO = config.getInt('Iridium', 'modemGPIO')
TIMEOUT = config.getInt('Iridium', 'timeout')

SUPPORTED_PAYLOADS = [50,51,52]

########################################################################



#arbitrary message counter
id = 0

def init_modem():

    # Turn on the pin to power on the modem
    try:
        GPIO.setup(MODEM_GPIO, GPIO.OUT)
        GPIO.output(MODEM_GPIO,GPIO.HIGH) #power on GPIO enable pin
        logger.info('modem powered on')
        t.sleep(3)
        logger.info('done')
    except Exception as e:
        logger.info('error powering on modem')
        logger.info(e)
        
    #open serial port
    logger.info('opening serial port with modem at {0} on port {1}...'.format(MODEM_BAUD_RATE,MODEM_PORT))
    try:
        ser=serial.Serial(MODEM_PORT,MODEM_BAUD_RATE,timeout=TIMEOUT)
        logger.info('serial port opened successfully')
    except serial.SerialException as e:
        logger.info('unable to open serial port: {}'.format(e))
        return ser, False
    except Exception as e:
        logger.info('unable to open serial port')
        logger.info(e)
        return ser, False

    logger.info('command = AT')
    if get_response(ser,'AT'): #send AT command
        logger.info('command = AT&F')
        if get_response(ser,'AT&F'): #set default parameters with AT&F command 
            logger.info('command = AT&K=0')  
            if get_response(ser,'AT&K=0'): #important, disable flow control
                logger.info('modem initialized')
                return ser, True
    else:
        return ser, False

def send(payload_data, TIMEOUT):
    """TODO:"""
    # Read in the sensor type from the binary payload file.
    # This check is neccessary for a stack with multiple
    # sensor types in it.
    PAYLOAD_START_INDEX = 0 # (no header) otherwise it is: = payload_data.index(b':') 
    SENSOR_TYPE_FROM_PAYLOAD = ord(payload_data[PAYLOAD_START_INDEX+1:PAYLOAD_START_INDEX+2]) # sensor type is stored 1 byte after the header
    
    if SENSOR_TYPE_FROM_PAYLOAD not in SUPPORTED_PAYLOADS: #TODO: make this list a constant 
        logger.info(f'Failed to read sensor type properly; read sensor type as: {SENSOR_TYPE_FROM_PAYLOAD}')
        logger.info(f'Trying to send as configured sensor type instead ({SENSOR_TYPE})')
        send_sensor_type = SENSOR_TYPE
    else:
        send_sensor_type = SENSOR_TYPE_FROM_PAYLOAD

    # send either payload type 50, 51, or 52
    if send_sensor_type == 50:
        successful_send = send_microSWIFT_50(payload_data, TIMEOUT)
    elif send_sensor_type == 51:
        successful_send = send_microSWIFT_51(payload_data, TIMEOUT)
    elif send_sensor_type == 52:
        successful_send = send_microSWIFT_52(payload_data, TIMEOUT)
    else:
        logger.info(f'Specified sensor type ({send_sensor_type}) is invalid or not currently supported')

    return successful_send

# Telemetry test functions
def createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, lat, lon,  temp, salinity, volt):
    logger.info('---------------sendSBD.createTX.py------------------')

    if PAYLOAD_TYPE != 7:
        logger.info('invalid payload type: {}'.format(PAYLOAD_TYPE))
        logger.info('exiting')
        sys.exit(1)

    now=datetime.utcnow()

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
    logger.info('Hs: {0} Tp: {1} Dp: {2} lat: {3} lon: {4} temp: {5} salinity: {6} volt: {7} uMean: {8} vMean: {9} zMean: {10}'.format(
        Hs, Tp, Dp, lat, lon, temp, salinity, volt, uMean, vMean, zMean))

    if SENSOR_TYPE == 50:

        #create formatted struct with all payload data
        payload_size = struct.calcsize('<sbbhfff42f42f42f42f42f42f42ffffffffiiiiii')
        payload_data = (struct.pack('<sbbhfff', str(PAYLOAD_TYPE).encode(),SENSOR_TYPE,PORT, payload_size,Hs,Tp,Dp) + 
                        struct.pack('<42f', *E) +
                        struct.pack('<42f', *f) +
                        struct.pack('<42f', *a1) +
                        struct.pack('<42f', *b1) +
                        struct.pack('<42f', *a2) +
                        struct.pack('<42f', *b2) +
                        struct.pack('<42f', *check) +
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
    
    elif SENSOR_TYPE == 51:
        
        #compute fmin fmax and fstep
        fmin = np.min(f)
        fmax = np.max(f)
        fstep = (fmax - fmin)/41

        payload_size = struct.calcsize('<sbbhfff42fffffffffffiiiiii')
        payload_data = (struct.pack('<sbbhfff', str(PAYLOAD_TYPE).encode(), SENSOR_TYPE, PORT, payload_size,Hs,Tp,Dp) + 
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
    
    
    elif SENSOR_TYPE == 52:

        # extract frequency range
        fmin = np.min(f)
        fmax = np.max(f)
        # fstep = (fmax - fmin)/(len(E)-1)

        # round, scale, and convert a1,b1...+ to 8-bit, signed integers
        a1_8bit = np.byte(np.round(100*a1)) # could be 127
        b1_8bit = np.byte(np.round(100*b1))
        a2_8bit = np.byte(np.round(100*a2))
        b2_8bit = np.byte(np.round(100*b2))

        # round, scale, clip, and convert check to 8-bit, unsigned integers
        checkRoundedAndScaled = np.round(10*check)
        checkRoundedAndScaled[checkRoundedAndScaled > 255] = 255
        check_8bit = np.ubyte(checkRoundedAndScaled)

        # current time to UNIX timestamp
        nowEpoch = now.timestamp() # unpack with datetime.fromtimestamp(nowEpoch)  

        # create formatted struct with all payload data
        payload_size = struct.calcsize('<sbbheee42eee42b42b42b42b42Bffeeef') 
        payload_data = (struct.pack('<sbbh', str(PAYLOAD_TYPE).encode(), SENSOR_TYPE, PORT, payload_size) + 
                        struct.pack('<eee', Hs,Tp,Dp) +
                        struct.pack('<42e', *E) +
                        struct.pack('<e', fmin) +
                        struct.pack('<e', fmax) +
                        struct.pack('<42b', *a1_8bit) +
                        struct.pack('<42b', *b1_8bit) +
                        struct.pack('<42b', *a2_8bit) +
                        struct.pack('<42b', *b2_8bit) +
                        struct.pack('<42B', *check_8bit) +
                        struct.pack('<f', lat) +
                        struct.pack('<f', lon) +
                        struct.pack('<e', temp) + 
                        struct.pack('<e', salinity) +
                        struct.pack('<e', volt) +
                        struct.pack('<f', nowEpoch) # float saves 4 bytes but looses +/- 1s precision 
                        )

    else: 
        logger.info('invalid sensor type: {}'.format(SENSOR_TYPE))
        logger.info('exiting')
        sys.exit(1)

    #Create file name
    TX_fname = dataDir + floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(now) 
    if os.path.exists(TX_fname): # support secondary estimate
        TX_fname = dataDir+floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC}".format(now)+'_2.dat'

    # Open the TX file and start to write to it    
    with open(TX_fname, 'wb') as file:
        logger.info('create telemetry file: {}'.format(TX_fname))
        # Write the binary packed data to a file 
        logger.info('writing data to file')
        file.write(payload_data)
        logger.info('done')
        file.flush()

    logger.info('----------------------------------------------------')

    return TX_fname, payload_data


def checkTX(TX_fname):

    with open(TX_fname, mode='rb') as file: # b is important -> binary
        fileContent = file.read()
    data = struct.unpack('<sbbhfff42fffffffffffiiiiii', fileContent)
    logger.info('data = ', data)


def get_response(ser,command, response='OK'):
    ser.flushInput()
    logger.info('command = {}'.format(command))
    ser.write((command+'\r').encode())
    t.sleep(1)
    try:
        while ser.in_waiting > 0:
            r=ser.readline().decode().strip('\r\n')
            if response in r:
                logger.info('response = {}'.format(r))
                return True
            elif 'ERROR' in response:
                logger.info('response = ERROR')
                return False
    except serial.SerialException as e:
        logger.info('error: {}'.format(e))
        return False

#Get signal quality using AT+CSQF command (see AT command reference).
#Returns signal quality, default range is 0-5. Returns -1 for an error or no response
#Example modem output: AT+CSQF +CSQF:0 OK    
def sig_qual(ser, command='AT+CSQ'):
    ser.flushInput()
    ser.write((command+'\r').encode())
    logger.info('command = {} '.format(command))
    r=ser.read(23).decode()
    if 'CSQ:' in r:
        response=r[9:15]
        qual = r[14]
        logger.info('response = {}'.format(response))
        return int(qual) #return signal quality (0-5)
    elif 'ERROR' in r:
        logger.info('Response = ERROR')
        return -1
    elif r == '':
        logger.info('No response from modem')
        return -1
    else:
        logger.info('Unexpected response: {}'.format(r))  
        return -1




#send binary message to modem buffer and transmits
#returns true if trasmit command is sent, but does not mean a successful transmission
#checksum is least significant 2 bytes of sum of message, with higher order byte sent first
#returns false if anything goes wrong
def transmit_bin(ser,msg):
    
    bytelen=len(msg)
    logger.info('payload bytes = {}'.format(bytelen))
                    
    #check signal quality and attempt to send until timeout reached
            
    try:
        logger.info('Command = AT+SBDWB')
        ser.flushInput()
        ser.write(('AT+SBDWB='+str(bytelen)+'\r').encode()) #command to write bytes, followed by number of bytes to write
        t.sleep(0.25)
    except serial.SerialException as e:
        logger.info('Serial error: {}'.format(e))
        return False
    except Exception as e:
        logger.info('Error: {}'.format(e))
        return False
    
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        logger.info('response = READY')
        logger.info('passing message to modem buffer')
        ser.flushInput()
        ser.write(msg) #pass bytes to modem
        t.sleep(0.25)
        
        #The checksum is the least significant 2-bytes of the summation of the entire SBD message. 
        #The high order byte must be sent first. 
        checksum=sum(msg) #calculate checksum value
        byte1 = (checksum >> 8).to_bytes(1,'big') #bitwise operation shift 8 bits right to get firt byte of checksum and convert to bytes
        byte2 = (checksum & 0xFF).to_bytes(1,'big')#bitwise operation to get second byte of checksum, convet to bytes
        logger.info('passing checksum to modem buffer')
        ser.write(byte1) #first byte of 2-byte checksum 
        t.sleep(0.25)
        ser.write(byte2) #second byte of checksum
        t.sleep(0.25)
        
        r=ser.read(3).decode() #read response to get result code from SBDWB command (0-4)
        try:
            r=r[2] #result code of expected response
            logger.info('response = {}'.format(r))
            
            if r == '0': #response of zero = successful write, ready to send
                logger.info('command = AT+SBDIX')
                ser.flushInput()
                ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                t.sleep(5)
                ser.read(11)
                r=ser.readline().decode().strip('\r\n')  #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                logger.info('response = {}'.format(r))
                
                if '+SBDIX: ' in r:
                    r=r.strip('+SBDIX:').split(', ')
                    #interpret response and check MO status code (0=success, 2=success but no location update). See ISU AT Command ref page 96.
                    if int(r[0]) == 0 or int(r[0]) == 2:
                        logger.info('Message send success')
                        return True
                    else:
                        logger.info('Message send failure, status code = {}'.format(r[0]))
                        #TODO: lookup table of status codes here
                        return False
                else:
                    logger.info('Unexpected response from modem')
                    return False
            elif r == '1':
                logger.info('SBD write timeout')
                return False
            elif r == '2':
                logger.info('SBD checksum does not match the checksum calculated by the modem')
                return False
            elif r == '3':
                logger.info('SBD message size is not correct')
                return False
            else:
                logger.info('Unexpected response from modem')
                return False   
        except IndexError:
            logger.info('Unexpected response from modem')
            return False
    else:
        logger('did not receive READY message')
        return False
    
#same as transmit_bin but sends ascii text using SBDWT command instead of bytes
def transmit_ascii(ser,msg):
 
    msg_len=len(msg)
    
    if msg_len > 340: #check message length
        logger.info('message too long. must be 340 bytes or less')
        return False
    
    if not msg.isascii(): #check for ascii text
        logger.info('message must be ascii text')
        return False
    
    try:  
        ser.flushInput()
        logger.info('command = AT+SBDWT')
        ser.write(b'AT+SBDWT\r') #command to write text to modem buffer
        t.sleep(0.25)
    except serial.SerialException as e:
        logger.info('serial error: {}'.format(e))
        return False
    except Exception as e:
        logger.info('error: {}'.format(e))
        return False
    
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        logger.info('response = READY')
        ser.flushInput()
        ser.write((msg + '\r').encode()) #pass bytes to modem. Must have carriage return
        t.sleep(0.25)
        logger.info('passing message to modem buffer')
        r=ser.read(msg_len+9).decode() #read response to get result code (0 for successful save in buffer or 1 for fail)
        if 'OK' in r:
            index=msg_len+2 #index of result code
            r=r[index:index+1] 
            logger.info('response = {}'.format(r))        
            if r == '0':
                logger.info('command = AT+SBDIX')
                ser.flushInput()
                ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                t.sleep(5)
                r=ser.read(36).decode()
                if '+SBDIX: ' in r:
                    r=r[11:36] #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                    r=r.strip('\r') #remove any dangling carriage returns
                    logger.info('response = {}'.format(r)) 
                    return True
    else:
        return False
    

#MAIN
#
#Packet Structure
#<packet-type> <sub-header> <data>
#Sub-header 0:
#    ,<id>,<start-byte>,<total-bytes>:
#Sub-header 1 thru N:
#    ,<id>,<start-byte>:
#--------------------------------------------------------------------------------------------
def send_microSWIFT_50(payload_data, TIMEOUT):
    logger.info('---------------sendSBD.send_microSWIFT_50------------------')
    logger.info('sending microSWIFT telemetry (type 50)')
    
    global id
    payload_size = len(payload_data)
    
    #check for data
    if payload_size == 0:
        logger.info('Error: payload data is empty')
        successful_send = False
        return successful_send
 
    if payload_size != 1245:
        logger.info('Error: unexpected number of bytes in payload data. Expected bytes: 1245, bytes received: {}'.format(payload_size))
        successful_send = False
        return successful_send
    
    index = 0 #byte index
    packet_type = 1 #extended message
        
    #split up payload data into packets    
    #first packet to send
    header = str(packet_type).encode('ascii') #packet type as as ascii number
    sub_header0 = str(','+str(id)+','+str(index)+','+str(payload_size)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes0 = payload_data[index:325] #data bytes for packet 0
    packet0 = header + sub_header0 + payload_bytes0
    
    
    #second packet to send
    index = 325
    sub_header1 = str(','+str(id)+','+str(index)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes1 = payload_data[index:653] #data bytes for packet 1    
    packet1 = header + sub_header1 + payload_bytes1         
    
    
    #third packet to send
    index = 653
    sub_header2 = str(','+str(id)+','+str(index)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes2 = payload_data[index:981] #data bytes for packet 2
    packet2 = header + sub_header2 + payload_bytes2      
   
    
    #fourth packet to send
    index = 981
    sub_header3 = str(','+str(id)+','+str(index)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes3 = payload_data[index:1245] #data bytes for packet 3
    packet3 = header + sub_header3 + payload_bytes3 
    
    message = [packet0, packet1, packet2, packet3] #list of packets
    ordinal = ['first', 'second', 'third', 'fourth']


    while datetime.utcnow() < TIMEOUT:
    
        #initialize modem
        ser, modem_initialized = init_modem()

        if not modem_initialized:
            logger.info('Modem not initialized')
            GPIO.output(MODEM_GPIO,GPIO.LOW) #power off modem
            continue
        
        #send packets
        logger.info('Sending 4 packet message (50)')
        
        i=0
        signal=[]
        while datetime.utcnow() <= TIMEOUT:
            
            isignal = sig_qual(ser)
            if isignal < 0:
                continue
            else: 
                signal.append(isignal)
                i+=1
            
            if len(signal) >= 3 and np.mean(signal[i-3:i]) >= 3: #check rolling average of last 3 values, must be at least 3 bars
                signal.clear() #clear signal values
                i=0 #reset counter
                
                #attempt to transmit packets
                for i in range(4):
                    retry = 0
                    issent  = False
                    while issent == False:
                        if datetime.utcnow() < TIMEOUT:
                            logger.info('Sending {} packet. Retry {}'.format(ordinal[i], retry))
                            issent  = transmit_bin(ser,message[i])            
                            retry += 1
                        else:
                            logger.info('Send SBD timeout. Message not sent')
                            #turn off modem
                            logger.info('Powering down modem')    
                            GPIO.output(MODEM_GPIO,GPIO.LOW)
                            successful_send = False
                            
                            logger.info('-----------------------------------------------------------')

                            return successful_send
                #increment message counter for each completed message
                if id >= 99:
                     id = 0
                else:   
                    id+=1

                # Final print statement that it sent
                logger.info('Sent SBD successfully')      
                #turn off modem
                logger.info('Powering down modem')    
                GPIO.output(MODEM_GPIO,GPIO.LOW)
                successful_send = True
                
                logger.info('-----------------------------------------------------------')

                return successful_send
            

    #turn off modem
    logger.info('Send SBD timeout. Message not sent')
    logger.info('powering down modem')    
    GPIO.output(MODEM_GPIO,GPIO.LOW)
    successful_send = False

    logger.info('-----------------------------------------------------------')
    return successful_send
   

def send_microSWIFT_51(payload_data, TIMEOUT):
    logger.info('---------------sendSBD.send_microSWIFT_51------------------')
    logger.info('sending microSWIFT telemetry (type 51)')
    
    global id
    payload_size = len(payload_data)
    
    #check for data
    if payload_size == 0:
        logger.info('Error: payload data is empty')
        successful_send = False
        return successful_send
    
    if payload_size != 249:
        logger.info('Error: unexpected number of bytes in payload data. Expected bytes: 249, bytes received: {}'.format(payload_size))
        successful_send = False
        return successful_send
    
    #split up payload data into packets    
    index = 0 #byte index
    packet_type = 0 #single packet
    
    #packet to send
    header = str(packet_type).encode('ascii') #packet type as as ascii number
    sub_header0 = str(','+str(id)+','+str(index)+','+str(payload_size)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes0 = payload_data[index:249] #data bytes for packet
    packet0 = header + sub_header0 + payload_bytes0 
    
    while datetime.utcnow() < TIMEOUT:
    
        #initialize modem
        ser, modem_initialized = init_modem()

        if not modem_initialized:
            logger.info('Modem not initialized')
            GPIO.output(MODEM_GPIO,GPIO.LOW) #power off modem
            continue
        
        #send packets
        logger.info('Sending single packet message (51)')
        
        i=0
        signal=[]
        while datetime.utcnow() < TIMEOUT:
            
            isignal = sig_qual(ser)
            if isignal < 0:
                continue
            else: 
                signal.append(isignal)
                i+=1
            
            if len(signal) >= 3 and np.mean(signal[i-3:i]) >= 3: #check rolling average of last 3 values, must be at least 3 bars
                signal.clear() #clear signal values
                i=0 #reset counter
                
                #attempt to transmit packets
                retry = 0
                issent  = False
                while issent == False and datetime.utcnow() < TIMEOUT:
                    logger.info('Sending packet. Retry {}'.format(retry))
                    issent  = transmit_bin(ser, packet0)            
                    retry += 1
                #increment message counter for each completed message
                if id >= 99:
                    id = 0
                else:   
                    id+=1

                # Final print statement that it sent
                logger.info('Sent SBD successfully')      
                #turn off modem
                logger.info('Powering down modem')    
                GPIO.output(MODEM_GPIO,GPIO.LOW)
                successful_send = True
                
                logger.info('-----------------------------------------------------------')

                return successful_send
             
            else: 
                continue
 
    #turn off modem
    logger.info('Send SBD timeout. Message not sent')
    logger.info('powering down modem')    
    GPIO.output(MODEM_GPIO,GPIO.LOW)
    successful_send = False

    logger.info('-----------------------------------------------------------')

    return successful_send
    
def send_microSWIFT_52(payload_data, TIMEOUT): #TODO: finish working on!
    logger.info('---------------sendSBD.send_microSWIFT_52------------------')
    logger.info('sending microSWIFT telemetry (type 52)')
    
    global id
    payload_size = len(payload_data)
    payload_size_exp = 327 #struct.calcsize('<sbbheee42eee42b42b42b42b42Bffeeef') 
    
    #check for data
    if payload_size == 0:
        logger.info('Error: payload data is empty')
        successful_send = False
        return successful_send
    
    if payload_size != payload_size_exp:
        logger.info(f'Error: unexpected number of bytes in payload data. Expected bytes: {payload_size_exp}, bytes received: {payload_size}')
        successful_send = False
        return successful_send
    
    #split up payload data into packets    
    index = 0 #byte index
    packet_type = 0 #single packet
    
    #packet to send
    header = str(packet_type).encode('ascii') #packet type as as ascii number
    sub_header0 = str(','+str(id)+','+str(index)+','+str(payload_size)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes0 = payload_data[index:payload_size_exp] #data bytes for packet
    packet0 = header + sub_header0 + payload_bytes0 
    
    while datetime.utcnow() < TIMEOUT:
    
        #initialize modem
        ser, modem_initialized = init_modem()

        if not modem_initialized:
            logger.info('Modem not initialized')
            GPIO.output(MODEM_GPIO,GPIO.LOW) #power off modem
            continue
        
        #send packets
        logger.info('Sending single packet message with complete wave statistics (52)')
        
        i=0
        signal=[]
        while datetime.utcnow() < TIMEOUT:
            
            isignal = sig_qual(ser)
            if isignal < 0:
                continue
            else: 
                signal.append(isignal)
                i+=1
            
            if len(signal) >= 3 and np.mean(signal[i-3:i]) >= 3: #check rolling average of last 3 values, must be at least 3 bars
                signal.clear() #clear signal values
                i=0 #reset counter
                
                #attempt to transmit packets
                retry = 0
                issent  = False
                while issent == False and datetime.utcnow() < TIMEOUT:
                    logger.info('Sending packet. Retry {}'.format(retry))
                    issent  = transmit_bin(ser, packet0)            
                    retry += 1
                #increment message counter for each completed message
                if id >= 99:
                    id = 0
                else:   
                    id+=1

                # Final print statement that it sent
                logger.info('Sent SBD successfully')      
                #turn off modem
                logger.info('Powering down modem')    
                GPIO.output(MODEM_GPIO,GPIO.LOW)
                successful_send = True
                
                logger.info('-----------------------------------------------------------')

                return successful_send
             
            else: 
                continue
 
    #turn off modem
    logger.info('Send SBD timeout. Message not sent')
    logger.info('powering down modem')    
    GPIO.output(MODEM_GPIO,GPIO.LOW)
    successful_send = False

    logger.info('-----------------------------------------------------------')

    return successful_send

# def sendSBD(ser, payload_data, next_start):
#     import time
#     from adafruit_rockblock import RockBlock
    
#     # Setup loging 
#     logger = getLogger('microSWIFT.'+__name__) 
#     logger.info('---------------sendSBD------------------')

#     # Setup instance of RockBlock 
#     rockblock = RockBlock(ser)

#     # Send payload data through the RockBlock
#     rockblock.data_out = payload_data
#     logger.info('Talking to Satellite')
#     retry = 0
#     sent_status_val = 0 # any returned status value less than this means the message sent successfully.
#     status = rockblock.satellite_transfer()
#     now = datetime.utcnow().minute + datetime.utcnow().second/60
#     while status[0] > sent_status_val and now < next_start:
#         t.sleep(10)
#         status = rockblock.satellite_transfer()
#         logger.info('Retry number = {}'.format(retry))
#         logger.info('status = {}'.format(status))
#         now = datetime.utcnow().minute + datetime.utcnow().second/60
#         retry += 1
    
#     if status[0] == 0:
#         # Final print statement that it sent
#         logger.info('Sent SBD successfully')

#     else:
#         logger.info('Could not send SBD')

#     logger.info('----------------------------------------')
