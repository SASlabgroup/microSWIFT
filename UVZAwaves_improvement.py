from os import access
from termios import VEOL
from matplotlib import markers
import numpy as np
import matplotlib.pyplot as plt
from IMU.IMUtoXYZ import IMUtoXYZ
from GPS.GPStoUVZ import GPStoUVZ
from waves.UVZAwaves import UVZAwaves
from waves.GPSwaves import GPSwaves
from datetime import datetime, timedelta
from utils.collateIMUandGPS import collateIMUandGPS
from IMU.calibrateMag import calibrateMag
# from waves.cumtrapz import cumtrapz
# TODO: organize test files! and make this a proper test function...
dataDir  = './waves/testdata/'
IMUdataFilename = 'microSWIFT017_IMU_23Aug2022_222010UTC.dat'
GPSdataFilename = 'microSWIFT017_GPS_23Aug2022_222012UTC.dat'


# IMUdataFilename = 'microSWIFT017_IMU_23Aug2022_220012UTC.dat'
# GPSdataFilename = 'microSWIFT017_GPS_23Aug2022_220013UTC.dat'
# IMUdataFilename =  'microSWIFT057_IMU_17Aug2022_000146UTC.dat'  #'microSWIFT043_IMU_16Aug2022_002021UTC.dat'# 'microSWIFT043_IMU_15Aug2022_210005UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
# GPSdataFilename =  'microSWIFT057_GPS_17Aug2022_000151UTC.dat' #'microSWIFT043_GPS_16Aug2022_002022UTC.dat'#'microSWIFT043_GPS_15Aug2022_210006UTC.dat' #'microSWIFT043_GPS_05May2022_200007UTC.dat'#'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT014_GPS_27Oct2021_190009UTC.dat'
# IMUdataFilename = 'microSWIFT014_IMU_27Oct2021_190006UTC.dat' #'microSWIFT021_IMU_12Jul2021_210000UTC.dat' # 'microSWIFT057_IMU_17Aug2022_000146UTC.dat'  #'microSWIFT043_IMU_16Aug2022_002021UTC.dat'# 'microSWIFT043_IMU_15Aug2022_210005UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
# GPSdataFilename = 'microSWIFT014_GPS_27Oct2021_190009UTC.dat' # 'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT057_GPS_17Aug2022_000151UTC.dat' #'microSWIFT043_GPS_16Aug2022_002022UTC.dat'#'microSWIFT043_GPS_15Aug2022_210006UTC.dat' #'microSWIFT043_GPS_05May2022_200007UTC.dat'#'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT014_GPS_27Oct2021_190009UTC.dat'
# IMUdataFilename = 'microSWIFT021_IMU_12Jul2021_210000UTC.dat' # 'microSWIFT057_IMU_17Aug2022_000146UTC.dat'  #'microSWIFT043_IMU_16Aug2022_002021UTC.dat'# 'microSWIFT043_IMU_15Aug2022_210005UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
# GPSdataFilename = 'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT057_GPS_17Aug2022_000151UTC.dat' #'microSWIFT043_GPS_16Aug2022_002022UTC.dat'#'microSWIFT043_GPS_15Aug2022_210006UTC.dat' #'microSWIFT043_GPS_05May2022_200007UTC.dat'#'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT014_GPS_27Oct2021_190009UTC.dat'
# testName = 'Offshore Duck 27Oct2021' #'Westport 12Jul2021'

# testName = 'Westport 12Jul2021'
# CDIPfile = 'CDIP192_Oct2021.csv' # './waves/testdata/CDIP036_Jul2021.csv'
# CDIPfile = 'CDIP036_Jul2021.csv'
# fs = 12 #TODO: fix from input or timestamp diff; does NOT work for 48Hz

#%%
#%% import CDIP
# import pandas as pd
# """Evaluate dataframe columns to convert them from strings to lists"""
# def str_to_list(df,columns):
#     for col in columns:
#         df[col] = [eval(freq) for freq in df[col]]
#     return df
    
# df_buoy = pd.read_csv(dataDir+CDIPfile,delimiter=';',skiprows=0)#.set_index('datetime',inplace=True)

# df_buoy['time'] = pd.to_datetime(df_buoy['time'])
# df_buoy.set_index('time',inplace=True)
# str_to_list(df_buoy,columns=['freq','energy','a1','b1','a2','b2','check','dir','spread'])
# CDIP = df_buoy[df_buoy.index==datetime(2021, 10, 27, 19, 30, 0, 0)]

#%%

magCal, A_inv, b = calibrateMag(mag = [], fromFile = True, imufile = f'{dataDir}{IMUdataFilename}')

#%%
GPS = GPStoUVZ(f'{dataDir}{GPSdataFilename}')
# u, v, z, lat, lon, GPStime = GPStoUVZ(f'{dataDir}{GPSdataFilename}')
#%%
startTime = datetime(2022,8,23,22,22,0)
endTime = datetime(2022,8,23,22,30,0)
imufile = f'{dataDir}{IMUdataFilename}'
timeWindow = (startTime, endTime)
# IMU = IMUtoXYZ(f'{dataDir}{IMUdataFilename}', fs, timeWindow = (startTime, endTime)) #(startTime, endTime)
#%%
#TODO:
# - 
# - 
# - 
""" content of IMUtoXYZ.py """
# Initialization:
from IMU.readIMU import readIMU #TODO: if name is main here?
from IMU.integrateIMU import integrate_acc
from IMU.transformIMU import change_up_axis, correct_mag, ekfCorrection
from IMU.IMUtoXYZ import sec, add_ms_to_IMUtime, datetimearray2relativetime, RCfilter #TODO: make filters module
IMU = {'ax':None,'ay':None,'az':None,
       'vx':None,'vy':None,'vz':None,
       'px':None,'py':None,'pz':None,
       'time':None}

# Read in acceleration, magnetometer, and gyroscope data:
# logger.info('Reading and sorting IMU')
timestamp, acc, mag, gyo = readIMU(imufile)
# Sorting:
sortInd = np.asarray(timestamp).argsort()
timestampSorted = np.asarray(timestamp)[sortInd]
accSorted = np.asarray(acc)[sortInd,:].transpose()
magSorted = np.asarray(mag)[sortInd,:].transpose()
gyoSorted = np.asarray(gyo)[sortInd,:].transpose()

# Trim
if timeWindow is not None:
    skipBool = np.logical_and(timestampSorted >= timeWindow[0], timestampSorted <= timeWindow[-1])
    skipBool3 = np.tile(skipBool, (3,1))
    accSorted = accSorted[skipBool3].reshape((3, -1))
    magSorted = magSorted[skipBool3].reshape((3, -1))
    gyoSorted = gyoSorted[skipBool3].reshape((3, -1))
    timestampSorted = timestampSorted[skipBool]

# Correct mag:
# A_inv = np.array([[ 2.03529978e-02, -7.95883196e-05, -3.98024918e-04],
#                   [-7.95883196e-05,  2.02178972e-02,  1.78961242e-04],
#                   [-3.98024918e-04,  1.78961242e-04,  2.22384399e-02]])
# b = np.array([[-50.91885137],
#               [-19.06614668],
#               [-85.08888731]])
magSorted  = correct_mag(magSorted, A_inv, b)

# Trimming #TODO: not tested live...
# print(len(timestampSorted))
# skipFirstSecs = 60 #TODO: make input on config, log etc.


# print(len(timestampSorted))

# Determine which way is up:
# logger.info('Finding up')
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
# logger.info(f'Coordinate position {upIdx} assigned as up')

accSorted_f = np.zeros(np.shape(accSorted))
from scipy import signal
for i, ai in enumerate(accSorted):
    sig = ai
    sos = signal.butter(3, 2, 'lp', fs=12, output='sos')
    accSorted_f[i] = signal.sosfilt(sos, sig)

accSorted = accSorted_f.copy()

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
# logger.info('Interpolating IMU onto master clock')

# Convert datetime ranges to a relative number of total seconds:
masterTimeSec = datetimearray2relativetime(masterTime)
imuTimeSec    = datetimearray2relativetime(timestampSorted_ms)

# Interpolate:
accInterp = [np.interp(masterTimeSec,imuTimeSec,a) for a in accSorted]
magInterp = [np.interp(masterTimeSec,imuTimeSec,m) for m in magSorted]
gyoInterp = [np.interp(masterTimeSec,imuTimeSec,g) for g in gyoSorted]

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
# logger.info('Integrating IMU')
fc = 0.04
filt = lambda *b : RCfilter(*b,fc,fs)
# X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accEarth][:] # X = [ax,ay,az], Y = ... 
X,Y,Z=[integrate_acc(a,masterTimeSec,filt) for a in accInterp][:] # X = [ax,ay,az], Y = ... 
# Unpack outputs into IMU dictionary:
IMU['ax'],IMU['vx'],IMU['px'] = X # IMU.update({'ax': X[0], 'ay': Y[0], 'az': Z[0]})
IMU['ay'],IMU['vy'],IMU['py'] = Y
IMU['az'],IMU['vz'],IMU['pz'] = Z
IMU['time'] = masterTime



# ax, ay, az, vx, vy, vz, px, py, pz, IMUtime = IMUtoXYZ(f'{dataDir}{IMUdataFilename}',fs)
#TODO: be certain the right az is being returned...
#%%

# def hyst(x, th_lo, th_hi, initial = False):
#     hi = x >= th_hi
#     lo_or_hi = (x <= th_lo) | hi
#     ind = np.nonzero(lo_or_hi)[0]
#     if not ind.size: # prevent index error if ind is empty
#         return np.zeros_like(x, dtype=bool) | initial
#     cnt = np.cumsum(lo_or_hi) # from 0 to len(x)
#     return np.where(cnt, hi[ind[cnt-1]], initial)

# idx = hyst(IMU['az'], -0.5, 0.1, False)

# def zcr(x, y):
#     return x[np.diff(np.sign(y)) != 0]

# zcrtime = zcr(IMU['time'], IMU['az'])

# zero_crossings = np.where(np.diff(np.sign(IMU['az'])))[0]
# IMU['time'][zero_crossings]
#%%
from IMU.integrateIMU import demean
from IMU.integrateIMU import cumtrapz

def integrate_acc_loc(a,t,filt):

    # determine 30 second window to zero out after filtering
    fs = np.mean(np.diff(t))**(-1)
    zeroPts = 0 #int(np.round(30*fs))

    ai = a.copy()
    # ai = demean(ai) #IMU.acc(:,i) - 10.025;
    # ai[:zeroPts] = 0 # zero initial oscillations from filtering
    # ai = demean(ai) #IMU.acc(:,i) - 10.025;

    # fig, ax = plt.subplots(3,1)
    # ax[0].plot(t, ai, alpha=1, marker = '.')


    vi = cumtrapz(y=ai, x=t, initial=0)  # [m/s]
    # vi = filt(vi)
    # vi = demean(vi) 
    # vi[:zeroPts] = 0
    vi = demean(vi) 

    # ax[1].plot(t, vi, alpha=1, marker = '.')


    pi = cumtrapz(y=vi,x=t,initial=0)  # [m/s]
    pi = pi - pi[0]#TODO:
    # pi = filt(pi)
    # pi = demean(pi) 
    # pi[:zeroPts] = 0
    # pi = demean(pi) 

    # ax[2].plot(t, pi, alpha=1, marker = '.')


    return ai,vi,pi
#%%
trimStart = datetime(2022,8,23,22,22,29) #NOTE: for wake data
trimEnd = datetime(2022,8,23,22,22,59)

# trimStart = datetime(2021,10,27,19,0,30) #NOTE: for Oct Duck data
# trimEnd = datetime(2021,10,27,19,50,0)

#TODO: use threshold to increase density near zeros
npts_intp = int(np.round(masterTimeSec[-1] - masterTimeSec[0])*100)
t_intp = np.linspace(masterTimeSec[0], masterTimeSec[-1], npts_intp)
az_intp = np.interp(t_intp, masterTimeSec, (accInterp[2] - 9.81))
zero_crossings = np.where(np.diff(np.sign(az_intp)))[0]
#TODO: remove outliers
zero_crossings = zero_crossings[::2]

""" rel time plots """
trimRel = datetimearray2relativetime(np.array([trimStart, trimEnd]), masterTime[0])
fig, ax = plt.subplots(1,1)
# acc z
ax.plot(t_intp, az_intp, alpha=0.5, marker = '.')
# ax.plot(t_intp,az_intp,alpha=0.5, marker = '.')
# ax.plot(t_intp[zero_crossings],az_intp[zero_crossings],alpha=0.5, marker = 'x')
[ax.axvline(x, linewidth=1, color='g') for x in t_intp[zero_crossings] if x < trimRel[-1]]
ax.set_xlim(trimRel)
ax.axhline(0, linewidth = 0.5, color = 'k')


#%%
for i in range(0,len(zero_crossings[0:])-1):

    t_i  = t_intp[zero_crossings[i]: zero_crossings[i+1]]
    az_i = az_intp[zero_crossings[i]: zero_crossings[i+1]]

    fs_interp = np.mean(np.diff(t_i))**(-1)
    filt = lambda *b : RCfilter(*b,fc = 0.04,fs = fs_interp)
    az_interval , vz_interval, pz_interval  = integrate_acc_loc(az_i, t_i, filt)

    if i == 0:
        t_intv  =  t_i
        az_intv =  az_interval
        vz_intv =  vz_interval
        pz_intv =  pz_interval

    else:
        t_intv  =  np.concatenate((t_intv, t_i), axis=0)
        az_intv =  np.concatenate((az_intv, az_interval), axis=0)
        vz_intv =  np.concatenate((vz_intv, vz_interval), axis=0)
        pz_intv =  np.concatenate((pz_intv, pz_interval), axis=0)


#%%
""" rel time plots """

fig, ax = plt.subplots(2,1)
# acc z
# ax[0].plot(masterTimeSec,IMU['az'],alpha=0.5, marker = '.')
ax[0].plot(t_intv,az_intv,alpha=0.5, marker = '.')
# ax[0].plot(t_intp,az_intp,alpha=0.5, marker = '.')
# ax[0].plot(t_intp[zero_crossings],az_intp[zero_crossings],alpha=0.5, marker = 'x')
# [ax[0].axvline(x, linewidth=1, color='g') for x in t_intp[zero_crossings] if x < trimRel[-1]]
# ax[0].set_xlim(trimRel)
# ax[0].set_ylim([-5, 5])
ax[0].axhline(0, linewidth = 0.5, color = 'k')

# pos z
ax[1].plot(t_intv, pz_intv, alpha=1)
# [ax[1].axvline(x, linewidth=1, color='g') for x in t_intp[zero_crossings] if x < trimRel[-1]]
# ax[1].set_xlim(trimRel)
ax[1].axhline(0, linewidth = 0.5, color = 'k')
ax[1].set_ylim([-1.5, 1.5])
# ax[1].axhline(CDIP['sigwaveheight'][0], color= 'r')


# pos z spectrum
nperseg = 2**4*np.round(fs_interp) # [samples]
overlap = 0.75
fw,Ew = signal.welch(pz_intv, fs = fs_interp, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
fig, ax = plt.subplots(1,1)
ax.plot(fw,Ew)
# ax.plot(CDIP['freq'][0],CDIP['energy'][0],'k',label='CDIP')
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlim([10**(-2),10**(0)])
ax.set_ylim([10**(-4),10**(2)])
#%% 
""" test with manually set intervals """
intervals = [
    datetime(2022,8,23,22,22,30,100*10**3),
    datetime(2022,8,23,22,22,30,500*10**3),
    datetime(2022,8,23,22,22,31,30*10**3),
    datetime(2022,8,23,22,22,31,450*10**3),
    datetime(2022,8,23,22,22,32,550*10**3),
    datetime(2022,8,23,22,22,33,150*10**3),
    datetime(2022,8,23,22,22,33,300*10**3),
    datetime(2022,8,23,22,22,33,800*10**3),
    datetime(2022,8,23,22,22,33,800*10**3),
]


""" actual time plots """
fig, ax = plt.subplots(1,1)
ax.plot(IMU['time'],IMU['az'],alpha=0.5, marker = '.')
ax.set_xlim([trimStart, trimEnd])
ax.set_ylim([-2.5, 2.5])
ax.axhline(0, linewidth = 0.5, color = 'k')
[plt.axvline(x, linewidth=1, color='g') for x in intervals]


for i in range(0,len(intervals)-1):

    interval_rel = datetimearray2relativetime(np.array([intervals[i], 
                                                        intervals[i+1]]),
                                                        masterTime[0])
    interval_rel_intp = np.linspace(interval_rel[0], interval_rel[-1], 100)

    az_interval_intp = np.interp(interval_rel_intp, masterTimeSec, IMU['az'])

    fs_interp = np.mean(np.diff(interval_rel_intp))
    filt = lambda *b : RCfilter(*b,fc = 0.04,fs = fs_interp)
    az_interval , vz_interval, pz_interval  = integrate_acc_loc(az_interval_intp, interval_rel_intp, filt)

    if i == 0:
        t_intv  =  interval_rel_intp
        az_intv =  az_interval
        vz_intv =  vz_interval
        pz_intv =  pz_interval

    else:
        t_intv  =  np.concatenate((t_intv, interval_rel_intp), axis=0)
        az_intv =  np.concatenate((az_intv, az_interval), axis=0)
        vz_intv =  np.concatenate((vz_intv, vz_interval), axis=0)
        pz_intv =  np.concatenate((pz_intv, pz_interval), axis=0)


# #%%
# fig, ax = plt.subplots(1,1)
# ax.plot(IMU['time'],IMU['px'],alpha=0.5)

# fig, ax = plt.subplots(1,1)
# ax.plot(IMU['time'],IMU['py'],alpha=0.5)

# fig, ax = plt.subplots(1,1)
# ax.plot(GPS['time'],GPS['u'],alpha=0.5)
# # ax.set_xlim([datetime(2021,10,27,19,0,0),datetime(2021,10,27,19,12,30)])

# #TODO: export and plot MATLAB az PSD
# from scipy import signal
# nperseg = 256*fs # [samples]
# overlap = 0.75
# fw,Ew = signal.welch(IMU['az'], fs= fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
# fig, ax = plt.subplots(1,1)
# ax.plot(fw,Ew)
# ax.set_yscale('log')
# ax.set_xscale('log')
# ax.set_xlim([10**(-2),10**(0)])
# ax.set_ylim([10**(-4),10**(2)])

# nperseg = 256*fs # [samples]
# overlap = 0.75
# fw,Ew = signal.welch(IMU['pz'], fs= fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
# fig, ax = plt.subplots(1,1)
# ax.plot(fw,Ew)
# ax.set_yscale('log')
# ax.set_xscale('log')
# ax.set_xlim([10**(-2),10**(0)])
# ax.set_ylim([10**(-4),10**(2)])

# #%%
# IMUcol,GPScol = collateIMUandGPS(IMU,GPS) 
# # ax, ay, az, vx, vy, vz, px, py, pz, IMUtime = IMUcol.values() #TODO: beware: unpacking can be unordered...
# # u, v, z, lat, lon, GPStime = GPScol.values() # 

# #%%
# zeroPts = int(np.round(120*fs))

# Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], fs) #TODO: check

# Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], 4)
# #TODO: error with length of freq vector...compare with GPSwaves

# #%%
# fig, ax = plt.subplots(1,1)
# ax.plot(IMUcol['time'][zeroPts:],IMUcol['az'][zeroPts:],alpha=0.5)

# fig, ax = plt.subplots(1,1)
# ax.plot(IMUcol['time'][zeroPts:],IMUcol['pz'][zeroPts:],alpha=0.5)

# #%% import CDIP
# import pandas as pd
# """Evaluate dataframe columns to convert them from strings to lists"""
# def str_to_list(df,columns):
#     for col in columns:
#         df[col] = [eval(freq) for freq in df[col]]
#     return df
    
# df_buoy = pd.read_csv(dataDir+CDIPfile,delimiter=';',skiprows=0)#.set_index('datetime',inplace=True)

# df_buoy['time'] = pd.to_datetime(df_buoy['time'])
# df_buoy.set_index('time',inplace=True)
# str_to_list(df_buoy,columns=['freq','energy','a1','b1','a2','b2','check','dir','spread'])

# CDIP = df_buoy[df_buoy.index==datetime(2021, 10, 27, 19, 30, 0, 0)]

# # import xarray as xr
# # import pandas as pd
# # # url = 'https://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/192p1/192p1_historic.nc'
# # # url = './waves/testdata/192p1_rt.nc'
# # # url = './waves/testdata/036p1_rt.nc'
# # url = './waves/testdata/036p1_d46.nc'


# # ds = xr.open_dataset(url)

# # d_buoy = {
# #     'lat' : ds['waveEnergyDensity']['metaDeployLatitude'].values,
# #     'lon' : ds['waveEnergyDensity']['metaDeployLongitude'].values,
# #     'Datetime' : ds['waveTime'].values,
# #     'frequency' : len(ds['waveTime'].values)*[ds['waveFrequency'].values],
# #     'energyDensity' : [np.array(E) for E in ds['waveEnergyDensity'].values],
# #     'a1' : [np.array(E) for E in ds['waveA1Value'].values],
# #     'b1' : [np.array(E) for E in ds['waveB1Value'].values],
# #     'a2' : [np.array(E) for E in ds['waveA2Value'].values],
# #     'b2' : [np.array(E) for E in ds['waveB2Value'].values],            
# #     'significantHeight' : ds['waveHs'].values,
# #     'peakPeriod' : ds['waveTp'].values,
# #     'energyPeriod' : ds['waveTa'].values,
# # }

# # df_buoy = pd.DataFrame(d_buoy)
# # df_buoy = df_buoy.set_index('Datetime')

# meanTime = datetime.fromtimestamp(np.mean([t.timestamp() for t in IMU['time']]))
# CDIP = df_buoy[df_buoy.index==datetime(2021, 10, 27, 19, 30, 0, 0)]
# # CDIP = df_buoy[df_buoy.index==datetime(2021, 7, 12, 21, 0, 0, 0)]

# #%% import RV Carson data from MATLAB
# # import pandas as pd
# # filename = './waves/testdata/RV_Carson_microSWIFT043_earth.csv'
# # MATLAB = pd.read_csv(filename)
# #%% compare results
# fig, ax = plt.subplots(1,1,figsize=(6, 4))
# plt.title(testName)
# ax.plot(f,E,label='UVZAwaves')
# # ax.plot(MATLAB.f,MATLAB.E)
# # ax.plot(fw,Ew,label='Welch')
# ax.plot(f_2,E_2,label='GPSwaves')
# ax.plot(CDIP['freq'][0],CDIP['energy'][0],'k',label='CDIP')
# # ax.plot(CDIP['frequency'][0],CDIP['energyDensity'][0],'k',label='CDIP')
# ax.set_yscale('log')
# ax.set_xscale('log')
# ax.set_xlim([10**(-2),10**(0)])
# ax.set_ylim([10**(-4),10**(2)])
# ax.set_ylabel('energy (m^2/Hz)')
# ax.set_xlabel('frequency (Hz)')
# ax.legend()
# # fig.savefig('UVZA_Westport_12Jul2021_scalar_updatedMATLABcdip.png',dpi=400)

# fig, ax = plt.subplots(4,1,figsize=(6, 6))
# ax[0].plot(f,a1)
# ax[0].plot(f_2,a1_2)
# ax[0].plot(CDIP['freq'][0],CDIP['a1'][0],'k')
# # ax[0].plot(CDIP['frequency'][0],CDIP['a1'][0],'k')
# ax[0].set_xlim([10**(-2),0.5*10**(0)])
# ax[0].set_ylim([-1 ,1])
# ax[0].set_xticks([])
# ax[0].set_ylabel('a1')
# ax[0].axhline(0,linestyle='-.',linewidth=0.5,color='k')

# ax[1].plot(f,b1)
# ax[1].plot(f_2,b1_2)
# ax[1].plot(CDIP['freq'][0],CDIP['b1'][0],'k')
# # ax[1].plot(CDIP['frequency'][0],CDIP['b1'][0],'k')
# ax[1].set_xlim([10**(-2),0.5*10**(0)])
# ax[1].set_ylim([-1 ,1])
# ax[1].set_xticks([])
# ax[1].set_ylabel('b1')
# ax[1].axhline(0,linestyle='-.',linewidth=0.5,color='k')


# ax[2].plot(f,a2)
# ax[2].plot(f_2,a2_2)
# ax[2].plot(CDIP['freq'][0],CDIP['a2'][0],'k')
# # ax[2].plot(CDIP['frequency'][0],CDIP['a2'][0],'k')
# ax[2].set_xlim([10**(-2),0.5*10**(0)])
# ax[2].set_ylim([-1 ,1])
# ax[2].set_xticks([])
# ax[2].set_ylabel('a2')
# ax[2].axhline(0,linestyle='-.',linewidth=0.5,color='k')

# ax[3].plot(f,b2)
# ax[3].plot(f_2,b2_2)
# ax[3].plot(CDIP['freq'][0],CDIP['b2'][0],'k')
# # ax[3].plot(CDIP['frequency'][0],CDIP['b2'][0],'k')
# ax[3].set_xlim([10**(-2),0.5*10**(0)])
# ax[3].set_ylim([-1 ,1])
# ax[3].set_xlabel('frequency (Hz)')
# ax[3].set_ylabel('b2')
# ax[3].axhline(0,linestyle='-.',linewidth=0.5,color='k')
# # fig.savefig('UVZA_Westport_12Jul2021_moments_updatedMATLABcdip.png',dpi=400)

# #%%



