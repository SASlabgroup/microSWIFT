#generate simulated payload telemetry for microSWIFT

import numpy as np
from random import random

payload_type=7
sensor_type=50
port=1
size=1245

u=np.empty(2048)
v=np.empty(2048)
z=np.empty(2048)

for i in range (0, 2048):
    u[i]=randint(0,20)
    v[i]=randint(0,20)
    z[i]=randint(0,20)

lat= 47.377169
lon= 121.69546

Hs=10 
Tp=20
Dp=270

temp= 21.5
volt= 6.0

uMean=np.mean(u)
vMean=np.mean(v)
zMean=np.mean(z)


uMean = round(uMean,6)
vMean = round(vMean,6)
zMean = round(zMean,6)
lat = round(lat,6)
lon = round(lon,6)
Hs = round(Hs,6)
Tp = round(Tp,6)
Dp = round(Dp,6)


payload_data = (struct.pack('<sbbhfff', str(payload_type).encode(),sensor_type,port, payload_size,Hs,Tp,Dp) + 
                        struct.pack('<42f', *E) +
                        struct.pack('<42f', *f) +
                        struct.pack('<42f', *a1) +
                        struct.pack('<42f', *b1) +
                        struct.pack('<42f', *a2) +
                        struct.pack('<42f', *b2) +
                        struct.pack('<42f', *checkdata) +
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