#!/usr/bin/python3
#
# Opens a serial connection with a RockBlock 9603 SBD modem and
# transmits binary data that is passed to the main function
# Data is converted into binary in this script and then seperated
# into 4 messages send out through iridium in  specified format.

# standard imports 
import serial, sys
#from logging import *
import struct
import numpy as np
import time
from datetime import datetime
from logging import *
import RPi.GPIO as GPIO
from time import sleep

import logging


#Iridium parameters - fixed for now
modemPort = '/dev/ttyUSB0' #config.getString('Iridium', 'port')
modemBaud = 19200 #config.getInt('Iridium', 'baud')
modemGPIO =  16 #config.getInt('Iridium', 'modemGPIO')
formatType = 10 #config.getInt('Iridium', 'formatType')
call_interval = 60 #config.getInt('Iridium', 'call_interval')
call_time = 10 #config.getInt('Iridium', 'call_time')
timeout=60 #some commands can take a long time to complete

packet_type = 1
id = 0

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
#handler = logging.StreamHandler(sys.stdout)
#handler.setLevel(logging.INFO)
#format = logging.Formatter('%(asctime)s, %(name)s - [%(levelname)s] - %(message)s')
#handler.setFormatter(format)
#logger.addHandler(handler)


#open binary data file and return bytes
def open_bin(binfile):
    try:
        with open(binfile, 'rb') as f:
            bytes=bytearray(f.read())
    except FileNotFoundError:
        sbdlogger.info('file not found: {}'.format(binfile))   
    except Exception as e:
        sbdlogger.info('error opening file: {}'.format(e))
    return bytes

def init_modem():
   
    try:
        GPIO.output(modemGPIO,GPIO.HIGH) #power on GPIO enable pin
        sbdlogger.info('power on modem...')
        sleep(3)
        sbdlogger.info('done')
    except Exception as e:
        sbdlogger.info('error powering on modem')
        sbdlogger.info(e)
        
    #open serial port
    sbdlogger.info('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
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
                return ser, True
    else:
        return ser, False

def get_response(ser,command, response='OK'):
    ser.flushInput()
    command=(command+'\r').encode()
    ser.write(command)
    sleep(0.25)
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


#Get signal quality using AT+CSQF command (see AT command reference).
#Returns signal quality, default range is 0-5. Returns -1 for an error or no response
#Example modem output: AT+CSQF +CSQF:0 OK    
def sig_qual(ser, command='AT+CSQ'):
    ser.flushInput()
    ser.write((command+'\r').encode())
    sbdlogger.info('command = {}, '.format(command))
    r=ser.read(23).decode()
    if 'CSQ:' in r:
        response=r[9:15]
        qual = r[14]
        sbdlogger.info('response = {}'.format(response))
        return qual #return signal quality (0-5)
    elif 'ERROR' in r:
        sbdlogger.info('response = ERROR')
        return -1
    else:
        sbdlogger.info('unexpected response: {}'.format(r))  
        return -1

#send binary message to modem buffer and transmit
#returns true if trasmit command is sent, but does not mean a successful transmission
#checksum is least significant 2 bytes of sum of message, with hgiher order byte sent first
#returns false if anything goes wrong
def transmit_bin(ser,msg):
    
    bytelen=len(msg)
    
    try:  
        sbdlogger.info('command = AT+SBDWB')
        ser.flushInput()
        ser.write(('AT+SBDWB='+str(bytelen)+'\r').encode()) #command to write bytes, followed by number of bytes to write
        sleep(0.25)
    except serial.SerialException as e:
        sbdlogger.info('serial error: {}'.format(e))
        return False
    except Exception as e:
        sbdlogger.info('error: {}'.format(e))
        return False
    
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        sbdlogger.info('response = READY')

        sbdlogger.info('passing message to modem buffer')
        ser.flushInput()
        ser.write(msg) #pass bytes to modem
        
        #The checksum is the least significant 2-bytes of the summation of the entire SBD message. 
        #The high order byte must be sent first. 
        checksum=sum(msg) #calculate checksum value
        byte1 = (checksum >> 8).to_bytes(1,'big') #bitwise operation shift 8 bits right to get firt byte of checksum and convert to bytes
        byte2 = (checksum & 0xFF).to_bytes(1,'big')#bitwise operation to get second byte of checksum, convet to bytes
        sbdlogger.info('passing checksum to modem buffer')
        ser.write(byte1) #first byte of 2-byte checksum 
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
                r=ser.read(36).decode()
                if '+SBDIX: ' in r:
                    r=r[11:36] #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                    r=r.strip('\r') #remove any dangling carriage returns
                    sbdlogger.info('response = {}'.format(r)) 
                    return True
            else:
                return False
        except IndexError:
            sbdlogger.info('no response from modem')
            return False
    else:
        sbdlogger('did not receive READY message')
        return False
    
#same as transmit_bin but sends ascii text using SBDWT command instead of bytes
def transmit_ascii(ser,msg):
 
    msg_len=len(msg)
    
    if msg_len > 340: #check message length
        sbdlogger.info('message too long. must be 340 bytes or less')
        return False
    
    if not msg.isascii(): #check for ascii text
        sbdlogger.info('message must be ascii text')
        return Falsem
    
    try:  
        ser.flushInput()
        sbdlogger.info('command = AT+SBDWT')
        ser.write(b'AT+SBDWT\r') #command to write text to modem buffer
        sleep(0.25)
    except serial.SerialException as e:
        sbdlogger.info('serial error: {}'.format(e))
        return False
    except Exception as e:
        sbdlogger.info('error: {}'.format(e))
        return False
    
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        sbdlogger.info('response = READY')
        ser.flushInput()
        ser.write((msg + '\r').encode()) #pass bytes to modem. Must have carriage return
        sleep(0.25)
        sbdlogger.info('passing message to modem buffer')
        r=ser.read(msg_len+9).decode() #read response to get result code (0 for successful save in buffer or 1 for fail)
        if 'OK' in r:
            index=msg_len+2 #index of result code
            r=r[index:index+1] 
            sbdlogger.info('response = {}'.format(r))        
            if r == '0':
                sbdlogger.info('command = AT+SBDIX')
                ser.flushInput()
                ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                sleep(5)
                r=ser.read(36).decode()
                if '+SBDIX: ' in r:
                    r=r[11:36] #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                    r=r.strip('\r') #remove any dangling carriage returns
                    sbdlogger.info('response = {}'.format(r)) 
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
def send_microSWIFT(payload_data):
    sbdlogger.info('sending microSWIFT telemetry')
    global id
    #check for data
    if len(payload_data) == 0:
        sbdlogger.info('payload data is empty')
        return 
    
    #initialize modem
    ser, modem_initialized = init_modem()
    
    if not modem_initialized:
        sbdlogger.info('modem not initialized, unable to send data')
        return
        
 
    #split up payload data into packets    
    #----------------------------------------------------------------------------------------
    index = 0 #byte index
    payload_size = 1245
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
    
    if id >= 99:
        id = 0
    else:   
       id+=1    

    #send packets
    #--------------------------------------------------------------------------------------
    sbdlogger.info('sending first packet')
    #sbdlogger.info(packet0)
    transmit_bin(ser,packet0)
    
    sbdlogger.info('sending second packet')
    #sbdlogger.info(packet1)
    transmit_bin(ser,packet1)
    
    sbdlogger.info('sending third packet')
    #sbdlogger.info(packet2)
    transmit_bin(ser,packet2)
    
    sbdlogger.info('sending fourth packet')
    #sbdlogger.info(packet3)
    transmit_bin(ser,packet3)
    
    
    
    #turn off modem
    #--------------------------------------------------------------------------------------
    sbdlogger.info('powering down modem')    
    GPIO.output(modemGPIO,GPIO.LOW)

    


