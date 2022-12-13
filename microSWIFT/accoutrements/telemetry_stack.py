"""
Manage text file containing stack of .sbd filenames.

Telemetry stack initialization and push/pop operations. The stack of
.sbd filenames is stored locally on the microSWIFT and is appended/
modified during the record-send sequencing handled by microSWIFT.py.

NOTE: This may be asborbed by sbd.py in future implementations.
"""

####TODO: Update this block when EJ finishes the config integration ####
# this will probably go in a developer settings/config
TELEMETRY_STACK_FILE = './microSWIFT/utils/telemetry_stack.txt'

########################################################################


def init():
    """
    Initialize the stack file.

    Create the telemetry stack file in the specified directory if it
    does not already exist. By opening the file in 'append' mode, a new
    file will be written if a telemetry stack .txt file doesn't exist,
    otherwise no changes will be made to the existing stack file.
    """
    telemetry_stack = open(TELEMETRY_STACK_FILE, mode='a', encoding='utf-8')
    telemetry_stack.close()

def write(payload_filenames_stripped):
    """
    Write a list of filenames to the stack.

    Args:
        payload_filenames_stripped (List[Str]): filenames to be written to
        the stack. The contents of the list must be stripped of any
        leading or trailing whitespace prior to writing.
    """
    with open(TELEMETRY_STACK_FILE, 'w', encoding='utf-8') as telemetry_stack:
        for line in payload_filenames_stripped:
            telemetry_stack.write(line) #TODO: I think the .strip() method can just be used here.
            telemetry_stack.write('\n')

def push(tx_filename):
    """
    Push a telemetry .sbd filename onto the stack file.

    Reads the current filenames on the stack into memory, appends the
    newest file, and then re-writes the stack.

    Args:
        tx_filename (Str): .sbd filename to push onto the stack

    Returns:
        List: filenames currently on the stack (after pushing)
    """
    payload_filenames = get_filenames()
    payload_filenames.append(tx_filename)
    write(payload_filenames)

    return payload_filenames

def pop(index = -1):
    """
    Pop a filename from the stack.

    Args:
        index (int, optional): index in `payload_filenames` to pop.
            Defaults to -1.

    Returns:
        (Str, List[Str]): the popped filename and the updated list of
            filenames currently on the stack.
    """
    payload_filenames = get_filenames()
    popped_filename = payload_filenames[index]
    del payload_filenames[index]
    write(payload_filenames)

    return popped_filename, payload_filenames

def clear():
    """
    Clear the stack.
    
    Warning: this will completely overwrite any existing filenames on
    the stack!
    """
    telemetry_stack = open(TELEMETRY_STACK_FILE, mode='w', encoding='utf-8')
    telemetry_stack.close()

    # TODO: add this to checkout.py to make sure the stack is empty before it goes
    # out. Could be a function in telemetry_stack that gets called by checkout.py

def strip_filenames(payload_filenames):
    """"
    Strip payload filenames of whitespace prior to writing.

    Args:
        payload_filenames (List[Str]): filenames to strip of whitespace.

    Returns:
       (List[Str]): stripped filenames.
    """
    payload_filenames_stripped = []
    for line in payload_filenames:
        payload_filenames_stripped.append(line.strip())

    return payload_filenames_stripped

def get_filenames():
    """
    Get the current list of .sbd filenames on the stack.

    Returns:
        List[Str]: filenames on the stack.
    """
    with open(TELEMETRY_STACK_FILE, 'r', encoding='utf-8') as telemetry_stack:
        payload_filenames = telemetry_stack.readlines()

    return strip_filenames(payload_filenames)

def get_length():
    """
    Get the length of the stack.

    Returns:
        Int: number of filenames on the stack.
    """
    payload_filenames = get_filenames()
    return len(payload_filenames)
