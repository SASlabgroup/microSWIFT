#! /usr/bin/python2
# Reads temperaure sensor. Writes date and temperature to file.
# Writes date and mean temperature to file

import serial, io
import time
from time import sleep
import numpy as np
import tsys01
import sys
import os
from datetime import datetime
from config2 import Config

##########################################################################
#Load config file 
configDat =  sys.argv[1]
configFilename = configDat #Load config file/parameters needed
config = Config() # Create object and load file
ok = config.loadFile( configFilename )
if( not ok ):
	sys.exit(0)

tempFreq=config.getInt('Temp', 'tempFreq')
#tempNumSamples = tempFreq*512
tempNumSamples = 10

print (tempNumSamples)
burstInterval = config.getInt('Iridium', 'burstInt')
burstNum = config.getInt('Iridium', 'burstNum')
dataDir = config.getString('LogLocation', 'dataDir')
floatID = config.getString('System', 'floatID')
bad = config.getInt('System', 'badValue')
projectName = config.getString('System', 'projectName')

sensor = tsys01.TSYS01()

def main():

    temp = np.empty(tempNumSamples)
    if not sensor.init():
        print("Error initializing temperature sensor")
        exit(1)

    while True:
        now = datetime.now()
    
        # at burst time interval
        if now.minute % burstInterval == 0 and now.second == 0:
            dname = now.strftime('%d%b%Y')
            tname = now.strftime('%H:%M:%S')
            fname = (dataDir + floatID +
                    '_Temp_' + dname + '_' + tname +'UTC_burst_' +
                     str(burstInterval) + '.dat')
            fname_dir = os.path.join(dataDir)

            fid=open(fname,'w')
            print('filename = ',fname)
            for isample in range(tempNumSamples):
                systime = time.gmtime()
                if not sensor.read():
                    print("Error reading sensor")
                    exit(1)
                temp[isample] = sensor.temperature()
                print('temp',temp[isample],isample, tempNumSamples)
                timestring = (str(now.year) + ',' + str(now.month) + ',' + str(now.day) +
                              ',' + str(now.hour) + ',' + str(now.minute) + ',' + str(now.second))
                print('TIME ',timestring,dname,tname)
                fid.write('%s,%15.10f\n' %(timestring,temp[isample]))
                fid.flush()

            fid.close()

            idgood = np.where(temp != bad)[0]
            if(len(idgood) > 0):
                mean_temperature = np.mean(temp[idgood])
            else:
                mean_temperature = bad
            print('mean temp ',mean_temperature)
            fnameMean = ('microswift_' + floatID +
                '_' + projectName +'_TempMean.dat')
            fnameMeanNew = ('microswift_' + floatID +
                '_' + projectName +'_TempMean_New.dat')
            fnameMean_dir = os.path.join(dataDir)
            fnameMeanFile = os.path.join(fnameMean_dir,fnameMean)
            fnameMeanNewFile = os.path.join(fnameMean_dir,fnameMeanNew)
            if not (os.path.exists(fnameMeanFile)):
                fid = open(fnameMeanFile,'w')
            else:
                fid = open(fnameMeanFile,'a')
            fidNew = open(fnameMeanNewFile,'w')
            print fnameMean
            fid.write('%s,%15.10f\n'%(timestring,mean_temperature))
            fidNew.write('%s,%15.10f\n'%(timestring,mean_temperature))
            fidNew.flush()
            fidNew.close()

#run main function unless importing as a module
if __name__ == "__main__":
    main()