"""
Author: @jacobrdavis

A collection of functions for magnetometer calibratation. Heavily adapted from code shared online by
Riki @ thepoorengineer.com and @nliaudat on Gitub. See the following for more information:
    * original post, https://thepoorengineer.com/en/calibrating-the-magnetometer/#Calibrations
    * github repo, https://github.com/nliaudat/magnetometer_calibration
    * Qingde et al. 2010, https://ieeexplore.ieee.org/document/1290055/authors#authors
    * Manon et al. 2012, https://ieeexplore.ieee.org/document/6289882

NOTE: This code is NOT intended to be run onboard the microSWIFTs. Instead, calibration data should
be collected and run through this code to produce hard and soft iron corrections constants for a 
particular microSWIFT. #TODO: instructions and where to put constants!

Contents:
    - s

Log:
    - Sep 2022, J.Davis: created calibrateMag.py

TODO:
    - docstrings
    - instructions and where to put constants!
"""
import matplotlib.pyplot as plt
import numpy as np
from IMU.readIMU import readIMU
from mpl_toolkits.mplot3d import Axes3D
from scipy import linalg

def ellipsoid_fit(s):
        ''' 
            Original Author: @nliaudat 

            Estimate ellipsoid parameters from a set of points.
            Parameters
            ----------
            s : array_like
              The samples (M,N) where M=3 (x,y,z) and N=number of samples.
            Returns
            -------
            M, n, d : array_like, array_like, float
              The ellipsoid parameters M, n, d.
            References
            ----------
            .. [1] Qingde Li; Griffiths, J.G., "Least squares ellipsoid specific
               fitting," in Geometric Modeling and Processing, 2004.
               Proceedings, vol., no., pp.335-340, 2004
        '''

        # D (samples)
        D = np.array([s[0]**2., s[1]**2., s[2]**2.,
                      2.*s[1]*s[2], 2.*s[0]*s[2], 2.*s[0]*s[1],
                      2.*s[0], 2.*s[1], 2.*s[2], np.ones_like(s[0])])

        # S, S_11, S_12, S_21, S_22 (eq. 11)
        S = np.dot(D, D.T)
        S_11 = S[:6,:6]
        S_12 = S[:6,6:]
        S_21 = S[6:,:6]
        S_22 = S[6:,6:]

        # C (Eq. 8, k=4)
        C = np.array([[-1,  1,  1,  0,  0,  0],
                      [ 1, -1,  1,  0,  0,  0],
                      [ 1,  1, -1,  0,  0,  0],
                      [ 0,  0,  0, -4,  0,  0],
                      [ 0,  0,  0,  0, -4,  0],
                      [ 0,  0,  0,  0,  0, -4]])

        # v_1 (eq. 15, solution)
        E = np.dot(linalg.inv(C),
                   S_11 - np.dot(S_12, np.dot(linalg.inv(S_22), S_21)))

        E_w, E_v = np.linalg.eig(E)

        v_1 = E_v[:, np.argmax(E_w)]
        if v_1[0] < 0: v_1 = -v_1

        # v_2 (eq. 13, solution)
        v_2 = np.dot(np.dot(-np.linalg.inv(S_22), S_21), v_1)

        # quadric-form parameters
        M = np.array([[v_1[0], v_1[3], v_1[4]],
                      [v_1[3], v_1[1], v_1[5]],
                      [v_1[4], v_1[5], v_1[2]]])
        n = np.array([[v_2[0]],
                      [v_2[1]],
                      [v_2[2]]])
        d = v_2[3]

        return M, n, d


def calibrateMag(mag, fromFile = False, imufile = None):
    """
    TODO: _summary_

    Arguments:
    TODO: update
        # - imufile (str), path to IMU .dat file containing calibration mag data
        #     * note acceleration and gyroscope entries are not used
    Returns:
        - magCal (np.ndarray), [3xn] array of calibrated mag data
        - Ainv (np.ndarray), [3x3] soft iron correction matrix
        - b (np.ndarray), [3x1] hard iron offsets
    """

    if fromFile == True:
        _, _, mag, _ = readIMU(imufile)

        mag = np.asarray(mag).transpose()
 

    magX = mag[0] #  * 0.080 ?
    magY = mag[1]
    magZ = mag[2]

    fig,ax = plt.subplots(1,1)
    ax.scatter(mag[0],mag[1],label = 'x-y')
    ax.scatter(mag[0],mag[2],label = 'x-z')
    ax.scatter(mag[1],mag[2],label = 'y-z')
    ax.axhline(y=0 , color='k')
    ax.axvline(x=0 , color='k')
    # ax.set_xlim([-60,60])
    # ax.set_ylim([-60,60])
    ax.set_aspect('equal')
    ax.legend()


    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')

    ax1.scatter(magX, magY, magZ, s=5, color='r')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')

    # plot unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax1.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
    ax1.plot_surface(x, y, z, alpha=0.3, color='b')


    Q, n, d = ellipsoid_fit(mag)
    # Q, n, d = fitEllipsoid(magX, magY, magZ)

    Qinv = np.linalg.inv(Q)
    b = -np.dot(Qinv, n)
    Ainv = np.real(1 / np.sqrt(np.dot(n.T, np.dot(Qinv, n)) - d) * linalg.sqrtm(Q))

    print("A_inv: ")
    print(Ainv)
    print()
    print("b")
    print(b)
    print()

    calibratedX = np.zeros(magX.shape)
    calibratedY = np.zeros(magY.shape)
    calibratedZ = np.zeros(magZ.shape)

    totalError = 0
    for i in range(len(magX)):
        h = np.array([[magX[i], magY[i], magZ[i]]]).T
        hHat = np.matmul(Ainv, h-b)
        calibratedX[i] = hHat[0]
        calibratedY[i] = hHat[1]
        calibratedZ[i] = hHat[2]
        mag0 = np.dot(hHat.T, hHat)
        err = (mag0[0][0] - 1)**2
        totalError += err
    print("Total Error: %f" % totalError)


    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')

    ax2.scatter(calibratedX, calibratedY, calibratedZ, s=1, color='r')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')

    # plot unit sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax2.plot_wireframe(x, y, z, rstride=10, cstride=10, alpha=0.5)
    ax2.plot_surface(x, y, z, alpha=0.3, color='b')

    ax2.set_xlim([-1.2, 1.2])
    ax2.set_ylim([-1.2, 1.2])
    ax2.set_zlim([-1.2, 1.2])

    plt.show()

    magCal = np.array([calibratedX, calibratedY, calibratedZ])

    return magCal, Ainv, b


# def fitEllipsoid(magX, magY, magZ):
#     """
#     _summary_

#     Arguments:
#         - magX (_type_), _description_
#         - magY (_type_), _description_
#         - magZ (_type_), _description_

#     Returns:
#         - Q, 
#         - n,
#         - d,
#     """
#     a1 = magX ** 2
#     a2 = magY ** 2
#     a3 = magZ ** 2
#     a4 = 2 * np.multiply(magY, magZ)
#     a5 = 2 * np.multiply(magX, magZ)
#     a6 = 2 * np.multiply(magX, magY)
#     a7 = 2 * magX
#     a8 = 2 * magY
#     a9 = 2 * magZ
#     a10 = np.ones(len(magX)).T
#     D = np.array([a1, a2, a3, a4, a5, a6, a7, a8, a9, a10])

#     # Eqn 7, k = 4
#     C1 = np.array([[-1, 1, 1, 0, 0, 0],
#                    [1, -1, 1, 0, 0, 0],
#                    [1, 1, -1, 0, 0, 0],
#                    [0, 0, 0, -4, 0, 0],
#                    [0, 0, 0, 0, -4, 0],
#                    [0, 0, 0, 0, 0, -4]])

#     # Eqn 11
#     S = np.matmul(D, D.T)
#     S11 = S[:6, :6]
#     S12 = S[:6, 6:]
#     S21 = S[6:, :6]
#     S22 = S[6:, 6:]

#     # Eqn 15, find eigenvalue and vector
#     # Since S is symmetric, S12.T = S21
#     tmp = np.matmul(np.linalg.inv(C1), S11 - np.matmul(S12, np.matmul(np.linalg.inv(S22), S21)))
#     eigenValue, eigenVector = np.linalg.eig(tmp)
#     u1 = eigenVector[:, np.argmax(eigenValue)]

#     # Eqn 13 solution
#     u2 = np.matmul(-np.matmul(np.linalg.inv(S22), S21), u1)

#     # Total solution
#     u = np.concatenate([u1, u2]).T

#     Q = np.array([[u[0], u[5], u[4]],
#                   [u[5], u[1], u[3]],
#                   [u[4], u[3], u[2]]])

#     n = np.array([[u[6]],
#                   [u[7]],
#                   [u[8]]])

#     d = u[9]

#     return Q, n, d