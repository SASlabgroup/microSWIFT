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
from IMU.readIMU import readIMU

#%%
# from waves.cumtrapz import cumtrapz
# TODO: organize test files! and make this a proper test function...
dataDir  = './waves/testdata/test_stand/round7/'
IMUdataFilename = 'microSWIFT022_IMU_24Jun2021_200000UTC.dat'
fs = 12 #TODO: fix from input or timestamp diff; does NOT work for 48Hz

#%%
import os

# mag0 = np.empty((3,1))

directory = os.fsencode(dataDir)
    
for i, file in enumerate(os.listdir(directory)):
    filename = os.fsdecode(file)
    if filename.endswith(".dat"): 
        _, _, mag_i, _ = readIMU(f'{dataDir}{filename}')
        mag_i = np.asarray(mag_i).transpose()

        print(np.sum(mag_i))

        if np.sum(mag_i) != 0:
            if i == 0:
                mag = mag_i
            else:
                mag = np.concatenate((mag, mag_i), axis = 1)
            continue
    else:
        continue


#%%
magCal, Ainv, b = calibrateMag(mag)

#%%
IMU = IMUtoXYZ(f'{dataDir}{IMUdataFilename}',fs)

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
