"""
Description: This function initializes and records GPS data from the
onboard GPS sensor. Within the main microSWIFT.py script this is run
as an asynchronous task at the same time as the recordIMU function.

TODO:
    - data attributes need to be set in init() (as empty or bad val) and
        in record() method when acquired (i.e. GPS.lon, GPS.lat etc.); 
        GPS.u and GPS.v will be set by to_uvz() method. See to_uvz() todos.
    - gps_data_filename needs to be set as an attribute in record() method
    - Else clause on loop without a break statement in record() method
    - class docstr
    - log formatting to lazy
    - record and checkout need to be passed an active serial connection
        OR it needs to be stored as an attribute
    - gprmc_line() method needs to have var names checked
    - to_uvz() method needs updating; need to decide if data will be read
        from attributes or from a file. Maybe we include an additional
        method for reading the data into memory/attributes?
    
"""
try:
    import RPi.GPIO as GPIO
    import serial
    mocked_hardware = False
except ImportError as e:
    from mocks import mock_rpi_gpio as GPIO
    from mocks import mock_serial as serial
    mocked_hardware = True
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
    Methods for interfacing with the GPS module. Stores the GPS
    configuration and data as attributes.

    TODO: Class long description.

    Attributes
    ----------
    attribute1 : type
        Description.
    attribute2 : type
        Description.

    Methods
    -------
    method1(argument1, argument2)
        Description.
    method2(argument1, argument2)
        Description.

    """

    def __init__(self, config):
        """
        Initializes the GPS module.

        TODO: Long description.

        Parameters
        ----------
        config: Config
            Configuration containing IMU settings.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the config object does not contain an int GPIO setting.

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
            self.gps_freq_ms = int(1000/self.gps_freq)
            self.gps_gpio = config.GPS_GPIO
            self.floatID = os.uname()[1]
            self.dataDir = config.DATA_DIR
            self.gps_port = config.GPS_PORT
            self.start_baud = config.START_BAUD
            self.baud = config.BAUD
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gps_gpio,GPIO.OUT)
            GPIO.setwarnings(False)
            self.initialized = True
            self.gpgga_found = False
            self.gprmc_found = False
            logger.info('GPS initialized')
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('error initializing GPS')

    def power_on(self):
        """
        Power on GPS module.

        Sets GPS's GPIO pin to high, flips the state of the `powered_on`
        attribute to True, opens a serial connection and writes the baud
        rate, and sets the output sentences.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the GPS is unable to be powered on, the serial port
            did not open, the baud rate is unable to be set, the sampling
            frequency is unable to be set, or checkout is not passed.

        """
        try:
            GPIO.output(self.gps_gpio,GPIO.HIGH)
            self.powered_on = True
            logger.info('GPS powered on')
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('unable to turn on GPS')

        # Open the serial connection to the GPS module and set baud rate
        try:
            logger.info("try GPS serial port at 9600")
            ser = serial.Serial(self.gps_port, self.start_baud,
                              timeout=1)
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('Serial port did not open')

        try:
            # set device baud rate to 115200
            ser.write(f'$PMTK251,{self.baud}*1F\r\n'.encode())
            sleep(1)
            ser.baudrate = self.baud
            logger.info("switching to %s on port %s" % \
                        (self.baud, self.gps_port))
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('could not update GPS baud rate')

        try:
            # set output sentence to GPGGA and GPVTG,plus GPRMC
            # once every 4 positions
            # (See GlobalTop PMTK command packet PDF)
            ser.write('$PMTK314,0,4,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'
                      '*2C\r\n'.encode())
            sleep(1)
            ser.write(f"$PMTK220,{self.gps_freq_ms}*29\r\n".encode())
            sleep(1)
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('Failed to set sampling frequency')

        try:
            self.checkout(ser)
            if self.initialized is True:
                pass
            else:
                logger.info('GPS failed to initialize, timeout')
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('GPS did not pass checkout')

    def power_off(self):
        """
        Power off GPS module.

        Sets GPS's GPIO pin to low and flips the state of the
        `powered_on` attribute to False.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the GPS is unable to be powered off.
        """
        try:
            GPIO.output(self.gps_gpio,GPIO.LOW)
            self.powered_on = False
            logger.info('GPS powered off')
        except RuntimeError as exception:
            logger.info(exception)
            logger.info('not able to turn off GPS')


    def record(self, end_time):
        """
        Record GPS data and write it to a file.

        #TODO: long description.

        Parameters
        ----------
        end_time : datetime
            The end of the record burst.

        Returns
        -------
        None

        Raises
        ------
        RuntimeError
            If the GPS data can not be read.
        """
        if self.powered_on is True:
            gps_data_filename = self.data_dir + self.floatID + \
                                '_GPS_'+"{:%d%b%Y_%H%M%SUTC.dat}". \
                                format(datetime.utcnow())
            logger.info("file name: {}".format(gps_data_filename))
            logger.info('starting GPS burst')
        else:
            logger.info('GPS is not on - trying to power on')
            self.power_on()

        while datetime.utcnow() < end_time:
                
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
                except RuntimeError as exception:
                    logger.info(exception, exc_info=True)
                    logger.info('unable to record')
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

    def checkout(self, ser):
        """
        Checks proper functioning of the GPS module.

        TODO: long description

        Parameters
        ----------
        ser : Serial
            An active serial connection.

        Returns
        -------
        TODO: Calibration document

        Raises
        ------
        RuntimeError
            If a GPS signal is unable to be acquired.
        """
        try:
            while self.gpgga_found is False and self.gprmc_found is False:
                ser.flushInput()
                ser.read_until('\n'.encode())
                newline = ser.readline().decode('utf-8')
                if 'GPGGA'in newline:
                    self.gpgga_line(newline)
                elif 'GPRMC' in newline:
                    self.gprmc_line(newline)
                else:
                    continue

        except RuntimeError as exception:
            logger.info(exception)
            logger.info('not able to recieve GPS signal')

    def gpgga_line(self, newline):
        """
        TODO: Description.

        Parameters
        ----------
        newline : type
            Description.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If GPGGA not correct.
        """
        try:
            logger.info('found GPGGA sentence')
            logger.info(newline)
            gpgga = pynmea2.parse(newline,check=True)
            logger.info('GPS quality= {}'.format(gpgga.gps_qual))
            if gpgga.gps_qual > 0:
                logger.info('GPS fix acquired')
            self.gpgga_found = True
        except ValueError as exception:
            logger.info(exception)
            logger.info('GPGGA not correct')

    def gprmc_line(self, newline):
        """
        TODO: Description.

        Parameters
        ----------
        newline : type
            description

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If unable to parse GPRMC.
        """
        logger.info('found GPRMC sentence')
        try:
            gprmc = pynmea2.parse(newline)
            nmea_time=gprmc.timestamp
            nmea_date=gprmc.datestamp
            logger.info("nmea time: {}".format(nmea_time))
            logger.info("nmea date: {}".format(nmea_date))
        except ValueError as exception:
            logger.info(exception)
            logger.info('unable to parse GPRMC')

        if mocked_hardware is False:
            try:
                logger.info('setting system time from GPS:{0} {1}'.format(nmea_date,
                                                                        nmea_time))
                os.system('sudo timedatectl set-timezone UTC')
                os.system(f'sudo date -s "{nmea_date} {nmea_time}"')
                os.system('sudo hwclock -w')
                logger.info('System time reset')
                self.gpgga_found = True TODO: gprmc?
            except Exception as exception:
                logger.info(exception)
                logger.info('Not able to set system time from GPS time')
        else:
            self.gpgga_found = True #TODO: gprmc?

    def to_uvz(self, gps_data_filename):
        """
        This function reads in data from the GPS files
        and stores the fields in memory for post-processing.

        Parameters
        ----------
        end_time : datetime


        Returns
        --------
        GPS_variables: a dictionary

        """
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
        ymd = gps_data_filename[-23:-14]
        # ymd = datetime.utcnow().strftime("%Y-%m-%d")
        with open(gps_data_filename, 'r') as file:
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
