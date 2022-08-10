"""
Author: @jacobrdavis

A collection of functions that collate the IMU and GPS records in preparation for final processing.

TODO:
    - remove reassignment of the same variable?

"""
#--Import Statements
import numpy as np
from logging import getLogger
from datetime import datetime, timedelta

#--helper functions: #TODO: create more clear function descriptions

def crop_dict(d,cropBool):
    """
    Helper function to crop each key of dict based on a boolean array
    Input:
        - d, description...
        - cropBool, description...
    Output:
        - relTime, description...
    """
    # loop over the keys of the input dictonary
    for key in d.keys():
        d[key] = d[key][cropBool] # crop the values and re-assign to the original dictionary
    return d

def datetimearray2relativetime(datetimeArr,t0):
    """
    Helper function to convert datetime array to relative time in seconds
    Inputs:
        datetimeArr - 
        t0 - 
    Outputs:
        relTime - 
    """
    relTime = [timestep.total_seconds() for timestep in (np.asarray(datetimeArr)-t0)]
    return relTime   

def collateIMUandGPS(IMU,GPS):
    """
    Main function to collate IMU and GPS records. The IMU fields are cropped to lie within the available 
    GPS record and then the GPS is interpolated up to the IMU rate using the IMU as the master time.

    Inputs:
        - IMU, description...
        - GPS, description...
        
    Outputs:
        - IMU, description...
        - GPS, description...
    """
    #-- Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 

    #-- crop IMU values to lie within the GPS times (since GPS is being interpolated onto IMU time)
    startCrop = GPS['time'][0]
    endCrop   = GPS['time'][-1]
    cropIMUbool = np.logical_and(IMU['time'] >= startCrop, IMU['time'] <= endCrop)
    IMUcrop = crop_dict(IMU,cropIMUbool)

    logger.info('IMU cropped')
    
    #-- convert datetimes to relative times for interpolation
    relTimeGPS = datetimearray2relativetime(GPS['time'],t0=startCrop)
    relTimeIMU = datetimearray2relativetime(IMUcrop['time'],t0=startCrop)
    
    logger.info('datetimearray conversion complete')

    #-- interpolate the GPS values onto the IMU time
    GPSintp = dict()
    NaNbools = [] # initialize a list of to store logical array of NaN locations
    for key in GPS.keys()-['time']:
        print(len(relTimeIMU))
        print(len(relTimeGPS))
        print(len(GPS[key]))
        if len(GPS[key]) < len(relTimeGPS):
            relTimeGPS = np.delete(relTimeGPS,-1)
        GPSintp[key] = np.interp(relTimeIMU,relTimeGPS,GPS[key]) # interpolate GPS onto IMU
        NaNbools.append(~np.isnan(GPSintp[key])) # record any NaNs as False

    GPSintp.update({'time':IMUcrop['time']}) # update new GPS dict with datetime 

    logger.info('GPS interpolated')

    #TODO: indicate successful interpolation and log length?

    #-- Crop NaN values; if NaNs exist, they should be exterior
    nonNaN = np.logical_and.reduce(np.asarray(NaNbools)) # intersect all NaN locations
    numNaNs = len(nonNaN) - sum(nonNaN)
    logger.info(f'{numNaNs} detected')
    if numNaNs>0:
        IMUcrop   = crop_dict(IMU,nonNaN)
        GPSintp = crop_dict(GPSintp,nonNaN)
        logger.info(f'{numNaNs} NaNs removed')


    return IMU,GPSintp
    