"""
Definition of the configuration class for the microSWIFT. The
configuration will read in a few variables from the 
"""

from datetime import datetime, timedelta
import logging
import os
import warnings

from . import log

class Config:
    """
    Class object for configuration of the microSWIFT.
    """
    def __init__(self, config_fname: str):
        """
        Initialize the configuration of the microSWIFT with all
        settings. The settings include values that really should not
        be changed and are hardcoded into the class and parameters that
        can be regularly changed from the config.txt file.

        Parameters
        ----------
        config_fname : str
            File that contains simple parameters for configuration of
            the microSWIFT that can be easily changed.

        Returns
        -------
        config : class
            A class that contains all the parameters for the microSWIFT
            configuration including user changeable settings and
            hardcoded settings.
        """
        logger = logging.getLogger('microSWIFT')

        (duty_cycle_length,
         record_window_length,
         gps_sampling_frequency,
         imu_sampling_frequency) = self.read_config_file(config_fname)

        # Check read in parameters
        if record_window_length >= duty_cycle_length:
            raise ValueError('record_window_length must be strictly less than'
                             'the duty_cycle_length')
        else:
            pass

        if (duty_cycle_length - record_window_length) < 5:
            warnings.warn('send and process window SHOULD be longer than 5'
                          ' minutes')
                         
        if gps_sampling_frequency >=1 and gps_sampling_frequency <= 4:
            pass
        else:
            raise ValueError('gps_sampling_frequency is out of range')

        if imu_sampling_frequency >=1 and imu_sampling_frequency <= 30:
            pass
        else:
            raise ValueError('imu_sampling_frequency is out of range')

        # Timing Parameters
        self.DUTY_CYCLES_PER_HOUR = int(60/duty_cycle_length)
        self.DUTY_CYCLE_LENGTH = timedelta(minutes=duty_cycle_length)
        self.RECORD_WINDOW_LENGTH = timedelta(minutes=record_window_length)
        self.START_TIME = self.get_start_time()
        self.END_RECORD_TIME = self.START_TIME + self.RECORD_WINDOW_LENGTH
        self.END_DUTY_CYCLE_TIME = self.START_TIME + self.DUTY_CYCLE_LENGTH

        # System Parameters
        self.ID = os.uname()[1]
        self.PAYLOAD_TYPE = 7
        self.SENSOR_TYPE = 52

        # GPS Parameters
        self.GPS_SAMPLING_FREQ = gps_sampling_frequency
        self.gpsGPIO = 21
        self.GPS_PORT = '/dev/ttyS0'
        self.START_BAUD = 9600
        self.BAUD = 115200

        # IMU Parameters
        self.IMU_SAMPLING_FREQ = imu_sampling_frequency

        # Data Parameters
        self.WAVE_PROCESSING_TYPE = 'gps_waves'
        self.BAD_VALUE = 999
        self.NUM_COEF = 42

        logger.info(log.header(''))
        logger.info('Booted up. microSWIFT configuration: \n'
                    f'float ID: {self.ID}, payload type: {self.PAYLOAD_TYPE},'
                    f' sensor type: {self.SENSOR_TYPE},'
                    f'duty cycle length: {self.DUTY_CYCLE_LENGTH},'
                    f'record window length: {self.RECORD_WINDOW_LENGTH}')

        return
        
    def read_config_file(self, config_fname):
        """
        Read configuration parameters from the configuration file.

        Parameters
        ----------
        config_fname : str
            File that contains simple parameters for configuration of
            the microSWIFT that can be easily changed.

        Returns
        -------

        
        """
        try:
            config_file = open(config_fname, 'r')
        except:
            raise FileNotFoundError('cannot find config.txt file')

        lines = config_file.readlines()

        for line in lines:
            vals = line.split()
            if 'duty_cycle_length' in vals:
                try:
                    duty_cycle_length = int(vals[-1])
                except:
                    raise ValueError('duty_cycle_length must be an integer')

            elif 'record_window_length' in vals: 
                try:
                    record_window_length = int(vals[-1])
                except:
                    raise ValueError('record_window_length must be an integer')

            elif 'gps_sampling_frequency' in vals: 
                try:
                    gps_sampling_frequency = int(vals[-1])
                except:
                    raise ValueError('gps_sampling_frequency must be an'
                                     'integer')

            elif 'imu_sampling_frequency' in vals:
                try:
                    imu_sampling_frequency = int(vals[-1])
                except:
                    raise ValueError('imu_sampling_frequnecy must be an'
                                     'integer')
            else:
                continue

        return (duty_cycle_length,
                record_window_length,
                gps_sampling_frequency,
                imu_sampling_frequency)

    def get_start_time(self):
        """
        Find the start of the current duty cycle as a datetime.
        """
        current_hour = datetime.utcnow().replace(minute=0, second=0)
        for i in range(self.DUTY_CYCLES_PER_HOUR):
            possible_start_time = current_hour + i*self.DUTY_CYCLE_LENGTH
            if possible_start_time <= datetime.utcnow() \
                                    < possible_start_time + self.DUTY_CYCLE_LENGTH:
                start_time = possible_start_time
            else:
                continue

        return start_time

    def update_times(self):
        """
        Update timing parameters.
        """
        self.START_TIME = self.START_TIME + self.DUTY_CYCLE_LENGTH
        self.END_RECORD_TIME = self.START_TIME + self.RECORD_WINDOW_LENGTH
        self.END_DUTY_CYCLE_TIME = self.START_TIME + self.DUTY_CYCLE_LENGTH
