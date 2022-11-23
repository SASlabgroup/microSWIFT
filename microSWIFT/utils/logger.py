"""
MicroSWIFT-specific logging utilities.

#TODO:
    - fix the configuration import
"""

import logging
import math
import sys

from config3 import Config


# Define Config file name and load file
CONFIG_FILENAME = r'/home/pi/microSWIFT/utils/Config.dat'
config = Config() # Create object and load file
loaded = config.loadFile(CONFIG_FILENAME)
if not loaded:
    print("Error loading config file")
    sys.exit(1)

LOG_HEADER_LENGTH = 50 #TODO: put this in the config

def init_logger() -> logging.Logger:
    """
    Initialize the logger for printing to the microSWIFT's pi terminal.

    Returns:
        Logger: initialized logger
    """
    logger = logging.getLogger('microSWIFT')

    # Get log parameters from configuration:
    LOG_DIR = config.getString('Loggers', 'logDir')
    LOG_LEVEL = config.getString('Loggers', 'DefaultLogLevel')
    LOG_FORMAT = ('%(asctime)s, %(name)s - [%(levelname)s] - %(message)s')
    LOG_FILE = (LOG_DIR  + logger.name + '.log')

    # Set log parameters:
    logger.setLevel(LOG_LEVEL)
    log_file_handler = logging.FileHandler(LOG_FILE)
    log_file_handler.setLevel(LOG_LEVEL)
    log_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(log_file_handler)

    return logger

def log_header(header_name: str, length: int = LOG_HEADER_LENGTH) -> str:
    """
    Utility to create uniform length log headers with a function name.

    Arguments:
        - header_name (str), header text, typically the function name
            * Accessed programmatically using {fun}.__name__
        - length (int, optional), desired header length; defaults to 30

    Returns:
        - (str), log header

    Example:
        log_header(__name__, length = 50)
    """
    header_name = header_name
    header_line_length = math.floor((length-len(header_name))/2)
    return header_line_length*'-' + header_name + header_line_length*'-'
