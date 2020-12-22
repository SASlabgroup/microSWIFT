import serial,io
import pynmea2
from time import sleep



ser=serial.Serial('/dev/ttyS0',9600,timeout=1)
sio=io.TextIOWrapper(io.BufferedRWPair(ser,ser))


#test for incoming data over serial port
while True:
	ser.flushInput()
	newline=ser.readline()
	print(('newline= ' + newline))
	if 'GPGGA' in newline:
		print('found GPGGA sentence')
		msg=pynmea2.parse(newline,check=True)
		print(('GPS quality= ' + str(msg.gps_qual)))
		if msg.gps_qual > 0:
			print('GPS fix acquired')
			break
	sleep(1)

print('exit loop')
