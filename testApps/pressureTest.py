#! /usr/bin/python2.7

#Read and record temp from sensors
# Partial code by Author: Tony DiCola
#--------------------------------------------------------------
#standard imports
import time,spidev,sys,socket, os
from datetime import datetime
import numpy as np

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

#---------------------------------------------------------------

# Software SPI configuration:
CLK  = 11
MISO = 9
MOSI = 10
CS   = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)

#-------------------------------------------------------------------
#Loop Begins
#-------------------------------------------------------------------
def main():
    
    while True:
                
        data = mcp.read_adc(1)
        print(("Data: %f" % data))
        
        volts = (data * 5)/float(1023) 
        volts = round(volts,4)
        
        print(("volts", volts))
        
        psi = 50.0 * volts - 25.0
        print(("Psi", psi))
        water = 1/1.4233
        p = 14.7
        depth = ((psi-p)*water)
        print(("depth" , depth))
        time.sleep(0.5)
        
    
#run main function unless importing as a module
if __name__ == "__main__":
    main()
