#! /usr/bin/python2.7
#import time
import os
path = ('/home/pi/microSWIFT/testmicroWave/data')
os.chdir(path)
files = sorted(os.listdir(os.getcwd()), key=os.path.getctime)
print (files)
#oldest = min(os.listdir(path), key=os.path.getctime)
#newest = max(os.listdir(path), key=os.path.getctime)
oldest = files[0]
newest = files[-1]
print (newest)
print (oldest)

def getNewFile(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

with open(newest,'r') as f:
    line = f.readlines()[-10]
    print (line)
    #time.sleep(.05)'
    #lastline = (list(line)[-1])
#print (lastline[-6:])