"""
Functions to test the installation, calibration, and validity of the onboard IMU.
"""
import time
from . import imu

def run_tests(run_time):
    """
    Function to run tests for calibration of the IMU

    Parameters:
    -----------
    run_time = time in minutes to run tests. Minumum:1, maximum:60

    Returns:
    --------
    Calibration document
    """

    #initialize the imu
    imu_initialized = imu.init()
    if imu_initialized == False:
        raise Exception('IMU failed to initialize')

    if run_time < 1:
        raise ValueError('Run time must be greater than or equal to 1')

    if run_time > 60:
        raise ValueError('Run time must be less than or equal to 60')

    t_end = time.time() + (60 * run_time)

    print("IMU checkout beginning. Please keep buoy still for", run_time,
    "minute(s).")

    imu.record(t_end)
