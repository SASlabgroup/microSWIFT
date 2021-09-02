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
import time as t
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
def createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, lat, lon,  temp, volt):

    if payload_type != 7:
        logger.info('invalid payload type: {}'.format(payload_type))
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
    logger.info('Hs: {0} Tp: {1} Dp: {2} lat: {3} lon: {4} temp: {5} volt: {6} uMean: {7} vMean: {8} zMean: {9}'.format(
        Hs, Tp, Dp, lat, lon, temp, volt, uMean, vMean, zMean))

    if sensor_type == 50:

        #create formatted struct with all payload data
        payload_size = struct.calcsize('<sbbhfff42f42f42f42f42f42f42ffffffffiiiiii')
        payload_data = (struct.pack('<sbbhfff', str(payload_type).encode(),sensor_type,port, payload_size,Hs,Tp,Dp) + 
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
    
    elif sensor_type == 51:
        
        #compute fmin fmax and fstep
        fmin = np.min(f)
        fmax = np.max(f)
        fstep = (fmax - fmin)/41

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

    else: 
        logger.info('invalid sensor type: {}'.format(sensor_type))
        logger.info('exiting')
        sys.exit(1)


    #Create file name
    TX_fname = dataDir + floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(now) 

    # Open the TX file and start to write to it    
    with open(TX_fname, 'wb') as file:
        
        logger.info('create telemetry file: {}'.format(TX_fname))
        # Write the binary packed data to a file 
        logger.info('writing data to file')
        file.write(payload_data)
        logger.info('done')
        file.flush()

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

def initModem():

    # Turn on the pin to power on the modem
    try:
        GPIO.setup(modemGPIO, GPIO.OUT)
        GPIO.output(modemGPIO,GPIO.HIGH) #power on GPIO enable pin
        logger.info('modem powered on')
        t.sleep(3)
        logger.info('done')
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
                    #interpret response and check MO status code (0=success)
                    if int(r[0]) == 0:
                        logger.info('Message send success')
                        return True
                    else:
                        logger.info('Message send failure, status code = {}'.format(r[0]))
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
def send_microSWIFT_50(payload_data, timeout):
    logger.info('sending microSWIFT telemetry (type 50)')
    
    global id
    payload_size = len(payload_data)
    
    #check for data
    if payload_size == 0:
        logger.info('Error: payload data is empty')
        return 
    
    if payload_size != 1245:
        logger.info('Error: unexpected number of bytes in payload data. Expected bytes: 1245, bytes received: {}'.format(payload_size))
        return
    
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


    while datetime.utcnow() < timeout:  
    
        #initialize modem
        ser, modem_initialized = initModem()

        if not modem_initialized:
            logger.info('Modem not initialized')
            GPIO.output(modemGPIO,GPIO.LOW) #power off modem
            continue
        
        #send packets
        logger.info('Sending 4 packet message (50)')
        
        i=0
        signal=[]
        while datetime.utcnow() <= timeout:
            
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
                        if datetime.utcnow() < timeout:
                            logger.info('Sending {} packet. Retry {}'.format(ordinal[i], retry))
                            issent  = transmit_bin(ser,message[i])            
                            retry += 1
                        else:
                            logger.info('Send SBD timeout. Message not sent')
                            #turn off modem
                            logger.info('Powering down modem')    
                            GPIO.output(modemGPIO,GPIO.LOW)
                            return 
                #increment message counter for each completed message
                if id >= 99:
                     id = 0
                else:   
                    id+=1

                # Final print statement that it sent
                logger.info('Sent SBD successfully')      
                #turn off modem
                logger.info('Powering down modem')    
                GPIO.output(modemGPIO,GPIO.LOW)
                return 
            

    #turn off modem
    logger.info('Send SBD timeout. Message not sent')
    logger.info('powering down modem')    
    GPIO.output(modemGPIO,GPIO.LOW)
   

def send_microSWIFT_51(payload_data, timeout):
    logger.info('sending microSWIFT telemetry (type 51)')
    
    global id
    payload_size = len(payload_data)
    
    #check for data
    if payload_size == 0:
        logger.info('Error: payload data is empty')
        return 
    
    if payload_size != 249:
        logger.info('Error: unexpected number of bytes in payload data. Expected bytes: 249, bytes received: {}'.format(payload_size))
        return
    
    #split up payload data into packets    
    index = 0 #byte index
    packet_type = 0 #single packet
    
    #packet to send
    header = str(packet_type).encode('ascii') #packet type as as ascii number
    sub_header0 = str(','+str(id)+','+str(index)+','+str(payload_size)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes0 = payload_data[index:248] #data bytes for packet
    packet0 = header + sub_header0 + payload_bytes0
    
    while datetime.utcnow() < timeout:
    
        #initialize modem
        ser, modem_initialized = initModem()

        if not modem_initialized:
            logger.info('Modem not initialized')
            GPIO.output(modemGPIO,GPIO.LOW) #power off modem
            continue
        
        #send packets
        logger.info('Sending single packet message (51)')
        
        i=0
        signal=[]
        while datetime.utcnow() < timeout:
            
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
                while issent == False and datetime.utcnow() < timeout:
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
                GPIO.output(modemGPIO,GPIO.LOW)
                return   
             
            else: 
                continue
 
    #turn off modem
    logger.info('Send SBD timeout. Message not sent')
    logger.info('powering down modem')    
    GPIO.output(modemGPIO,GPIO.LOW)
    


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
        t.sleep(10)
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
