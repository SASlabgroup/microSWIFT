def GPStoUVZ(gpsfile):
    '''
    Author: @AlexdeKlerk
    Edited: @edwinrainville

    This function reads in data from the GPS files and saves it as python variables to be used in calculations 
    for wave properties. 

    '''
    # Import Statements
    import numpy as np
    import pynmea2

    # Define empty lists of variables to append
    u = []
    v = []
    z = []
    lat = []
    lon = []
    ipos=0
    ivel=0
    
    # Define Constants 
    badValue=999

    with open(gpsfile, 'r') as file:
    
        for line in file:
            if "GPGGA" in line:
                gpgga = pynmea2.parse(line,check=True)   #grab gpgga sentence and parse
                #check to see if we have lost GPS fix, and if so, continue to loop start. a badValue will remain at this index
                if gpgga.gps_qual < 1:
                    z.append(badValue)
                    lat.append(badValue)
                    lon.append(badValue)
                    ipos+=1
                    continue
                z.append(gpgga.altitude)
                lat.append(gpgga.latitude)
                lon.append(gpgga.longitude)
                ipos+=1
            elif "GPVTG" in line:
                gpvtg = pynmea2.parse(line,check=True)   #grab gpvtg sentence
                u.append( 0.2777 * gpvtg.spd_over_grnd_kmph*np.sin(np.deg2rad(gpvtg.true_track)))#units are m/s
                v.append( 0.2777 * gpvtg.spd_over_grnd_kmph*np.cos(np.deg2rad(gpvtg.true_track))) #units are m/s
                ivel+=1
            else: #if not GPGGA or GPVTG, continue to start of loop
                continue
           
    print('GPGGA lines: {}.'.format(ipos))
    print('GPVTG lines: {}'.format(ivel))

    return u,v,z,lat,lon