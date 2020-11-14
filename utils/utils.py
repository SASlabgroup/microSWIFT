import datetime
from datetime import datetime
import time

# Names files created with current date and time and return it
def currentTimeString():    
    # Name the file according to the current time and date  
    dataFile = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
    return dataFile

def ConvertVolts(data):
    volts = (data * 3.3)/float(1023)
    volts = round(volts,4)
    return volts
def ConvertTemp(data):
    temp = ((data * 330)/float(1023))-50
    temp = round(temp,4)
    return temp
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data