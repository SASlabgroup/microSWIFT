## Send Short Burst Data (SBD) Functions 
'''
author: @erainvil

'''

# Import Statements
import datetime
from struct import *
from logging import *
import sys, os
from utils.config3 import Config

# Telemetry test functions
def createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2, umean, vmean, zmean, temp, volt, configFilename):
    #load config file and get parameters
    config = Config() # Create object and load file
    ok = config.loadFile( configFilename )
    dataDir = config.getString('System', 'dataDir')
    floatID = os.uname()[1]

    #create module level logger
    logger = getLogger('system_logger.'+__name__)   
    now=datetime.utcnow()
    TX_fname = dataDir + floatID+'_TX_'+"{:%d%b%Y_%H%M%SUTC.dat}".format(now)
    logger.info('telemetry file = %s' %TX_fname)



    print('TX file created with the variables Hs, Tp, Dp, E, f, a1, b1, a2, b2')
    TX_fname = 'TX-file'
    return TX_fname

def sendSBD(TX_fname):
    print('Sending SBD...')
    print('Sent SBD...')