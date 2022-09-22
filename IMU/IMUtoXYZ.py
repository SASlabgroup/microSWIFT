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
from array import array
from typing import List
import numpy as np
from logging import getLogger
from utils.create_log_header import create_log_header
from datetime import date, datetime, timedelta
from IMU.readIMU import readIMU
from IMU.integrateIMU import integrate_acc
from IMU.transformIMU import change_up_axis, correct_mag, ekfCorrection

#--helper functions:
def sec(n_secs):
    """
    Helper function to convert timedelta into second
    
    Arguments:
        - n_secs (float), number of seconds

    Returns:
        - s (timedelta), time delta in seconds
    """
    s = timedelta(seconds=n_secs)    
    return s


def datetimearray2relativetime(datetimeArr, t0 = 'start'):
    """
    Helper function to convert datetime array to relative time in seconds

    Arguments:
        - datetimeArr (np.ndarray[datetime]), input array of datetimes
        - TODO: t0 
    Returns:
        - relTime (np.ndarray), time array (in seconds) relative to the first time in datetimeArr
    """

    if t0 == 'start':
        t0 = datetimeArr[0]

    relTime = [timestep.total_seconds() for timestep in (datetimeArr-t0)]
    return relTime


def RCfilter(b, fc, fs):
    """
    Helper function to perform RC filtering

    Arguments:
        - b (np.ndarray), array of values to be filtered
        - fc (float), cutoff frequency, fc = 1/(2πRC)
        - fsn(float), sampling frequency 

    Returns:
        - a (np.ndarray), array of filtered input values
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

    Arguments:
        - timestampSorted (np.ndarray[datetime]), sorted array of rounded IMU timestamps

    Returns
        - timestampSorted_ms (np.ndarray[datetime]), sorted datetime array with added milliseconds
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
    
def IMUtoXYZ(imufile: str, fs: float, timeWindow: tuple = None ) -> dict:
    """
    Main function to collate IMU and GPS records. The IMU fields are cropped to lie within the available 
    GPS record and then the GPS is interpolated up to the IMU rate using the IMU as the master time.

    Arguments:
        - imufile (str), path to file containing IMU data
        - fs (float),  sampling frequency

    Returns:
        - IMU (dict), dictionary containing acc ['ai'], vel ['vi'], pos ['pi'], and time ['time'] as entries
    """
    #-- Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 
    logger.info(create_log_header(__name__))
    #TODO: handle badvalues

    # Initialization:
    IMU = {'ax':None,'ay':None,'az':None,
           'vx':None,'vy':None,'vz':None,
           'px':None,'py':None,'pz':None,
           'time':None}
    
    # Read in acceleration, magnetometer, and gyroscope data:
    logger.info('Reading and sorting IMU')
    timestamp, acc, mag, gyo = readIMU(imufile)

    # Sorting:
    sortInd = np.asarray(timestamp).argsort()
    timestampSorted = np.asarray(timestamp)[sortInd]
    accSorted = np.asarray(acc)[sortInd,:].transpose()
    magSorted = np.asarray(mag)[sortInd,:].transpose()
    gyoSorted = np.asarray(gyo)[sortInd,:].transpose()
    
    # Correct mag:
    A_inv = np.array([[ 2.03529978e-02, -7.95883196e-05, -3.98024918e-04],
                      [-7.95883196e-05,  2.02178972e-02,  1.78961242e-04],
                      [-3.98024918e-04,  1.78961242e-04,  2.22384399e-02]])

    b = np.array([[-50.91885137],
                  [-19.06614668],
                  [-85.08888731]])

    magSorted  = correct_mag(magSorted, A_inv, b)

    
    # Trimming #TODO: not tested live...
    # print(len(timestampSorted))
    # skipFirstSecs = 60 #TODO: make input on config, log etc.
    # skipBool = timestampSorted >= timestampSorted[0] + timedelta(seconds=skipFirstSecs)
    # skipBool3 = np.tile(skipBool, (3,1))
    # accSorted = accSorted[skipBool3].reshape((3, -1))
    # magSorted = magSorted[skipBool3].reshape((3, -1))
    # gyoSorted = gyoSorted[skipBool3].reshape((3, -1))
    # timestampSorted = timestampSorted[skipBool]
    # print(len(timestampSorted))
    
    # Determine which way is up:
    logger.info('Finding up')
    accMeans = list()
    for ai in accSorted:
        accMeans.append(np.mean(ai))
    upIdx = np.argmin(np.abs(np.asarray(accMeans) - 9.81))
    
    # print(accSorted[upIdx])
    accSorted = change_up_axis(accSorted,upIdx)
    gyoSorted = change_up_axis(gyoSorted,upIdx)
    magSorted = change_up_axis(magSorted,upIdx)
     # print(accSorted[2])

    print(f'Coordinate position {upIdx} assigned as up')
    logger.info(f'Coordinate position {upIdx} assigned as up')

    # Create a master time array based on the specified sampling frequency and the start and end times:
    dt = sec(fs**(-1))
    t0 = timestampSorted[0]
    tf = timestampSorted[-1]
    masterTime = np.arange(t0,tf,dt).astype(datetime)

    print(masterTime[0])
    print(masterTime[-1])

    # Add milliseconds to each second of the rounded IMU timestamps:
    timestampSorted_ms = add_ms_to_IMUtime(timestampSorted)

    # Interpolate IMU onto master clock:
    logger.info('Interpolating IMU onto master clock')
    
    # Convert datetime ranges to a relative number of total seconds:
    masterTimeSec = datetimearray2relativetime(masterTime)
    imuTimeSec    = datetimearray2relativetime(timestampSorted_ms)

    # Interpolate:
    accInterp = [np.interp(masterTimeSec,imuTimeSec,a) for a in accSorted]
    magInterp = [np.interp(masterTimeSec,imuTimeSec,m) for m in magSorted]
    gyoInterp = [np.interp(masterTimeSec,imuTimeSec,g) for g in gyoSorted]

    if timeWindow is not None:
        t_win0 = timeWindow[0]
        t_winf = timeWindow[-1]

        winBool = np.logical_and(masterTime >= t_win0, masterTime <= t_winf)
        accInterp = accInterp[:,winBool]





    # Count number of NaNs TODO: handle nans; log?
    np.isnan(accInterp).sum()
    np.isnan(magInterp).sum()
    np.isnan(gyoInterp).sum()
    
    

    # Reference frame transformation:
    import matplotlib.pyplot as plt
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')

    ax1.scatter(magInterp[0], magInterp[1], magInterp[2], s=5, color='r')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')

    # plot unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax1.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
    ax1.plot_surface(x, y, z, alpha=0.3, color='b')
    
    ax1.set_xlim([-1.2, 1.2])
    ax1.set_ylim([-1.2, 1.2])
    ax1.set_zlim([-1.2, 1.2])

    #TODO: del below
    fig, ax = plt.subplots(1,1)
    ax.plot(masterTime,accInterp[2] - np.mean(accInterp[2]),alpha=0.5)
    ax.axvline(t0)
    ax.axvline(tf)

    #TODO: del above

    ax_earth, ay_earth, az_earth = ekfCorrection(*accInterp,*gyoInterp,*magInterp)
    
    # accInterp = [ax_earth, ay_earth, az_earth]  #TODO: uncomment

    ax.plot(masterTime,accInterp[2] - np.mean(accInterp[2]),alpha=0.5)

    # *accEarth = ekfCorrection(*accInterp,*gyoInterp,*magInterp)
    # accEarth = [ax_earth,ay_earth,az_earth]
    #TODO:  comment out above

    # Integration:
    logger.info('Integrating IMU')
    fc = 0.04
    filt = lambda *b : RCfilter(*b,fc,fs)
    # X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accEarth][:] # X = [ax,ay,az], Y = ... 
    X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accInterp][:] # X = [ax,ay,az], Y = ... 

    # Unpack outputs into IMU dictionary:
    IMU['ax'],IMU['vx'],IMU['px'] = X # IMU.update({'ax': X[0], 'ay': Y[0], 'az': Z[0]})
    IMU['ay'],IMU['vy'],IMU['py'] = Y
    IMU['az'],IMU['vz'],IMU['pz'] = Z
    IMU['time'] = masterTime
    
    logger.info('--------------------------------------------')
    return IMU  # X[0], Y[0], Z[0], X[1], Y[1], Z[1], X[2], Y[2], Z[2], masterTime # ax, ay, az, vx, vy, vz, px, py, pz
