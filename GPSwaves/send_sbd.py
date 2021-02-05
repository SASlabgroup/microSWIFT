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
from builtins import False

#Iridium parameters - fixed for now
modemPort = '/dev/tty/USB0' #config.getString('Iridium', 'port')
modemBaud = 19200 #config.getInt('Iridium', 'baud')
modemGPIO =  16 #config.getInt('Iridium', 'modemGPIO')
formatType = 10 #config.getInt('Iridium', 'formatType')
call_interval = 60 #config.getInt('Iridium', 'call_interval')
call_time = 10 #config.getInt('Iridium', 'call_time')
timeout=60 #some commands can take a long time to complete

#set up GPIO and turn on modem
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(modemGpio,GPIO.OUT)

#open file and read bytes
try:
    with open(telem_file, 'rb') as f:
        bytes=f.read()
except FileNotFoundError:
    print('file not found: {}'.format(telem_file))   
except Exception as e:
    print('error opening file: {}'.format(e))
    

#split up file into multiple message packets with headers






#open serial port with modem
#power on
print('power on modem...',end='')
GPIO.output(modemGPIO,GPIO.HIGH)
sleep(3)
print('done')
#open serial port
print('opening serial port with modem at {0} on port {1}...'.format(baud,modemPort),end='')
ser=serial.Serial(modemPort,modemBaud,timeout)
print('done')

#Set default parameters with AT&F command
ser.write('AT&F\r'.encode())
print('command = ',end='')

ser.write('AT&K=0\r'



#test with AT command, should return 'OK'
def status():
    ser.flushInput()
    ser.write('AT\r'.encode())
    print('command = AT, ',end='')
    while ser.in_waiting > 0:
        r=ser.readline().decode().strip('\r\n')
        if r == 'OK':
            print('response = {}'.format(r))
            return True
        elif r == 'ERROR':
            print('response = {}'.format(r))
            return False
    return False

#Get signal quality using AT+CSQF command (see AT command reference).
#Returns signal quality, default range is 0-5. Returns -1 for an error or no response
#Example modem output: AT+CSQF +CSQF:0 OK    
def sig_qual():
    ser.flushInput()
    ser.write('AT+CSQF\r'.encode())
    print('command = AT+CSQF, ',end='')
    while ser.in_waiting > 0:
        r=ser.readline().decode().strip('\r\n')
        if 'CSQF:' in r:
            print('response = {}'.format(r))
            qual = r.split(':')[1]
            return qual
        elif r == 'ERROR':
            print('response = {}'.format(r))
            return -1
    return -1

#Send binary message to modem buffer and transmit
#Returns true if trasmit command is sent, but does not mean a successful transmission
#Returns false if anything goes wrong.
def transmit_bin(msg,bytelen):
    ser.flushInput()
    ser.write(('AT+SBDWB='+str(bytelen)+'\r').encode()) #command to write bytes, followed by number of bytes to write
    print('command = AT+SBDWB, ',end='')
    r = ser.read_until('READY'.encode()).decode() #block until READY message is received
    if 'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        ser.write(msg) #pass bytes to modem. Must include 2 byte checksum
    else:
        return False
    ser.flushInput()
    ser.write('AT+SBDIX\r').encode()) #start extended Iridium session (transmit)
    print('command = AT+SBDIX, ',end='')
    r=ser.read_until('SBDIX: '.encode()).decode()
    if '+SBDIX: ' in r:
        r=ser.read_until('\r'.encode()) #get command response 
        r=r.decode().strip('\r') #remove carriage return and convert to string
        print('response = {}'.format(r))
        r=r.split(',')
        return True
    else:
        return False
        

def transmit_ascii(message):
    
    


def write_binary(cmd):
   ser.flushInput() 
   ser.write(cmd)
   
def write_ascii(cmd):
    cmd = cmd.encode()
    ser.flushInput()
    ser.write(cmd)

#send messages to modem buffer and then send out

def send_ascii(message):    
   

#check for text data rathen than binary

    ser.write(('AT+SBDWT='+message + '\r').encode()) #command to write text to modem buffer
    
    ser.write('AT+SBDIX\r').encode())
   
    
def send_binary(message):
    
    








#------------------------------------------------------------------------

# Takes in message created from GPS, IMU, TEMP, VOLT. Complete message i s
# split up into 4 different messages, all converted into binary form
# messages are sent out through iridium modem 
def send_sbd_msg(message,
                 bytelen,
                 modemPort,
                 modemBaud,
                 MakeCall,
                 eventLog,
                 elapsed,
                 modemGpio):
    
 
    tStart = time.time()
    sleepTime = 6
    GPIO.output(modemGpio,GPIO.HIGH) #turn modem on
    
    #calculate elapsed time
    elapsedTime = getElapsedTime(tStart,elapsed)

    print('[%.3f] - Initializing SBD modem' % elapsedTime)
    eventLog.info('[%.3f] - Initializing SBD modem' % elapsedTime)

    #create serial object and open port
    sbd = serial.Serial(modemPort, modemBaud, timeout=1)
    try: 
        sbd.open() # Open port 
    except:
        print ("port already open")
        
    if sbd.isOpen():
        try:
            #calculate elapsed time here
            elapsedTime = getElapsedTime(tStart,elapsed)
            
            eventLog.info('[%.3f] - Start pushing data out iridium modem' % elapsedTime)

            sbd.flushInput()  # clear inpupt buffer
            sbd.flushOutput() # clean output buffer
            
            #sys.stdout.flush()
            #sys.stdin.flush()
            sleep(2)
            #issue AT command and check for OK response
            sbd.write('AT\r'.encode())
            status = sbd.readlines()
            print('[%.3f] - Iridium modem status: %s' % (elapsedTime,status))
            
            #get signal strength
            sbd.write('AT+CSQ\r'.encode())
            signal_strength = sbd.readlines()
            print('[%.3f] - Iridium modem signal strength: %s' % (elapsedTime,signal_strength))
            eventLog.info('[%.3f] - Send AT and AT+CSQ. Response: %s, %s' % (elapsedTime,status,signal_strength))

            #write data to MO buffer
            sleep(sleepTime)
            eventLog.info('[%.3f] - Write data to MO buffer' % elapsedTime)

            print ('[%.3f] - Length in bytes: %d' % (elapsedTime, bytelen))
            eventLog.info('[%.3f] - Length in bytes: %d' % (elapsedTime, bytelen))
            
            sbd.write(('AT+SBDWB='+str(bytelen) + '\r').encode())
            sleep(sleepTime)
            reply = sbd.readlines()
            print('[%.3f] - Write to MO buffer reply: %s' % (elapsedTime,reply))
            eventLog.info('[%.3f] - Write to MO buffer reply: %s' % (elapsedTime, reply))
            
            checksum = sum(bytearray(message))
            print('[%.3f] - Checksum: %s, message: %s' % (elapsedTime,checksum,message))
            eventLog.info('[%.3f] - Checksum: %s, message: %s' % (elapsedTime,checksum,message))

            sbd.write(message)
            sleep(sleepTime)
            print ('[%.3f] - wrote message: %s' % (elapsedTime,reply))
            
            sbd.write(chr(checksum >> 8))
            sbd.write(chr(checksum & 0xFF))
            
            reply = sbd.readlines()
            print('[%.3f] - Wrote message and checksum to modem. Response: %s' % (elapsedTime, reply))
            eventLog.info('[%.3f] - Wrote message and checksum to modem. Response: %s' % (elapsedTime, reply))


            if (MakeCall):
            #send SBD message
                sbd.write('AT+SBDIX\r'.encode())
                eventLog.info('[%.3f] - Send SBD message' % elapsedTime)
                print ('[%.3f] - Send SBD message' % elapsedTime)
                
            sleep(10)
            reply = sbd.readlines()
            eventLog.info('[%.3f] - Reply to send SBD message: %s' %(elapsedTime, reply))
            print('[%.3f] - Reply to send SBD message: %s' %(elapsedTime, reply))
            #sleep(sleepTime)

        except Exception as e1:
            eventLog.error("Error communicating...: " + str(e1))
            
    eventLog.info('[%.3f] - Powering down SBD modem and closing port' % elapsedTime)
    GPIO.output(modemGpio,GPIO.LOW)
    print ("Closing modem port")
    sbd.flushInput()  # clear inpupt buffer
    sbd.flushOutput() # clean output buffer
    sbd.close()
#--------------------------------------------------------------------------------------------
#MAIN
#
#Packet Structure
#<packet-type> <sub-header> <data>
#Sub-header 0:
#    ,<id>,<start-byte>,<total-bytes>:
#Sub-header 1 thru N:
#    ,<id>,<start-byte>:
#--------------------------------------------------------------------------------------------
def main(formatType,
         Port,
         Hs,
         Peakwave_Period,
         Peakwave_dirT,
         WaveSpectra_Energy,
         WaveSpectra_Freq,
         WaveSpectra_a1,
         WaveSpectra_b1,
         WaveSpectra_a2,
         WaveSpectra_b2,
         checkdata,
         lat,lon,
         MeanTemp,
         u,v,z,
         now,
         modemPort,
         modemBaud,
         PayLoadType,
         payloadVersion,
         MakeCall,
         eventLog,
         elapsedTime,
         decStr,
         MeanVoltage,
         modemGpio):
    
    GPIO.output(modemGpio,GPIO.HIGH) #turn modem on

    print ("UNRECORDED VALUES")
    print ("Pay load", PayLoadType)
    print ("voltage", MeanVoltage)
    print ("temp", MeanTemp)
    print ("Hs", Hs)
    print ("lon", lon)
    print ("lat", lat)
    print ("============================")
    #time.sleep(1)
    #f = open("/home/pi/Desktop/newFile.txt","w+")
    
    #-------------------------------------------------------
    if PayLoadType == 50:
        PayLoadSize =  (16 + 7*42)*4 
        eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, PayLoadType))
        SizeInBytes = struct.calcsize('sbbhfff42f42f42f42f42f42f42ffffffffiiiiii') -3

    else:
        PayLoadSize =  (5 + 7*42)*4
        eventLog.info('[%.3f] - Payload type: %d' % (elapsedTime, PayLoadType))
        SizeInBytes = struct.calcsize('sbbhfff42f42f42f42f42f42f42ffff') -3

    packetType = 1
    packetTypeId = '1,' + decStr + ','
    eventLog.info('[%.3f] - PacketTypeId: %s' % (elapsedTime, packetTypeId))

    print ('[%.3f] - SizeInBytes: %s' % (elapsedTime,str(SizeInBytes)))
    
    # 1st message sent 
    dataToSend0= (struct.pack('<5sss4sssbbhfff',
                                packetTypeId, str(0),',',str(SizeInBytes),':',
                                str(payloadVersion),
                                PayLoadType,Port,PayLoadSize,
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
    main()

