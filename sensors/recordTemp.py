#! /usr/bin/python3

#Read and record temp from sensors
#--------------------------------------------------------------
#standard imports
import time,spidev,sys,socket, os
from datetime import datetime
import numpy as np
import logging
from logging import *

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

#my imports
from utils import *
from config3     import Config
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
temp_samples = int(busrt_seconds/rec_interval)

# Software SPI configuration:
CLK  = config.getInt('Temp', 'CLK')
MISO = config.getInt('Temp', 'MISO')
MOSI = config.getInt('Temp', 'MOSI')
CS   = config.getInt('Temp', 'CS')
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

#-------------------------------------------------------------------
#Loop Begins
#-------------------------------------------------------------------
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
                t_end = time.time() + burst_seconds #get end time for burst
                isample=0
                while time.time() <= t_end or isample < temp_samples:
                    try:
                       analog_output = mcp.read_adc(0) #read output from ADC channel 0
                    except Exception as e:
                        logger.info(e)
                        logger.info('error reading temperature data')
                
                    #temp calculation. see TMP36 data sheet for calculation.
                    raw_temp = (330*analog_output/1024)-50
                    raw_temp = round(temp,2)
                    temp[isample] = raw_temp
                
                
                    timestamp='{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())
           
                
                time.sleep(recInterval)
                tSinceLastRead = tNow - tLastRead
                if (tSinceLastRead >= recInterval):
                    fnow = datetime.utcnow()
                    fdname = fnow.strftime('%d%b%Y')
                    ftname = fnow.strftime('%H:%M:%S')
                
                    temp[isample] = temperature
                
                    print('temp',temp[isample],isample, tempNumSamples)
                    timestring = ("%d,%d,%d,%d,%d,%d" % (fnow.year,
                                                     fnow.month,
                                                     fnow.day,
                                                     fnow.hour,
                                                     fnow.minute,
                                                     fnow.second))
                    timestring = str(timestring)
                    print('TIME ',timestring,fdname,ftname)
                    fid.write('%s,%15.10f\n' %(timestring,temp[isample]))
                    fid.flush()
                    #time.sleep(1)
                    tLastRead = tNow

                #fid.close()
            mean_temperature = np.mean(temp)

            eventLog.info('[%.3f] - Mean temp: %s' % (elapsedTime,mean_temperature))
                
            print('mean temp ',mean_temperature)
            fnameMean = ('microswift_' + floatID +'_' + projectName +'_TempMean.dat')
            eventLog.info('[%.3f] - Mean temp file: %s' % (elapsedTime,fnameMean))
            
            fnameMeanNew = ('microswift_' + floatID +'_' + projectName +'_TempMean_New.dat')
            eventLog.info('[%.3f] - New mean temp file: %s' % (elapsedTime,fnameMeanNew))

            #go to 
            fnameMean_dir = os.path.join(dataDir)
            fnameMeanFile = os.path.join(fnameMean_dir,fnameMean)
            fnameMeanNewFile = os.path.join(fnameMean_dir,fnameMeanNew)
            
            if not (os.path.exists(fnameMeanFile)):
                fid = open(fnameMeanFile,'w')
            else:
                fid = open(fnameMeanFile,'a')
                

            fidNew = open(fnameMeanNewFile,'w')
            print (fnameMean)
            
            #set file permissions to write to 
            os.chmod(fnameMeanFile, 0777)
            os.chmod(fnameMeanNewFile, 0777)
            
            fid.write('%s,%15.10f\n'%(timestring,mean_temperature))
            fidNew.write('%s,%.10f\n'%(timestring,mean_temperature))
            fid.flush()
            fidNew.flush()
            fidNew.close()
            eventLog.info('[%.3f] - End burst interval' % elapsedTime)
            fid.close()
            
        time.sleep(0.5)
        
    
#run main function unless importing as a module
if __name__ == "__main__":
    main()
