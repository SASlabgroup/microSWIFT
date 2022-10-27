    #generate simulated payload telemetry for microSWIFT

import numpy as np
import random
import struct
from datetime import datetime


payload_type=7
sensor_type=50
port=1
payload_size=1245

u=np.empty(2048)
v=np.empty(2048)
z=np.empty(2048)

for i in range (0, 2048):
    u[i]=random.randint(0,20)
    v[i]=random.randint(0,20)
    z[i]=random.randint(0,20)

lat= 47.36
lon= 121.69

Hs=10 
Tp=20
Dp=270


    
#create arrays of arbitrary value for E, f, a1, b1, a2, b2 and c
E=np.empty(42,dtype=np.float32)
f=np.empty(42,dtype=np.float32)
a1=np.empty(42,dtype=np.float32)
b1=np.empty(42,dtype=np.float32)
a2=np.empty(42,dtype=np.float32)
b2=np.empty(42,dtype=np.float32)
c=np.full(42,1)

for i in range(0,41):
    E[i]=random.randint(0,1000000)/1000000
    f[i]=random.randint(0,1000000)/1000000
    a1[i]=random.randint(0,1000000)/1000000
    b1[i]=random.randint(0,1000000)/1000000
    a2[i]=random.randint(0,1000000)/1000000
    b2[i]=random.randint(0,1000000)/1000000

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

print(u,v,z)
print(lat,lon)
print(Hs,Tp,Dp)
print(E)
print(f)
print(a1);print(b1);print(a2);print(b2)
print(c)

with open(r'C:\Users\Alex de Klerk\Desktop\binfile.dat', 'wb') as file:
    now=datetime.now()
    payload_data = (struct.pack('<sbbhfff', str(payload_type).encode(),sensor_type,port, payload_size,Hs,Tp,Dp) + 
                    struct.pack('<42f', *E) +
                    struct.pack('<42f', *f) +
                    struct.pack('<42f', *a1) +
                    struct.pack('<42f', *b1) +
                    struct.pack('<42f', *a2) +
                    struct.pack('<42f', *b2) +
                    struct.pack('<42f', *c) +
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
    
    file.write(payload_data)
    file.flush()


print(payload_data)






