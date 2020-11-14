import RPi.GPIO as GPIO
import time
import serial

'''GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.OUT)

#GPIO.output(21,HIGH)
#time.sleep(5)
GPIO.output(21,GPIO.LOW)'''


sbd = serial.Serial('/dev/ttyUSB0', 19200, timeout=1)
sbd.write('AT\r')
#time.sleep(5)
while True:
    reply = sbd.readlines()
    print(reply)
