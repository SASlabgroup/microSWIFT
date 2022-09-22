import math

def create_log_header(funName, length = 30):
    """
    Author: @jacobrdavis

    Utility to create uniform length log headers with a function name

    Arguments:
        - funName (str), function name
            * Accessed programmatically using {fun}.__name__
        - length (int, optional), desired header length; defaults to 30

    Returns:
        - (str), log header

    Example:
        create_log_header(__name__, length = 50)
    """
    funName = funName + '.py'
    headerLineLength = math.floor((length-len(funName))/2)
    return headerLineLength*'-' + funName + headerLineLength*'-'