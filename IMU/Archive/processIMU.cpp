/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * processIMU.cpp
 *
 * Code generation for function 'processIMU'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "XYZwaves.h"
#include "IMUtoXYZ.h"
#include "mean.h"
#include "std.h"
#include "abs.h"
#include "detrend.h"
#include "processIMU_emxutil.h"

/* Function Declarations */
static void despike(double raw[2048]);

/* Function Definitions */
static void despike(double raw[2048])
{
  double raw_data[2048];
  double dv21[2048];
  double d11;
  int trueCount;
  int i;
  int partialTrueCount;
  boolean_T spikes;
  int b_trueCount;
  boolean_T b_spikes[2048];
  short tmp_data[2048];
  int raw_size[1];
  short b_tmp_data[2048];

  /*  EMBEDDED despike function */
  /*  find spikes greater than n standard deviations  */
  /*  and replace with mean */
  memcpy(&raw_data[0], &raw[0], sizeof(double) << 11);
  detrend(raw_data);
  b_abs(raw_data, dv21);
  d11 = 5.0 * b_std(raw);
  trueCount = 0;
  for (i = 0; i < 2048; i++) {
    spikes = (dv21[i] > d11);
    if (spikes) {
      trueCount++;
    }

    b_spikes[i] = spikes;
  }

  partialTrueCount = 0;
  b_trueCount = 0;
  for (i = 0; i < 2048; i++) {
    if (b_spikes[i]) {
      tmp_data[partialTrueCount] = (short)(i + 1);
      partialTrueCount++;
    }

    if (!b_spikes[i]) {
      b_trueCount++;
    }
  }

  partialTrueCount = 0;
  for (i = 0; i < 2048; i++) {
    if (!b_spikes[i]) {
      b_tmp_data[partialTrueCount] = (short)(i + 1);
      partialTrueCount++;
    }
  }

  raw_size[0] = b_trueCount;
  for (i = 0; i < b_trueCount; i++) {
    raw_data[i] = raw[b_tmp_data[i] - 1];
  }

  d11 = mean(raw_data, raw_size);
  for (i = 0; i < trueCount; i++) {
    raw[tmp_data[i] - 1] = d11;
  }
}

void processIMU(double ax[2048], double ay[2048], double az[2048], double gx
                [2048], double gy[2048], double gz[2048], double mx[2048],
                double my[2048], double mz[2048], double mxo, double myo, double,
                double Wd, double fs, double *Hs, double *Tp, double *Dp,
                emxArray_real_T *E, emxArray_real_T *f, emxArray_real_T *a1,
                emxArray_real_T *b1, emxArray_real_T *a2, emxArray_real_T *b2,
                emxArray_real_T *check)
{
  double b_Hs;
  double b_Tp;
  double b_Dp;
  int i0;
  static double b_ax[2048];
  static double b_ay[2048];
  static double b_az[2048];
  static double b_mx[2048];
  static double b_my[2048];
  static double b_mz[2048];
  static double x[2048];
  static double y[2048];
  static double z[2048];
  static double roll[2048];
  static double pitch[2048];
  static double yaw[2048];
  static double heading[2048];

  /*   */
  /*  Matlab function to process microSWIFT IMU measurements  */
  /*   */
  /*  Inputs are raw accelerometer, gyro, and magnotometer readings (3 axis each) */
  /*  along with magnetometer offsets (3), a weight coef for filtering the gyro,  */
  /*  and the sampling frequency of the raw data */
  /*  */
  /*    [ Hs, Tp, Dp, E, f, a1, b1, a2, b2, check ] = processIMU(ax, ay, az, gx, gy, gz, mx, my, mz, mxo, myo, mzo, Wd, fs ); */
  /*  */
  /*  Outputs are significat wave height [m], dominant period [s], dominant direction  */
  /*  [deg T, using meteorological from which waves are propagating], spectral  */
  /*  energy density [m^2/Hz], frequency [Hz], and  */
  /*  the normalized spectral moments a1, b1, a2, b2,  */
  /*  */
  /*  Outputs will be '9999' for invalid results. */
  /*  */
  /*  The input weight coef Wd must be between 0 and 1, with 0 as default  */
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
  /*  check data sizes */
  if ((2048.0 > fs * 256.0) && (fs > 1.0)) {
    /*  despike */
    despike(ax);
    despike(ay);
    despike(az);
    despike(gx);
    despike(gy);
    despike(gz);
    despike(mx);
    despike(my);
    despike(mz);

    /*  rotate, filter, and integrate to get wave displacements */
    memcpy(&b_ax[0], &ax[0], sizeof(double) << 11);
    memcpy(&b_ay[0], &ay[0], sizeof(double) << 11);
    memcpy(&b_az[0], &az[0], sizeof(double) << 11);
    memcpy(&b_mx[0], &mx[0], sizeof(double) << 11);
    memcpy(&b_my[0], &my[0], sizeof(double) << 11);
    memcpy(&b_mz[0], &mz[0], sizeof(double) << 11);
    IMUtoXYZ(b_ax, b_ay, b_az, gx, gy, gz, b_mx, b_my, b_mz, mxo, myo, Wd, fs, x,
             y, z, roll, pitch, yaw, heading);

    /* plot(z) */
    /*  wave calcs */
    XYZwaves(x, y, z, fs, &b_Hs, &b_Tp, &b_Dp, E, f, a1, b1, a2, b2, check);

    /*  error codes if not enough points or sufficent sampling rate or data, give 9999 */
  } else {
    b_Hs = 9999.0;
    b_Tp = 9999.0;
    b_Dp = 9999.0;
    i0 = E->size[0] * E->size[1];
    E->size[0] = 1;
    E->size[1] = 1;
    emxEnsureCapacity_real_T(E, i0);
    E->data[0] = 9999.0;
    i0 = f->size[0] * f->size[1];
    f->size[0] = 1;
    f->size[1] = 1;
    emxEnsureCapacity_real_T(f, i0);
    f->data[0] = 9999.0;
    i0 = a1->size[0] * a1->size[1];
    a1->size[0] = 1;
    a1->size[1] = 1;
    emxEnsureCapacity_real_T(a1, i0);
    a1->data[0] = 9999.0;
    i0 = b1->size[0] * b1->size[1];
    b1->size[0] = 1;
    b1->size[1] = 1;
    emxEnsureCapacity_real_T(b1, i0);
    b1->data[0] = 9999.0;
    i0 = a2->size[0] * a2->size[1];
    a2->size[0] = 1;
    a2->size[1] = 1;
    emxEnsureCapacity_real_T(a2, i0);
    a2->data[0] = 9999.0;
    i0 = b2->size[0] * b2->size[1];
    b2->size[0] = 1;
    b2->size[1] = 1;
    emxEnsureCapacity_real_T(b2, i0);
    b2->data[0] = 9999.0;
    i0 = check->size[0] * check->size[1];
    check->size[0] = 1;
    check->size[1] = 1;
    emxEnsureCapacity_real_T(check, i0);
    check->data[0] = 9999.0;
  }

  *Hs = b_Hs;
  *Tp = b_Tp;
  *Dp = b_Dp;
}

/* End of code generation (processIMU.cpp) */
