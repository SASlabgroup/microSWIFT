#! /usr/bin/python2.7

import serial
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(20,GPIO.OUT)


GPIO.output(20,GPIO.HIGH)
    

addr = '/dev/ttyS0'

bootBaud = 9600         #baud rate of serial device#
bootPort = serial.Serial(addr, bootBaud, timeout=1)
print ('writing to port')
#bootPort.write('$PMTK220,250*29\r\n'.encode())
#time.sleep(5)
#bootPort.write('$PMTK251,115200*1F\r\n'.encode())
#bootPort.write('$PMTK220,250*29\r\n'.encode())
time.sleep(5)
bootPort.write('$PMTK251,115200*1F\r\n'.encode())

time.sleep(10)
#bootPort.write(b'PMTK220,250')
data = bootPort.readline()
print(data) 
print ('test')

bootPort.flush()
bootPort.close()

#time.sleep(20)
time.sleep(10)

wantedBaud = 115200
wantedPort = serial.Serial(addr, wantedBaud, timeout=1)
#wantedPort.open()
wantedPort.write('$PMTK220,250*29\r\n'.encode())
while True: 
    data = wantedPort.readline()
    print(data)
'''wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()'''


#print ('writing to port')
'''wantedPort.write(b'PMTK220,250')#*29\r\n'.encode())
print ('change freq')

time.sleep(5)
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()
wantedPort.readline()


#while True: 
    #line = wantedPort.readline()
   # print (wantedPort.readline())
#wantedPort.write('$PMTK220,250*29\r\n'.encode())'''


#Adafruit GPS 
#if sbd.isOpen():
#    print ('writing to port')
#    sbd.write('$PMTK251,115200*1F\r\n')
    #sbd.write('$PMTK220,250*29\r\n')
    #sbd.write(('$PMTK251,115200*1F'))
    #status = sbd.readlines()
    #print(status)

#Berry GPS 
#echo -e -n "\xB5\x62\x06\x00\x14\x00\x01\x00\x00\x00\xD0\x08\x00\x00\x00\xC2\x01\x00\x07\x00\x03\x00\x00\x00\x00\x00\xC0\x7E" > /dev/ttyS0
