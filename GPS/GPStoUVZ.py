

import numpy as np
import pynmea2

gps_samples=2048
badValue=999

def GPStoUVZ(gpsfile):
    
    # u = np.empty(gps_samples)
    # u.fill(badValue)
    # v = np.empty(gps_samples)
    # v.fill(badValue)
    # z = np.empty(gps_samples)
    # z.fill(badValue)
    # lat = np.empty(gps_samples)
    # lat.fill(badValue)
    # lon = np.empty(gps_samples)
    # lon.fill(badValue)
    u = []
    v = []
    z = []
    lat = []
    lon = []
    
    ipos=0
    ivel=0
    
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
                if gpgga.gps_qual < 1:
                    u.append(badValue)
                    v.append(badValue)
                    ivel+=1
                    continue
                gpvtg = pynmea2.parse(line,check=True)   #grab gpvtg sentence
                u.append( 0.2777 * gpvtg.spd_over_grnd_kmph*np.sin(np.deg2rad(gpvtg.true_track)))#units are m/s
                v.append( 0.2777 * gpvtg.spd_over_grnd_kmph*np.cos(np.deg2rad(gpvtg.true_track))) #units are m/s
                ivel+=1
            else: #if not GPGGA or GPVTG, continue to start of loop
                continue
           
    print('GPGGA lines: {}.'.format(ipos))
    print('GPVTG lines: {}'.format(ivel))

    return u,v,z,lat,lon

# if __name__ == "__main__":

#     import sys

#     if len(sys.argv) != 2:
#         print("Provide the path to the GPS file.")
#         sys.exit(1)

#     gpsfile = sys.argv[1]
    
#     u,v,z,lat,lon = getUVZ(gpsfile)