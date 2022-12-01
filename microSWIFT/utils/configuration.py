"""
Definition of the configuration class for the microSWIFT. The
configuration will read in a few variables from the 
"""

import warnings

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

        # System Parameters
        


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
        
        try:
            duty_cycle_length
        except:
            raise 
        
        return (duty_cycle_length, 
                record_window_length, 
                gps_sampling_frequency,
                imu_sampling_frequency)