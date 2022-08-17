"""
Author: @jacobrdavis

A collection of functions to read in data from an IMU file, process it, and store 
the output as python variables to be used in calculations for wave properties.

Contents:
    - sec(n_secs)
    - datetimearray2relativetime(datetimeArr)
    - RCfilter(b, fc, fs)
    - add_ms_to_IMUtime(timestampSorted)
    - IMUtoXYZ(imufile,fs) [main]

Log:
    - Jun 2022, J.Davis: created IMUtoXYZ.py
    - Aug 2022, J.Davis: created integrateIMU.py and moved demean(), cumtrapz(), and integrate_acc() there
    - Aug 2022, J.Davis: created transformIMU.py and moved ekfCorrection() there

TODO:
    - remove reassignment of the same variable?
"""
#--Import Statements
import numpy as np
from logging import getLogger
from datetime import datetime, timedelta
from IMU.integrateIMU import integrate_acc
# from IMU.transformIMU import ekfCorrection
# from scipy import integrate

#--helper functions:
def sec(n_secs):
    """
    Helper function to convert timedelta into second
    
    Input:
        - n_secs, float indicating number of seconds

    Output:
        - s, time delta in seconds
    """
    s = timedelta(seconds=n_secs)    
    return s


def datetimearray2relativetime(datetimeArr):
    """
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


def add_ms_to_IMUtime(timestampSorted):
    """
    Helper function to add milliseconds to rounded IMU timestamps. This method interprets
    a sampling frequency based on the number of samples present in a given clock second, and
    then adds an array of millisecond increments to the datetimes in that second. This assumes
    the samples in a second are centered in that second, and thus does not bias the samples to 
    either the start of end of the second.

    Input:
        - timestampSorted, sorted array of rounded IMU timestamps (as datetimes)

    Output:
        - timestampSorted_ms, sorted datetime array with added milliseconds
    """
    timestampSorted_ms = timestampSorted.copy() 
    i = 1
    for n in np.arange(1, len(timestampSorted)):
        if timestampSorted[n] == timestampSorted[n-1] and n != len(timestampSorted)-1: 
            i += 1 # count number of occurences in second
        else:
            if n == len(timestampSorted)-1: # if in last second, manually increment i & n
                i += 1; n += 1
            dt0 = sec(float(i)**(-1)) # interpret current timestep size based on number of samples reported in this second  #
            secSteps = np.arange(0,i)*dt0 # create array of time increments from zero
            timestampSorted_ms[n-i:n] = timestampSorted[n-i:n] + secSteps
            i = 1 # restart i at one so that it can start again on the next second 
    return timestampSorted_ms
    

def IMUtoXYZ(imufile,fs):
    """ 
    Main function to collate IMU and GPS records. The IMU fields are cropped to lie within the available 
    GPS record and then the GPS is interpolated up to the IMU rate using the IMU as the master time.
    
    Inputs:
        - imufile, path to file containing IMU data
        - fs, sampling frequency
        
    Outputs:
        - IMU, dictionary containing acc ['ai'], vel ['vi'], pos ['pi'], and time ['time'] as entries
    
    Example:
        IMU = IMUtoXYZ(imufile,fs)
    """
    #-- Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 
    logger.info('---------------IMUtoXYZ.py------------------')

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
            if currentLine[0] is not '':
                timestamp.append(datetime.strptime(currentLine[0],'%Y-%m-%d %H:%M:%S'))
                acc.append(list(map(float,currentLine[1:4])))  # acc = [ax,ay,az]
                mag.append(list(map(float,currentLine[4:7])))  # mag = [mx,my,mz]
                gyo.append(list(map(float,currentLine[7:10]))) # gyo = [gx,gy,gz]
          

    #--sorting:
    sortInd = np.asarray(timestamp).argsort()
    timestampSorted = np.asarray(timestamp)[sortInd]
    accSorted = np.asarray(acc)[sortInd,:].transpose()
    magSorted = np.asarray(mag)[sortInd,:].transpose()
    gyoSorted = np.asarray(gyo)[sortInd,:].transpose()
    
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
    t0 = timestampSorted[0]
    tf = timestampSorted[-1]
    masterTime = np.arange(t0,tf,dt).astype(datetime)

    # add milliseconds to each second of the rounded IMU timestamps:
    timestampSorted_ms = add_ms_to_IMUtime(timestampSorted)

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
