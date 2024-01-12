import serial
import time

# specify timeout in case of blocking readline()
com = serial.Serial('/dev/ttyUSB0', baudrate=57600, timeout=3600)

# no activity for more than 1.5 sec
time.sleep(1.75)
com.write(b'+++')
# no activity for more than 1.5 sec
time.sleep(1.75)

com.write(b'ATS6?\n\r')
line = com.readline()
print(".", end="")
print (line, flush=True)
time.sleep(0.5)

com.write(b'ATS6=0\n\r')
line = com.readline()
print(".", end="")
print (line, flush=True)
time.sleep(0.5)

com.write(b'ATS6?\n\r')
line = com.readline()
print(".", end="")
print (line, flush=True)
time.sleep(0.5)

com.write(b'AT&T=RSSI\n\r')
line = com.readline()
print(".", end="")
print (line, flush=True)
time.sleep(0.5)

com.write(b'AT&T\n\r')
line = com.readline()
print(".", end="")
print (line, flush=True)
time.sleep(0.5)

com.write(b'ATO\n\r')
line = com.readline()
print(".", end="")
print (line, flush=True)


print ("Waiting for message")

while True:
    line = com.readline()
    print(".", end="")
    time.sleep(0.25)
    if not line.decode().startswith("L/R"):
        com.write(b'READY\r')
    print (line, flush=True)
    
com.close()

