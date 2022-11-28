""" 
Catch-all for general utilities.
"""

import numpy as np


def fill_bad_values(badVal=999, spectralLen=42):
    """
    Utility to fill wave parameters with bad values.

    Input:
        - badVal, the bad value to use (default = 999)
        - spectralLen, length of spectral parameters (default = 42)

    Output:
        - u,    (1x1)  = badVal
        - v,    (1x1)
        - z,    (1x1)
        - lat,  (1x1)
        - lon,  (1x1)
        - Hs,   (1x1)
        - Tp,   (1x1)
        - Dp,   (1x1)
        - E,    (spectralLen x 1) = badVal*ones(spectralLen)
        - f,    (spectralLen x 1)
        - a1,   (spectralLen x 1)
        - b1,   (spectralLen x 1)
        - a2,   (spectralLen x 1)
        - b2,   (spectralLen x 1)
        - check,(spectralLen x 1)

    Example:
        u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(badVal=999,spectralLen=42)
    """

    u     = badVal
    v     = badVal
    z     = badVal
    lat   = [badVal]
    lon   = [badVal]
    Hs    = badVal
    Tp    = badVal
    Dp    = badVal
    E     = badVal * np.ones(spectralLen)
    f     = badVal * np.ones(spectralLen)
    a1    = badVal * np.ones(spectralLen)
    b1    = badVal * np.ones(spectralLen)
    a2    = badVal * np.ones(spectralLen) 
    b2    = badVal * np.ones(spectralLen)
    check = badVal * np.ones(spectralLen)

    return u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check

def get_uvzmean(badValue, pts):
    """TODO:"""
    mean = badValue #set values to 999 initially and fill if valid value
    index = np.where(pts != badValue)[0] #get index of non bad values
    pts=pts[index] #take subset of data without bad values in it

    if(len(index) > 0):
        mean = np.mean(pts)

    return mean

def get_last(badValue, pts):
    """TODO:"""
    for i in range(1, len(pts)): #loop over entire lat/lon array
        if pts[-i] != badValue: #count back from last point looking for a real position
            return pts[-i]
        
    return badValue #returns badValue if no real position exists