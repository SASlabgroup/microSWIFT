def GPStoUVZ(gpsfile):
    '''
    Author: @AlexdeKlerk
    Edited: @edwinrainville
            @jacobrdavis 2022-07-20: added timestamp parsing; wrapped outputs in GPS dictionary
    This function reads in data from the GPS files and saves it as python variables to be used in calculations 
    for wave properties. 

    '''
    # Import Statements
    import numpy as np
    import pynmea2
    from datetime import datetime, timedelta
    from logging import getLogger

    # Set up module level logger
    logger = getLogger('microSWIFT.'+__name__) 
    logger.info('---------------GPStoUVZ.py------------------')

    # Define empty lists of variables to append
    u = []
    v = []
    z = []
    lat = []
    lon = []
    time = []
    ipos=0
    ivel=0
    GPS = {'u':None,'v':None,'z':None,'lat':None,'lon':None,'time':None}
    
    # Define Constants 
    badValue=999
    
    # current year, month, date for timestamp creation; can also be obtained from utcnow()
    ymd = gpsfile[-23:-14]
    # ymd = datetime.utcnow().strftime("%Y-%m-%d")


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
                # construct a datetime from the year, month, date, and timestamp
                dt = f'{ymd} {gpgga.timestamp}'  #.rstrip('0')
                if '.' not in dt: # if the datetime does not contain a float, append a trailing zero
                    dt += '.0'
                time.append(datetime.strptime(dt,'%d%b%Y %H:%M:%S.%f'))
                ipos+=1
            elif "GPVTG" in line:
                gpvtg = pynmea2.parse(line,check=True)   #grab gpvtg sentence
                u.append( 0.2777 * gpvtg.spd_over_grnd_kmph*np.sin(np.deg2rad(gpvtg.true_track)))#units are m/s
                v.append( 0.2777 * gpvtg.spd_over_grnd_kmph*np.cos(np.deg2rad(gpvtg.true_track))) #units are m/s
                ivel+=1
            else: #if not GPGGA or GPVTG, continue to start of loop
                continue
           
    if ivel < ipos: # if an extra GPGGA line exists, remove the last entry
        del z[-(ipos-ivel)]
        del lat[-(ipos-ivel)]
        del lon[-(ipos-ivel)]
        del time[-(ipos-ivel)]
        logger.info(f'{ipos-ivel} GPGGA lines removed at end')

    logger.info('GPS file read')

    # TODO: bug here, fix!
    # sortInd    = np.asarray(time).argsort()
    # timeSorted = np.asarray(time)[sortInd]
    # uSorted    = np.asarray(u)[sortInd].transpose()
    # vSorted    = np.asarray(v)[sortInd].transpose()
    # zSorted    = np.asarray(z)[sortInd].transpose()
    # latSorted  = np.asarray(lat)[sortInd].transpose()
    # lonSorted  = np.asarray(lon)[sortInd].transpose()

    

    # assign outputs to GPS dict
    GPS.update({'u':u,'v':v,'z':z,'lat':lat,'lon':lon,'time':time})
    # GPS.update({'u':uSorted,'v':vSorted,'z':zSorted,'lat':latSorted,'lon':lonSorted,'time':timeSorted})

    logger.info('GPGGA lines: {}'.format(len(lat)))
    logger.info('GPVTG lines: {}'.format(len(u)))

    return GPS #u,v,z,lat,lon, time