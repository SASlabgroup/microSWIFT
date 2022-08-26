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

# read in the sensor type from the binary payload file
payloadStartIdx = payload_data.index(b':') 

print(payloadStartIdx)