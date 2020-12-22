import serial
import sys
baud=115200
gpsPort="/dev/ttyS0"


try:
	#open serial port with expected baud rate 115200
	ser = serial.Serial(gpsPort,baud,timeout=1)
	print(("GPS serial port open at %s baud" % (baud, gpsPort)))
	#set interval to 250ms (4 Hz)
	ser.write('$PMTK220,250*29\r\n'.encode())
	print("setting GPS to 4 Hz rate")
except:
	print("unable to open GPS serial port, trying default baud rate 9600")
	try:
		#try default baud rate 9600
		ser = serial.Serial(gpsPort,9600,timeout=1)
		#set baud rate to 115200 and interval to 250ms (4 Hz)
		print("setting baud rate to 115200")
		ser.write('$PMTK251,115200*1F\r\n'.encode())
		print("setting GPS to 4 Hz rate")
		ser.write('$PMTK220,250*29\r\n'.encode())
	except:
		print("unable to open GPS serial port on 9600")
else:
	print(("unable to open GPS serial port at %s and 9600 on port %s" % (baud, gpsPort)))
	sys.exit(0)
	

