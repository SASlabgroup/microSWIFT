"""
Telemetry stack initalization and push/pop operations; this may be 
asbored by sbd.py in future implementations. To minimize opening the
file, dont use push/pop.
"""
####TODO: Update this block when EJ finishes the config integration ####
# this will probably go in a developer settings/config
TELEMETRY_STACK_FILE = '/home/pi/microSWIFT/SBD/telemetry_stack.txt'

########################################################################


def init():
    telemetry_stack = open(TELEMETRY_STACK_FILE, 'a')
    telemetry_stack.close()

def push(tx_filename):
    """TODO: 
    Read in the file names from the telemetry queue and strip
    """
    payload_filenames = get_filenames()
    payload_filenames.append(tx_filename)
    write(payload_filenames)

    return payload_filenames

def write(payload_filenames_stripped):
    """TODO: Write all the filenames to the file including the newest file name"""
    with open(TELEMETRY_STACK_FILE, 'w') as telemetry_stack:
        for line in payload_filenames_stripped:
            telemetry_stack.write(line)
            telemetry_stack.write('\n')


def remove_last(): # or pop?
    """TODO: 
    Read in the file names from the telemetry queue and strip
    """
    payload_filenames = get_filenames()
    del payload_filenames[-1]
    write(payload_filenames)

    return payload_filenames

# def peek():


def clear():
    """TODO:"""
    telemetry_stack = open(TELEMETRY_STACK_FILE, 'w')
    telemetry_stack.close()

    # TODO: add this to checkout.py to make sure the stack is empty before it goes
    # out. Could be a function in telemetry_stack that gets called by checkout.py

def strip_filenames(payload_filenames):
    """TODO:"""
    payload_filenames_stripped = []
    for line in payload_filenames:
        payload_filenames_stripped.append(line.strip())

    return payload_filenames_stripped


def get_filenames():
    """ TODO: Read in the file names from the telemetry queue """
    with open(TELEMETRY_STACK_FILE, 'r') as telemetry_stack:
        payload_filenames = telemetry_stack.readlines()

    return strip_filenames(payload_filenames)


def get_length():
    """TODO:"""
    payload_filenames = get_filenames()
    return len(payload_filenames)
