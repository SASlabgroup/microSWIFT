import serial
import time, sys
from config2 import Config
import datetime

#Load config file 
configDat =  sys.argv[1]
configFilename = configDat #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	sys.exit(0)

#system parameters
float_id = config.getString('System', 'floatID') #double check the type 

#Log parameters
dataDir = config.getString('LogLocation', 'dataDir')

#GPS parameters 
usb_addr = config.getString('GPS', 'port')
baud = config.getInt('GPS', 'baud')

burst_interval = config.getInt('Iridium', 'burstInt')
systime = time.gmtime()

dname = time.strftime('%d%b%Y',systime)
tname = time.strftime('%H:%M:%S',systime) 
fname = (dataDir + float_id + 
        '_GPS_' + dname + '_' + tname +'UTC_burst_' + 
        str(burst_interval) + '.dat')
print (fname)

gpsPort = (serial.Serial('/dev/ttyS0',9600))

logDir = '/home/pi/microSWIFT/testmicroWave/data/'

logFile = open(fname, 'w')
print (logFile)
while True: 
    line = gpsPort.readline()
    print (line)
    logFile.write(line)
    logFile.flush()
    time.sleep(1)