#!/usr/bin/python3

#This script opens a serial connection with a RockBlock 9602 SBD modem and
#transmits binary data that is passed to the main function

from gpiozero import OutputDevice
import serial
import sys
from time import sleep
import logging
import struct
logging.basicConfig()
import numpy as np

addr =  '/dev/ttyUSB1'
baud = 19200

 #initialize gpio pin 21 as modem on/off control
modem = OutputDevice(21)

def send_sbd_msg(message,bytelen):
    #turn modem on using GPIO pins
    logger = logging.getLogger('send_sbd_data')
    print('initializing SBD modem')
    modem.on()
    #create serial object and open port
    sbd = serial.Serial(addr, baud, timeout=1)

    if sbd.isOpen():
        try:
            sbd.reset_input_buffer()  #renamed since version 3.0
            sbd.reset_output_buffer()

            #issue AT command and check for OK response
            sleep(8)
            sbd.write('AT\r'.encode())
            status = sbd.readlines()
            print(status)
            #get signal strength
            sbd.write('AT+CSQ\r'.encode())
            signal_strength = sbd.readlines()
            print(signal_strength)

            #if response[1].decode("ascii").rstrip("\r\n"))=='OK':

            #write data to MO buffer
            sleep(8)

            print 'length in bytes =',bytelen

            sbd.write(('AT+SBDWB='+str(bytelen) + '\r').encode())
            sleep(8)
            reply = sbd.readlines()
            print(reply)

            checksum = sum(bytearray(message))
            print 'checksum = ',checksum

            print 'message ',message
            sbd.write(message)
            sleep(10)
            print 'wrote message ',reply
            sbd.write(chr(checksum >> 8))
            sbd.write(chr(checksum & 0xFF))
            sleep(10)
            reply = sbd.readlines()
            print('wrote checksum ',reply)



            #send SBD message
            #sbd.write('AT+SBDIX\r'.encode())
            sleep(10)
            reply = sbd.readlines()
            print(reply)
            #put modem to sleep
            sleep(10)
            logger.info("powering down SBD modem")
            modem.off()

        except Exception as e1:
            logger.error("Error communicating...: " + str(e1))


def main(idStr,PayLoadType,FormatType,Port,DataSize,SigwaveHeight,
    Peakwave_Period,Peakwave_dirT,WaveSpectra_Energy,WaveSpectra_Freq,
    WaveSpectra_a1,WaveSpectra_b1,WaveSpectra_a2,WaveSpectra_b2,checkdata,
    lat,lon,temp,u,v,z,systime):
    
    # multiple packets
    #turn modem on using GPIO pins
    logger = logging.getLogger('send_sbd_data')
    logger.info('initializing SBD modem')
    modem.on()
    #create serial object and open port               
    sbd = serial.Serial(addr, baud, timeout=1)
    
    logger.info('opening port')


    #Packet Structure
    #<packet-type> <sub-header> <data>
    #Sub-header 0:
    #    ,<id>,<start-byte>,<total-bytes>:
    #Sub-header 1 thru N:
    #    ,<id>,<start-byte>:

#-------------------------------------------------------
    PayLoadSize =  (12 + 7*42)*4
    packetType = 1
    packetTypeId = '1,' + idStr + ','
    SizeInBytes = struct.calcsize('sbbhfff42f42f42f42f42f42f42fffffffffffff') -3
    print 'SizeInBytes',SizeInBytes
    print str(packetType)
    print idStr
    print 'SizeInBytes',str(SizeInBytes)
    print 'PayLoadSize',PayLoadSize

    dataToSend0= (struct.pack('<5sss4sssbbhfff',packetTypeId, str(0),',',
        str(SizeInBytes),':',str(PayLoadType),
        FormatType,Port,PayLoadSize,
        SigwaveHeight,Peakwave_Period,Peakwave_dirT) +
        struct.pack('42f',*WaveSpectra_Energy) +
        struct.pack('35f\r',*WaveSpectra_Freq[0:35]))
    bytelen0  = struct.calcsize('sbbhfff42f35f') + 9
    print 'bytelen0',bytelen0

    bytestart = struct.calcsize('sbbhfff42f35f')-3
    print 'bytestart 1',bytestart
    dataToSend1=(struct.pack('<5s3ss7f', packetTypeId,str(bytestart),':',
                 *WaveSpectra_Freq[35:42]) +
                 struct.pack('42f',*WaveSpectra_a1) +
                 struct.pack('33f\r',*WaveSpectra_b1[0:33]))
    bytelen1 = struct.calcsize('7f42f33f') + 9
    bytestart = struct.calcsize('sbbhfff42f42f42f33f')-3
    print 'bytestart 2',bytestart
    dataToSend2=(struct.pack('<5s3ss9f', packetTypeId,str(bytestart),':',
                 *WaveSpectra_b1[33:42])+
                 struct.pack('42f',*WaveSpectra_a2) +
                 struct.pack('31f\r',*WaveSpectra_b2[0:31]))
    bytelen2 = struct.calcsize('9f42f31f') + 9

    bytestart = struct.calcsize('sbbhfff42f42f42f42f42f31f')-3
    print 'bytestart3',bytestart
    dataToSend3=(struct.pack('<5s3ss11f', packetTypeId,str(bytestart),':',
                 *WaveSpectra_b2[31:42])+
                 struct.pack('42f',*checkdata) + 
                 struct.pack('ffffffiiiiii\r',lat,lon,temp,u,v,z,
                 int(systime.tm_year), int(systime.tm_mon),int(systime.tm_m_day),
                 int(systime.tm_hour), int(systime.tm_min),int(systime.tm_sec))
year,month,day,hour,minute,second))
    bytelen3 = struct.calcsize('11f42fffffffiiiiii') + 9
    print 'bytelen3',bytelen3

    print '----- dataToSend0 ='
    print dataToSend0
    print 'byte len =',bytelen0
    send_sbd_msg(dataToSend0,bytelen0)

    print '----- dataToSend1 ='
    print dataToSend1
    print 'byte len ',bytelen1
    send_sbd_msg(dataToSend1,bytelen1)

    print '----- dataToSend2 ='
    print dataToSend2
    print 'byte len ',bytelen2
    send_sbd_msg(dataToSend2,bytelen2)
    print '----- dataToSend3 ='
    print dataToSend3
    print 'byte len ',bytelen3
    send_sbd_msg(dataToSend3,bytelen3)

#run main function unless importing as a module
if __name__ == "__main__":
    main()

