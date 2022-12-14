"""
Mocked serial connection
"""
import logging

# Set up module level logger
logger = logging.getLogger('microSWIFT.'+__name__)

class Serial:
    """
    Mocked Serial connection class
    """
    def __init__(self, gps_port, start_baud, timeout):
        """
        Initialize the Serial connection mock class
        """
        self.port = gps_port
        self.baud = start_baud
        self.timeout = timeout
        self.messages = []

    def write(self, binary):
        """
        Write a binary message to the GPS module. This is used to set up
        the chipset.

        Parameters
        ----------
        string :
        """
        self.messages.append(binary)

    def flushInput(self):
        """
        clear the input from the serial port
        """
        self.messages = []
    
    def read_unitl(self, binary):
        """
        Open serial connection to read for  agiven amount of time.

        Parameters
        ----------
        binary : input message in binary
        """

    def readline(self):
        """
        Read new lines from the serial port.
        """
        
