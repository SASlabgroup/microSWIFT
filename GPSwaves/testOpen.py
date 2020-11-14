import os
import time

def getNewFile(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

readGPSpipe = getNewFile('/home/pi/microSWIFT/testmicroWave/data')
print (readGPSpipe)
readGPS = open(readGPSpipe,'r')
print (readGPS)

while True: 
    try:
        newline = readGPS.readlines()
        print (newline)
        time.sleep(.05)
        #if len(newline.strip()) == 0:
        #    break
            
    except Exception as e1:
        print('error: ' + str(e1 ))
