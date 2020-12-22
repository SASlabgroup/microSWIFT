#!/usr/bin/python3
#Read and record temp from 3 sensors
# Partial code by Author: Tony DiCola
#--------------------------------------------------------------
#standard imports
import time,spidev,sys,socket,os
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
#my imports
from utils import *
from config2 import Config
#---------------------------------------------------------------
configDat = sys.argv[1]
configFilename = configDat #Load config file/parameters needed

config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    sys.exit(0)

# Software SPI configuration:
CLK  = config.getInt('Temp', 'CLK')
MISO = config.getInt('Temp', 'MOSI')
MOSI = config.getInt('Temp', 'MISO')
CS   = config.getInt('Temp', 'CS')
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)
#totalRunTime=config.getFloat('Temp', 'TotalRunTime')
# get the requested rate in Hz (records/sec)#
#recordingRate=config.getFloat('Temp', 'RecordingRate')
# get the file name from currentTimeString function 
#dataFile = str(currentTimeString())
# convert to time-between-recordings (sec)
recordingInterval=1./4
#print ("Interval: %.6f" % recordingInterval)

#directory to open a file to write to 
#logDir = config.getString('System', 'LogDir')
# get the file name from currentTimeString function
#dataFile = str(currentTimeString())

#f = open(logDir + '/' + 'BuoyTempData-' + dataFile + '.txt', 'w')
tStart = time.time()
tLastRead = time.time()
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print ("UDP socket successfully created")
except:
    print ("unable to open UDP socket")
    sys.exit()
    
def ConvertVolts(data):
    volts = (data * 3.3)/float(1023)
    volts = round(volts,4)
    return volts
def ConvertTemp(data):
    temp = ((data * 330)/float(1023))-50
    temp = round(temp,4)
    return temp
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
#----------------------------------------------------------------
#Loop Begins
#----------------------------------------------------------------
while True:
    time.sleep(.25)
    tNow = time.time()
    elapsedTime = tNow - tStart
    print (elapsedTime)
    tSinceLastRecord = tNow - tLastRead
    if tSinceLastRecord >= recordingInterval:
        temp_output0 = mcp.read_adc(0)
        temp_output1 = mcp.read_adc(2)
        #temp_output0 = ReadChannel(0)
        #temp_output1 = ReadChannel(1)
        #temp 1
        temp_volts0 = ConvertVolts(temp_output0)
        temp0 = ConvertTemp(temp_output0)
        print(("Temp0 : {} ({}V) {} deg C".format(temp_output0,temp_volts0,temp0)))
        #temp 2
        temp_volts1 = ConvertVolts(temp_output1)
        temp1 = ConvertTemp(temp_output1)
        print(("Temp1 : {} ({}V) {} deg C".format(temp_output1,temp_volts1,temp1)))

        #f.write('%f,%f,%f,%f,%f,%f,%f\n' % (elapsedTime,temp_volts0,temp0,temp_volts1,temp1,temp_volts2,temp2))
        #f.flush()
        #sock.sendto((('%f,%f,%f,%f,%f,%f,%f\n' % (elapsedTime,temp_volts0,temp0,temp_volts1,temp1,temp_volts2,temp2)).encode('utf_8')),(ipAddress,UDPPort))
        tLastRead = tNow
        
    #if (elapsedTime) >= totalRunTime:
     #   break
     #   sys.exit()
#----------------------------------------------------------------
#Loop Ends
#----------------------------------------------------------------
print ("Done!")

