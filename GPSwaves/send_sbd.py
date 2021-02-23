#!/usr/bin/python3
#
# Opens a serial connection with a RockBlock 9603 SBD modem and
# transmits binary data that is passed to the main function
# Data is converted into binary in this script and then seperated
# into 4 messages send out through iridium in  specified format.

# standard imports 
import serial, sys
from logging import *
import struct
import numpy as np
import time
import datetime
import RPi.GPIO as GPIO
from time import sleep

#logger = getLogger('system_logger.'+__name__)  

#Iridium parameters - fixed for now
modemPort = '/dev/ttyUSB0' #config.getString('Iridium', 'port')
modemBaud = 19200 #config.getInt('Iridium', 'baud')
modemGPIO =  16 #config.getInt('Iridium', 'modemGPIO')
formatType = 10 #config.getInt('Iridium', 'formatType')
call_interval = 60 #config.getInt('Iridium', 'call_interval')
call_time = 10 #config.getInt('Iridium', 'call_time')
timeout=60 #some commands can take a long time to complete

packet_type = 1
id =0

#set up GPIO pins for modem control
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(modemGPIO,GPIO.OUT)

#modem_initialized = False #set global modem state

#open binary data file and return bytes
def open_bin(binfile):
    try:
        with open(binfile, 'rb') as f:
            bytes=bytearray(f.read())
    except FileNotFoundError:
        print('file not found: {}'.format(binfile))   
    except Exception as e:
        print('error opening file: {}'.format(e))
    return bytes

def init_modem():
    #power on GPIO enable pin
    try:
        GPIO.output(modemGPIO,GPIO.HIGH)
        print('power on modem...')
        sleep(3)
        print('done')
    except Exception as e:
        print('error powering on modem')
        print(e)
        
    #open serial port
    print('opening serial port with modem at {0} on port {1}...'.format(modemBaud,modemPort))
    try:
        ser=serial.Serial(modemPort,modemBaud,timeout=timeout)
        print('done')
    except serial.SerialException as e:
        print('unable to open serial port: {}'.format(e))
        return ser
        sys.exit(1)
   
    print('command = AT')
    if get_response(ser,'AT'): #send AT command
        print('command = AT&F')
        if get_response(ser,'AT&F'): #set default parameters with AT&F command 
            print('command = AT&K=0, ')
            if get_response(ser,'AT&K=0'): #important, disable flow control
                print('modem initialized')
                #global modem_initialized
                #modem_initialized = True
                return ser
    else:
        return ser

def get_response(ser,command, response='OK'):
    ser.flushInput()
    command=(command+'\r').encode()
    ser.write(command)
    sleep(0.25)
    try:
        while ser.in_waiting > 0:
            r=ser.readline().decode().strip('\r\n')
            if response in r:
                print('response = {}'.format(r))
                return True
            elif 'ERROR' in response:
                print('response = ERROR')
                return False
    except serial.SerialException as e:
        print('error: {}'.format(e))
        return False


#Get signal quality using AT+CSQF command (see AT command reference).
#Returns signal quality, default range is 0-5. Returns -1 for an error or no response
#Example modem output: AT+CSQF +CSQF:0 OK    
def sig_qual(ser, command='AT+CSQ'):
    ser.flushInput()
    ser.write(command+'\r'.encode())
    print('command = {}, '.format(command))
    r=ser.read(25).decode()
    if 'CSQ:' in r:
        r=r[9:15]
        print('response = {}'.format(r))
        return r[14] #return signal quality (0-5)
    elif 'ERROR' in r:
        print('response = ERROR')
        return -1
    else:
        print('unexpected response: {}'.format(r))  
        return -1

#send binary message to modem buffer and transmit
#returns true if trasmit command is sent, but does not mean a successful transmission
#checksum is least significant 2 bytes of sum of message, with hgiher order byte sent first
#returns false if anything goes wrong
def transmit_bin(ser,msg,bytelen):

    #if modem_initialized == False:
       # print('modem not initialized')
       # return False
    
    ser.flushInput()
    ser.write('AT+SBDWB='+str(bytelen)+'\r').encode() #command to write bytes, followed by number of bytes to write
    print('command = AT+SBDWB, ')
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        print('response = READY')
        ser.flushInput()
        ser.write(msg) #pass bytes to modem
        checksum=sum(msg) #calculate checksum value
        ser.write(chr(checksum >> 8)) #first byte of 2-byte checksum (shift bytes right by 8 bits)
        ser.write(chr(checksum & 0xFF)) #second byte of checksum
    
        print('passing message to modem buffer')
        r=ser.read(3).decode() #read response to get result code from SBDWB command (0-4)
        try:
            r=r[2] #result code of expected response
            print('response = {}'.format(r))
            if r == 0: #response of zero = successful write, ready to send
                ser.flushInput()
                ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                print('command = AT+SBDIX')
                r=ser.read(36).decode()
                if '+SBDIX: ' in r:
                    r=r[11:36] #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                    r=r.strip('\r') #remove any dangling carriage returns
                    print('response = {}'.format(r)) 
                    return True
            else:
                return False
        except IndexError:
            print('no response from modem')
            return False
    else:
        return False
    
#same as transmit_bin but sends ascii text using SBDWT command instead of bytes
def transmit_ascii(ser,msg):
    #checks before attempting to send
    #if modem_initialized == False:
        #print('modem not initialized')
        #return False 
       
    msg_len=len(msg)
    if msg_len > 340: #check message length
        print('message too long. must be 340 bytes or less')
        return False
    
    if not msg.isascii(): #check for ascii text
        print('message must be ascii text')
        return False
    
    ser.flushInput()
    ser.write(b'AT+SBDWT\r') #command to write text to modem buffer
    print('command = AT+SBDWT')
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        print('response = READY')
        ser.flushInput()
        ser.write(msg + '\r'.encode()) #pass bytes to modem. Must have carriage return
        print('passing message to modem buffer')
        r=ser.read(msg_len+9).decode() #read response to get result code (0 or 1)
        if 'OK' in r:
            index=msg_len+2 #index of result code
            r=r[index:index+1] 
            print('response = {}'.format(r))        
            if r == 0:
                ser.flushInput()
                print('command = AT+SBDIX')
                ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                r=ser.read(36).decode()
                if '+SBDIX: ' in r:
                    r=r[11:36] #get command response in the form +SBDIX:<MO status>,<MOMSN>,<MT status>,<MTMSN>,<MT length>,<MT queued>
                    r=r.strip('\r') #remove any dangling carriage returns
                    print('response = {}'.format(r)) 
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
def main(payload_data):

    #check for data
    if len(payload_data) == 0:
           print('payload data is empty')
           return 
    
    #initialize modem
    ser = init_modem()
    
    if not modem_initialized:
        print('modem not initialized, unable to send data')
        return
        
 
    #split up payload data into packets    
    #----------------------------------------------------------------------------------------
    index = 0 #byte index
    
    #first packet to send
    header = str(packet_type).encode('ascii') #packet type as as ascii number
    sub_header0 = str(','+str(id)+','+str(index)+','+str(total_bytes)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes0 = payload_data[index:324] #data bytes for packet 0
    packet0 = struct.pack('<s10s', header, sub_header0) + payload_bytes0   
    bytelen0 = len(packet0) #number of bytes to modem
    
    
    #second packet to send
    index = 325
    sub_header1 = str(','+str(id)+','+str(index)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes1 = payload_data[index:652] #data bytes for packet 1    
    packet1 = struct.pack('<s10s', header, sub_header1) + payload_bytes1         
    bytelen1 = len(packet1) #number of bytes to modem
    
    
    #third packet to send
    index = 653
    sub_header2 = str(','+str(id)+','+str(index)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes2 = payload_data[index:980] #data bytes for packet 2
    packet2 = struct.pack('<s10s', header, sub_header2) + payload_bytes2 
    bytelen2 = len(packet2) #number of bytes to modem     
   
    
    #fourth packet to send
    index = 981
    sub_header3 = str(','+str(id)+','+str(index)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes3 = payload_data[index:1244] #data bytes for packet 3
    packet3 = struct.pack('<s10s', header, sub_header3) + payload_bytes3
    bytelen3 = len(packet3) #number of bytes to modem   
        
    id+=1    


    #send packets
    #--------------------------------------------------------------------------------------
    
    transmit_bin(ser,packet0, bytelen0)
    print('sending first packet')

    transmit_bin(ser,packet1, bytelen1)
    print('sending second packet')

    transmit_bin(ser,packet2, bytelen2)
    print('sending third packet')

    transmit_bin(ser,packet3, bytelen3)
    print('sending fourth packet')
    
    
    #turn off modem
    #--------------------------------------------------------------------------------------
    GPIO.output(modemGpio,GPIO.LOW)
    

#if __name__ == "__main__":



