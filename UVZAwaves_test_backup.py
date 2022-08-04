from os import access
from termios import VEOL
from matplotlib import markers
import numpy as np
import matplotlib.pyplot as plt
from IMU.IMUtoXYZ import IMUtoXYZ
from GPS.GPStoUVZ import GPStoUVZ
from waves.UVZAwaves import UVZAwaves
from datetime import datetime, timedelta

dataDir  = './IMU/testdata/'
IMUdataFilename = 'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
GPSdataFilename = 'microSWIFT014_GPS_27Oct2021_190009UTC.dat'
#%%
u, v, z, lat, lon = GPStoUVZ(f'{dataDir}{GPSdataFilename}')

fs = 12 #TODO: fix from input or timestamp diff
ax, ay, az, vx, vy, vz, px, py, pz = IMUtoXYZ(f'{dataDir}{IMUdataFilename}',fs)



#%% content of IMUtoXYZ

"wrapper function for timedelta in seconds"
def sec(n_secs):
    s = timedelta(seconds=n_secs)    
    return s

"datetime array to relative time in seconds"
def datetimearray2relativetime(datetimeArr):
    t0 = datetimeArr[0]
    relTime = [timestep.total_seconds() for timestep in (datetimeArr-t0)]
    return relTime

#s%%

timestamp = []
acc = []
mag = []
gyo = []

with open(f'{dataDir}{IMUdataFilename}', 'r') as file: #encoding="utf8", errors='ignore'
    for line in file:
        currentLine = line.strip('\n').split(',') 
        timestamp.append(datetime.strptime(currentLine[0],'%Y-%m-%d %H:%M:%S'))
        acc.append(list(map(float,currentLine[1:4])))
        mag.append(list(map(float,currentLine[4:7])))
        gyo.append(list(map(float,currentLine[7:10])))
        # timestamp,ax,ay,az,mx,my,mz,gx,gy,gz

#%%

sortInd = np.asarray(timestamp).argsort()

timestampSorted = np.asarray(timestamp)[sortInd]
accSorted = np.asarray(acc)[sortInd,:].transpose()
magSorted = np.asarray(mag)[sortInd,:].transpose()
gyoSorted = np.asarray(gyo)[sortInd,:].transpose()

#TODO: log sorting errors?

#%%
#TODO: comment

fs = 12 #TODO: fix from input or timestamp diff
dt = sec(fs**(-1))
t0 = timestampSorted[0]
tf = timestampSorted[-1]

masterTime = np.arange(t0,tf,dt).astype(datetime)

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

# NOTE:
# - Center sorting and fast
# - Comparing 1 and 3: np.array_equal(imu_time_with_millisecond1,imu_time_with_millisecond3) is True

#%%Interpolate IMU onto master clock
# first convert datetime ranges to a relative number of total seconds
# masterTimeSec = [step.total_seconds() for step in (masterTime-masterTime[0])]
# imuTimeSec = [step.total_seconds() for step in (timestampSorted_ms-timestampSorted_ms[0])]

masterTimeSec = datetimearray2relativetime(masterTime)
imuTimeSec    = datetimearray2relativetime(timestampSorted_ms)

#TODO: DO it for all dimensions of the array

#%%
accInterpTest = np.interp(masterTimeSec,imuTimeSec,accSorted[2])
magInterpTest = np.interp(masterTimeSec,imuTimeSec,magSorted[2])
gyoInterpTest = np.interp(masterTimeSec,imuTimeSec,gyoSorted[2])
#%%
# accInterp2 = [np.interp(masterTimeSec,imuTimeSec,a) for a in accSorted]
accInterp = [np.interp(masterTimeSec,imuTimeSec,a) for a in accSorted]
magInterp = [np.interp(masterTimeSec,imuTimeSec,m) for m in magSorted]
gyoInterp = [np.interp(masterTimeSec,imuTimeSec,g) for g in gyoSorted]

# from scipy import interpolate
# acc_f = interpolate.CubicSpline(x=imuTimeSec, y=accSorted[:,1])
# accInterp = acc_f(masterTimeSec)

#%%
# fig,ax = plt.subplots()
# ax.plot(imuTimeSec,accSorted[:,1],marker='.',alpha=0.5)
# ax.plot(masterTimeSec,accInterp,marker='.',alpha=0.5)
# ax.set_xlim([110,120]) #[0,10]

# fig,ax = plt.subplots()
# ax.plot(imuTimeSec,magSorted[:,1],marker='.',alpha=0.5)
# ax.plot(masterTimeSec,magInterp,marker='.',alpha=0.5)
# ax.set_xlim([110,120]) #[0,10]
#%%
fig,ax = plt.subplots()
ax.plot(masterTimeSec,accInterp[2],marker='.',alpha=0.5)
ax.plot(masterTimeSec,accInterpTest,marker='.',alpha=0.5)

#%% cnt number of NaNs
np.isnan(accInterp).sum()
np.isnan(magInterp).sum()
np.isnan(gyoInterp).sum()
#%%TODO: handle nans



#%% RC filter definition and testing

"RC filter function"
def RCfilter(b, fc, fs):
    RC = (2*np.pi*fc)**(-1)
    alpha = RC / (RC + 1./fs)
    a = b.copy()
    for ui in np.arange(1,len(b)): # speed this up
        a[ui] = alpha * a[ui-1] + alpha * ( b[ui] - b[ui-1] )
    return a

fc = 0.04
accInterp_filt = RCfilter(accInterpTest,fc,fs)

from scipy import signal

nperseg = 256*fs # [samples]
overlap = 0.75
f,accPSD = signal.welch(accInterpTest, fs= fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
f_filt,accPSD_filt  = signal.welch(accInterp_filt, fs=fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))

#%%
fig,ax = plt.subplots()
ax.plot(masterTimeSec,accInterp_filt,marker='.',alpha=0.5)
ax.plot(masterTimeSec,accInterpTest,marker='.',alpha=0.5)
ax.set_xlim([110,120]) #[0,10]

fig,ax = plt.subplots()
ax.plot(f_filt,accPSD_filt,marker='.',alpha=0.5)
ax.plot(f_filt,accPSD,marker='.',alpha=0.5)
ax.axvline(fc)
ax.set_yscale('log')
ax.set_xscale('log')

#%% reference frame transformation and integration
from scipy import integrate

def demean(x):
        x_demean = x - np.mean(x)
        return x_demean

def integrate_acc(a):
    #TODO: validate use of initial
    ai = RCfilter(a,fc,fs)
    ai = demean(ai) #IMU.acc(:,i) - 10.025;
    vi = integrate.cumtrapz(y=ai,x=masterTimeSec,initial=ai[0])  # [m/s]
    vi = demean(vi) 
    vi = RCfilter(vi,fc,fs)
    pi = integrate.cumtrapz(y=vi,x=masterTimeSec,initial=vi[0])  # [m/s]
    pi = demean(pi) 
    pi = RCfilter(pi,fc,fs)
    return ai,vi,pi
#%%
#TODO: DO this but for all dimensions of acc
X,Y,Z=[integrate_acc(a) for a in accInterp][:] # X = [ax,ay,az], Y = ...
# X =[integrate_acc(a) for a in [accInterp[0]]][:]
# Y =[integrate_acc(a) for a in [accInterp[1]]][:]
# Z =[integrate_acc(a) for a in [accInterp[2]]][:]

ax,vx,px = X 
ay,vy,py = Y 
az,vz,pz = Z

#%% plot outputs
# accelerations
fig,axe = plt.subplots(3,1)
axe[0].plot(masterTimeSec,ax,marker='.',alpha=0.25)
axe[1].plot(masterTimeSec,ay,marker='.',alpha=0.25)
axe[2].plot(masterTimeSec,az,marker='.',alpha=0.25)
# velocities
fig,axe = plt.subplots(3,1)
axe[0].plot(masterTimeSec,vx,marker='.',alpha=0.25)
axe[1].plot(masterTimeSec,vy,marker='.',alpha=0.25)
axe[2].plot(masterTimeSec,vz,marker='.',alpha=0.25)
# positions
fig,axe = plt.subplots(3,1)
axe[0].plot(masterTimeSec,px,marker='.',alpha=0.25)
axe[1].plot(masterTimeSec,py,marker='.',alpha=0.25)
axe[2].plot(masterTimeSec,pz,marker='.',alpha=0.25)

#%%
#%%
# def initRCfilt(fc,fs):
#     def RCfilter(b):
#         RC = (2*np.pi*fc)**(-1)
#         alpha = RC / (RC + 1./fs)
#         a = b.copy()
#         for ui in np.arange(1,len(b)): # speed this up
#             a[ui] = alpha * a[ui-1] + alpha * ( b[ui] - b[ui-1] )
#         return f(b,fc,fs)
#     return RCfilter
fc = 0.04
fs = 12
filt = lambda *b : RCfilter(*b,fc,fs)
filt([1,2,3])


# filt = initRCfilt(fc,fs)    

# filtParams = (fc,fs)







#%%
#TODO: validate fs
ax2, ay2, az2, vx2, vy2, vz2, px2, py2, pz2 = IMUtoXYZ(f'{dataDir}{IMUdataFilename}',fs)
#ax2, vx2, px2, ay2, vy2, py2, az2, vz2, pz2
#%%

print(sum(ax-ax2))
print(sum(ay-ay2))
print(sum(az-az2))

print(sum(vx-vx2))
print(sum(vy-vy2))
print(sum(vz-vz2))

print(sum(px-px2))
print(sum(py-py2))
print(sum(pz-pz2))

#%%


# accelerations
fig,axe = plt.subplots(3,1)
axe[0].plot(masterTimeSec,ax,alpha=0.5)
axe[0].plot(masterTimeSec,ax2,alpha=0.5)
axe[1].plot(masterTimeSec,ay,alpha=0.5)
axe[1].plot(masterTimeSec,ay2,alpha=0.5)
axe[2].plot(masterTimeSec,az,alpha=0.5)
axe[2].plot(masterTimeSec,az2,alpha=0.5)

# velocities
fig,axe = plt.subplots(3,1)
axe[0].plot(masterTimeSec,vx,alpha=0.5)
axe[0].plot(masterTimeSec,vx2,alpha=0.5)
axe[1].plot(masterTimeSec,vy,alpha=0.5)
axe[1].plot(masterTimeSec,vy2,alpha=0.5)
axe[2].plot(masterTimeSec,vz,alpha=0.5)
axe[2].plot(masterTimeSec,vz2,alpha=0.5)

# positions
fig,axe = plt.subplots(3,1)
axe[0].plot(masterTimeSec,px,alpha=0.5)
axe[0].plot(masterTimeSec,px2,alpha=0.5)
axe[1].plot(masterTimeSec,py,alpha=0.5)
axe[1].plot(masterTimeSec,py2,alpha=0.5)
axe[2].plot(masterTimeSec,pz,alpha=0.5)
axe[2].plot(masterTimeSec,pz2,alpha=0.5)


#-------------- scraps ---------------%
#%% timing code
# import time
# t0 = time.time()
# code here
# t1 = time.time()
# total_n = t1-t0
# print(total_n)
#%% Logical indexing by whole second 
# "wrapper function for timedelta in seconds"
# def sec(n_secs):
#     s = timedelta(seconds=n_secs)    
#     return s

# fs = 12 #TODO: fix from input or timestamp diff
# dt = sec(fs**(-1))
# t0 = timestampSorted[0]
# tf = timestampSorted[-1]

# masterTime = np.arange(t0,tf,dt).astype(datetime)
# wholeSecs  = np.arange(t0,tf,sec(1)).astype(datetime)

# imu_time_with_millisecond1 = timestampSorted.copy()
# for second in wholeSecs:
#     inSec = timestampSorted==second #0.001127
#     length = inSec.sum() # 0.00042
#     dt0 = sec(float(length)**(-1)) # 7.0810e-05
#     secSteps = np.arange(0,length)*dt0 #0.00012; 
#     imu_time_with_millisecond1[inSec] = timestampSorted[inSec] + secSteps # 0.000101

# NOTE:
# - Center sorting but kind of slow

#%% From EJ codes
# fs = 12 #TODO: fix from input or timestamp diff
# dt = sec(fs**(-1))

# # cnt = []
# imu_time_with_millisecond2 = timestampSorted.copy()
# i = 1
# for n in np.arange(1, len(timestampSorted)):
#     if timestampSorted[n] == timestampSorted[n-1]: 
#         imu_time_with_millisecond2[n] = timestampSorted[n] + (i * dt) 
#         i += 1
#         # if i > 12: #check for n > dt^(-1)
#         #     cnt.append(n)     
#     else:
#         # Restart i at one so that it can start again on the next second 
#         i = 1 

# NOTE:
# - Much faster, but what happens when this method has n > dt^(-1)?
#       -> seconds are double counted (see line 170 for example)
#       -> But for 12 Hz, n > 12 samples only occurs about 1% of the time
# - This version shifts times to the start of a second, which could result in errors 
#   when n is small (seconds will end prematurely) -> may be better to center in second?

#%% combination of both
#TODO: fix so it does the last second
# imu_time_with_millisecond3 = timestampSorted.copy()
# i = 1
# for n in np.arange(1, len(timestampSorted)):
#     if timestampSorted[n] == timestampSorted[n-1]: 
#         i += 1 # count number of occurences in second
#     else:
#         dt0 = sec(float(i)**(-1))
#         secSteps = np.arange(0,i)*dt0
#         imu_time_with_millisecond3[n-i:n] = timestampSorted[n-i:n] + secSteps

#         # Restart i at one so that it can start again on the next second 
#         i = 1 

# NOTE:
# - Center sorting and fast
# - Comparing 1 and 3: np.array_equal(imu_time_with_millisecond1,imu_time_with_millisecond3) is True

#%%---- content of collateIMUandGPS
"function to crop each key of dict based on a boolean array"
def crop_dict(d,cropBool):
    for key in d.keys():
        d[key] = d[key][cropBool]
    return d    
#%% crop IMU values to lie within the GPS times (since GPS is being interpolated onto IMU time)

startCrop = GPS['time'][0]
endCrop   = GPS['time'][-1]

imuCrop = np.logical_and(IMU['time'] >= startCrop, IMU['time'] <= endCrop)

IMU = crop_dict(IMU,imuCrop)
#%%
"datetime array to relative time in seconds"
def datetimearray2relativetime(datetimeArr,t0):
    relTime = [timestep.total_seconds() for timestep in (datetimeArr-t0)]
    return relTime

relTimeGPS = datetimearray2relativetime(GPS['time'],t0=startCrop)
relTimeIMU = datetimearray2relativetime(IMU['time'],t0=startCrop)

#%%
# interpolate the GPS values onto the IMU time
GPSinterp = {}
NaNbools = []

for key in GPS.keys()-['time']:
    GPSinterp[key] = np.interp(relTimeIMU,relTimeGPS,GPS[key]) 
    #TODO: make GPS instead of GPSinterp
    if key is 'u':
        GPSinterp['u'][0] = np.NaN #TODO: delete me
    NaNbools.append(~np.isnan(GPSinterp[key])) # record any exterior NaNs

GPSinterp.update({'time':IMU['time']}) # update new GPS dict with datetime 

#TODO: indicate successful interpolation and log length?

#%%
fig, ax = plt.subplots(1,1)
ax.scatter(relTimeGPS,GPS['v'],alpha=1)
ax.scatter(relTimeIMU,GPSinterp['v'],alpha=0.2)
# ax.set_xlim([2986,2990])
# ax.set_xlim([0,.5])
#%%
#% Crop NaN values

# np.logical_and(NaNbools)
nonNaN = np.logical_and.reduce(np.asarray(NaNbools))
numNaNs = len(nonNaN) - sum(nonNaN)
if numNaNs>0:
    IMU = crop_dict(IMU,nonNaN)
    GPSinterp = crop_dict(GPSinterp,nonNaN)
    #TODO: log "numNaNs removed
#%%

np.nansum(IMU['az'] - IMUcol['az'])







#%%
# [np.interp(masterTimeSec,imuTimeSec,g) for g in gyoSorted]
# return

%% Interpolate GPS onto master clock
masterTime = IMU.time
# [C,ia,ic] = unique(masterTime)
# [C,ia,ic] = unique(GPS.time);
GPS.lat = interp1(GPS.time.',GPS.lat.',masterTime);
GPS.lon = interp1(GPS.time.',GPS.lon.',masterTime);
GPS.sog = interp1(GPS.time.',GPS.sog.',masterTime);
GPS.cog = interp1(GPS.time.',GPS.cog.',masterTime);
GPS.z   = interp1(GPS.time.',GPS.z.'  ,masterTime);
GPS.u   = interp1(GPS.time.',GPS.u.'  ,masterTime);
GPS.v   = interp1(GPS.time.',GPS.v.'  ,masterTime);
GPS.x   = interp1(GPS.time.',GPS.x.'  ,masterTime);
GPS.y   = interp1(GPS.time.',GPS.y.'  ,masterTime);
GPS.time = masterTime;

#%%

# # collateIMUandGPS(IMU,GPS)

# # set crop window based on minimum structure array length:
# # startCrop = max([IMU['time'][0],GPS['time'][0]])
# # endCrop   = min([IMU['time'][-1],GPS['time'][-1]])

# # imuCrop = np.logical_and(IMU['time'] >= startCrop, IMU['time'] <= endCrop)
# # gpsCrop = np.logical_and(GPS['time'] >= startCrop, GPS['time'] <= endCrop)

# # crop IMU values to lie within the GPS times (since GPS is being interpolated onto IMU time)
# startCrop = GPS['time'][0]
# endCrop   = GPS['time'][-1]

# imuCrop = np.logical_and(IMU['time'] >= startCrop, IMU['time'] <= endCrop)
# # gpsCrop = np.logical_and(GPS['time'] >= startCrop, GPS['time'] <= endCrop)

# # def crop_dict(dict,cropBool):
# #     for key in dict.keys():
# #         dict[key] = dict[key][cropBool]

# #     return dict

# IMU = crop_dict(IMU,imuCrop)

# for key in dict.keys():
#     IMU[key] = IMU[key][imuCrop]
# # GPS = crop_dict(GPS,gpsCrop)
#%%
    # % create logical arrays:
    # imuCrop = IMU.time >= startCrop & IMU.time <= endCrop;
    # gpsCrop = GPS.time >= startCrop & GPS.time <= endCrop;

    # % perform cropping for each field:
    # IMU = cropStructFields(IMU,imuCrop);
    # GPS = cropStructFields(GPS,gpsCrop);

    # %% Interpolate GPS onto master clock
    # masterTime = IMU.time;
    # % datetime(masterTime, 'ConvertFrom', 'datenum','Format', 'yyyy-MM-dd HH:mm:ss.SSS')
    # % 
    # % [C,ia,ic] = unique(masterTime)
    # % 
    # % figure; hold on
    # % plot(ia)
    # % plot(ic)
    # % 
    # % [C,ia,ic] = unique(GPS.time);
    # % ;
    # % 




    # GPS.lat = interp1(GPS.time.',GPS.lat.',masterTime);
    # GPS.lon = interp1(GPS.time.',GPS.lon.',masterTime);
    # GPS.sog = interp1(GPS.time.',GPS.sog.',masterTime);
    # GPS.cog = interp1(GPS.time.',GPS.cog.',masterTime);
    # GPS.z   = interp1(GPS.time.',GPS.z.'  ,masterTime);
    # GPS.u   = interp1(GPS.time.',GPS.u.'  ,masterTime);
    # GPS.v   = interp1(GPS.time.',GPS.v.'  ,masterTime);
    # GPS.x   = interp1(GPS.time.',GPS.x.'  ,masterTime);
    # GPS.y   = interp1(GPS.time.',GPS.y.'  ,masterTime);

    # GPS.time = masterTime;

    # %% Crop NaN values
    # nonNaN = ~isnan(GPS.lat) & ~isnan(GPS.lon) & ...
    #         ~isnan(GPS.sog) & ~isnan(GPS.cog) & ~isnan(GPS.z) & ...
    #         ~isnan(GPS.u)   & ~isnan(GPS.v)   & ...
    #         ~isnan(GPS.x)   & ~isnan(GPS.y)   ;

    # IMU = cropStructFields(IMU,nonNaN);
    # GPS = cropStructFields(GPS,nonNaN);

    # end

    # %% Subfunctions
    # function x = interp1NaN(x)
    #     nanx = isnan(x);
    #     t    = 1:numel(x);
    #     x(nanx) = interp1(t(~nanx), x(~nanx), t(nanx));
    # end

    # function S = cropStructFields(S,cropIdx)
    #     fields = fieldnames(S);
    #     for f = 1:length(fields)
    #         if length(S.(fields{f})) == length(cropIdx)
    #             S.(fields{f}) = S.(fields{f})(cropIdx,:);
    #         end
    #     end
    # end


#%%