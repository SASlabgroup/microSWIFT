#!usr/bin/python3

#Test Iridium signal quality and log output
#needs send_sbd.py in python path to run

#8 April 2021
#Alex de Klerk



import send_sbd
from datetime import datetime
import sys

if __name__=='__main__':
    
    ser, success = send_sbd.init_modem()
    
    if success == True:
        ser.timeout = 60
        now = datetime.utcnow()
        fname = 'home/pi/microSWIFT/data/' + 'Iridium_signal_quality_' + '{:%d%b%Y_%H%M%SUTC.dat}'.format(datetime.utcnow())
        
        with open(fname, 'w') as datafile:
            qual = send_sbd.signal_qual(ser)
            datafile.write(qual)
        
    else:
        print('modem not initialized, exiting')
        sys.exit(1)   
        

