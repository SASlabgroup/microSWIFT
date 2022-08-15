from os import access
from termios import VEOL
from matplotlib import markers
import numpy as np
import matplotlib.pyplot as plt
from IMU.IMUtoXYZ import IMUtoXYZ
from GPS.GPStoUVZ import GPStoUVZ
from waves.UVZAwaves import UVZAwaves
from GPS.GPSwaves import GPSwaves
from datetime import datetime, timedelta
from waves.collateIMUandGPS import collateIMUandGPS
# from waves.cumtrapz import cumtrapz

dataDir  = './waves/testdata/'
IMUdataFilename = 'microSWIFT043_IMU_15Aug2022_210005UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
GPSdataFilename = 'microSWIFT043_GPS_15Aug2022_210006UTC.dat' #'microSWIFT043_GPS_05May2022_200007UTC.dat'#'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT014_GPS_27Oct2021_190009UTC.dat'
fs = 12 #TODO: fix from input or timestamp diff; does NOT work for 48Hz
#%%
#%%
GPS = GPStoUVZ(f'{dataDir}{GPSdataFilename}')
# u, v, z, lat, lon, GPStime = GPStoUVZ(f'{dataDir}{GPSdataFilename}')
#%%
IMU = IMUtoXYZ(f'{dataDir}{IMUdataFilename}',fs)
# ax, ay, az, vx, vy, vz, px, py, pz, IMUtime = IMUtoXYZ(f'{dataDir}{IMUdataFilename}',fs)
#TODO: be certain the right az is being returned...
#%%
fig, ax = plt.subplots(1,1)
ax.plot(IMU['time'],IMU['pz'],alpha=0.5)

fig, ax = plt.subplots(1,1)
ax.plot(IMU['time'],IMU['az'],alpha=0.5)

fig, ax = plt.subplots(1,1)
ax.plot(IMU['time'],IMU['px'],alpha=0.5)

fig, ax = plt.subplots(1,1)
ax.plot(IMU['time'],IMU['py'],alpha=0.5)

fig, ax = plt.subplots(1,1)
ax.plot(GPS['time'],GPS['u'],alpha=0.5)
# ax.set_xlim([datetime(2021,10,27,19,0,0),datetime(2021,10,27,19,12,30)])

#TODO: export and plot MATLAB az PSD
from scipy import signal
nperseg = 256*fs # [samples]
overlap = 0.75
fw,Ew = signal.welch(IMU['az'], fs= fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))
fig, ax = plt.subplots(1,1)
ax.plot(fw,Ew)
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlim([10**(-2),10**(0)])
ax.set_ylim([10**(-4),10**(2)])

#%%
IMUcol,GPScol = collateIMUandGPS(IMU,GPS) 
# ax, ay, az, vx, vy, vz, px, py, pz, IMUtime = IMUcol.values() #TODO: beware: unpacking can be unordered...
# u, v, z, lat, lon, GPStime = GPScol.values() # 

#%%
zeroPts = int(np.round(30*fs))

Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], fs) #TODO: check

Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], 4)
#TODO: error with length of freq vector...compare with GPSwaves

#TODO: plot dir coeff

#%% import CDIP
import xarray as xr
import pandas as pd
# url = 'https://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/192p1/192p1_historic.nc'
# url = './waves/testdata/192p1_rt.nc'
# url = './waves/testdata/036p1_rt.nc'
url = './waves/testdata/036p1_d46.nc'


ds = xr.open_dataset(url)

d_buoy = {
    'lat' : ds['waveEnergyDensity']['metaDeployLatitude'].values,
    'lon' : ds['waveEnergyDensity']['metaDeployLongitude'].values,
    'Datetime' : ds['waveTime'].values,
    'frequency' : len(ds['waveTime'].values)*[ds['waveFrequency'].values],
    'energyDensity' : [np.array(E) for E in ds['waveEnergyDensity'].values],
    'a1' : [np.array(E) for E in ds['waveA1Value'].values],
    'b1' : [np.array(E) for E in ds['waveB1Value'].values],
    'a2' : [np.array(E) for E in ds['waveA2Value'].values],
    'b2' : [np.array(E) for E in ds['waveB2Value'].values],            
    'significantHeight' : ds['waveHs'].values,
    'peakPeriod' : ds['waveTp'].values,
    'energyPeriod' : ds['waveTa'].values,
}

df_buoy = pd.DataFrame(d_buoy)
df_buoy = df_buoy.set_index('Datetime')

CDIP = df_buoy[df_buoy.index==datetime(2021,7,12,21,0,0)]

#%%
import pandas as pd
filename = './waves/testdata/RV_Carson_microSWIFT043_earth.csv'
MATLAB = pd.read_csv(filename)
#%%
# from scipy import signal
# nperseg = 256*fs # [samples]
# overlap = 0.75
# fw,Ew = signal.welch(IMUcol['pz'][zeroPts:], fs= fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))

fig, ax = plt.subplots(1,1)
ax.plot(f,E,label='UVZAwaves')
ax.plot(MATLAB.f,MATLAB.E)
# ax.plot(fw,Ew,label='Welch')
ax.plot(f_2,E_2,label='GPSwaves')
# ax.plot(CDIP['frequency'][0],CDIP['energyDensity'][0],'k',label='CDIP')
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlim([10**(-2),10**(0)])
ax.set_ylim([10**(-4),10**(2)])
ax.legend()
# fig.savefig('UVZA_Westport_12Jul2021_scalar.png',dpi=400)

fig, ax = plt.subplots(4,1)
ax[0].plot(f,a1)
ax[0].plot(f_2,a1_2)
# ax[0].plot(CDIP['frequency'][0],CDIP['a1'][0],'k')
ax[0].set_xlim([10**(-2),0.5*10**(0)])
ax[0].set_ylim([-1 ,1])

ax[1].plot(f,b1)
ax[1].plot(f_2,b1_2)
# ax[1].plot(CDIP['frequency'][0],CDIP['b1'][0],'k')
ax[1].set_xlim([10**(-2),0.5*10**(0)])
ax[1].set_ylim([-1 ,1])

ax[2].plot(f,a2)
ax[2].plot(f_2,a2_2)
# ax[2].plot(CDIP['frequency'][0],CDIP['a2'][0],'k')
ax[2].set_xlim([10**(-2),0.5*10**(0)])
ax[2].set_ylim([-1 ,1])

ax[3].plot(f,b2)
ax[3].plot(f_2,b2_2)
# ax[3].plot(CDIP['frequency'][0],CDIP['b2'][0],'k')
ax[3].set_xlim([10**(-2),0.5*10**(0)])
ax[3].set_ylim([-1 ,1])

# fig.savefig('UVZA_Westport_12Jul2021_moments.png',dpi=400)

#%%



