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
# from waves.cumtrapz import cumtrapz

dataDir  = './waves/testdata/'
IMUdataFilename = 'microSWIFT021_IMU_12Jul2021_210000UTC.dat' # 'microSWIFT057_IMU_17Aug2022_000146UTC.dat'  #'microSWIFT043_IMU_16Aug2022_002021UTC.dat'# 'microSWIFT043_IMU_15Aug2022_210005UTC.dat' #'microSWIFT043_IMU_05May2022_200006UTC.dat'#'microSWIFT021_IMU_12Jul2021_210000UTC.dat' #'microSWIFT014_IMU_27Oct2021_190006UTC.dat' 
GPSdataFilename = 'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT057_GPS_17Aug2022_000151UTC.dat' #'microSWIFT043_GPS_16Aug2022_002022UTC.dat'#'microSWIFT043_GPS_15Aug2022_210006UTC.dat' #'microSWIFT043_GPS_05May2022_200007UTC.dat'#'microSWIFT021_GPS_12Jul2021_210000UTC.dat' #'microSWIFT014_GPS_27Oct2021_190009UTC.dat'
testName = 'Westport 12Jul2021'
fs = 12 #TODO: fix from input or timestamp diff; does NOT work for 48Hz
#%% possible to use this to gen headers
# def funfun():
#     print(funfun.__name__)
#     return 

# funfun()
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
zeroPts = int(np.round(120*fs))

Hs, Tp, Dp, E, f, a1, b1, a2, b2, check = UVZAwaves(GPScol['u'][zeroPts:], GPScol['v'][zeroPts:], IMUcol['pz'][zeroPts:], IMUcol['az'][zeroPts:], fs) #TODO: check

Hs_2, Tp_2, Dp_2, E_2, f_2, a1_2, b1_2, a2_2, b2_2, check_2 = GPSwaves(GPS['u'], GPS['v'], GPS['z'], 4)
#TODO: error with length of freq vector...compare with GPSwaves

#TODO: plot dir coeff
#%% reducing TX size
import sys
import struct

# Telemetry test functions
def createTX(sensor_type, Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean, v_mean, z_mean, lat, lon,  temp, volt):
    payload_type = 7
    port = 1

    now=datetime.utcnow()
    nowEpoch = now.timestamp() # unpack with datetime.fromtimestamp(nowEpoch)  
    
    # Round the values each to 6 decimal places
    Hs = round(Hs,6)
    Tp = round(Tp,6)
    Dp = round(Dp,6)
    lat = round(lat,6)
    lon = round(lon,6)
    uMean = round(u_mean,6)
    vMean = round(v_mean,6)
    zMean = round(z_mean,6)
        
    # Log the data that will be sent    
    print('Hs: {0} Tp: {1} Dp: {2} lat: {3} lon: {4} temp: {5} volt: {6} uMean: {7} vMean: {8} zMean: {9}'.format(
        Hs, Tp, Dp, lat, lon, temp, volt, uMean, vMean, zMean))

    if sensor_type == 50:

        #create formatted struct with all payload data
        payload_size = struct.calcsize('<sbbhfff42f42f42f42f42f42f42ffffffffiiiiii')
        payload_data = (struct.pack('<sbbhfff', str(payload_type).encode(),sensor_type,port, payload_size,Hs,Tp,Dp) + 
                        struct.pack('<42f', *E) +
                        struct.pack('<42f', *f) +
                        struct.pack('<42f', *a1) +
                        struct.pack('<42f', *b1) +
                        struct.pack('<42f', *a2) +
                        struct.pack('<42f', *b2) +
                        struct.pack('<42f', *check) +
                        struct.pack('<f', lat) +
                        struct.pack('<f', lon) +
                        struct.pack('<f', temp) +
                        struct.pack('<f', volt) +
                        struct.pack('<f', uMean) +
                        struct.pack('<f', vMean) +
                        struct.pack('<f', zMean) +
                        struct.pack('<i', int(now.year)) +
                        struct.pack('<i', int(now.month)) +
                        struct.pack('<i', int(now.day)) +
                        struct.pack('<i', int(now.hour)) +
                        struct.pack('<i', int(now.minute)) +
                        struct.pack('<i', int(now.second)))

    if sensor_type == 52:

        fmin = np.min(f)
        fmax = np.max(f)
        fstep = (fmax - fmin)/(len(E)-1)
        salinity = 0.0

        #create formatted struct with all payload data
        payload_size = struct.calcsize('<sbbheee42eee42b42b42b42b42Bffeeef') 
        payload_data = (struct.pack('<sbbh', str(payload_type).encode(), sensor_type, port, payload_size) + 
                        struct.pack('<eee', Hs,Tp,Dp) +
                        struct.pack('<42e', *E) +
                        struct.pack('<e', fmin) +
                        struct.pack('<e', fmax) +
                        struct.pack('<42b', *a1) +
                        struct.pack('<42b', *b1) +
                        struct.pack('<42b', *a2) +
                        struct.pack('<42b', *b2) +
                        struct.pack('<42B', *check) +
                        struct.pack('<f', lat) +
                        struct.pack('<f', lon) +
                        struct.pack('<e', temp) + 
                        struct.pack('<e', salinity) +
                        struct.pack('<e', volt) +
                        struct.pack('<f', nowEpoch) # float saves 4 bytes but looses +/- 1s precision 
                        )

    return payload_data, payload_size

def send_microSWIFT_52(payload_data, timeout):
   
    #TODO: global id
    id = 99 # or 99; placeholder
    
    payload_size = len(payload_data)
    expected_payload_size = 327
    #check for data
    if payload_size != expected_payload_size:
        # logger.info('Error: unexpected number of bytes in payload data. Expected bytes: 249, bytes received: {}'.format(payload_size))
        successful_send = False
        return successful_send
    
    #split up payload data into packets    
    index = 0 #byte index
    packet_type = 0 #single packet
    
    #packet to send
    header = str(packet_type).encode('ascii') #packet type as as ascii number
    sub_header0 = str(','+str(id)+','+str(index)+','+str(payload_size)+':').encode('ascii') # ',<id>,<start-byte>,<total-bytes>:'
    payload_bytes0 = payload_data[index:expected_payload_size] #data bytes for packet
    print(f'len(index) {len(str(index))}')
    print(f'len(payload_size) {len(str(payload_size))}')
    print(f'len(header): {len(header)}')
    print(f'len(sub_header0): {len(sub_header0)}')
    print(f'len(payload_bytes0): {len(payload_bytes0)}')

    packet0 = header + sub_header0 + payload_bytes0 #TODO: <= 340 bytes
    
    print(f'len(packet0) {len(packet0)}')

    # while datetime.utcnow() < timeout: ...
    # ...
    #               issent  = transmit_bin(ser, packet0) 

    return packet0           
                   
#%% goal: convert a1,b1...+ check factor to integer ranges
a1_8bit = np.byte(np.round(100*a1)) # could be 127
b1_8bit = np.byte(np.round(100*b1))
a2_8bit = np.byte(np.round(100*a2))
b2_8bit = np.byte(np.round(100*b2))
# check_8bit = np.ubyte(np.round(10*check)) #TODO: try w/o enforcing ubyte
checkRoundedAndScaled = np.round(10*check)
checkRoundedAndScaled[checkRoundedAndScaled > 255] = 255
check_8bit = np.ubyte(checkRoundedAndScaled) 
    #TODO: pack as np.ubyte(np.round(10*check)) and decode as np.ubyte(np.round(10*check))/10  
    #TODO: be cautious of rollover for numbers > 255...
payload_data50, payload_size50 = createTX(50, Hs, Tp, Dp, E, f, a1, b1, a2, b2, check, u_mean=1.0, v_mean=1.0, z_mean=1.0, lat=47.65586, lon=-122.32106, temp=1.0, volt=0.0)
payload_data52, payload_size52 = createTX(52, Hs, Tp, Dp, E, f, a1_8bit, b1_8bit, a2_8bit, b2_8bit, check_8bit, u_mean=1.0, v_mean=1.0, z_mean=1.0, lat=47.65586, lon=-122.32106, temp=1.0, volt=0.0)

packet52 = send_microSWIFT_52(payload_data52,[])

#TODO: cut by 4 bytes!

with open(f'TX_sensortype52_test.dat', 'wb') as file:
    # Write the binary packed data to a file 
    file.write(packet52)
    file.flush()

# payload_data52, payload_size52 = createTX(52, Hs, Tp, Dp, E32, f, a1, b1, a2, b2, check, u_mean=1.0, v_mean=1.0, z_mean=1.0, lat=1.0, lon=1.0, temp=1.0, volt=1.0)
#%%
data50 = struct.unpack('<sbbhfff42f42f42f42f42f42f42ffffffffiiiiii', payload_data50)
data52 = struct.unpack('<sbbheee42eee42b42b42b42b42Bffeeef', payload_data52)
# data52 = struct.unpack('<sbbheee42e42e42e42e42e42e42eeeeeeeeiiiiii', payload_data52)
# data52log = struct.unpack('<sbbheee42e42e42e42e42e42e42eeeeeeeeiiiiii', payload_data52log)

payload_size_data52 = data52[3]
Hsig_data52 = data52[4]
Tp_data52 =data52[5]
Dp_data52 =data52[6]
E_data52 = data52[7:7+42]
fmin_data52 = data52[7+42]
fmax_data52 = data52[7+42+1]
fstep_data52 = (fmax_data52 - fmin_data52)/(len(E_data52)-1)
f_data52 = np.arange(fmin_data52,fmax_data52+fstep_data52,fstep_data52)
a1_data52 = np.asarray(data52[7+42+2+0*42:7+42+2+1*42])/100
b1_data52 = np.asarray(data52[7+42+2+1*42:7+42+2+2*42])/100
a2_data52 = np.asarray(data52[7+42+2+2*42:7+42+2+3*42])/100
b2_data52 = np.asarray(data52[7+42+2+3*42:7+42+2+4*42])/100
check_data52 = np.asarray(data52[7+42+2+4*42:7+42+2+5*42])/10
lat_data52 = data52[261]
lon_data52 = data52[262]
temp_data52 = data52[263]
salinity_data52 = data52[264]
volt_data52 = data52[265]
nowEpoch_data52 = data52[266]
datetime_data52 = datetime.fromtimestamp(nowEpoch_data52)  
print(datetime_data52)

Hsig_data50     = data50[4]
Tp_data50       = data50[5]
Dp_data50       = data50[6]
E_data50        = data50[7+0*42:7+1*42]
f_data50        = data50[7+1*42:7+2*42]
a1_data50       = data50[7+2*42:7+3*42]
b1_data50       = data50[7+3*42:7+4*42]
a2_data50       = data50[7+4*42:7+5*42]
b2_data50       = data50[7+5*42:7+6*42]
check_data50    = data50[7+6*42:7+7*42]
lat_data50      = data50[301]
lon_data50      = data50[302]
temp_data50     = data50[303]
volt_data50     = data50[304]
uMean_data50    = data50[305]
vMean_data50    = data50[306]
zMean_data50    = data50[307]
datetime_data50 = datetime(data50[308], data50[309], data50[310] ,data50[311], data50[312], data50[313])
print(datetime_data50)
#np.round(data52[4],4)
#%% comparison
fig, ax = plt.subplots(1,1)
ax.plot(f_data52,E_data52,'k-',alpha=1,label='e (16-bit float); sensor_type=52')
ax.plot(data50[49:49+42],data50[7:7+42],'r--',alpha=1,label='f (32-bit float) ; sensor_type=50')
ax.legend()
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_ylim([10**(-3),10**(1)])
ax.set_xlim([10**(-2), 10**(0)])
ax.set_title(f'microSWIFT021:\n'+
    f'  type50: ({np.round(lat_data50,5)},{np.round(lon_data50,5)}); Hsig = {np.round(Hsig_data50,2)}; Tp = {np.round(Tp_data50,3)};  Dp = {np.round(Dp_data50,3)}\n'+
    f'type52: ({np.round(lat_data52,5)},{np.round(lon_data52,5)}); Hsig = {np.round(Hsig_data52,2)}; Tp = {np.round(Tp_data52,3)};  Dp = {np.round(Dp_data52,3)}')
# fig.savefig('TX_16bitfloat_test_Westport_12Jul2021_scalar_py.png',dpi=400)
# fig.savefig('TX_16bitfloatscalar_and_8bitintdirmom_test_Westport_12Jul2021_scalar_py.png',bbox_inches='tight',dpi=400)

fig, ax = plt.subplots(5,1)
ax[0].plot(f_data52,a1_data52,'k-',alpha=1,label='b (8-bit int) or B (check) (8-bit uint); sensor_type=52')
ax[0].plot(data50[49:91],data50[91:133],'r--',alpha=1,label='f (32-bit float) ; sensor_type=50')
ax[0].set_xticks([])
ax[0].set_ylim([-1,1])
ax[0].set_ylabel('a1')
ax[0].legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
                mode="expand", borderaxespad=1, ncol=1)

ax[0].axhline(y=0, linestyle='-.', color='b', linewidth=0.5)

ax[1].plot(f_data52,b1_data52,'k-',alpha=1,label='b (8-bit int); sensor_type=52')
ax[1].plot(data50[49:91],data50[133:175],'r--',alpha=1,label='f (32-bit float) ; sensor_type=50')
ax[1].set_xticks([])
ax[1].set_ylim([-1,1])
ax[1].set_ylabel('b1')
ax[1].axhline(y=0, linestyle='-.', color='b', linewidth=0.5)

ax[2].plot(f_data52,a2_data52,'k-',alpha=1,label='b (8-bit int); sensor_type=52')
ax[2].plot(data50[49:91],data50[133+1*42:133+2*42],'r--',alpha=1,label='f (32-bit float) ; sensor_type=50')
ax[2].set_xticks([])
ax[2].set_ylim([-1,1])
ax[2].set_ylabel('a2')
ax[2].axhline(y=0, linestyle='-.', color='b', linewidth=0.5)

ax[3].plot(f_data52,b2_data52,'k-',alpha=1,label='b (8-bit int); sensor_type=52')
ax[3].plot(data50[49:91],data50[133+2*42:133+3*42],'r--',alpha=1,label='f (32-bit float) ; sensor_type=50')
ax[3].set_xlabel('frequency (Hz)')
ax[3].set_ylim([-1,1])
ax[3].set_ylabel('b2')
ax[3].axhline(y=0, linestyle='-.', color='b', linewidth=0.5)

ax[4].plot(f_data52,check_data52,'k-',alpha=1,label='B (8-bit uint); sensor_type=52')
ax[4].plot(data50[49:91],data50[133+3*42:133+4*42],'r--',alpha=1,label='f (32-bit float) ; sensor_type=50')
ax[4].set_xlabel('frequency (Hz)')
# ax[4].set_ylim([0,50])
ax[4].set_ylabel('check')
ax[4].axhline(y=25.5, linestyle='-.', color='b', linewidth=0.5)
# fig.savefig('TX_16bitfloatscalar_and_8bitintdirmom_test_Westport_12Jul2021_dirmom_py.png',bbox_inches='tight',dpi=400)


#%%
# print(f'E: {E}')

c = 30000                # scalar multiplier
E64 = c*E             # 64-bit float
E32 = np.float32(c*E) # cast as 32-bit float
E16 = np.float16(c*E) # cast as 16-bit float

# print a bunch of stuff for comparison:
print(f'max(E64): {max(E64)}') # max 
print(f'max(E32): {max(E32)}') # min
print(f'max(E16): {max(E16)}')
print(f'min(E64): {min(E64)}')
print(f'min(E32): {min(E32)}')
print(f'min(E16): {min(E16)}')
print(f'size of E16: {sys.getsizeof(E16)} bits') #size in bits
print(f'size of E32: {sys.getsizeof(E32)} bits')
print(f'size of E64: {sys.getsizeof(E64)} bits')

# plot
fig, ax = plt.subplots(1,1)
ax.plot(f,E64,'k--',label='64-bit')
ax.plot(f,E32,'b-.',label='32-bit')
ax.plot(f,E16,'r:' ,label='16-bit')
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlim([0.05,1])
ax.set_title(f'c={c}')
ax.legend()
# fig.savefig(f'float_test_c={c}.png', dpi=200)


#%% telemetry queue update for multi-sensor type
import struct
TX_file52 = 'TX_sensortype52_test.dat'
with open(TX_file52, mode='rb') as file: # b is important -> binary
	payload_data = file.read()

# with open(TX_file, "rb") as binfile:
#         payload_data2 = bytearray(binfile.read())

payloadStart = payload_data.index(b':')
sensorType = ord(payload_data[payloadStart+2:payloadStart+3]) # read from start of header

sensorType = ord(payload_data[-326:-325]) # read from end

payload_data0 = payload_data[payloadStart:]
payloadStart = 0
sensorType = ord(payload_data[payloadStart+2:payloadStart+3]) # read from start of header

sensorType not in [50,51,52]
# %%
