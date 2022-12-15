"""
MicroSWIFT-specific logging utilities.
"""

import logging
import math

def init() -> logging.Logger:
    """
    Initialize the logger for printing to the microSWIFT's log file.

    Returns:
        Logger: initialized logger
    """
    logger = logging.getLogger('microSWIFT')

    # Get log parameters from configuration:
    LOG_FILE_NAME = './logs/microSWIFT.log'
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = ('%(asctime)s, %(name)s - [%(levelname)s] - %(message)s')

    # Set log parameters:
    logger.setLevel(LOG_LEVEL)
    try:
        log_file_handler = logging.FileHandler(LOG_FILE_NAME)
        log_file_handler.setLevel(LOG_LEVEL)
        log_file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(log_file_handler)
    except FileNotFoundError as err:
         print(err, 'please create a ./microSWIFT/logs/ directory.')


    return logger

def header(header_name: str, length: int = 50) -> str:
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
    header_line_length = math.floor((length-len(header_name))/2)
    return header_line_length*'-' + header_name + header_line_length*'-'
