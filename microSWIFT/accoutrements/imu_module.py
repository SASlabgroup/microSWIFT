"""
Initialize and record IMU.

authors: @EJRainville, @AlexdeKlerk, @Viviana Castillo
"""
try:
    import busio
    import board
    import RPi.GPIO as GPIO
    from . import adafruit_fxos8700, adafruit_fxas21002c
except ImportError as e:
    from ..mocks import mock_busio as busio
    from ..mocks import mock_board as board
    from ..mocks import mock_rpi_gpio as GPIO
    from ..mocks import mock_adafruit_fxos8700 as adafruit_fxos8700
    from ..mocks import mock_adafruit_fxas21002c as adafruit_fxas21002c
    print(e, "Using mock hardware")

import logging
import os
import sys
import numpy as np
import time


from datetime import datetime, timedelta
from ..processing.integrate_imu import integrate_acc


# Set up module level logger
logger = logging.getLogger('microSWIFT.'+__name__)

class IMU:
    """Instantiates an IMU object"""
    def __init__(self, config):
        """
        Initialize the IMU module.

        Paramenters:
        ------------
        config object

        Returns:
        --------
        none
        """
        try:
            # power on IMU module and set up fxas and fxos objects
            self.imu_initialized = False
            logger.info('initializing IMU')
            self.imuFreq = config.IMU_SAMPLING_FREQ
            self.imu_samples = config.IMU_SAMPLING_FREQ * config.RECORD_WINDOW_LENGTH.total_seconds()
            self.imu_gpio = config.IMU_GPIO
            self.floatID = os.uname()[1]
            self.dataDir = './microSWIFT/microSWIFT/data/'
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.imu_gpio,GPIO.OUT)
            logger.info('power on IMU')
            GPIO.output(self.imu_gpio,GPIO.HIGH)
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.fxos = adafruit_fxos8700.FXOS8700(self.i2c, accel_range=0x00)
            self.fxas = adafruit_fxas21002c.FXAS21002C(self.i2c, gyro_range=500)
        except Exception as e:
            logger.info(e)
            logger.info('error initializing imu')
            exit(e)
        self.imu_initialized = True
        logger.info('IMU initialized')

    def record(self, end_time):
        """
        Record IMU data and create data file

        Paramenters:
        ------------
        End time

        Returns:
        --------
        file name and imu initialized
        """
        # IMU is not Initialzied at first
        if self.imu_initialized == False:
            Exception("IMU module not initialized")

        # Loop if the imu did not initialize and it is still within a recording block
        while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time:
            # Sleep to start recording at same time as GPS
            time.sleep(5.1)

            ## --------------- Record IMU ----------------------
            #create new file for to record IMU to
            logger.info('---------------recordIMU.py------------------')
            IMUdataFilename = self.dataDir + self.floatID + '_IMU_'+'{:%d%b%Y_%H%M%SUTC.dat}'.format(datetime.utcnow())
            logger.info('file name: {}'.format(IMUdataFilename))
            logger.info('starting IMU burst at {}'.format(datetime.now()))

            # Open the new IMU data file for logging
            with open(IMUdataFilename, 'w',newline='\n') as imu_out:
                logger.info('open file for writing: {}'.format(IMUdataFilename))
                isample=0
                while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and isample < self.imu_samples:
                    # Get values from IMU
                    try:
                        accel_x, accel_y, accel_z = self.fxos.accelerometer
                        mag_x, mag_y, mag_z = self.fxos.magnetometer
                        gyro_x, gyro_y, gyro_z = self.fxas.gyroscope
                    except Exception as e:
                        logger.info(e)
                        logger.info('error reading IMU data')

                    # Get current timestamp
                    timestamp='{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.utcnow())

                    # Write data and timestamp to file
                    imu_out.write('%s,%f,%f,%f,%f,%f,%f,%f,%f,%f\n' %(timestamp,accel_x,accel_y,accel_z,mag_x,mag_y,mag_z,gyro_x,gyro_y,gyro_z))
                    imu_out.flush()

                    # Index up number of samples
                    isample = isample + 1

                    # hard coded sleep to control recording rate. NOT ideal but works for now
                    time.sleep(0.065)

                # End of IMU sampling
                logger.info('end burst')
                logger.info('IMU samples {}'.format(isample))
                logger.info('IMU ending burst at: {}'.format(datetime.now()))

            # Return IMUdataFilename to main microSWIFT.py
            return IMUdataFilename, self.imu_initialized

    def checkout(self, run_time):
        """
        Function to run tests for calibration of the IMU

        Parameters:
        -----------
        run_time = time in minutes to run tests. Minumum:1, maximum:60

        Returns:
        --------
        Calibration document
        """

        #setup checks
        if self.imu_initialized == False:
            Exception("IMU module not initialized")

        if run_time < 1:
            raise ValueError('Run time must be greater than or equal to 1')

        if run_time > 60:
            raise ValueError('Run time must be less than or equal to 60')

        t_end = time.time() + (60 * run_time)

        #update imu_samples for the shorter record window
        self.imu_samples = self.imuFreq * (60 * run_time)

        print("IMU checkout beginning. Please keep buoy still for", run_time,
        "minute(s).")

        self.record(t_end)

    def power_off(self):
        """
        power off IMU module

        Paramenters:
        ------------
        none

        Returns:
        --------
        none
        """

        logger.info('power down IMU')
        GPIO.output(self.imu_gpio,GPIO.LOW)

    def sec(n_secs):
        """
        #TODO: fix docstr
        Helper function to convert timedelta into second

        Input:
            - n_secs, float indicating number of seconds

        Output:
            - s, time delta in seconds
        """
        return timedelta(seconds=n_secs)


    def datetimearray2relativetime(datetimeArr):
        """
        #TODO: fix docstr
        Helper function to convert datetime array to relative time in seconds

        Input:
            - datetimeArr, input array of datetimes

        Output:
            - relTime, time array (in seconds) relative to the first time in datetimeArr
        """
        t0 = datetimeArr[0]
        relTime = [timestep.total_seconds() for timestep in (datetimeArr-t0)]
        return relTime


    def RCfilter(b, fc, fs):
        """
        #TODO: fix docstr
        Helper function to perform RC filtering

        Input:
            - b, array of values to be filtered
            - fc, cutoff frequency, fc = 1/(2πRC)
            - fs, sampling frequency

        Output:
            - a, array of filtered input values
        """
        RC = (2*np.pi*fc)**(-1)
        alpha = RC / (RC + 1./fs)
        a = b.copy()
        for ui in np.arange(1,len(b)): # speed this up
            a[ui] = alpha * a[ui-1] + alpha * ( b[ui] - b[ui-1] )
        return a

    def to_xyz(self, imufile, fs):
        """
        #TODO: fix docstr
        Main function to collate IMU and GPS records. The IMU fields are cropped to lie within the available
        GPS record and then the GPS is interpolated up to the IMU rate using the IMU as the master time.

        Inputs:
            - imufile, path to file containing IMU data
            - fs, sampling frequency

        Outputs:
            - IMU, dictionary containing acc ['ai'], vel ['vi'], pos ['pi'], and time ['time'] as entries

        Example:
            IMU = to_xyz(imufile,fs)
        """
        #-- Set up module level logger
        logger = logging.getLogger('microSWIFT.'+__name__)
        logger.info('---------------to_xyz.py------------------')

        #TODO: handle badvalues

        #--initialization
        timestamp = []
        acc = []
        mag = []
        gyo = []
        IMU = {'ax':None,'ay':None,'az':None,'vx':None,'vy':None,'vz':None,'px':None,'py':None,'pz':None,'time':None}

        #--open imu file and read in acceleration, magnetometer, and gyroscope data
        logger.info('Reading and sorting IMU')
        with open(imufile, 'r') as file: #encoding="utf8", errors='ignore'
            for line in file:
                currentLine = line.strip('\n').rstrip('\x00').split(',')
                if currentLine[0] != '':
                    timestamp.append(datetime.strptime(currentLine[0],'%Y-%m-%d %H:%M:%S'))
                    acc.append(list(map(float,currentLine[1:4])))  # acc = [ax,ay,az]
                    mag.append(list(map(float,currentLine[4:7])))  # mag = [mx,my,mz]
                    gyo.append(list(map(float,currentLine[7:10]))) # gyo = [gx,gy,gz]


        #--sorting:
        sortInd = np.asarray(timestamp).argsort()
        timestamp_sorted = np.asarray(timestamp)[sortInd]
        accSorted = np.asarray(acc)[sortInd,:].transpose()
        magSorted = np.asarray(mag)[sortInd,:].transpose()
        gyoSorted = np.asarray(gyo)[sortInd,:].transpose()

        #--trimming #TODO: not tested live...
        # print(len(timestamp_sorted))
        # skipFirstSecs = 60 #TODO: make input on config, log etc.
        # skipBool = timestamp_sorted >= timestamp_sorted[0] + timedelta(seconds=skipFirstSecs)
        # skipBool3 = np.tile(skipBool, (3,1))
        # accSorted = accSorted[skipBool3].reshape((3, -1))
        # magSorted = magSorted[skipBool3].reshape((3, -1))
        # gyoSorted = gyoSorted[skipBool3].reshape((3, -1))
        # timestamp_sorted = timestamp_sorted[skipBool]
        # print(len(timestamp_sorted))

        # determine which way is up
        logger.info('Finding up')
        accMeans = list()
        for ai in accSorted:
            accMeans.append(np.mean(ai))
        upIdx = np.argmin(np.abs(np.asarray(accMeans) - 9.81))

        if upIdx == 0: #[x y z] -> [-z y x]
            transformIdx = [2, 1, 0]
            signs = [-1, 1, 1]
        elif upIdx == 1: #[x y z] == [x -z y]
            transformIdx = [0, 2, 1]
            signs = [1, -1, 1]
        elif upIdx == 2: #[x y z] == [x -z y]
            transformIdx = [0, 1, 2]
            signs = [1, 1, 1]

        accSorted    = accSorted[transformIdx]
        accSorted[0] = accSorted[0]*signs[0]
        accSorted[1] = accSorted[1]*signs[1]
        accSorted[2] = accSorted[2]*signs[2]

        gyoSorted    = gyoSorted[transformIdx]
        gyoSorted[0] = gyoSorted[0]*signs[0]
        gyoSorted[1] = gyoSorted[1]*signs[1]
        gyoSorted[2] = gyoSorted[2]*signs[2]

        magSorted    = magSorted[transformIdx]
        magSorted[0] = magSorted[0]*signs[0]
        magSorted[1] = magSorted[1]*signs[1]
        magSorted[2] = magSorted[2]*signs[2]

        print(f'Coordinate position {upIdx} assigned as up')
        logger.info(f'Coordinate position {upIdx} assigned as up')

        # create a master time array based on the specified sampling frequency and the start and end times.
        dt = sec(fs**(-1))
        t0 = timestamp_sorted[0]
        tf = timestamp_sorted[-1]
        masterTime = np.arange(t0,tf,dt).astype(datetime)

        # add milliseconds to each second of the rounded IMU timestamps:
        timestampSorted_ms = add_ms_to_time(timestamp_sorted)

        #--Interpolate IMU onto master clock
        logger.info('Interpolating IMU onto master clock')
        # convert datetime ranges to a relative number of total seconds
        masterTimeSec = datetimearray2relativetime(masterTime)
        imuTimeSec    = datetimearray2relativetime(timestampSorted_ms)

        #interpolate
        accInterp = [np.interp(masterTimeSec,imuTimeSec,a) for a in accSorted]
        magInterp = [np.interp(masterTimeSec,imuTimeSec,m) for m in magSorted]
        gyoInterp = [np.interp(masterTimeSec,imuTimeSec,g) for g in gyoSorted]

        #cnt number of NaNs TODO: handle nans; log?
        np.isnan(accInterp).sum()
        np.isnan(magInterp).sum()
        np.isnan(gyoInterp).sum()

        #-- reference frame transformation #TODO: reference frame transformation
        # ax_earth, ay_earth, az_earth = ekfCorrection(*accInterp,*gyoInterp,*magInterp)
        # *accEarth = ekfCorrection(*accInterp,*gyoInterp,*magInterp)
        # accEarth = [ax_earth,ay_earth,az_earth]

        #-- integration
        logger.info('Integrating IMU')
        fc = 0.04
        filt = lambda *b : RCfilter(*b,fc,fs)
        # X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accEarth][:] # X = [ax,ay,az], Y = ...
        X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accInterp][:] # X = [ax,ay,az], Y = ...

        # assign outputs to IMU dict
        IMU['ax'],IMU['vx'],IMU['px'] = X # IMU.update({'ax': X[0], 'ay': Y[0], 'az': Z[0]})
        IMU['ay'],IMU['vy'],IMU['py'] = Y
        IMU['az'],IMU['vz'],IMU['pz'] = Z
        IMU['time'] = masterTime

        logger.info('--------------------------------------------')
        return IMU # X[0], Y[0], Z[0], X[1], Y[1], Z[1], X[2], Y[2], Z[2], masterTime # ax, ay, az, vx, vy, vz, px, py, pz
