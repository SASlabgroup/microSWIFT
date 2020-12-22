#!/usr/bin/python

# standard imports 
import numpy as np
import datetime 
import time 
from datetime import datetime 

#################################################################
# General purpose navigational and file naming utilities
#################################################################

#################################################################
# Trig functions with args in degrees
#################################################################
def sind(val):
    return np.sin(np.deg2rad(val))
def cosd(val):
    return np.cos(np.deg2rad(val))
#################################################################
# Inverse trig functions returning values in degrees
#################################################################
def asind(val):
    return np.rad2deg(np.arcsin(val))
def acosd(val):
    return np.rad2deg(np.arccos(val))
def atan2d(y,x):
    return np.rad2deg(np.arctan2(y,x))

#################################################################
# This function converts a Latitude,Longitude pair into
# a Cartesian 3-vector.
#
# Lat, Lon assumed to be provided in deg.dec
#################################################################
def latLon2Vec( lat, lon ):
    v1 = cosd(lat)*cosd(lon)
    v2 = cosd(lat)*sind(lon)
    v3 = sind(lat)
    v = np.array( [v1, v2, v3] )

    return v

#################################################################
# This function converts a Cartesian 3-vector into lat,lon
#
# Lat, Lon returned in deg.dec
#################################################################
def vec2LatLon( v ):

    lat = asind( v[2] )
    lon = atan2d( v[1], v[0] )

    return (lat,lon)
    
#################################################################
# This function converts a Latitude or Longitude from the form
#   'DDMM.ddd'
# To a single numeric float of the form:
#   deg.ddd
#
# NOTE: The former form is very common with GPS receivers
#
# Example 1:
# - Input = "4218.345"
#   (This is 42 deg, 18.345 minutes (positive))
# - Output = 42.30575
#   (This is 42.30575 deg)
#
# Example 2:
# - Input = "0218.345"
#   (This is 2 deg, 18.345 minutes (positive))
# - Output = 2.30575
#   (This is 2.30575 deg)
#
# Example 3:
# - Input = "-4218.345"
#   (This is 42 deg, 18.345 minutes (negative)
# - Output = -42.30575
#   (This is -42.30575 deg)

#################################################################
def latLonDegMin2Dec( string ):
    
    lat = (float(string.split(",")[3].strip()))
    # Get input string as a float
    total = (lat)
    # Determine sign
    hSign = np.sign(total)
    # Work on absolute value
    total = np.fabs(total)
    # Get deg,min part (sans decimal)
    ddmm = np.fix(total)
    # Get remainder
    dec = total - ddmm
    # Get deg part
    dd = np.fix(ddmm/100)
    # Get minute part
    mm = (ddmm-dd*100) + dec
    # Combine to deg.dec
    latdeg = (dd+mm/60)
    # Recover sign
    latdeg = latdeg*hSign

    lon = (float(string.split(",")[5].strip()))
    # Get input string as a float
    lontotal = (lon)
    # Determine sign
    hSign = np.sign(lontotal)
    # Work on absolute value
    lontotal = np.fabs(lontotal)
    # Get deg,min part (sans decimal)
    ddmm = np.fix(lontotal)
    # Get remainder
    dec = lontotal - ddmm
    # Get deg part
    dd = np.fix(ddmm/100)
    # Get minute part
    mm = (ddmm-dd*100) + dec
    # Combine to deg.dec
    londeg = (dd+mm/60)
    # Recover sign
    londeg = londeg*hSign

    return (latdeg,londeg)

###############################################################
# This function names files created with current date and time 
###############################################################
def currentTimeString(): 	
    # Name the file according to the current time and date  
    dataFile = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
    print(dataFile)
    return dataFile

