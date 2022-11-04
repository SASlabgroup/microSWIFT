#!/usr/bin/python3

#This script opens a serial connection with a RockBlock 9602 SBD modem and
#transmits ASCII data that is passed to the main function

from gpiozero import OutputDevice
import serial
import sys
from time import sleep
import logging
logging.basicConfig()
import zlib
import struct
import numpy as np

addr =  '/dev/ttyUSB1'
baud = 19200

#initialize gpio pin 21 as modem on/off control
modem = OutputDevice(21)

#turn modem on using GPIO pins
#logger = logging.getLogger('send_sbd_data')
print('initializing SBD modem')
modem.on()
#create serial object and open port
sbd = serial.Serial(addr, baud, timeout=1)

#turn modem on using GPIO pins
logger = logging.getLogger('send_sbd_msg')
sbd.reset_input_buffer()  #renamed since version 3.0
sbd.reset_output_buffer()

#issue AT command and check for OK response
sleep(2)
sbd.write('AT\r'.encode())
status = sbd.readlines()
print(status)

for i in range(20):
    #get signal strength
    sbd.write('AT+CSQ\r'.encode())
    signal_strength = sbd.readlines()
    print(signal_strength)
    #get signal strength
    sleep(2)

#put modem to sleep
sleep(2)
logger.info("powering down SBD modem")
modem.off()

