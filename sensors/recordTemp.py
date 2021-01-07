#! /usr/bin/python3

#Read and record temp from sensors
#--------------------------------------------------------------
#standard imports
import time, spidev, sys
from datetime import datetime
import numpy as np
import logging
from logging import *

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

#my imports
from config3 import Config
#---------------------------------------------------------------
configDat = sys.argv[1]
configFilename = configDat #Load config file/parameters needed

config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    sys.exit(0)

#set up logging
logDir = config.getString('Loggers', 'logDir')
LOG_LEVEL = config.getString('Loggers', 'DefaultLogLevel')
#format log messages (example: 2020-11-23 14:31:00,578, recordTemp - info - this is a log message)
#NOTE: TIME IS SYSTEM TIME
LOG_FORMAT = ('%(asctime)s, %(filename)s - [%(levelname)s] - %(message)s')
#log file name (example: home/pi/microSWIFT/recordGPS_23Nov2020.log)
LOG_FILE = (logDir + '/' + 'recordTemp' + '_' + datetime.strftime(datetime.now(), '%d%b%Y') + '.log')
logger = getLogger('system_logger')
logger.setLevel(LOG_LEVEL)
logFileHandler = FileHandler(LOG_FILE)
logFileHandler.setLevel(LOG_LEVEL)
logFileHandler.setFormatter(Formatter(LOG_FORMAT))
logger.addHandler(logFileHandler)

#system parameters
dataDir = config.getString('System', 'dataDir')
floatID = config.getString('System', 'floatID') 
projectName = config.getString('System', 'projectName')
payLoadType = config.getInt('System', 'payLoadType')
badValue = config.getInt('System', 'badValue')
numCoef = config.getInt('System', 'numCoef')
Port = config.getInt('System', 'port')
payloadVersion = config.getInt('System', 'payloadVersion')
burst_seconds = config.getInt('System', 'burst_seconds')
burst_time = config.getInt('System', 'burst_time')
burst_int = config.getInt('System', 'burst_interval')

#temp configuration
rec_interval = config.getFloat('Temp', 'rec_interval')
temp_samples = int(burst_seconds/rec_interval)

# Software SPI configuration:
CLK  = config.getInt('Temp', 'CLK')
MISO = config.getInt('Temp', 'MISO')
MOSI = config.getInt('Temp', 'MOSI')
CS   = config.getInt('Temp', 'CS')
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


def get_temp():

    try:
       adc_0 = mcp.read_adc(0) #read output from ADC channel 0
    except Exception as e:
        logger.info(e)
        logger.info('error reading temperature data')
    #temp calculation. see TMP36 data sheet for calculation.
    raw_temp = (330*adc_0/1024)-50
    raw_temp = round(raw_temp,2)
    return raw_temp

def get_mean_temp(temp_array):
    
    mean_temp = np.mean(temp_array)
    return mean_temp

def main():
     #make empty numpy array to write to
    temp = np.empty(temp_samples)

    logger.info("---------------recordTemp.py------------------")
    logger.info(sys.version)

    while True:
        # at burst time interval
        now = datetime.utcnow()
        if  now.minute == burst_time or now.minute % burst_int == 0 and now.second == 0:
            logger.info("starting burst")
            #create new file for burst interval
            fname = dataDir + 'microSWIFT'+floatID + '_Temp_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
            logger.info("file name: %s" %fname)
            
            with open(fname, 'w',newline='\n') as temp_out:
                
                logger.info('open file for writing: %s' %fname)
                
                #get first sample at time zero
                isample = 0
                t_start = time.time()
                t_end = time.time() + burst_seconds #get end time for burst
                while time.time() <= t_end and isample < temp_samples:
                    
                    #if at a rec_interval, record temp and add to np array
                    if (int(time.time())-int(t_start)) % rec_interval == 0:
                        temp_sample = get_temp()
                        timestamp='{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())
                        temp_out.write('%s,%15.10f\n' % (timestamp, temp_sample))
                        temp_out.flush()
                        temp[isample] = temp_sample
                        isample += 1
                        time.sleep(0.99*rec_interval)
                
                logger.info('end of burst')   
                logger.info('number of samples expected = %d' % temp_samples)   
                logger.info('number of samples recorded = %d' % (isample))   
                    
            mean_temp = get_mean_temp(temp)
            logger.info('mean temperature = %f' % mean_temp)
            sys.exit(0)

        time.sleep(0.25) 
    
#run main function unless importing as a module
if __name__ == "__main__":
    main()
