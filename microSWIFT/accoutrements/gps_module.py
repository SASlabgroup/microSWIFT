"""
Description: This function initializes and records GPS data from the
onboard GPS sensor. Within the main microSWIFT.py script this is run
as an asynchronous task at the same time as the recordIMU function.

Authors: @EJRainville, @AlexdeKlerk, @VivianaCastillo
"""
try:
    import RPi.GPIO as GPIO
    import serial
except ImportError as e:
    from mocks import mock_rpi_gpio as GPIO
    from mocks import mock_serial as serial
    print(e, "Using mock hardware")

import logging
import os
from datetime import datetime
from time import sleep

import numpy as np
import pynmea2

# Set up module level logger
logger = logging.getLogger('microSWIFT.'+__name__)

class GPS:
    """
    This class is for the GPS component on the RPi.
    """
    def __init__(self, config):
        """
        This method initializes the gps module
        Parameters
        ----------
        config object
        Returns:
        --------
        none
        """
        self.initialized = False
        self.powered_on = False
        try:
            isinstance(config.GPS_GPIO, int)
        except Exception as exception:
            logger.info(exception)
            raise ValueError('input config object is not correct')

        try:
            logger.info('initializing GPS')
            self.gps_freq = config.GPS_SAMPLING_FREQ
            self.gps_gpio = config.GPS_GPIO
            self.floatID = os.uname()[1]
            self.dataDir = config.DATA_DIR
            self.gps_port = config.GPS_PORT
            self.start_baud = config.START_BAUD
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gps_gpio,GPIO.OUT)
            GPIO.setwarnings(False)
            self.initialized = True
            logger.info('GPS initialized')
        except Exception as exception:
            logger.info(exception)
            logger.info('error initializing GPS')

    def power_on(self):
        """
        Power on the GPS module.
        """
        try:
            GPIO.output(self.gps_gpio,GPIO.HIGH)
            logger.info('GPS powered on')
        except Exception as exception:
            logger.info(exception)
            logger.info('not able to turn on GPS')

        try:
            # start with GPS default baud
            logger.info("try GPS serial port at 9600")
            ser=serial.Serial(self.gps_port, self.start_baud,
                              timeout=1)
        except Exception as err:
            logger.info('Serial port did not open')
            logger.info(err)

        try:
            # set device baud rate to 115200
            ser.write('$PMTK251,115200*1F\r\n'.encode())
            sleep(1)
            # switch ser port to 115200
            ser.baudrate = config.baud
            logger.info("switching to %s on port %s" % \
                (config.baud, config.gps_port))
            # set output sentence to GPGGA and GPVTG,plus GPRMC
            # once every 4 positions
            # (See GlobalTop PMTK command packet PDF)
            ser.write('$PMTK314,0,4,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
                      '*2C\r\n'.encode())
            sleep(1)
            # set interval to 250ms (4 Hz)
            ser.write("$PMTK220,{}*29\r\n".format(
                config.GPS_SAMPLING_FREQ).encode())
            # TODO: change sampling freq to milliseconds from HZ
            sleep(1)
        except Exception as err:
            logger.info('Failed to set baudrate'
                        'and sampling frequency')
            logger.info(err)
        # read lines from GPS serial port and wait for fix
        try:
            # loop until timeout dictated by gps_timeout value
            # (seconds) or the gps is initialized
            while datetime.utcnow().minute + datetime.utcnow().second/60 < \
                  end_time and self.initialized is False:
                self.initialized = self.__checkout__(self.initialized)
            if self.initialized is False:
                logger.info('GPS failed to initialize, timeout')
        except Exception as err:
            logger.info('GPS failed to initialize')
            logger.info(err)


    def power_off(self):
        """
        Power off the GPS module.
        """

    def checkout(self, init_status):
        """
        This is the check out function for the GPS to initialize.

        Parameters
        ----------
        init_status : boolean object
        Returns
        --------
        none

        """
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
                # check gps_qual value from GPGGS sentence.
                # 0=invalid,1=GPS fix,2=DGPS fix
                if gpgga.gps_qual > 0:
                    logger.info('GPS fix acquired')
                    # Set gprmc line to False and enter while loop to
                    # read new lines until it gets the correct line
                    gprmc_line = False
                    while gprmc_line is False:
                    # Get date and time from GPRMC sentence - GPRMC
                    # reported only once every 8 lines
                        newline=ser.readline().decode('utf-8')
                        if 'GPRMC' in newline:
                            logger.info('found GPRMC sentence')
                            # Change value to True so that the while
                            # loop exits once a gprmc line is found
                            gprmc_line = True
                            try:
                                gprmc=pynmea2.parse(newline)
                                nmea_time=gprmc.timestamp
                                nmea_date=gprmc.datestamp
                                logger.info("nmea time: {}".format(nmea_time))
                                logger.info("nmea date: {}".format(nmea_date))
                                # set system time
                                try:
                                    logger.info('setting system time from GPS:'
                                                ' {0} {1}'.format(nmea_date,
                                                                  nmea_time))
                                    os.system('sudo timedatectl '
                                              'set-timezone UTC')
                                    os.system('sudo date -s "{0} {1}"'.format(
                                              nmea_date, nmea_time))
                                    os.system('sudo hwclock -w')
                                    # GPS is initialized
                                    logger.info("GPS initialized")
                                    init_status = True
                                    return init_status

                                except Exception as err:
                                    logger.info(err)
                                    logger.info('error setting system time')
                                    continue
                            except Exception as err:
                                logger.info(err)
                                logger.info('error parsing nmea sentence')
                                continue

    def record(self, end_time):
        """
        This is the function that record the gps component on RPi.

        Parameters
        ----------
        end_time : object

        Returns
        --------
        gps_data_filename: a dat file

        """
        # get float_id for file names
        float_id = os.uname()[1]

        # loop while within the recording block
        while datetime.utcnow().minute + \
              datetime.utcnow().second/60 < end_time:
        # If GPS signal is initialized start recording
            if self.initialized:
                #create file name
                gps_data_filename = gps.data_dir + float_id + \
                                    '_GPS_'+"{:%d%b%Y_%H%M%SUTC.dat}". \
                                    format(datetime.utcnow())
                logger.info("file name: {}".format(gps_data_filename))
                logger.info('starting GPS burst')
                try:
                    ser.flushInput()
                    with open(gps_data_filename, 'w',newline='\n') as gps_out:
                        logger.info('open file for writing: %s'
                                    % gps_data_filename)
                        ipos=0
                        ivel=0
                        while datetime.utcnow().minute + \
                              datetime.utcnow().second/60 <= end_time:
                            newline=ser.readline().decode()
                            gps_out.write(newline)
                            gps_out.flush()
                            # Grab gpgga sentence and parse.
                            # Check to see if we have lost GPS fix.
                            # If so, continue to loop start.
                            # A bad value will remain at this index.
                            # If the number of position and velocity
                            # samples is enough then end the loop
                            if "GPGGA" in newline:
                                gpgga = pynmea2.parse(newline,check=True)
                                if gpgga.gps_qual < 1:
                                    logger.info('lost GPS fix, sample not '
                                        'recorded. Waiting 10 seconds')
                                    sleep(10)
                                    ipos+=1
                                    continue
                                ipos+=1
                            elif "GPVTG" in newline:
                                ivel+=1
                            if ipos == gps_samples and ivel == gps_samples:
                                break
                        # Output logger information on samples
                        logger.info('Ending GPS burst at {}'
                                    .format(datetime.now()))
                        logger.info('number of GPGGA samples = {}'
                                    .format(ipos))
                        logger.info('number of GPVTG samples = {}'
                                    .format(ivel))
                except Exception as err:
                    logger.info(err, exc_info=True)
                # Output logger information on samples
                logger.info('Ending GPS burst at {}'.format(datetime.now()))
                logger.info('number of GPGGA samples = {}'.format(ipos))
                logger.info('number of GPVTG samples = {}'.format(ivel))
                return gps_data_filename
        # If GPS signal is not initialized exit
        else:
            logger.info("GPS not initialized, exiting")

            #create file name but it is a placeholder
            gps_data_filename = ''

            # Return the GPS filename to be read
            # into the onboard processing
            return gps_data_filename

    def to_uvz(self, gps_file):
        """
        This function reads in data from the GPS files
        and stores the fields in memory for post-processing.

        Parameters
        ----------
        end_time : a datetime object

        Returns
        --------
        GPS_variables: a dictionary
        """
        # Set up module level logger
        logger.info('---------------GPStoUVZ.py------------------')

        # Define empty lists of variables to append
        east_west = []
        north_south = []
        up_down = []
        lat = []
        lon = []
        time = []
        ipos=0
        ivel=0
        GPS_variables = {'east_west':None,'north_south':None,
               'up_down':None,'lat':None,'lon':None,'time':None}
        # Define Constants
        bad_value=999
        # current year, month, date for timestamp creation;
        # can also be obtained from utcnow()
        ymd = gps_file[-23:-14]
        # ymd = datetime.utcnow().strftime("%Y-%m-%d")
        with open(gps_file, 'r') as file:
            for line in file:
                if "GPGGA" in line:
                    #grab gpgga sentence and parse
                    gpgga = pynmea2.parse(line,check=True)
                    #check to see if we have lost GPS fix, and if so,
                    # continue to loop start. a bad value will remain at this index
                    if gpgga.gps_qual < 1:
                        up_down.append(bad_value)
                        lat.append(bad_value)
                        lon.append(bad_value)
                        ipos += 1
                        continue
                    up_down.append(gpgga.altitude)
                    lat.append(gpgga.latitude)
                    lon.append(gpgga.longitude)
                    # construct a datetime from the year, month, date,
                    # and timestamp
                    date_time = f'{ymd} {gpgga.timestamp}'  #.rstrip('0')
                    # if the datetime does not contain a float,
                    # append a trailing zero
                    if '.' not in date_time:
                        date_time += '.0'
                    time.append(datetime.strptime(date_time,
                                '%d%b%Y %H:%M:%S.%f'))
                    ipos += 1
                elif "GPVTG" in line:
                    # Grab gpvtg sentence; units are m/s.
                    # If not GPGGA or GPVTG,
                    # continue to start of loop
                    gpvtg = pynmea2.parse(line,check=True)
                    east_west.append( 0.2777 * gpvtg.spd_over_grnd_kmph * \
                                      np.sin(np.deg2rad(gpvtg.true_track)))
                    north_south.append( 0.2777 * gpvtg.spd_over_grnd_kmph * \
                                        np.cos(np.deg2rad(gpvtg.true_track)))
                    ivel += 1
                else:
                    continue
        # if an extra GPGGA line exists,remove the last entry
        if ivel < ipos:
            del up_down[-(ipos-ivel)]
            del lat[-(ipos-ivel)]
            del lon[-(ipos-ivel)]
            del time[-(ipos-ivel)]
            logger.info(f'{ipos-ivel} GPGGA line(s) removed at end')

        logger.info('GPS file read')

        # TODO: bug here, fix!
        # sortInd    = np.asarray(time).argsort()
        # timeSorted = np.asarray(time)[sortInd]
        # uSorted    = np.asarray(east_west)[sortInd].transpose()
        # vSorted    = np.asarray(north_south)[sortInd].transpose()
        # zSorted    = np.asarray(up_down)[sortInd].transpose()
        # latSorted  = np.asarray(lat)[sortInd].transpose()
        # lonSorted  = np.asarray(lon)[sortInd].transpose()
        # assign outputs to GPS dict
        GPS_variables.update({'east_west':east_west,'north_south':north_south,
                    'up_down':up_down,'lat':lat,'lon':lon,'time':time})
        # GPS.update({'east_west':uSorted,'north_south':vSorted,
        # 'up_down':zSorted,'lat':latSorted,'lon':lonSorted,'time':timeSorted})
        logger.info('GPGGA lines: {}'.format(len(lat)))
        logger.info('GPVTG lines: {}'.format(len(east_west)))
        logger.info('------------------------------------------')
        return GPS_variables #east_west,north_south,up_down,lat,lon, time
