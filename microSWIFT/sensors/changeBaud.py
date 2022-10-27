import serial
import time


addr = '/dev/ttyS0'

baud = 9600         
sbd = serial.Serial(addr, baud, timeout=1)

#Adafruit GPS 
if sbd.isOpen():
    print ('writing to port')
    sbd.write('$PMTK251,115200*1F\r\n'.encode())
    
time.sleep(10)

newbaud = 115200   
newsbd = serial.Serial(addr, newbaud, timeout=1)

if newsbd.isOpen():
    print ('writing to port')
    newsbd.write('$PMTK220,250*29\r\n'.encode())