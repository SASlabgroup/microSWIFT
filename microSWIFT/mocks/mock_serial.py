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
        self.return_gpgga = False
        self.return_gprmc = False

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

    def read_until(self, binary):
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
        if self.return_gpgga is False:
            self.return_gpgga = True
            return ('GPGGA,140008.500,3610.9582,N,07544.9381,W,2,09,' \
                   '1.00,14.6,M,-35.6,M,0000,0000*60').encode()
        else:
            self.return_gprmc = True
            return ('GPRMC,140008.500,A,3610.9582,N,07544.9381,W,2.45,' \
                    '81.33,081021,,,D*42').encode()

        

