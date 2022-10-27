
import serial, io
import numpy as np
import time
import logging
import struct
logging.basicConfig()
import sys
float_data_dir = '/home/pi/Data/'

def GetMeanTemp(datewant):
    meanTemp = bad
    fnameMean = ('microswift_' + float_id_short +
                '_' + project_name +'_TempMean_New.dat')
    fnameMean_dir = os.path.join(float_data_dir)
    fnameMeanFile = os.path.join(fnameMean_dir,fnameMean)
    if (os.path.exists(trajectory_filename)):
        fid = fopen(fnameMeanfile,'r')
        templine = fid.readline()
        tempdata = templine.split(',')
        print tempdata
        tempdate = datetime.datetime(year=tempdata[0], month=tempdata[1],
                   day=tempdata[2], hour = tempdata[3],min=tempdata[4],
                  sec=tempdata[5])
        delTime = tempdate - datewant
        print delTime

        meanTemp = tempdata[6]
        
    return MeanTemp
def main():
    systime = time.gmtime()
    meanTemp = GetMeanTemp(systime)
    print 'mean temp',meanTemp
