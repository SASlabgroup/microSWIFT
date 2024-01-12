from logging import *
import subprocess
import os
import time
import threading
from datetime import datetime, timedelta
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

#Define Config file name and load file
from utils.config3 import Config
configFilename = r'/home/pi/microSWIFT/utils/Config.dat'
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
    print("Error loading config file")
    sys.exit(1)

# Set up module level logger
logger = getLogger('microSWIFT.'+__name__)  
logger.info('---------------recordHTH.py------------------')

#Config parameters 
dataDir = config.getString('System', 'dataDir')
floatID = os.uname()[1]

def recordHTH(current_end):
    
    # INA is not Initialzied at first
    hth_initialized = False
    
    logger.info('got those times : ' )
    logger.info( str(datetime.utcnow()) )
    logger.info('got those times : ' )
    logger.info( str(current_end) )

    # Loop if the imu did not initialize and it is still within a recording block
    # while datetime.utcnow().minute + datetime.utcnow().second/60 <= end_time and hth_initialized==False:
    while True:
    
        logger.info('entered Health recording')
        
        i2c_bus = board.I2C()  # uses board.SCL and board.SDA
        # i2c_bus = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        
        ina219 = INA219(i2c_bus)
        
        # optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
        ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        # optional : change voltage range to 16V
        ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

        hth_initialized=True
        logger.info('initialed INA current sensor')
        
        HTHdataFilename = dataDir + floatID + '_HTH_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(datetime.utcnow())
        logger.info("file name: {}".format(HTHdataFilename))
        
        with open(HTHdataFilename, 'w',newline='\n') as hth_out:
            
            utl=0
            ntl=0
            stl=0
            itl=0
            
            while datetime.utcnow() + timedelta(minutes=1) <= current_end:
                
                # remember time now to sleep for 60 seconds - runtime
                now=time.time()
                health=str(now)+","

                # get memory information
                file1 = open('/proc/meminfo', 'r')
                
                found_ma=False
                found_sf=False
                count = 0
                while True:
                    
                    count += 1
                    # Get next line from file
                    line = file1.readline()
                    
                    # if line is empty
                    # end of file is reached
                    if not line:
                        break
                    if line.startswith("MemAvailable"):
                        # print(line[13:25])
                        availablemem=int(line[13:25])
                        found_ma=True
                    if line.startswith("SwapFree"):
                        # print(line[13:25])
                        freeswap=int(line[13:25])
                        found_sf=True
                
                    #    print("Line{}: {}".format(count, line.strip()))
                    if found_ma and found_sf:
                        break
                
                health+="memavail=%d,swapfree=%d,"% (availablemem, freeswap)
                file1.close()
                
                file2 = open("/proc/stat", "r")
                sline = file2.readline().split()
                # print(sline)
                file2.close
                
                ut = int(sline[1]) - utl
                nt = int(sline[2]) - ntl
                st = int(sline[3]) - stl
                it = int(sline[4]) - itl

                utl = ut
                ntl = nt
                stl = st
                itl = it
                
                health+="usertm=%d,nicetm=%d,systm=%d,idletm=%d," %(ut, nt, st, it)
                
                # print("add voltages from ino sensor")
                
                # some more raspberry pi info:
                # temperature, and further info like :
                #  vcgencmd measure_temp | head -1
                #  vcgencmd get_throttled | head -1
                #  vcgencmd measure_volts | head -1
                #  vcgencmd get_mem arm | head -1
                #  vcgencmd get_mem gpu | head -1
                #  vcgencmd mem_oom | head -1
                #  temp=35.8'C
                #  throttled=0x0
                #  volt=1.3500V
                #  arm=448M
                #  gpu=64M
                #  oom events: 0
                # print("would be calling shell script now")
                
                for info in ['measure_temp', 'get_throttled', 'measure_volts', 'get_mem arm', 'get_mem gpu']:
                    health+=subprocess.getoutput("vcgencmd " + info)
                    health+=","
                
                health+=subprocess.getoutput("vcgencmd mem_oom | head -1 | tr ':' '=' | tr -d ' '")
                health+=","
                
                # measure and display loop
                # while True:
                bus_voltage = ina219.bus_voltage  # voltage on V- (load side)
                shunt_voltage = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
                current = ina219.current  # current in mA
                power = ina219.power  # power in watts
                
                # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
                # print("Voltage (VIN+) : {:6.3f}   V".format(bus_voltage + shunt_voltage))
                # print("Voltage (VIN-) : {:6.3f}   V".format(bus_voltage))
                # print("Shunt Voltage  : {:8.5f} V".format(shunt_voltage))
                # print("Shunt Current  : {:7.4f}  A".format(current / 1000))
                # print("Power Calc.    : {:8.5f} W".format(bus_voltage * (current / 1000)))
                # print("Power Register : {:6.3f}   W".format(power))
                # print("", flush=True)
                health+="Vin=%f," % bus_voltage
                health+="Ish=%f," % current
                health+="pwr=%f" % power
                # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
                if ina219.overflow:
                    logger.info("Internal Math Overflow Detected!")
                
                health+="\n"
                hth_out.write(health)
                hth_out.flush()
                
                # remember last value for some infrequent transmissions to shore
                #  don't update during transmission (locked in this case)
                #  os.replace makes it an atomic operation
                with open("/dev/shm/HTH2", "w") as file:
                    file.write("0,0,"+health)
                os.replace("/dev/shm/HTH2", "/dev/shm/HTH")
                
                time.sleep(60+now-time.time())
                
        # Return HTHdataFilename to main microSWIFT.py
        return HTHdataFilename, hth_initialized
