## recordGPS.py - centralized version
'''
Authors: @EJRainville, @AlexdeKlerk, @VivianaCastillo

Description: This function initializes and records GPS data from the onboard GPS sensor. Within the main microSWIFT.py script this is 
run as an asynchronous task at the same time as the recordIMU function. 

'''

# Package imports
import serial, sys, os
from struct import *
from logging import *
from datetime import datetime
import time as t
import pynmea2
from time import sleep

# Raspberry pi GPIO
import RPi.GPIO as GPIO

#Define Config file name and load file
from utils.config3 import Config
configFilename = r'/home/pi/microSWIFT/utils/Config.dat'
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    print("Error loading config file")
    sys.exit(1)

# Set up module level logger
logger = getLogger('microSWIFT.'+__name__)  

#GPS parameters 
dataDir = config.getString('System', 'dataDir')
floatID = os.uname()[1]
gps_port = config.getString('GPS', 'port')
baud = config.getInt('GPS', 'baud')
startBaud = config.getInt('GPS', 'startBaud')
gps_freq = config.getInt('GPS', 'GPS_frequency')
gps_timeout = config.getInt('GPS', 'timeout')
burst_seconds = config.getInt('System', 'burst_seconds')
gps_samples = gps_freq*burst_seconds
gpsGPIO = config.getInt('GPS', 'gpsGPIO')
gps_timeout = config.getInt('GPS','timeout')

# setup GPIO and initialize
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(gpsGPIO,GPIO.OUT)
GPIO.output(gpsGPIO,GPIO.HIGH) #set GPS enable pin high to turn on and start acquiring signal


def recordGPS(end_time):
    # GPS has not been initialized yet
    gps_initialized = False

    # loop while within the recording block and the gps hasn't initialized yet
    while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and gps_initialized==False:

        ##------------ Initalize GPS -------------------------
        logger.info('initializing GPS')
        try:
            #start with GPS default baud
            logger.info("try GPS serial port at 9600")
            ser=serial.Serial(gps_port,startBaud,timeout=1)
            try:
                #set device baud rate to 115200
                logger.info("setting baud rate to 115200 $PMTK251,115200*1F\r\n")
                ser.write('$PMTK251,115200*1F\r\n'.encode())
                sleep(1)
                #switch ser port to 115200
                ser.baudrate=baud
                logger.info("switching to %s on port %s" % (baud, gps_port))
                #set output sentence to GPGGA and GPVTG, plus GPRMC once every 4 positions (See GlobalTop PMTK command packet PDF)
                logger.info('setting NMEA output sentence $PMTK314,0,4,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n')
                ser.write('$PMTK314,0,4,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n'.encode())
                sleep(1)
                #set interval to 250ms (4 Hz)
                logger.info("setting GPS to 4 Hz rate $PMTK220,250*29\r\n")
                ser.write("$PMTK220,250*29\r\n".encode())
                sleep(1)
            except Exception as e:
                logger.info('GPS failed to initialize')
                logger.info(e)
        except Exception as e:
            logger.info('GPS failed to initialize')
            logger.info(e)
                        
        #read lines from GPS serial port and wait for fix
        try:
            #loop until timeout dictated by gps_timeout value (seconds) or the gps is initialized
            while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and gps_initialized==False:
                ser.flushInput()
                ser.read_until('\n'.encode())
                newline=ser.readline().decode('utf-8')
                if not 'GPGGA' in newline:
                    newline=ser.readline().decode('utf-8')
                    if 'GPGGA' in newline:
                        logger.info('found GPGGA sentence')
                        logger.info(newline)
                        gpgga=pynmea2.parse(newline,check=True)
                        logger.info('GPS quality= {}'.format(gpgga.gps_qual))
                        #check gps_qual value from GPGGS sentence. 0=invalid,1=GPS fix,2=DGPS fix
                        if gpgga.gps_qual > 0:
                            logger.info('GPS fix acquired')
                            # Set gprmc line to False and enter while loop to read new lines until it gets the correct line
                            gprmc_line = False
                            #get date and time from GPRMC sentence - GPRMC reported only once every 8 lines
                            while gprmc_line==False:
                                newline=ser.readline().decode('utf-8')
                                if 'GPRMC' in newline:
                                    logger.info('found GPRMC sentence')
                                    # Change value to True so that the while loop exits once a gprmc line is found
                                    gprmc_line = True
                                    try:
                                        gprmc=pynmea2.parse(newline)
                                        nmea_time=gprmc.timestamp
                                        nmea_date=gprmc.datestamp
                                        logger.info("nmea time: {}".format(nmea_time))
                                        logger.info("nmea date: {}".format(nmea_date))
                                        
                                        #set system time
                                        try:
                                            logger.info("setting system time from GPS: {0} {1}".format(nmea_date, nmea_time))
                                            os.system('sudo timedatectl set-timezone UTC')
                                            os.system('sudo date -s "{0} {1}"'.format(nmea_date, nmea_time))
                                            os.system('sudo hwclock -w')
                                            
                                            # GPS is initialized
                                            logger.info("GPS initialized")
                                            gps_initialized = True

                                        except Exception as e:
                                            logger.info(e)
                                            logger.info('error setting system time')
                                            continue	
                                    except Exception as e:
                                        logger.info(e)
                                        logger.info('error parsing nmea sentence')
                                        continue
                t.sleep(1)
            if gps_initialized == False:
                logger.info('GPS failed to initialize, timeout')
        except Exception as e:
            logger.info('GPS failed to initialize')
            logger.info(e)

    ## ------------- Record GPS ---------------------------
    # If GPS signal is initialized start recording
    if gps_initialized:
        #create file name
        GPSdataFilename = dataDir + floatID + '_GPS_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
        logger.info("file name: {}".format(GPSdataFilename))

        logger.info('starting GPS burst')
        try:
            ser.flushInput()
            with open(GPSdataFilename, 'w',newline='\n') as gps_out:
                logger.info('open file for writing: %s' %GPSdataFilename)
                ipos=0
                ivel=0
                while datetime.utcnow().minute + datetime.utcnow().second/60 <= end_time:
                    newline=ser.readline().decode()
                    gps_out.write(newline)
                    gps_out.flush()
            
                    if "GPGGA" in newline:
                        gpgga = pynmea2.parse(newline,check=True)   #grab gpgga sentence and parse
                        #check to see if we have lost GPS fix, and if so, continue to loop start. a badValue will remain at this index
                        if gpgga.gps_qual < 1:
                            logger.info('lost GPS fix, sample not recorded. Waiting 10 seconds')
                            logger.info('lost GPS fix, sample not recorded. Waiting 10 seconds')
                            sleep(10)
                            ipos+=1
                            continue
                        ipos+=1
                    elif "GPVTG" in newline:
                        ivel+=1
                    
                    # If the number of position and velocity samples is enough then and the loop
                    if ipos == gps_samples and ivel == gps_samples:
                        break
                    else:
                        continue
                # Output logger information on samples
                logger.info('Ending GPS burst at {}'.format(datetime.now()))
                logger.info('number of GPGGA samples = {}'.format(ipos))
                logger.info('number of GPVTG samples = {}'.format(ivel))

        except Exception as e:
            logger.info(e, exc_info=True)

        # Output logger information on samples
        logger.info('Ending GPS burst at {}'.format(datetime.now()))
        logger.info('number of GPGGA samples = {}'.format(ipos))
        logger.info('number of GPVTG samples = {}'.format(ivel))
        return GPSdataFilename, gps_initialized

    # If GPS signal is not initialized exit 
    else:
        logger.info("GPS not initialized, exiting")

        #create file name but it is a placeholder
        GPSdataFilename = ''

        # Return the GPS filename to be read into the onboard processing
        return GPSdataFilename, gps_initialized

