/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * IMUtoXYZ.cpp
 *
 * Code generation for function 'IMUtoXYZ'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "IMUtoXYZ.h"
#include "XYZwaves.h"
#include "detrend.h"
#include "cumtrapz.h"
#include "cosd.h"
#include "sind.h"
#include "atan2d.h"
#include "mean.h"
#include "sqrt.h"
#include "power.h"
#include "processIMU_rtwutil.h"

/* Function Declarations */
static void RCfilter(const double b[2048], double fs, double a[2048]);

/* Function Definitions */
static void RCfilter(const double b[2048], double fs, double a[2048])
{
  double alpha;
  int ui;

  /*  EMBEDDED RC FILTER function (high pass filter) %% */
  alpha = 4.0 / (4.0 + 1.0 / fs);
  memcpy(&a[0], &b[0], sizeof(double) << 11);
  for (ui = 0; ui < 2047; ui++) {
    a[ui + 1] = alpha * a[ui] + alpha * (b[ui + 1] - b[ui]);
  }
}

void IMUtoXYZ(double ax[2048], double ay[2048], double az[2048], const double
              gx[2048], const double gy[2048], const double gz[2048], double mx
              [2048], double my[2048], double mz[2048], double mxo, double myo,
              double Wd, double fs, double x[2048], double y[2048], double z
              [2048], double roll[2048], double pitch[2048], double yaw[2048],
              double heading[2048])
{
  double dt;
  static double vz[2048];
  static double dv0[2048];
  int i;
  double theta[2048];
  double dv1[2048];
  double b_ax;
  double b_ay;
  double b_az;
  int ii;
  double dv2[2048];
  double vx[2048];
  double dv3[2048];
  double vy[2048];
  double d0;
  double d1;
  double d2;
  double d3;
  double d4;
  double u[2048];
  double d5;
  double d6;
  double d7;
  double d8;
  double dv4[9];
  double dv5[9];
  double dv6[2048];
  double dv7[9];
  double dv8[2048];
  static const signed char iv0[3] = { 0, 1, 0 };

  static const signed char iv1[3] = { 1, 0, 0 };

  double dv9[2048];
  int i1;
  static const signed char iv2[3] = { 0, 0, 1 };

  double c_ax[3];
  double dv10[9];
  int i2;
  double dv11[2048];
  double a[3];
  double T[9];

  /*  */
  /*  Matlab function to calculate wave displacements in earth reference frame */
  /*  from microSWIFT IMU measurements in body reference frame */
  /*  */
  /*  Inputs are raw accelerometer, gyro, and magnotometer readings (3 axis each) */
  /*  along with magnetometer offsets (3), a weight coef for filtering the gyro, */
  /*  and the sampling frequency of the raw data */
  /*  */
  /*    [x, y, z, roll, pitch, yaw, heading] = IMUtoXYZ(ax, ay, az, gx, gy, gz, mx, my, mz, mxo, myo, mzo, Wd, fs ); */
  /*  */
  /*  Outputs are displacements x (east), y (north), and z (up), */
  /*  along with Euler angles and geographic heading for debugging */
  /*  */
  /*  The weight coef Wd must be between 0 and 1, with 0 as default */
  /*  (this controls importantce dynamic angles in a complimentary filter) */
  /*  */
  /*  The default magnetomoter offsets are mxo = 60, myo = 60, mzo = 120 */
  /*  */
  /*  The sampling rate is usually 4 Hz */
  /*  */
  /*  The body reference frame for the inputs is */
  /*    x: along bottle (towards cap), roll around this axis */
  /*    y: accross bottle (right hand sys), pitch around this axis */
  /*    z: up (skyward, same as GPS), yaw around this axis */
  /*  */
  /*  */
  /*  J. Thomson, Feb 2021 */
  /*  */
  /*  weighting (0 to 1) for static angles in complimentary filter */
  dt = 1.0 / fs;

  /*  time step */
  /*  high pass RC filter constant, T > (2 * pi * RC) */
  /*  estimate Euler angles with complementary filter */
  /*  roll around x axis [deg] in absence of linear acceleration */
  power(ay, vz);
  power(az, dv0);
  for (i = 0; i < 2048; i++) {
    vz[i] += dv0[i];
  }

  e_sqrt(vz);
  for (i = 0; i < 2048; i++) {
    theta[i] = -ax[i];
  }

  b_atan2d(theta, vz, dv0);

  /*  pitch around y axis [deg] in absence of linear acceleration */
  /*  yaw around z axis [deg], zero for now... it's relative until applying the magnetometer */
  if (Wd != 0.0) {
    /*  time integrate to get dynamic roll */
    cumtrapz(gx, vz);
    for (i = 0; i < 2048; i++) {
      theta[i] = vz[i] * dt;
    }

    RCfilter(theta, fs, roll);

    /*  high-pass filter to reduce drift */
    /*  time integrate to get dynamic roll */
    cumtrapz(gy, vz);
    for (i = 0; i < 2048; i++) {
      theta[i] = vz[i] * dt;
    }

    RCfilter(theta, fs, pitch);

    /*  high-pass filter to reduce drift */
    /*  time integrate to get dynamic yaw */
    cumtrapz(gz, vz);
    for (i = 0; i < 2048; i++) {
      theta[i] = vz[i] * dt;
    }

    RCfilter(theta, fs, yaw);

    /*  high-pass filter to reduce drift */
  } else {
    memset(&roll[0], 0, sizeof(double) << 11);
    memset(&pitch[0], 0, sizeof(double) << 11);
    memset(&yaw[0], 0, sizeof(double) << 11);
  }

  /*  combine orientation estimates (using weighted complementary filter) */
  b_atan2d(ay, az, dv1);
  b_ax = (1.0 - Wd) * b_mean(dv1);
  b_ay = (1.0 - Wd) * b_mean(dv0);
  b_az = (1.0 - Wd) * 0.0;
  for (i = 0; i < 2048; i++) {
    roll[i] = Wd * roll[i] + b_ax;
    pitch[i] = Wd * pitch[i] + b_ay;
    yaw[i] = Wd * yaw[i] + b_az;
  }

  /*  make rotation matrix for every time step */
  /*  careful here, order of Euler angles matters, see Zippel 2018 (JPO) and Edson 1998 for clues */
  for (ii = 0; ii < 2048; ii++) {
    /*  yaw matrix */
    /*  pitch matrix */
    /*  roll matrix */
    /*  transformation matrix from buoy to earth reference frame */
    b_ax = yaw[ii];
    b_cosd(&b_ax);
    b_ay = yaw[ii];
    b_sind(&b_ay);
    b_az = yaw[ii];
    b_sind(&b_az);
    d0 = yaw[ii];
    b_cosd(&d0);
    d1 = pitch[ii];
    b_cosd(&d1);
    d2 = pitch[ii];
    b_sind(&d2);
    d3 = pitch[ii];
    b_sind(&d3);
    d4 = pitch[ii];
    b_cosd(&d4);
    d5 = roll[ii];
    b_cosd(&d5);
    d6 = roll[ii];
    b_sind(&d6);
    d7 = roll[ii];
    b_sind(&d7);
    d8 = roll[ii];
    b_cosd(&d8);
    dv4[0] = d1;
    dv4[3] = 0.0;
    dv4[6] = d2;
    dv4[2] = -d3;
    dv4[5] = 0.0;
    dv4[8] = d4;
    dv5[1] = 0.0;
    dv5[4] = d5;
    dv5[7] = -d6;
    dv5[2] = 0.0;
    dv5[5] = d7;
    dv5[8] = d8;
    dv7[0] = b_ax;
    dv7[3] = -b_ay;
    dv7[6] = 0.0;
    dv7[1] = b_az;
    dv7[4] = d0;
    dv7[7] = 0.0;
    for (i = 0; i < 3; i++) {
      dv4[1 + 3 * i] = iv0[i];
      dv5[3 * i] = iv1[i];
      dv7[2 + 3 * i] = iv2[i];
    }

    for (i = 0; i < 3; i++) {
      for (i1 = 0; i1 < 3; i1++) {
        dv10[i + 3 * i1] = 0.0;
        for (i2 = 0; i2 < 3; i2++) {
          dv10[i + 3 * i1] += dv4[i + 3 * i2] * dv5[i2 + 3 * i1];
        }
      }
    }

    /*     %% rotate linear accelerations and magnetomer readings to horizontal (earth frame) */
    c_ax[0] = ax[ii];
    c_ax[1] = ay[ii];
    c_ax[2] = az[ii];
    for (i = 0; i < 3; i++) {
      a[i] = 0.0;
      for (i1 = 0; i1 < 3; i1++) {
        T[i + 3 * i1] = 0.0;
        for (i2 = 0; i2 < 3; i2++) {
          T[i + 3 * i1] += dv7[i + 3 * i2] * dv10[i2 + 3 * i1];
        }

        a[i] += T[i + 3 * i1] * c_ax[i1];
      }
    }

    b_ax = a[0];
    b_ay = a[1];
    b_az = a[2];
    c_ax[0] = mx[ii];
    c_ax[1] = my[ii];
    c_ax[2] = mz[ii];
    for (i = 0; i < 3; i++) {
      a[i] = 0.0;
      for (i1 = 0; i1 < 3; i1++) {
        a[i] += T[i + 3 * i1] * c_ax[i1];
      }
    }

    /*     %% create the angular rate matrix in earth frame and determine projected speeds */
    /*  (rotate the "strapped-down" gyro measurements from body to earth frame) */
    /*  skip this in onboard processing, effects are negligible, */
    /*  because IMU is close to center (M is small) */
    /*      M = [-0.076;  -0.013;  0; ]; % position vector of IMU relative to buoy center [meters] */
    /*      Omega = [0; 0; gz(ii);]  +    Y*[0; gy(ii); 0;]    +  Y*P*[gx(ii); 0; 0;]; */
    /*      Omega = deg2rad(Omega); */
    /*      [vxr(ii); vyr(ii); vzr(ii);] = cross(Omega, T*M); */
    ax[ii] = b_ax;
    ay[ii] = b_ay;
    az[ii] = b_az;
    mx[ii] = a[0];
    my[ii] = a[1];
    mz[ii] = a[2];
  }

  /*  close loop thru time steps */
  /*  filter and integrate linear accelerations to get linear velocities */
  detrend(ax);
  detrend(ay);
  detrend(az);
  memcpy(&theta[0], &ax[0], sizeof(double) << 11);
  RCfilter(theta, fs, dv2);
  cumtrapz(dv2, vx);

  /*  m/s */
  RCfilter(ay, fs, dv3);
  cumtrapz(dv3, vy);

  /*  m/s */
  /*  m/s */
  /*  remove rotation-induced velocities from total velocity (skip for onboard processing) */
  /*  vx = vx - vxr; */
  /*  vy = vy - vyr; */
  /*  vz = vz - vzr; */
  /*  determine geographic heading and correct horizontal velocities to East, North */
  for (i = 0; i < 2048; i++) {
    theta[i] = my[i] + myo;
    u[i] = mx[i] + mxo;
    vx[i] *= dt;
    vy[i] *= dt;
  }

  b_atan2d(theta, u, heading);

  /*  cartesian CCW heading from geographic CW heading */
  /*  x dir (horizontal in earth frame, but relative in azimuth) */
  /*  y dir (horizontal in earth frame, but relative in azimuth) */
  for (i = 0; i < 2048; i++) {
    b_ax = heading[i];
    if (heading[i] < 0.0) {
      b_ax = 360.0 + heading[i];
    }

    u[i] = vx[i];
    vz[i] = -(b_ax - 90.0);
    heading[i] = b_ax;
    theta[i] = -(b_ax - 90.0);
  }

  c_cosd(vz);
  memcpy(&dv0[0], &theta[0], sizeof(double) << 11);
  c_sind(dv0);

  /*  east component */
  for (i = 0; i < 2048; i++) {
    vx[i] = vx[i] * vz[i] - vy[i] * dv0[i];
    vz[i] = theta[i];
  }

  c_sind(vz);
  c_cosd(theta);
  for (i = 0; i < 2048; i++) {
    vy[i] = u[i] * vz[i] + vy[i] * theta[i];
  }

  /*  north compoent */
  /*  filter and integrate velocity for displacements, and filter again */
  detrend(vx);
  detrend(vy);
  RCfilter(az, fs, dv6);
  cumtrapz(dv6, vz);
  for (i = 0; i < 2048; i++) {
    vz[i] *= dt;
  }

  detrend(vz);
  RCfilter(vx, fs, dv8);
  cumtrapz(dv8, x);
  for (i = 0; i < 2048; i++) {
    x[i] *= dt;
  }

  detrend(x);
  RCfilter(vy, fs, dv9);
  cumtrapz(dv9, y);
  for (i = 0; i < 2048; i++) {
    y[i] *= dt;
  }

  detrend(y);
  RCfilter(vz, fs, dv11);
  cumtrapz(dv11, z);
  for (i = 0; i < 2048; i++) {
    z[i] *= dt;
  }

  detrend(z);
  memcpy(&theta[0], &x[0], sizeof(double) << 11);
  RCfilter(theta, fs, x);
  memcpy(&theta[0], &y[0], sizeof(double) << 11);
  RCfilter(theta, fs, y);
  memcpy(&theta[0], &z[0], sizeof(double) << 11);
  RCfilter(theta, fs, z);

  /*  remove first portion, which can has initial oscillations from filtering */
  b_ax = rt_roundd_snf(4.0 / dt * 10.0);
  if (1.0 > b_ax) {
    i = 0;
  } else {
    i = (int)b_ax;
  }

  if (0 <= i - 1) {
    memset(&x[0], 0, (unsigned int)(i * (int)sizeof(double)));
  }

  b_ax = rt_roundd_snf(4.0 / dt * 10.0);
  if (1.0 > b_ax) {
    i = 0;
  } else {
    i = (int)b_ax;
  }

  if (0 <= i - 1) {
    memset(&y[0], 0, (unsigned int)(i * (int)sizeof(double)));
  }

  b_ax = rt_roundd_snf(4.0 / dt * 10.0);
  if (1.0 > b_ax) {
    i = 0;
  } else {
    i = (int)b_ax;
  }

  if (0 <= i - 1) {
    memset(&z[0], 0, (unsigned int)(i * (int)sizeof(double)));
  }
}

/* End of code generation (IMUtoXYZ.cpp) */
