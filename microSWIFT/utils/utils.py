"""
Catch-all for general utilities.
"""

import numpy as np


def fill_bad_values(config):
    """
    Utility to fill wave parameters with bad values.

    Input:
        - config, configuration file

    Output:
        - Hs,   (1x1) = BAD_VALUE
        - Tp,   (1x1)
        - Dp,   (1x1)
        - E,    (NUM_COEFF x 1) = BAD_VALUE*ones(NUM_COEFF)
        - f,    (NUM_COEFF x 1)
        - a1,   (NUM_COEFF x 1)
        - b1,   (NUM_COEFF x 1)
        - a2,   (NUM_COEFF x 1)
        - b2,   (NUM_COEFF x 1)
        - check,(NUM_COEFF x 1)

    Example:
        u,v,z,lat,lon,Hs,Tp,Dp,E,f,a1,b1,a2,b2,check = fillBadValues(BAD_VALUE=999, NUM_COEFF=42)
    """
    Hs    = config.BAD_VALUE
    Tp    = config.BAD_VALUE
    Dp    = config.BAD_VALUE
    E     = config.BAD_VALUE * np.ones(config.NUM_COEFF)
    f     = config.BAD_VALUE * np.ones(config.NUM_COEFF)
    a1    = config.BAD_VALUE * np.ones(config.NUM_COEFF)
    b1    = config.BAD_VALUE * np.ones(config.NUM_COEFF)
    a2    = config.BAD_VALUE * np.ones(config.NUM_COEFF)
    b2    = config.BAD_VALUE * np.ones(config.NUM_COEFF)
    check = config.BAD_VALUE * np.ones(config.NUM_COEFF)

    wave_vars = {
        'Hs' : Hs,
        'Tp' : Tp,
        'Dp' : Dp,
        'E' : E,
        'f' : f,
        'a1' : a1,
        'b1' : b1,
        'a2' : a2,
        'b2' : b2,
        'check' : check,
    }
    return wave_vars

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