## Send Short Burst Data (SBD) Functions 

# Telemetry test functions
def createTX(Hs, Tp, Dp, E, f, a1, b1, a2, b2):
    print('TX file created with the variables Hs, Tp, Dp, E, f, a1, b1, a2, b2')
    TX_fname = 'TX-file'
    return TX_fname

def sendSBD(TX_fname):
    print('Sending SBD...')
    print('Sent SBD...')