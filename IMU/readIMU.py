from datetime import date, datetime, timedelta

def readIMU(imufile):
    """
    Read in acceleration, magnetometer, and gyroscope data from IMU .dat file

    Arguments:
        - imufile (str), path to IMU .dat file

    Returns:
        - timestamp (list[datetime]), list of datetimes from IMU timestamp entries
        - acc (list), acceleration entries
        - mag (list), magnetometer entries
        - gyo (list), gyroscope entries
    """
    # Initialization:
    timestamp = []
    acc = []
    mag = []
    gyo = []

    with open(imufile, 'r') as file: #encoding="utf8", errors='ignore'
            for line in file:
                currentLine = line.strip('\n').rstrip('\x00').split(',')
                if currentLine[0] is not '':
                    timestamp.append(datetime.strptime(currentLine[0],'%Y-%m-%d %H:%M:%S'))
                    acc.append(list(map(float,currentLine[1:4])))  # acc = [ax,ay,az]
                    mag.append(list(map(float,currentLine[4:7])))  # mag = [mx,my,mz]
                    gyo.append(list(map(float,currentLine[7:10]))) # gyo = [gx,gy,gz]

    return timestamp, acc, mag, gyo