def fillBadValues(badVal=999,spectralLen=42):
    """
    Author: @jacobrdavis
    
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
    #--Import Statements
    import numpy as np

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


