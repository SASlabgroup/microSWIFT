"""
Initialize and record IMU.

authors: @EJRainville, @AlexdeKlerk, @Viviana Castillo
"""
try:
    import busio
    import board
    import RPi.GPIO as GPIO
    from . import adafruit_fxos8700, adafruit_fxas21002c
except ImportError:
    from ..mocks import mock_busio as busio
    from ..mocks import mock_board as board
    from ..mocks import mock_rpi_gpio as GPIO
    from ..mocks import mock_adafruit_fxos8700 as adafruit_fxos8700
    from ..mocks import mock_adafruit_fxas21002c as adafruit_fxas21002c

import logging
import os
import sys
import numpy as np


from time import sleep
from datetime import datetime, timedelta
from ..processing.integrate_imu import integrate_acc
from ..utils import configuration


# Set up module level logger
logger = logging.getLogger('microSWIFT.'+__name__)

############## TODO: fix once EJ integrates config class ###############
# System and logging parameters

def init():
    """
    Initialize the IMU module.

    Paramenters:
    ------------
    Config object

    Returns:
    --------
    Return True if successful.
    If not successful, print the error to the logger and return False.
    TODO: I think this actually needs to return some config values
    """

    try:
        #config = configuration.Config('../config.txt')
        #system parameters
        """floatID = os.uname()[1]
        dataDir = config.getString('System', 'dataDir')
        burst_interval=config.getInt('System', 'burst_interval')
        burst_time=config.getInt('System', 'burst_time')
        burst_seconds=config.getInt('System', 'burst_seconds')
        bad = config.getInt('System', 'badValue')"""

        dataDir = '../'

        #IMU parameters TODO: use real ones later
        imuFreq=12
        imu_samples = imuFreq*60
        imu_gpio=16
    except Exception as e:
        logger.info(e)
        logger.info('error reading config')
        print(e)
        return False

    try:
        # initialize fxos and fxas devices (required after turning off device)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(imu_gpio,GPIO.OUT)
        logger.info('power on IMU')
        GPIO.output(imu_gpio,GPIO.HIGH)
        i2c = busio.I2C(board.SCL, board.SDA)
        fxos = adafruit_fxos8700.FXOS8700(i2c, accel_range=0x00)
        fxas = adafruit_fxas21002c.FXAS21002C(i2c, gyro_range=500)
    except Exception as e:
        logger.info(e)
        logger.info('error initializing imu')
        print(e)
        return False
    return fxos, fxas

def checkout():
    """
    TODO:
    """

def record(end_time):
    """
    TODO:
    """
    # IMU is not Initialzied at first
    imu_initialized = False
    dataDir = '../'
    floatID = os.uname()[1]
    imuFreq=12
    imu_samples = imuFreq*60
    imu_gpio=16

    # Loop if the imu did not initialize and it is still within a recording block
    while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and imu_initialized==False:

        ## --------------- Initialize IMU -----------------
        logger.info('initializing IMU')

        # initialize fxos and fxas devices (required after turning off device)
        fxos, fxas = init()

        # Sleep to start recording at same time as GPS
        sleep(5.1)

        logger.info('IMU initialized')

        ## --------------- Record IMU ----------------------
        #create new file for to record IMU to
        logger.info('---------------recordIMU.py------------------')
        IMUdataFilename = dataDir + floatID + '_IMU_'+'{:%d%b%Y_%H%M%SUTC.dat}'.format(datetime.utcnow())
        logger.info('file name: {}'.format(IMUdataFilename))
        logger.info('starting IMU burst at {}'.format(datetime.now()))

        # Open the new IMU data file for logging
        with open(IMUdataFilename, 'w',newline='\n') as imu_out:
            logger.info('open file for writing: {}'.format(IMUdataFilename))
            isample=0
            while datetime.utcnow().minute + datetime.utcnow().second/60 < end_time and isample < imu_samples:
                # Get values from IMU
                try:
                    accel_x, accel_y, accel_z = fxos.accelerometer
                    mag_x, mag_y, mag_z = fxos.magnetometer
                    gyro_x, gyro_y, gyro_z = fxas.gyroscope
                except Exception as e:
                    logger.info(e)
                    logger.info('error reading IMU data')

                # Get current timestamp
                timestamp='{:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow())

                # Write data and timestamp to file
                imu_out.write('%s,%f,%f,%f,%f,%f,%f,%f,%f,%f\n' %(timestamp,accel_x,accel_y,accel_z,mag_x,mag_y,mag_z,gyro_x,gyro_y,gyro_z))
                imu_out.flush()

                # Index up number of samples
                isample = isample + 1

                # hard coded sleep to control recording rate. NOT ideal but works for now
                sleep(0.065)

            # End of IMU sampling
            logger.info('end burst')
            logger.info('IMU samples {}'.format(isample))
            logger.info('IMU ending burst at: {}'.format(datetime.now()))

            # Turn IMU Off
            GPIO.output(imu_gpio,GPIO.LOW)
            logger.info('power down IMU')

        # Return IMUdataFilename to main microSWIFT.py
        return IMUdataFilename, imu_initialized


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


def add_ms_to_time(timestamp_sorted):
    """
    #TODO: fix docstr
    Helper function to add milliseconds to rounded IMU timestamps. This method interprets
    a sampling frequency based on the number of samples present in a given clock second, and
    then adds an array of millisecond increments to the datetimes in that second. This assumes
    the samples in a second are centered in that second, and thus does not bias the samples to
    either the start of end of the second.

    Input:
        - timestamp_sorted, sorted array of rounded IMU timestamps (as datetimes)

    Output:
        - timestampSorted_ms, sorted datetime array with added milliseconds
    """
    timestampSorted_ms = timestamp_sorted.copy()
    i = 1
    for n in np.arange(1, len(timestamp_sorted)):
        if timestamp_sorted[n] == timestamp_sorted[n-1] and n != len(timestamp_sorted)-1:
            i += 1 # count number of occurences in second
        else:
            if n == len(timestamp_sorted)-1: # if in last second, manually increment i & n
                i += 1; n += 1
            dt0 = sec(float(i)**(-1)) # interpret current timestep size based on number of samples reported in this second  #
            secSteps = np.arange(0,i)*dt0 # create array of time increments from zero
            timestampSorted_ms[n-i:n] = timestamp_sorted[n-i:n] + secSteps
            i = 1 # restart i at one so that it can start again on the next second
    return timestampSorted_ms


def to_xyz(imufile, fs):
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
