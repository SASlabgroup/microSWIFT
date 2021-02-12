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
from numpy import msg

#Iridium parameters - fixed for now
modemPort = '/dev/tty/USB0' #config.getString('Iridium', 'port')
modemBaud = 19200 #config.getInt('Iridium', 'baud')
modemGPIO =  16 #config.getInt('Iridium', 'modemGPIO')
formatType = 10 #config.getInt('Iridium', 'formatType')
call_interval = 60 #config.getInt('Iridium', 'call_interval')
call_time = 10 #config.getInt('Iridium', 'call_time')
timeout=60 #some commands can take a long time to complete

payloadType='7'.encode('ascii')
sensorType=50
packetType = 1
id=0
port=1

#set up GPIO pins for modem control
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(modemGpio,GPIO.OUT)

#open binary data and return bytes
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
    GPIO.output(modemGPIO,GPIO.HIGH)
    print('power on modem...',end='')
    sleep(3)
    print('done')
    #open serial port
    print('opening serial port with modem at {0} on port {1}...'.format(baud,modemPort),end='')
    try:
        ser=serial.Serial(modemPort,modemBaud,timeout)
        print('done')
    except SerialException:
        print('unable to open serial port')
        sys.exit(1)
    ser.flushInput()    
    ser.write(b'AT\r') #send AT command
    print('command = AT, ',end='')
    get_response()
    ser.flushInput()
    ser.write(b'AT&F\r') #set default parameters with AT&F command
    print('command = AT&F, ',end='')
    get_response()
    ser.flushInput()
    ser.write(b'AT&K=0\r') #important, disable flow control
    print('command = AT&K=0, ',end='')
    get_response()
    
    print('modem initialized')

def get_response(response='OK'):
    try:
        while ser.in_waiting > 0:
            r=ser.readline().decode().strip(b'\r\n')
            if response in r:
                print('response = {}'.format(r))
                return True
            elif 'ERROR' in response:
                print('response = ERROR')
                return False
    except SerialException as e:
        print('error: {}'.format(e))


#Get signal quality using AT+CSQF command (see AT command reference).
#Returns signal quality, default range is 0-5. Returns -1 for an error or no response
#Example modem output: AT+CSQF +CSQF:0 OK    
def sig_qual(command='AT+CSQ'):
    ser.flushInput()
    ser.write(command+'\r'.encode())
    print('command = {}, '.format(command),end='')
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
def transmit_bin(msg,bytelen,checksum):
    ser.flushInput()
    ser.write('AT+SBDWB='+str(bytelen)+'\r').encode() #command to write bytes, followed by number of bytes to write
    print('command = AT+SBDWB, ',end='')
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
                print('command = AT+SBDIX, ',end='')
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
def transmit_ascii(msg):
    msg_len=len(msg)
    if msg_len < 340: #check message length
        print('message too long. must be 340 bytes or less')
        return False
    if not msg.isascii(): #check for ascii text
        print('message must be ascii text')
        return Fasle
    
    ser.flushInput()
    ser.write(b'AT+SBDWT\r') #command to write text to modem buffer
    print('command = AT+SBDWT, ',end='')
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        print('response = READY')
        ser.flushInput()
        ser.write(msg.encode()+'\r') #pass bytes to modem. Must have carriage return
        print('passing message to modem buffer, ',end='')
        r=ser.read(msg_len+9).decode() #read response to get result code (0 or 1)
        if 'OK' in r:
            index=msg_len+2 #index of result code
            r=r[index:index+1] 
            print('response = {}'.format(r))        
            if r == 0:
                ser.flushInput()
                ser.write(b'AT+SBDIX\r') #start extended Iridium session (transmit)
                print('command = AT+SBDIX, ',end='')
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
def main():
    
    GPIO.output(modemGpio,GPIO.HIGH) #turn modem on
    
    #-------------------------------------------------------
    if PayLoadType == 50:
        payloadSize =  (16 + 7*42)*4 
        eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, PayLoadType))
        total_bytes = struct.calcsize('sbbhfff42f42f42f42f42f42f42ffffffffiiiiii') -3

    else:
        payloadSize =  (5 + 7*42)*4
        eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, PayLoadType))
        total_bytes = struct.calcsize('sbbhfff42f42f42f42f42f42f42ffff') -3

    #create header and first sub header according to SWIFT payload spec. see 'UW-APL v4.0.1.pdf'
    header = str(packetType).encode('ascii')
    sub_header_0 = str(','+str(id)+','+str(0)+','+str(total_bytes)+':').encode('ascii')
    
    # 1st message sent 
    dataToSend0= (struct.pack('<ss2ssss4sssbbhfff',
                                header,sub_header_0,
                                payloadType,
                                sensorType,port,payloadSize,
                                Hs,Peakwave_Period,Peakwave_dirT) +
                                struct.pack('42f',*WaveSpectra_Energy) +
                                struct.pack('35f\r',*WaveSpectra_Freq[0:35]))
    
    print (struct.unpack('<5sss4sssbbhfff42f35f',dataToSend0))
    bytelen0  = struct.calcsize('sbbhfff42f35f') +9
    print ('bytelen0',bytelen0)
    
    
    

    # 2nd message sent
    bytestart = struct.calcsize('sbbhfff42f35f')-3
    print ('bytestart 1',bytestart)
    dataToSend1=(struct.pack('<5s3ss7f', packetTypeId,str(bytestart),':',
                 *WaveSpectra_Freq[35:42]) +
                 struct.pack('42f',*WaveSpectra_a1) +
                 struct.pack('33f\r',*WaveSpectra_b1[0:33]))
    print (struct.unpack('<5s3ss7f42f33f', dataToSend1))
    
    bytelen1 = struct.calcsize('7f42f33f') +9
    print ('bytelen1',bytelen1)




    # 3rd message sent
    bytestart = struct.calcsize('sbbhfff42f42f42f33f')-3
    print ('bytestart 2',bytestart)
    dataToSend2=(struct.pack('<5s3ss9f', packetTypeId,str(bytestart),':',
                 *WaveSpectra_b1[33:42])+
                 struct.pack('42f',*WaveSpectra_a2) +
                 struct.pack('31f\r',*WaveSpectra_b2[0:31]))
    print (struct.unpack('<5s3ss9f42f31f', dataToSend2))
    
    bytelen2 = struct.calcsize('9f42f31f') +9
    print ('bytelen2',bytelen2)
    
    id+=1
    
    
    if PayLoadType==50:
        # 4th message sent
        bytestart = struct.calcsize('sbbhfff42f42f42f42f42f31f')-3 
        dataToSend3=(struct.pack('<5s3ss11f', packetTypeId,str(bytestart),':',
                 *WaveSpectra_b2[31:42])+
                 struct.pack('42f',*checkdata) +
                 struct.pack('fffffffiiiiii\r',lat,lon,MeanTemp,MeanVoltage,u,v,z,
                 int(now.year),int(now.month),int(now.day),
                 int(now.hour),int(now.minute),int(now.second)))
        print (struct.unpack('<5s3ss11f42ffffffffiiiiii', dataToSend3))
        bytelen3 = struct.calcsize('11f42ffffffffiiiiii') +9 
        print ('bytelen3',bytelen3)
    else:
        print ("[%.3f] - ERROR: Incorrect pay load type, try again" % elapsedTime)
        eventLog.error('[%.3f] - ERROR: Incorrect pay load type, try again' % elapsedTime)
        sys.exit()
        
        
        
        

    print ('----- dataToSend0 =')
    print (dataToSend0)
    send_sbd_msg(dataToSend0,bytelen0,modemPort,modemBaud,MakeCall,eventLog,elapsedTime,modemGpio)

    print ('----- dataToSend1 =')
    print (dataToSend1)
    send_sbd_msg(dataToSend1,bytelen1,modemPort,modemBaud,MakeCall,eventLog,elapsedTime,modemGpio)

    print ('----- dataToSend2 =')
    print (dataToSend2)
    send_sbd_msg(dataToSend2,bytelen2,modemPort,modemBaud,MakeCall,eventLog,elapsedTime,modemGpio)
    
    print ('----- dataToSend3 =')
    print (dataToSend3)
    send_sbd_msg(dataToSend3,bytelen3,modemPort,modemBaud,MakeCall,eventLog,elapsedTime,modemGpio)
    
 
    
    

#run main function unless importing as a module
if __name__ == "__main__":

#turn on modem and initalize serial port

#get argument passed for message

#send 
if len(sys.argv) != 2:
        print('provide an ascii text message to send')
        sys.exit(1)

    sys.argv[1] = msg
    transmit_ascii(msg)

