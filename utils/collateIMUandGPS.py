"""
Author: @jacobrdavis

A collection of functions that collate the IMU and GPS records in preparation for final processing.

Contents:
    - crop_dict(d,cropBool) 
    - datetimearray2relativetime(datetimeArr,t0)
    - collateIMUandGPS(IMU,GPS) [main]

TODO:
    - remove reassignment of the same variable?

"""
#--Import Statements
import numpy as np
from logging import getLogger
from datetime import datetime, timedelta

#--helper functions: 

def crop_dict(d,cropBool):
    """
    Helper function to crop each key of dict based on a boolean array

    Input:
        - d, input dict
        - cropBool, boolean array

    Output:
        - d, cropped dict
    """
    # loop over the keys of the input dictonary
    for key in d.keys():
        d[key] = d[key][cropBool] # crop the values and re-assign to the original dictionary
    return d

def datetimearray2relativetime(datetimeArr,t0):
    """
    Helper function to convert datetime array to relative time in seconds
    
    Inputs:
        - datetimeArr, array of datetimes
        - t0, initial (or reference) time 

    Outputs:
        relTime - list of floats describing time (in sec) relative to t0
    """
    relTime = [timestep.total_seconds() for timestep in (np.asarray(datetimeArr)-t0)]
    return relTime   

def collateIMUandGPS(IMU,GPS):
    """
    Main function to collate IMU and GPS records. The IMU fields are cropped to lie within the available 
    GPS record and then the GPS is interpolated up to the IMU rate using the IMU as the master time.

    Inputs:
        - IMU, input dictionary containing acc ['ai'], vel ['vi'], pos ['pi'], and time ['time'] as entries.
        - GPS, input dictionary containing GPS records as entries
        
    Outputs:
        - IMU, output dictionary containing collated IMU fields
        - GPS, output dictionary containing collated GPS fields
    """
    #-- Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 
    logger.info('---------------collateIMUandGPS.py------------------')

    #-- crop IMU values to lie within the GPS times (since GPS is being interpolated onto IMU time)
    logger.info('Cropping IMU')
    startCrop = GPS['time'][0]
    endCrop   = GPS['time'][-1]
    cropIMUbool = np.logical_and(IMU['time'] >= startCrop, IMU['time'] <= endCrop)
    IMUcrop = crop_dict(IMU,cropIMUbool)

    #-- convert datetimes to relative times for interpolation
    relTimeGPS = datetimearray2relativetime(GPS['time'],t0=startCrop)
    relTimeIMU = datetimearray2relativetime(IMUcrop['time'],t0=startCrop)
    
    #-- interpolate the GPS values onto the IMU time
    logger.info('Interpolating GPS')
    GPSintp = dict()
    NaNbools = [] # initialize a list of to store logical array of NaN locations
    GPS['z'] = GPS['z'][:-1]
    GPSlens = [len(GPS[key]) for key in GPS.keys()-['time']]
    minLen = np.min(GPSlens)

    for key in GPS.keys()-['time']:
        GPSintp[key] = np.interp(relTimeIMU,relTimeGPS[:minLen],GPS[key][:minLen]) # interpolate GPS onto IMU
        NaNbools.append(~np.isnan(GPSintp[key])) # record any NaNs as False

    GPSintp.update({'time':IMUcrop['time']}) # update new GPS dict with datetime 

    #-- Crop NaN values; if NaNs exist, they should be exterior
    nonNaN = np.logical_and.reduce(np.asarray(NaNbools)) # intersect all NaN locations
    numNaNs = len(nonNaN) - sum(nonNaN)
    logger.info(f'{numNaNs} NaNs detected')
    if numNaNs>0:
        IMUcrop   = crop_dict(IMU,nonNaN)
        GPSintp = crop_dict(GPSintp,nonNaN)
        logger.info(f'{numNaNs} NaNs removed')

    logger.info('----------------------------------------------------')

    return IMU,GPSintp
    