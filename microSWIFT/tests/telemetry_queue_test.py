import concurrent.futures
import datetime
import pwd
import numpy as np
from datetime import datetime, timedelta
from logging import *
import sys, os
from time import sleep
import struct

TX_file = '/home/pi/microSWIFT/data/microSWIFT043_TX_26Aug2022_195204UTC.dat'

with open(TX_file, mode='rb') as file: # b is important -> binary
						payload_data = file.read()
					# logger.info(f'Opened TX')
print(payload_data)
# read in the sensor type from the binary payload file
payloadStartIdx = -1
sensor_type0 = ord(payload_data[payloadStartIdx+2:payloadStartIdx+3]) # sensor type is the 2 byte after the header
				
print(sensor_type0)