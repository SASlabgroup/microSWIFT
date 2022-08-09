"""
Author: @jacobrdavis

A collection of functions to read in data from an IMU file, process it, and store 
the output as python variables to be used in calculations for wave properties.
TODO:
    - remove reassignment of the same variable?
    
"""
#--Import Statements
import numpy as np
from logging import getLogger
from datetime import datetime, timedelta
# from scipy import integrate

#--helper functions:
def sec(n_secs):
    """
    Helper function to convert timedelta into seconds
    Input:
        - n_secs, description...
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

def demean(x):
    """
    Helper function to demean an array
    Input:
        - x, array of values to be demeaned
    Output:
        - x_demean, array of demeaned input values
    """
    x_demean = x - np.mean(x)
    return x_demean

def integrate_acc(a,t,filt):
    """
    Helper function to perform double integration of acceleration values
    Input:
        - a, acceleration array
        - t, time array
        - filt, filter function (e.g. lambda function)
    Output:
        - x_demean, array of demeaned input values
    """
    #TODO: trim or zero out initial oscillations?
    #TODO: validate initial condition, can also just append the last point
    
    # determine 30 second window to zero out after filtering
    fs = np.mean(np.diff(t))**(-1)
    zeroPts = int(np.round(30*fs))
    ai = a.copy()
    # ai = np.delete(ai,np.s_[:250]) #TODO: wrap
    ai[:zeroPts] = 0 # zero initial oscillations from filtering
    # t  = np.delete(t,np.s_[:250])
    ai = demean(ai) #IMU.acc(:,i) - 10.025;
    vi = integrate.cumtrapz(y=ai,x=t,initial=0)  # [m/s]
    vi = filt(vi)
    vi[:zeroPts] = 0
    # vi = np.delete(vi,np.s_[:500])
    # t  = np.delete(t,np.s_[:500])
    vi = demean(vi) 
    pi = integrate.cumtrapz(y=vi,x=t,initial=0)  # [m/s]
    pi = filt(pi)
    pi[:zeroPts] = 0
    pi = demean(pi) 

    return ai,vi,pi

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

# from ahrs.filters import EKF
# from scipy.spatial.transform import Rotation as R

# def ekfCorrection(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z):
#     '''
#     @edwinrainville

#     Correct the body frame accelerations to the earth frame of reference through and extended Kalman Filter
#     '''

#     # Organize the acceleration data into arrays to be used in the ekf algorithm
#     acc_data = np.array([accel_x-np.mean(accel_x), accel_y-np.mean(accel_y), accel_z-np.mean(accel_z)]).transpose()
#     gyr_data = np.array([gyro_x-np.mean(gyro_x), gyro_y-np.mean(gyro_y), gyro_z-np.mean(gyro_z)]).transpose()
#     mag_data = np.array([mag_x-np.mean(mag_x), mag_y-np.mean(mag_y), mag_z-np.mean(mag_z)]).transpose()

#     # Rotate the acceleration data with extended Kalman filter
#     # ** the variance of each sensor needs to be further examined
#     # ** Variance is assumed from spec sheet
#     # ekf = EKF(gyr=gyr_data, acc=acc_data, mag_data=mag_data, frequency=12, var_acc=0.000003, var_gyro=0.04, var_mag=.1, frame='NED')
#     ekf = EKF(gyr=gyr_data, acc=acc_data, frequency=12, var_acc=0.000003, var_gyro=0.04, frame='NED')

    # # Rotate the acclerations from the computed Quaterions
    # r = R.from_quat(ekf.Q)
    # accel_rotated = r.apply(acc_data)

    # # Get acceleration data from the rotated structure
    # accel_x_earth = accel_rotated[:,0]
    # accel_y_earth = accel_rotated[:,1]
    # accel_z_earth = accel_rotated[:,2]

    # return accel_x_earth, accel_y_earth, accel_z_earth

def IMUtoXYZ(imufile,fs):
    """ 
    Main function to collate IMU and GPS records. The IMU fields are cropped to lie within the available 
    GPS record and then the GPS is interpolated up to the IMU rate using the IMU as the master time.
    Inputs:
        - IMU, description...
        - GPS, description...
        
    Outputs:
        - IMU, description...
        - GPS, description...
    """
    #-- Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 

    #TODO: handle badvalues

    #--initialization
    timestamp = []
    acc = []
    mag = []
    gyo = []
    IMU = {'ax':None,'ay':None,'az':None,'vx':None,'vy':None,'vz':None,'px':None,'py':None,'pz':None,'time':None}
    
    #--open imu file and read in acceleration, magnetometer, and gyroscope data
    with open(imufile, 'r') as file: #encoding="utf8", errors='ignore'
        for line in file:
            currentLine = line.strip('\n').rstrip('\x00').split(',')
            if currentLine[0] is not '':
                timestamp.append(datetime.strptime(currentLine[0],'%Y-%m-%d %H:%M:%S'))
                acc.append(list(map(float,currentLine[1:4])))  # acc = [ax,ay,az]
                mag.append(list(map(float,currentLine[4:7])))  # mag = [mx,my,mz]
                gyo.append(list(map(float,currentLine[7:10]))) # gyo = [gx,gy,gz]
          

    #--sorting: #TODO: log sorting errors?
    sortInd = np.asarray(timestamp).argsort()
    timestampSorted = np.asarray(timestamp)[sortInd]
    accSorted = np.asarray(acc)[sortInd,:].transpose()
    magSorted = np.asarray(mag)[sortInd,:].transpose()
    gyoSorted = np.asarray(gyo)[sortInd,:].transpose()
    
    #TODO:--determine which way is up
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
    
    #-- reference frame transformation and integration
    
    #TODO: reference frame transformation 
    # ax_earth, ay_earth, az_earth = ekfCorrection(*accInterp,*gyoInterp,*magInterp)
    # *accEarth = ekfCorrection(*accInterp,*gyoInterp,*magInterp)
    # accEarth = [ax_earth,ay_earth,az_earth]

    fc = 0.04
    filt = lambda *b : RCfilter(*b,fc,fs)
    # X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accEarth][:] # X = [ax,ay,az], Y = ... 
    X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accInterp][:] # X = [ax,ay,az], Y = ... 

    # assign outputs to IMU dict
    IMU['ax'],IMU['vx'],IMU['px'] = X # IMU.update({'ax': X[0], 'ay': Y[0], 'az': Z[0]})
    IMU['ay'],IMU['vy'],IMU['py'] = Y
    IMU['az'],IMU['vz'],IMU['pz'] = Z
    IMU['time'] = masterTime

    return IMU # X[0], Y[0], Z[0], X[1], Y[1], Z[1], X[2], Y[2], Z[2], masterTime # ax, ay, az, vx, vy, vz, px, py, pz


#---deleted:

    # def percent_diff(x1,x2):
    #     absDiff = np.abs(x2-x1)
    #     meanValue = (x2+x1)/2
    #     percentDiff = (absDiff/meanValue)*100
    #     return percentDiff

    # # check if inferred sampling frequency is different from specified frequency
    # fs0 = np.mean(np.diff(datetimearray2relativetime(timestampSorted)))**(-1)
    # fsPercentDiff = percent_diff(fs,fs0)
    # if fsPercentDiff > 10: # [%]
    #     #TODO: log this event?
    #     print(f'The IMU sampling frequency, inferred from the reported time series, is greater than 10 percent different from the set sampling frequency. Percent difference: {round(fsPercentDiff,1)}')


#---


    #--unpack variables and return
    # ax,vx,px = X; ay,vy,py = Y; az,vz,pz = X

    # ax, ay, az, vx, vy, vz, px, py, pz
    # X[0], Y[0], Z[0], X[1], Y[1], Z[1], X[2], Y[2], Z[2]
    # ax, ay, az, vx, vy, vz, x, y, z




    #%%
    # fig,ax = plt.subplots()
    # ax.plot(imuTimeSec,accSorted[:,1],marker='.',alpha=0.5)
    # ax.plot(masterTimeSec,accInterp,marker='.',alpha=0.5)
    # ax.set_xlim([110,120]) #[0,10]

    # fig,ax = plt.subplots()
    # ax.plot(imuTimeSec,magSorted[:,1],marker='.',alpha=0.5)
    # ax.plot(masterTimeSec,magInterp,marker='.',alpha=0.5)
    # ax.set_xlim([110,120]) #[0,10]
    # #%%
    # fig,ax = plt.subplots()
    # ax.plot(masterTimeSec,accInterp[2],marker='.',alpha=0.5)
    # ax.plot(masterTimeSec,accInterpTest,marker='.',alpha=0.5)

    # masterTimeSec = [step.total_seconds() for step in (masterTime-masterTime[0])]
    # imuTimeSec = [step.total_seconds() for step in (timestampSorted_ms-timestampSorted_ms[0])]


    # cnt = []
    # timestampSorted_ms = timestampSorted.copy()
    # i = 1
    # for n in np.arange(1, len(timestampSorted)):
    #     if timestampSorted[n] == timestampSorted[n-1]: 
    #         timestampSorted_ms[n] = timestampSorted[n] + (i * dt) 
    #         i += 1
    #         # if i > 12: #check for n > dt^(-1)
    #         #     cnt.append(n)     
    #     else:
    #         # Restart i at one so that it can start again on the next second 
    #         i = 1 

# from scipy import signal

# nperseg = 256*fs # [samples]
# overlap = 0.75
# f,accPSD = signal.welch(accInterpTest, fs= fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
# f_filt,accPSD_filt  = signal.welch(accInterp_filt, fs=fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
