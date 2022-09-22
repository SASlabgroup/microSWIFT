"""
Author: @jacobrdavis, @edwinrainville

A collection of functions for transforming IMU accelerations, gyro, and mag readings 
from the body to earth frame.

Contents:
    - ekfCorrection(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z)

Log:
    - Jun 2022, J. Davis: copied ekfCorrection() into microSWIFT repo 
    - Aug 2022, J. Davis: created transformIMU.py
    - Sep 2022, J. Davis: mag cal functions
    
"""
import numpy as np
from ahrs.filters import EKF
from scipy.spatial.transform import Rotation as R

def change_up_axis(X0,upIdx):
    """
    TODO:_summary_
    TODO: handle cases when upside down :/

    Arguments:
        - X0 (_type_), _description_
        - upIdx (_type_), _description_

    Returns:
        - (_type_), _description_
    """
    if upIdx == 0: #[x y z] -> [-z y x]
        transformIdx = [2, 1, 0]
        signs = [-1, 1, 1]
    elif upIdx == 1: #[x y z] == [x -z y]
        transformIdx = [0, 2, 1]
        signs = [1, -1, 1]
    elif upIdx == 2: #[x y z] == [x -z y]
        transformIdx = [0, 1, 2]
        signs = [1, 1, 1]

    X0 = X0[transformIdx]
    X0[0] = X0[0]*signs[0]
    X0[1] = X0[1]*signs[1]
    X0[2] = X0[2]*signs[2]

    return X0

def correct_mag(mag, Ainv, b):
    """
    Correct magnetometer readings using hard and soft iron corrections.

    Arguments:
        - mag (np.ndarray), [3xn] array of calibrated mag data
        - Ainv (np.ndarray), [3x3] soft iron correction matrix
        - b (np.ndarray), [3x1] hard iron offsets

    Returns:
        - magCal (np.ndarray), [3xn] array of calibrated mag data
    """
    magCal = np.zeros(mag.shape)
    for i, h in enumerate(mag.T):
        h = h.reshape((3, 1))
        hHat = np.matmul(Ainv, h-b)
        magCal[:,i] = np.squeeze(hHat)

    return magCal

def ekfCorrection(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z):
    '''
    @edwinrainville

    Correct the body frame accelerations to the earth frame of reference through and extended Kalman Filter
    '''

    # Organize the acceleration data into arrays to be used in the ekf algorithm
    acc_data = np.array([accel_x-np.mean(accel_x), accel_y-np.mean(accel_y), accel_z-np.mean(accel_z)]).transpose()
    gyr_data = np.array([gyro_x-np.mean(gyro_x), gyro_y-np.mean(gyro_y), gyro_z-np.mean(gyro_z)]).transpose()
    mag_data = np.array([mag_x-np.mean(mag_x), mag_y-np.mean(mag_y), mag_z-np.mean(mag_z)]).transpose()

    # Rotate the acceleration data with extended Kalman filter
    # ** the variance of each sensor needs to be further examined
    # ** Variance is assumed from spec sheet
    # ekf = EKF(gyr=gyr_data, acc=acc_data, mag_data=mag_data, frequency=12, var_acc=0.000003, var_gyro=0.04, var_mag=.1, frame='NED')
    #
    # print(gyr_data)
    # TODO: check units required  by EFK algorithm
    # see : https://github.com/adafruit/Adafruit_AHRS/blob/master/examples/ahrs_fusion_ble_nrf51/ahrs_fusion_ble_nrf51.ino
    
    # ekf = EKF(gyr=gyr_data, acc=acc_data, mag=mag_data, magnetic_ref=60.0, frequency=12, var_acc=0.000003, var_gyro=0.04, frame='NED')
    ekf = EKF(gyr=gyr_data, acc=acc_data, mag=mag_data, frequency=12, var_acc=0.000003, var_gyro=0.04, frame='NED')
    # EKF(gyr=gyr_data, acc=acc_data, mag=mag_data, magnetic_ref=60.0)
    # Rotate the acclerations from the computed Quaterions
    r = R.from_quat(ekf.Q)
    accel_rotated = r.apply(acc_data)

    # Get acceleration data from the rotated structure
    accel_x_earth = accel_rotated[:,0]
    accel_y_earth = accel_rotated[:,1]
    accel_z_earth = accel_rotated[:,2]

    return accel_x_earth, accel_y_earth, accel_z_earth
