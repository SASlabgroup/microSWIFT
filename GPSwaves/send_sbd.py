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

#set up GPIO pins for modem control
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(modemGpio,GPIO.OUT)

#open file and read bytes
try:
    with open(telem_file, 'rb') as f:
        telem_file=bytearray(f.read())
except FileNotFoundError:
    print('file not found: {}'.format(telem_file))   
except Exception as e:
    print('error opening file: {}'.format(e))
    
#parse telemetry file
#-----------------------------------------------------------------------------------------------
def _checkSize(size, expected, name, p_id):
    if size != expected:
        raise Exception("Payload {} {} size {} expected {}".format(p_id,
                                                                   name,
                                                                   size,
                                                                   expected))


def _getDouble(data, index):
    end = index + 8
    return (unpack_from('d', data[index:end])[0], end)


def _getFloat(data, index):
    end = index + 4
    if end > len(data):
        print('Reached end of data unexpectedly')
    return (unpack_from('f', data[index:end])[0], end)


def _getInt1(data, index):
    end = index + 1
    return (ord(data[index:end]), end)


def _getInt2(data, index):
    end = index + 2
    return (unpack_from('h', data[index:end])[0], end)


def _getInt4(data, index):
    end = index + 4
    return (unpack_from('i', data[index:end])[0], end)


# Get Payload type, current valid types are 2 or 3
def _getPayloadType(data):
    (data_type,) = unpack_from('c', buffer(data[0:1]))
    return (data_type, 1)


def processData(p_id, data):
    # Get Payload type, current valid types are 2 or 3
    (data_type, index) = _getPayloadType(data)
    print("payload type: {}".format(data_type))

    index = 1
    if data_type != _4_0:
        print("Invalid payload type: 0x{}".format(codecs.encode(data_type, 
                                                                "hex")))
        sys.exit(1)

    data_len = len(data)
    while index < data_len:
        print("Index: {}".format(index))
        (sensor_type, index) = _getInt1(data, index)
        (com_port, index) = _getInt1(data, index)
        print("Sensor: {}\tCom Port: {}".format(sensor_type, com_port))

        (size, index) = _getInt2(data, index)
        print("Size: {}".format(size))

        if sensor_type == 50:
            index = _processMicroSWIFT(p_id, data, index, size)

        else:
            raise Exception(
                "Payload {} has unknown sensor type {} at index {}".format(
                    p_id, sensor_type, index))


def _processMicroSWIFT(p_id, data, index, size):
    if size == 0:
        print("MicroSWIFT empty")
        return index

    (hs, index) = _getFloat(data, index)
    print("hs {}".format(hs))
    (tp, index) = _getFloat(data, index)
    print("tp {}".format(tp))
    (dp, index) = _getFloat(data, index)
    print("dp {}".format(dp))

    arrays = [ 'e', 'f', 'a1', 'b1', 'a2', 'b2', 'cf']

    # TODO Get the array data
    for array in arrays:
        # 0 - 41
        for a_index in range(0, 42):
            (val, index) = _getFloat(data, index)
            print("{}{} {}".format(array, a_index, val))

    (lat, index) = _getFloat(data, index)
    print("lat {}".format(lat))
    (lon, index) = _getFloat(data, index)
    print("lon {}".format(lon))
    (mean_temp, index) = _getFloat(data, index)
    print("mean_temp {}".format(mean_temp))
    (mean_voltage, index) = _getFloat(data, index)
    print("mean_voltage {}".format(mean_voltage))
    (mean_u, index) = _getFloat(data, index)
    print("mean_u {}".format(mean_u))
    (mean_v, index) = _getFloat(data, index)
    print("mean_v {}".format(mean_v))
    (mean_z, index) = _getFloat(data, index)
    print("mean_z {}".format(mean_z))
    (year, index) = _getInt4(data, index)
    print("year {}".format(year))
    (month, index) = _getInt4(data, index)
    print("month {}".format(month))
    (day, index) = _getInt4(data, index)
    print("day {}".format(day))
    (hour, index) = _getInt4(data, index)
    print("hour {}".format(hour))
    (min, index) = _getInt4(data, index)
    print("min {}".format(min))
    (sec, index) = _getInt4(data, index)
    print("sec {}".format(sec))

    return index


#-----------------------------------------------------------------------------------------------
#open serial port with modem
#power on
print('power on modem...',end='')
GPIO.output(modemGPIO,GPIO.HIGH)
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

#send AT command
ser.write(b'AT\r')
print('command = AT, ',end='')
get_response()

#set default parameters with AT&F command
ser.write(b'AT&F\r')
print('command = AT&F, ',end='')
get_response()

#important, disable flow control
ser.flushInput()
ser.write(b'AT&K=0\r')
print('command = AT&K=0, ',end='')
get_response()

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
#returns false if anything goes wrong
def transmit_bin(msg,bytelen,wb='AT+SBDWB',ix='AT+SBDIX'):
    ser.flushInput()
    ser.write('AT+SBDWB='+str(bytelen)+'\r').encode() #command to write bytes, followed by number of bytes to write
    print('command = AT+SBDWB, ',end='')
    r = ser.read_until(b'READY') #block until READY message is received
    if b'READY' in r: #only pass bytes if modem is ready, otherwise it has timed out
        print('response = READY')
        ser.flushInput()
        ser.write(msg) #pass bytes to modem. Must include 2 byte checksum
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
    
    

#------------------------------------------------------------------------

# Takes in message created from GPS, IMU, TEMP, VOLT. Complete message i s
# split up into 4 different messages, all converted into binary form
# messages are sent out through iridium modem 
def send_sbd_msg
    if sbd.isOpen():
        try:
            
            checksum = sum(bytearray(message))
            print('[%.3f] - Checksum: %s, message: %s' % (elapsedTime,checksum,message))
            eventLog.info('[%.3f] - Checksum: %s, message: %s' % (elapsedTime,checksum,message))


            
            sbd.write(chr(checksum >> 8))
            sbd.write(chr(checksum & 0xFF))
            
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
def main():
    
    GPIO.output(modemGpio,GPIO.HIGH) #turn modem on
    
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

#turn on modem and initalize serial port

#get argument passed for message

#send 
if len(sys.argv) != 2:
        print('provide an ascii text message to send')
        sys.exit(1)

    sys.argv[1] = msg
    transmit_ascii(msg)

