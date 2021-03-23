#--------------------------------------------------------------------------
#
# test_processIMUC.py
# reads in matlab data to use as input to processIMUC.c
#
#--------------------------------------------------------------------------
import sys
import os.path
import numpy as np
import array
import struct

import processIMU_lib


from scipy.io import loadmat

# read in Jim's test matlab file
IMUdata = loadmat('microSWIFT035_IMU_14Jan2021_220011UTC',squeeze_me=True)
#,struct_as_record=False)


# IMU = 

# struct with fields:

#    clock: {2048×1 cell}
#      acc: [2048×3 double]
#      mag: [2048×3 double]
#     gyro: [2048×3 double]
#   angles: [2048×3 double]

axs = IMUdata['IMU']['acc'].item()[:,0][:]
ays = IMUdata['IMU']['acc'].item()[:,1][:]
azs = IMUdata['IMU']['acc'].item()[:,2][:]
gxs = IMUdata['IMU']['gyro'].item()[:,0][:]
gys = IMUdata['IMU']['gyro'].item()[:,1][:]
gzs = IMUdata['IMU']['gyro'].item()[:,2][:]
mxs = IMUdata['IMU']['mag'].item()[:,0][:]
mys = IMUdata['IMU']['mag'].item()[:,1][:]
mzs = IMUdata['IMU']['mag'].item()[:,2][:]

mxo = np.double(60.) 
myo = np.double(60.) 
mzo = np.double(120.)  
Wd = np.double(0.) 
fs = np.double(4.) 

nv=np.size(axs)

print('IMU inputs:')
print(nv, axs, ays, azs, gxs, gys, gzs,mxs, mys, mzs, mxo, myo, mzo, Wd, fs)

# call processIMU
IMU_results = processIMU_lib.main_processIMU(nv, axs, ays, azs, gxs, gys, gzs, 
                                                 mxs, mys, mzs, mxo, myo, mzo, Wd, fs)
SigwaveHeight = IMU_results[0]
Peakwave_Period = IMU_results[1]
Peakwave_dirT = IMU_results[2]
WaveSpectra_Energy = np.squeeze(IMU_results[3])
WaveSpectra_Freq   = np.squeeze(IMU_results[4])
WaveSpectra_a1 = np.squeeze(IMU_results[5])
WaveSpectra_b1 = np.squeeze(IMU_results[6])
WaveSpectra_a2 = np.squeeze(IMU_results[7])
WaveSpectra_b2 = np.squeeze(IMU_results[8])
checkdata = WaveSpectra_a1*0+1
print('IMU results:')
print('sigwaveHeight=',SigwaveHeight,'peakwave_period=',Peakwave_Period,'peawave_dirT=',Peakwave_dirT)
print('energy',WaveSpectra_Energy)
print('freq',WaveSpectra_Freq)
print('a1',WaveSpectra_a1)
print('b1',WaveSpectra_b1)
print('a2',WaveSpectra_a2)
print('b2',WaveSpectra_b2)
print('checkdata',checkdata)
