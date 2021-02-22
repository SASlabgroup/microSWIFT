/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * XYZwaves.cpp
 *
 * Code generation for function 'XYZwaves'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "XYZwaves.h"
#include "processIMU_emxutil.h"
#include "detrend.h"
#include "mean.h"
#include "nullAssignment.h"
#include "std.h"
#include "all.h"
#include "sqrt.h"
#include "sum.h"
#include "abs.h"
#include "cos.h"
#include "power.h"
#include "atan21.h"
#include "rdivide.h"
#include "fft.h"
#include "var.h"
#include "sin.h"
#include "processIMU_rtwutil.h"

/* Function Definitions */
void XYZwaves(const double x[2048], const double y[2048], const double z[2048],
              double fs, double *Hs, double *Tp, double *Dp, emxArray_real_T *E,
              emxArray_real_T *f, emxArray_real_T *a1, emxArray_real_T *b1,
              emxArray_real_T *a2, emxArray_real_T *b2, emxArray_real_T *check)
{
  double w;
  emxArray_real_T *xwindow;
  emxArray_real_T *ywindow;
  emxArray_real_T *zwindow;
  double windows;
  int i3;
  int n;
  emxArray_real_T *YY;
  double b_n;
  emxArray_real_T *XX;
  int loop_ub;
  int ixstart;
  emxArray_real_T *taper;
  emxArray_real_T *xwindowtaper;
  int b_loop_ub;
  int i4;
  emxArray_real_T *ywindowtaper;
  emxArray_real_T *r0;
  double factz_data[29];
  int factz_size[2];
  double tmp_data[29];
  int tmp_size[2];
  emxArray_real_T b_factz_data;
  emxArray_real_T b_tmp_data;
  double factx_data[29];
  emxArray_real_T c_factz_data;
  emxArray_real_T c_tmp_data;
  double facty_data[29];
  emxArray_real_T d_factz_data;
  emxArray_real_T d_tmp_data;
  emxArray_real_T *r1;
  emxArray_real_T *r2;
  emxArray_creal_T *Xwindow;
  emxArray_creal_T *Ywindow;
  emxArray_creal_T *Zwindow;
  emxArray_int32_T *b_w;
  emxArray_real_T *XXwindow;
  emxArray_real_T *YYwindow;
  double Xwindow_im;
  emxArray_real_T *ZZwindow;
  double Ywindow_re;
  double Ywindow_im;
  emxArray_creal_T *XYwindow;
  double Zwindow_re;
  double bandwidth;
  emxArray_creal_T *XZwindow;
  emxArray_creal_T *YZwindow;
  int mi;
  emxArray_creal_T *A;
  emxArray_creal_T *b_XYwindow;
  emxArray_real_T *b_XXwindow;
  int end;
  emxArray_real_T *b_xwindow;
  emxArray_real_T *b_YY;
  creal_T e_tmp_data[29];
  emxArray_real_T *ZZ;
  emxArray_creal_T *b_Xwindow;
  emxArray_creal_T *b_A;
  emxArray_real_T *spread1;
  emxArray_creal_T *c_A;
  emxArray_real_T *d_A;
  emxArray_real_T *r3;
  emxArray_boolean_T *eastdirs;
  emxArray_boolean_T *b_f;
  emxArray_int32_T *r4;
  boolean_T exitg1;
  emxArray_int32_T *r5;
  emxArray_int32_T *r6;
  emxArray_int32_T *r7;
  boolean_T inds[3];
  double b_inds[3];
  double c_YY[3];
  emxArray_real_T *d_YY;
  emxArray_real_T *c_f;

  /*  matlab function to read and process raw wave displacments */
  /*    to estimate wave height, period, direction, directional moments and */
  /*    check factor */
  /*  */
  /*  Inputs are displacements east [m], north [m], up [m], and sampling rate [Hz] */
  /*  */
  /*  For v3 SWIFTs, this assumes that post-processing of the IMU data using */
  /*  "rawdiplacements.m" has been completed. */
  /*  */
  /*  Sampling rate must be at least 1 Hz and the same */
  /*  for all variables.  Additionaly,  time series data must  */
  /*  have at least 512 points and all be the same size. */
  /*  */
  /*  Outputs are significat wave height [m], dominant period [s], dominant direction  */
  /*  [deg T, using meteorological from which waves are propagating], spectral  */
  /*  energy density [m^2/Hz], frequency [Hz], and  */
  /*  the normalized spectral moments a1, b1, a2, b2,  */
  /*  */
  /*  Outputs will be '9999' for invalid results. */
  /*  */
  /*  Outputs can be supressed, in order, full usage is as follows: */
  /*  */
  /*    [ Hs, Tp, Dp, E, f, a1, b1, a2, b2, check ] = XYZwaves(x,y,z,fs)  */
  /*  J. Thomson, Jun 2016, adapted from GPSandIMUwaves.m */
  /*  */
  /*  fixed parameters */
  /*  window length in seconds, should make 2^N samples */
  /*  freq bands to merge, must be odd? */
  /*  frequency cutoff for telemetry Hz */
  /*  begin processing, if data sufficient */
  /*  record length in data points */
  /*  minimum length and quality for processing */
  /*  break into windows (use 75 percent overlap) */
  w = rt_roundd_snf(fs * 256.0);

  /*  window length in data points */
  if (rt_remd_snf(w, 2.0) != 0.0) {
    w--;
  }

  emxInit_real_T(&xwindow, 2);
  emxInit_real_T(&ywindow, 2);
  emxInit_real_T(&zwindow, 2);

  /*  make w an even number */
  windows = std::floor(4.0 * (2048.0 / w - 1.0) + 1.0);

  /*  number of windows, the 4 comes from a 75% overlap */
  /*  degrees of freedom */
  /*  loop to create a matrix of time series, where COLUMN = WINDOW  */
  i3 = xwindow->size[0] * xwindow->size[1];
  xwindow->size[0] = (int)w;
  xwindow->size[1] = (int)windows;
  emxEnsureCapacity_real_T(xwindow, i3);
  i3 = ywindow->size[0] * ywindow->size[1];
  ywindow->size[0] = (int)w;
  ywindow->size[1] = (int)windows;
  emxEnsureCapacity_real_T(ywindow, i3);
  i3 = zwindow->size[0] * zwindow->size[1];
  zwindow->size[0] = (int)w;
  zwindow->size[1] = (int)windows;
  emxEnsureCapacity_real_T(zwindow, i3);
  n = 0;
  emxInit_real_T1(&YY, 1);
  while (n <= (int)windows - 1) {
    b_n = ((1.0 + (double)n) - 1.0) * (0.25 * w);
    i3 = YY->size[0];
    YY->size[0] = (int)(w - 1.0) + 1;
    emxEnsureCapacity_real_T1(YY, i3);
    loop_ub = (int)(w - 1.0);
    for (i3 = 0; i3 <= loop_ub; i3++) {
      YY->data[i3] = x[(int)(b_n + (double)(i3 + 1)) - 1];
    }

    loop_ub = YY->size[0];
    for (i3 = 0; i3 < loop_ub; i3++) {
      xwindow->data[i3 + xwindow->size[0] * n] = YY->data[i3];
    }

    b_n = ((1.0 + (double)n) - 1.0) * (0.25 * w);
    i3 = YY->size[0];
    YY->size[0] = (int)(w - 1.0) + 1;
    emxEnsureCapacity_real_T1(YY, i3);
    loop_ub = (int)(w - 1.0);
    for (i3 = 0; i3 <= loop_ub; i3++) {
      YY->data[i3] = y[(int)(b_n + (double)(i3 + 1)) - 1];
    }

    loop_ub = YY->size[0];
    for (i3 = 0; i3 < loop_ub; i3++) {
      ywindow->data[i3 + ywindow->size[0] * n] = YY->data[i3];
    }

    b_n = ((1.0 + (double)n) - 1.0) * (0.25 * w);
    i3 = YY->size[0];
    YY->size[0] = (int)(w - 1.0) + 1;
    emxEnsureCapacity_real_T1(YY, i3);
    loop_ub = (int)(w - 1.0);
    for (i3 = 0; i3 <= loop_ub; i3++) {
      YY->data[i3] = z[(int)(b_n + (double)(i3 + 1)) - 1];
    }

    loop_ub = YY->size[0];
    for (i3 = 0; i3 < loop_ub; i3++) {
      zwindow->data[i3 + zwindow->size[0] * n] = YY->data[i3];
    }

    n++;
  }

  /*  detrend individual windows (full series already detrended) */
  for (n = 0; n < (int)windows; n++) {
    loop_ub = xwindow->size[0];
    i3 = YY->size[0];
    YY->size[0] = loop_ub;
    emxEnsureCapacity_real_T1(YY, i3);
    for (i3 = 0; i3 < loop_ub; i3++) {
      YY->data[i3] = xwindow->data[i3 + xwindow->size[0] * n];
    }

    b_detrend(YY);
    loop_ub = YY->size[0];
    for (i3 = 0; i3 < loop_ub; i3++) {
      xwindow->data[i3 + xwindow->size[0] * n] = YY->data[i3];
    }

    loop_ub = ywindow->size[0];
    i3 = YY->size[0];
    YY->size[0] = loop_ub;
    emxEnsureCapacity_real_T1(YY, i3);
    for (i3 = 0; i3 < loop_ub; i3++) {
      YY->data[i3] = ywindow->data[i3 + ywindow->size[0] * n];
    }

    b_detrend(YY);
    loop_ub = YY->size[0];
    for (i3 = 0; i3 < loop_ub; i3++) {
      ywindow->data[i3 + ywindow->size[0] * n] = YY->data[i3];
    }

    loop_ub = zwindow->size[0];
    i3 = YY->size[0];
    YY->size[0] = loop_ub;
    emxEnsureCapacity_real_T1(YY, i3);
    for (i3 = 0; i3 < loop_ub; i3++) {
      YY->data[i3] = zwindow->data[i3 + zwindow->size[0] * n];
    }

    b_detrend(YY);
    loop_ub = YY->size[0];
    for (i3 = 0; i3 < loop_ub; i3++) {
      zwindow->data[i3 + zwindow->size[0] * n] = YY->data[i3];
    }
  }

  emxInit_real_T(&XX, 2);

  /*  taper and rescale (to preserve variance) */
  /*  form taper matrix (columns of taper coef) */
  i3 = XX->size[0] * XX->size[1];
  XX->size[0] = 1;
  XX->size[1] = (int)(w - 1.0) + 1;
  emxEnsureCapacity_real_T(XX, i3);
  loop_ub = (int)(w - 1.0);
  for (i3 = 0; i3 <= loop_ub; i3++) {
    XX->data[XX->size[0] * i3] = 1.0 + (double)i3;
  }

  i3 = XX->size[0] * XX->size[1];
  XX->size[0] = 1;
  emxEnsureCapacity_real_T(XX, i3);
  n = XX->size[0];
  ixstart = XX->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    XX->data[i3] = XX->data[i3] * 3.1415926535897931 / w;
  }

  emxInit_real_T(&taper, 2);
  b_sin(XX);
  i3 = taper->size[0] * taper->size[1];
  taper->size[0] = XX->size[1];
  taper->size[1] = (int)windows;
  emxEnsureCapacity_real_T(taper, i3);
  loop_ub = XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = (int)windows;
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      taper->data[i3 + taper->size[0] * i4] = XX->data[XX->size[0] * i3];
    }
  }

  emxInit_real_T(&xwindowtaper, 2);

  /*  taper each window */
  i3 = xwindowtaper->size[0] * xwindowtaper->size[1];
  xwindowtaper->size[0] = xwindow->size[0];
  xwindowtaper->size[1] = xwindow->size[1];
  emxEnsureCapacity_real_T(xwindowtaper, i3);
  loop_ub = xwindow->size[0] * xwindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    xwindowtaper->data[i3] = xwindow->data[i3] * taper->data[i3];
  }

  emxInit_real_T(&ywindowtaper, 2);
  i3 = ywindowtaper->size[0] * ywindowtaper->size[1];
  ywindowtaper->size[0] = ywindow->size[0];
  ywindowtaper->size[1] = ywindow->size[1];
  emxEnsureCapacity_real_T(ywindowtaper, i3);
  loop_ub = ywindow->size[0] * ywindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    ywindowtaper->data[i3] = ywindow->data[i3] * taper->data[i3];
  }

  i3 = taper->size[0] * taper->size[1];
  taper->size[0] = zwindow->size[0];
  taper->size[1] = zwindow->size[1];
  emxEnsureCapacity_real_T(taper, i3);
  loop_ub = zwindow->size[0] * zwindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    taper->data[i3] *= zwindow->data[i3];
  }

  emxInit_real_T(&r0, 2);

  /*  now find the correction factor (comparing old/new variance) */
  var(xwindow, factz_data, factz_size);
  var(xwindowtaper, tmp_data, tmp_size);
  b_factz_data.data = (double *)&factz_data;
  b_factz_data.size = (int *)&factz_size;
  b_factz_data.allocatedSize = 29;
  b_factz_data.numDimensions = 2;
  b_factz_data.canFreeData = false;
  b_tmp_data.data = (double *)&tmp_data;
  b_tmp_data.size = (int *)&tmp_size;
  b_tmp_data.allocatedSize = 29;
  b_tmp_data.numDimensions = 2;
  b_tmp_data.canFreeData = false;
  rdivide(&b_factz_data, &b_tmp_data, r0);
  f_sqrt(r0);
  ixstart = r0->size[1];
  loop_ub = r0->size[0] * r0->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    factx_data[i3] = r0->data[i3];
  }

  var(ywindow, factz_data, factz_size);
  var(ywindowtaper, tmp_data, tmp_size);
  c_factz_data.data = (double *)&factz_data;
  c_factz_data.size = (int *)&factz_size;
  c_factz_data.allocatedSize = 29;
  c_factz_data.numDimensions = 2;
  c_factz_data.canFreeData = false;
  c_tmp_data.data = (double *)&tmp_data;
  c_tmp_data.size = (int *)&tmp_size;
  c_tmp_data.allocatedSize = 29;
  c_tmp_data.numDimensions = 2;
  c_tmp_data.canFreeData = false;
  rdivide(&c_factz_data, &c_tmp_data, r0);
  f_sqrt(r0);
  n = r0->size[1];
  loop_ub = r0->size[0] * r0->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    facty_data[i3] = r0->data[i3];
  }

  var(zwindow, factz_data, factz_size);
  var(taper, tmp_data, tmp_size);
  d_factz_data.data = (double *)&factz_data;
  d_factz_data.size = (int *)&factz_size;
  d_factz_data.allocatedSize = 29;
  d_factz_data.numDimensions = 2;
  d_factz_data.canFreeData = false;
  d_tmp_data.data = (double *)&tmp_data;
  d_tmp_data.size = (int *)&tmp_size;
  d_tmp_data.allocatedSize = 29;
  d_tmp_data.numDimensions = 2;
  d_tmp_data.canFreeData = false;
  rdivide(&d_factz_data, &d_tmp_data, r0);
  f_sqrt(r0);
  factz_size[0] = 1;
  factz_size[1] = r0->size[1];
  loop_ub = r0->size[0] * r0->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    factz_data[i3] = r0->data[i3];
  }

  emxInit_real_T(&r1, 2);
  emxInit_real_T(&r2, 2);

  /*  and correct for the change in variance */
  /*  (mult each window by it's variance ratio factor) */
  /*  FFT */
  /*  calculate Fourier coefs */
  i3 = r2->size[0] * r2->size[1];
  r2->size[0] = (int)w;
  r2->size[1] = ixstart;
  emxEnsureCapacity_real_T(r2, i3);
  loop_ub = (int)w;
  for (i3 = 0; i3 < loop_ub; i3++) {
    for (i4 = 0; i4 < ixstart; i4++) {
      r2->data[i3 + r2->size[0] * i4] = factx_data[i4];
    }
  }

  i3 = r1->size[0] * r1->size[1];
  r1->size[0] = r2->size[0];
  r1->size[1] = r2->size[1];
  emxEnsureCapacity_real_T(r1, i3);
  loop_ub = r2->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = r2->size[0];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      r1->data[i4 + r1->size[0] * i3] = r2->data[i4 + r2->size[0] * i3] *
        xwindowtaper->data[i4 + xwindowtaper->size[0] * i3];
    }
  }

  emxFree_real_T(&xwindowtaper);
  emxInit_creal_T(&Xwindow, 2);
  fft(r1, Xwindow);
  i3 = r2->size[0] * r2->size[1];
  r2->size[0] = (int)w;
  r2->size[1] = n;
  emxEnsureCapacity_real_T(r2, i3);
  loop_ub = (int)w;
  for (i3 = 0; i3 < loop_ub; i3++) {
    for (i4 = 0; i4 < n; i4++) {
      r2->data[i3 + r2->size[0] * i4] = facty_data[i4];
    }
  }

  i3 = r1->size[0] * r1->size[1];
  r1->size[0] = r2->size[0];
  r1->size[1] = r2->size[1];
  emxEnsureCapacity_real_T(r1, i3);
  loop_ub = r2->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = r2->size[0];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      r1->data[i4 + r1->size[0] * i3] = r2->data[i4 + r2->size[0] * i3] *
        ywindowtaper->data[i4 + ywindowtaper->size[0] * i3];
    }
  }

  emxFree_real_T(&ywindowtaper);
  emxInit_creal_T(&Ywindow, 2);
  fft(r1, Ywindow);
  i3 = r2->size[0] * r2->size[1];
  r2->size[0] = (int)w;
  r2->size[1] = factz_size[1];
  emxEnsureCapacity_real_T(r2, i3);
  loop_ub = (int)w;
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = factz_size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      r2->data[i3 + r2->size[0] * i4] = factz_data[factz_size[0] * i4];
    }
  }

  i3 = r1->size[0] * r1->size[1];
  r1->size[0] = r2->size[0];
  r1->size[1] = r2->size[1];
  emxEnsureCapacity_real_T(r1, i3);
  loop_ub = r2->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = r2->size[0];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      r1->data[i4 + r1->size[0] * i3] = r2->data[i4 + r2->size[0] * i3] *
        taper->data[i4 + taper->size[0] * i3];
    }
  }

  emxFree_real_T(&r2);
  emxFree_real_T(&taper);
  emxInit_creal_T(&Zwindow, 2);
  emxInit_int32_T(&b_w, 2);
  fft(r1, Zwindow);

  /*  second half of fft is redundant, so throw it out */
  b_n = w / 2.0 + 1.0;
  i3 = b_w->size[0] * b_w->size[1];
  b_w->size[0] = 1;
  b_w->size[1] = (int)std::floor(w - b_n) + 1;
  emxEnsureCapacity_int32_T(b_w, i3);
  loop_ub = (int)std::floor(w - b_n);
  emxFree_real_T(&r1);
  for (i3 = 0; i3 <= loop_ub; i3++) {
    b_w->data[b_w->size[0] * i3] = (int)(b_n + (double)i3);
  }

  b_nullAssignment(Xwindow, b_w);
  b_n = w / 2.0 + 1.0;
  i3 = b_w->size[0] * b_w->size[1];
  b_w->size[0] = 1;
  b_w->size[1] = (int)std::floor(w - b_n) + 1;
  emxEnsureCapacity_int32_T(b_w, i3);
  loop_ub = (int)std::floor(w - b_n);
  for (i3 = 0; i3 <= loop_ub; i3++) {
    b_w->data[b_w->size[0] * i3] = (int)(b_n + (double)i3);
  }

  b_nullAssignment(Ywindow, b_w);
  b_n = w / 2.0 + 1.0;
  i3 = b_w->size[0] * b_w->size[1];
  b_w->size[0] = 1;
  b_w->size[1] = (int)std::floor(w - b_n) + 1;
  emxEnsureCapacity_int32_T(b_w, i3);
  loop_ub = (int)std::floor(w - b_n);
  for (i3 = 0; i3 <= loop_ub; i3++) {
    b_w->data[b_w->size[0] * i3] = (int)(b_n + (double)i3);
  }

  b_nullAssignment(Zwindow, b_w);

  /*  throw out the mean (first coef) and add a zero (to make it the right length)   */
  c_nullAssignment(Xwindow);
  c_nullAssignment(Ywindow);
  c_nullAssignment(Zwindow);
  loop_ub = Xwindow->size[1];
  ixstart = (int)(w / 2.0);
  emxFree_int32_T(&b_w);
  for (i3 = 0; i3 < loop_ub; i3++) {
    Xwindow->data[(ixstart + Xwindow->size[0] * i3) - 1].re = 0.0;
    Xwindow->data[(ixstart + Xwindow->size[0] * i3) - 1].im = 0.0;
  }

  loop_ub = Ywindow->size[1];
  ixstart = (int)(w / 2.0);
  for (i3 = 0; i3 < loop_ub; i3++) {
    Ywindow->data[(ixstart + Ywindow->size[0] * i3) - 1].re = 0.0;
    Ywindow->data[(ixstart + Ywindow->size[0] * i3) - 1].im = 0.0;
  }

  loop_ub = Zwindow->size[1];
  ixstart = (int)(w / 2.0);
  for (i3 = 0; i3 < loop_ub; i3++) {
    Zwindow->data[(ixstart + Zwindow->size[0] * i3) - 1].re = 0.0;
    Zwindow->data[(ixstart + Zwindow->size[0] * i3) - 1].im = 0.0;
  }

  emxInit_real_T(&XXwindow, 2);

  /*  POWER SPECTRA (auto-spectra) */
  i3 = XXwindow->size[0] * XXwindow->size[1];
  XXwindow->size[0] = Xwindow->size[0];
  XXwindow->size[1] = Xwindow->size[1];
  emxEnsureCapacity_real_T(XXwindow, i3);
  loop_ub = Xwindow->size[0] * Xwindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_n = Xwindow->data[i3].re;
    Xwindow_im = -Xwindow->data[i3].im;
    b_n = Xwindow->data[i3].re * b_n - Xwindow->data[i3].im * Xwindow_im;
    XXwindow->data[i3] = b_n;
  }

  emxInit_real_T(&YYwindow, 2);
  i3 = YYwindow->size[0] * YYwindow->size[1];
  YYwindow->size[0] = Ywindow->size[0];
  YYwindow->size[1] = Ywindow->size[1];
  emxEnsureCapacity_real_T(YYwindow, i3);
  loop_ub = Ywindow->size[0] * Ywindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Ywindow_re = Ywindow->data[i3].re;
    Ywindow_im = -Ywindow->data[i3].im;
    Ywindow_re = Ywindow->data[i3].re * Ywindow_re - Ywindow->data[i3].im *
      Ywindow_im;
    YYwindow->data[i3] = Ywindow_re;
  }

  emxInit_real_T(&ZZwindow, 2);
  i3 = ZZwindow->size[0] * ZZwindow->size[1];
  ZZwindow->size[0] = Zwindow->size[0];
  ZZwindow->size[1] = Zwindow->size[1];
  emxEnsureCapacity_real_T(ZZwindow, i3);
  loop_ub = Zwindow->size[0] * Zwindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Zwindow_re = Zwindow->data[i3].re;
    bandwidth = -Zwindow->data[i3].im;
    Zwindow_re = Zwindow->data[i3].re * Zwindow_re - Zwindow->data[i3].im *
      bandwidth;
    ZZwindow->data[i3] = Zwindow_re;
  }

  emxInit_creal_T(&XYwindow, 2);

  /*  CROSS-SPECTRA  */
  i3 = XYwindow->size[0] * XYwindow->size[1];
  XYwindow->size[0] = Xwindow->size[0];
  XYwindow->size[1] = Xwindow->size[1];
  emxEnsureCapacity_creal_T(XYwindow, i3);
  loop_ub = Xwindow->size[0] * Xwindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Ywindow_re = Ywindow->data[i3].re;
    Ywindow_im = -Ywindow->data[i3].im;
    b_n = Xwindow->data[i3].re;
    Xwindow_im = Xwindow->data[i3].im;
    XYwindow->data[i3].re = b_n * Ywindow_re - Xwindow_im * Ywindow_im;
    XYwindow->data[i3].im = b_n * Ywindow_im + Xwindow_im * Ywindow_re;
  }

  emxInit_creal_T(&XZwindow, 2);
  i3 = XZwindow->size[0] * XZwindow->size[1];
  XZwindow->size[0] = Xwindow->size[0];
  XZwindow->size[1] = Xwindow->size[1];
  emxEnsureCapacity_creal_T(XZwindow, i3);
  loop_ub = Xwindow->size[0] * Xwindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Zwindow_re = Zwindow->data[i3].re;
    bandwidth = -Zwindow->data[i3].im;
    b_n = Xwindow->data[i3].re;
    Xwindow_im = Xwindow->data[i3].im;
    XZwindow->data[i3].re = b_n * Zwindow_re - Xwindow_im * bandwidth;
    XZwindow->data[i3].im = b_n * bandwidth + Xwindow_im * Zwindow_re;
  }

  emxInit_creal_T(&YZwindow, 2);
  i3 = YZwindow->size[0] * YZwindow->size[1];
  YZwindow->size[0] = Ywindow->size[0];
  YZwindow->size[1] = Ywindow->size[1];
  emxEnsureCapacity_creal_T(YZwindow, i3);
  loop_ub = Ywindow->size[0] * Ywindow->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Zwindow_re = Zwindow->data[i3].re;
    bandwidth = -Zwindow->data[i3].im;
    Ywindow_re = Ywindow->data[i3].re;
    Ywindow_im = Ywindow->data[i3].im;
    YZwindow->data[i3].re = Ywindow_re * Zwindow_re - Ywindow_im * bandwidth;
    YZwindow->data[i3].im = Ywindow_re * bandwidth + Ywindow_im * Zwindow_re;
  }

  /*  merge neighboring freq bands (number of bands to merge is a fixed parameter) */
  /*  initialize */
  b_n = std::floor(w / 6.0);
  i3 = xwindow->size[0] * xwindow->size[1];
  xwindow->size[0] = (int)b_n;
  xwindow->size[1] = (int)windows;
  emxEnsureCapacity_real_T(xwindow, i3);
  loop_ub = (int)b_n * (int)windows;
  for (i3 = 0; i3 < loop_ub; i3++) {
    xwindow->data[i3] = 0.0;
  }

  b_n = std::floor(w / 6.0);
  i3 = ywindow->size[0] * ywindow->size[1];
  ywindow->size[0] = (int)b_n;
  ywindow->size[1] = (int)windows;
  emxEnsureCapacity_real_T(ywindow, i3);
  loop_ub = (int)b_n * (int)windows;
  for (i3 = 0; i3 < loop_ub; i3++) {
    ywindow->data[i3] = 0.0;
  }

  b_n = std::floor(w / 6.0);
  i3 = zwindow->size[0] * zwindow->size[1];
  zwindow->size[0] = (int)b_n;
  zwindow->size[1] = (int)windows;
  emxEnsureCapacity_real_T(zwindow, i3);
  loop_ub = (int)b_n * (int)windows;
  for (i3 = 0; i3 < loop_ub; i3++) {
    zwindow->data[i3] = 0.0;
  }

  b_n = std::floor(w / 6.0);
  i3 = Xwindow->size[0] * Xwindow->size[1];
  Xwindow->size[0] = (int)b_n;
  Xwindow->size[1] = (int)windows;
  emxEnsureCapacity_creal_T(Xwindow, i3);
  loop_ub = (int)b_n * (int)windows;
  for (i3 = 0; i3 < loop_ub; i3++) {
    Xwindow->data[i3].re = 0.0;
    Xwindow->data[i3].im = 1.0;
  }

  b_n = std::floor(w / 6.0);
  i3 = Ywindow->size[0] * Ywindow->size[1];
  Ywindow->size[0] = (int)b_n;
  Ywindow->size[1] = (int)windows;
  emxEnsureCapacity_creal_T(Ywindow, i3);
  loop_ub = (int)b_n * (int)windows;
  for (i3 = 0; i3 < loop_ub; i3++) {
    Ywindow->data[i3].re = 0.0;
    Ywindow->data[i3].im = 1.0;
  }

  b_n = std::floor(w / 6.0);
  i3 = Zwindow->size[0] * Zwindow->size[1];
  Zwindow->size[0] = (int)b_n;
  Zwindow->size[1] = (int)windows;
  emxEnsureCapacity_creal_T(Zwindow, i3);
  loop_ub = (int)b_n * (int)windows;
  for (i3 = 0; i3 < loop_ub; i3++) {
    Zwindow->data[i3].re = 0.0;
    Zwindow->data[i3].im = 1.0;
  }

  i3 = (int)(w / 2.0 / 3.0);
  mi = 0;
  emxInit_creal_T(&A, 2);
  emxInit_creal_T(&b_XYwindow, 2);
  emxInit_real_T(&b_XXwindow, 2);
  while (mi <= i3 - 1) {
    b_n = 3.0 + (double)mi * 3.0;
    if ((b_n - 3.0) + 1.0 > b_n) {
      i4 = 0;
      ixstart = 0;
    } else {
      i4 = (int)((b_n - 3.0) + 1.0) - 1;
      ixstart = (int)b_n;
    }

    loop_ub = XXwindow->size[1];
    n = b_XXwindow->size[0] * b_XXwindow->size[1];
    b_XXwindow->size[0] = ixstart - i4;
    b_XXwindow->size[1] = loop_ub;
    emxEnsureCapacity_real_T(b_XXwindow, n);
    for (n = 0; n < loop_ub; n++) {
      b_loop_ub = ixstart - i4;
      for (end = 0; end < b_loop_ub; end++) {
        b_XXwindow->data[end + b_XXwindow->size[0] * n] = XXwindow->data[(i4 +
          end) + XXwindow->size[0] * n];
      }
    }

    c_mean(b_XXwindow, r0);
    factz_size[0] = 1;
    factz_size[1] = r0->size[1];
    loop_ub = r0->size[0] * r0->size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      factz_data[i4] = r0->data[i4];
    }

    ixstart = (int)(b_n / 3.0);
    loop_ub = factz_size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      xwindow->data[(ixstart + xwindow->size[0] * i4) - 1] =
        factz_data[factz_size[0] * i4];
    }

    if ((b_n - 3.0) + 1.0 > b_n) {
      i4 = 0;
      ixstart = 0;
    } else {
      i4 = (int)((b_n - 3.0) + 1.0) - 1;
      ixstart = (int)b_n;
    }

    loop_ub = YYwindow->size[1];
    n = b_XXwindow->size[0] * b_XXwindow->size[1];
    b_XXwindow->size[0] = ixstart - i4;
    b_XXwindow->size[1] = loop_ub;
    emxEnsureCapacity_real_T(b_XXwindow, n);
    for (n = 0; n < loop_ub; n++) {
      b_loop_ub = ixstart - i4;
      for (end = 0; end < b_loop_ub; end++) {
        b_XXwindow->data[end + b_XXwindow->size[0] * n] = YYwindow->data[(i4 +
          end) + YYwindow->size[0] * n];
      }
    }

    c_mean(b_XXwindow, r0);
    factz_size[0] = 1;
    factz_size[1] = r0->size[1];
    loop_ub = r0->size[0] * r0->size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      factz_data[i4] = r0->data[i4];
    }

    ixstart = (int)(b_n / 3.0);
    loop_ub = factz_size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      ywindow->data[(ixstart + ywindow->size[0] * i4) - 1] =
        factz_data[factz_size[0] * i4];
    }

    if ((b_n - 3.0) + 1.0 > b_n) {
      i4 = 0;
      ixstart = 0;
    } else {
      i4 = (int)((b_n - 3.0) + 1.0) - 1;
      ixstart = (int)b_n;
    }

    loop_ub = ZZwindow->size[1];
    n = b_XXwindow->size[0] * b_XXwindow->size[1];
    b_XXwindow->size[0] = ixstart - i4;
    b_XXwindow->size[1] = loop_ub;
    emxEnsureCapacity_real_T(b_XXwindow, n);
    for (n = 0; n < loop_ub; n++) {
      b_loop_ub = ixstart - i4;
      for (end = 0; end < b_loop_ub; end++) {
        b_XXwindow->data[end + b_XXwindow->size[0] * n] = ZZwindow->data[(i4 +
          end) + ZZwindow->size[0] * n];
      }
    }

    c_mean(b_XXwindow, r0);
    factz_size[0] = 1;
    factz_size[1] = r0->size[1];
    loop_ub = r0->size[0] * r0->size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      factz_data[i4] = r0->data[i4];
    }

    ixstart = (int)(b_n / 3.0);
    loop_ub = factz_size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      zwindow->data[(ixstart + zwindow->size[0] * i4) - 1] =
        factz_data[factz_size[0] * i4];
    }

    if ((b_n - 3.0) + 1.0 > b_n) {
      i4 = 0;
      ixstart = 0;
    } else {
      i4 = (int)((b_n - 3.0) + 1.0) - 1;
      ixstart = (int)b_n;
    }

    loop_ub = XYwindow->size[1];
    n = b_XYwindow->size[0] * b_XYwindow->size[1];
    b_XYwindow->size[0] = ixstart - i4;
    b_XYwindow->size[1] = loop_ub;
    emxEnsureCapacity_creal_T(b_XYwindow, n);
    for (n = 0; n < loop_ub; n++) {
      b_loop_ub = ixstart - i4;
      for (end = 0; end < b_loop_ub; end++) {
        b_XYwindow->data[end + b_XYwindow->size[0] * n] = XYwindow->data[(i4 +
          end) + XYwindow->size[0] * n];
      }
    }

    d_mean(b_XYwindow, A);
    n = A->size[1];
    loop_ub = A->size[0] * A->size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      e_tmp_data[i4] = A->data[i4];
    }

    ixstart = (int)(b_n / 3.0);
    for (i4 = 0; i4 < n; i4++) {
      Xwindow->data[(ixstart + Xwindow->size[0] * i4) - 1] = e_tmp_data[i4];
    }

    if ((b_n - 3.0) + 1.0 > b_n) {
      i4 = 0;
      ixstart = 0;
    } else {
      i4 = (int)((b_n - 3.0) + 1.0) - 1;
      ixstart = (int)b_n;
    }

    loop_ub = XZwindow->size[1];
    n = b_XYwindow->size[0] * b_XYwindow->size[1];
    b_XYwindow->size[0] = ixstart - i4;
    b_XYwindow->size[1] = loop_ub;
    emxEnsureCapacity_creal_T(b_XYwindow, n);
    for (n = 0; n < loop_ub; n++) {
      b_loop_ub = ixstart - i4;
      for (end = 0; end < b_loop_ub; end++) {
        b_XYwindow->data[end + b_XYwindow->size[0] * n] = XZwindow->data[(i4 +
          end) + XZwindow->size[0] * n];
      }
    }

    d_mean(b_XYwindow, A);
    n = A->size[1];
    loop_ub = A->size[0] * A->size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      e_tmp_data[i4] = A->data[i4];
    }

    ixstart = (int)(b_n / 3.0);
    for (i4 = 0; i4 < n; i4++) {
      Ywindow->data[(ixstart + Ywindow->size[0] * i4) - 1] = e_tmp_data[i4];
    }

    if ((b_n - 3.0) + 1.0 > b_n) {
      i4 = 0;
      ixstart = 0;
    } else {
      i4 = (int)((b_n - 3.0) + 1.0) - 1;
      ixstart = (int)b_n;
    }

    loop_ub = YZwindow->size[1];
    n = b_XYwindow->size[0] * b_XYwindow->size[1];
    b_XYwindow->size[0] = ixstart - i4;
    b_XYwindow->size[1] = loop_ub;
    emxEnsureCapacity_creal_T(b_XYwindow, n);
    for (n = 0; n < loop_ub; n++) {
      b_loop_ub = ixstart - i4;
      for (end = 0; end < b_loop_ub; end++) {
        b_XYwindow->data[end + b_XYwindow->size[0] * n] = YZwindow->data[(i4 +
          end) + YZwindow->size[0] * n];
      }
    }

    d_mean(b_XYwindow, A);
    n = A->size[1];
    loop_ub = A->size[0] * A->size[1];
    for (i4 = 0; i4 < loop_ub; i4++) {
      e_tmp_data[i4] = A->data[i4];
    }

    ixstart = (int)(b_n / 3.0);
    for (i4 = 0; i4 < n; i4++) {
      Zwindow->data[(ixstart + Zwindow->size[0] * i4) - 1] = e_tmp_data[i4];
    }

    mi++;
  }

  emxFree_real_T(&b_XXwindow);
  emxFree_creal_T(&b_XYwindow);
  emxFree_creal_T(&YZwindow);
  emxFree_creal_T(&XZwindow);
  emxFree_creal_T(&XYwindow);
  emxFree_real_T(&ZZwindow);
  emxFree_real_T(&YYwindow);
  emxFree_real_T(&XXwindow);

  /*  freq range and bandwidth */
  b_n = w / 2.0 / 3.0;

  /*  number of f bands */
  /*  highest spectral frequency  */
  bandwidth = 0.5 * fs / b_n;

  /*  freq (Hz) bandwitdh */
  /*  find middle of each freq band, ONLY WORKS WHEN MERGING ODD NUMBER OF BANDS! */
  Xwindow_im = bandwidth / 2.0;
  i3 = f->size[0] * f->size[1];
  f->size[0] = 1;
  f->size[1] = (int)std::floor(b_n - 1.0) + 1;
  emxEnsureCapacity_real_T(f, i3);
  loop_ub = (int)std::floor(b_n - 1.0);
  for (i3 = 0; i3 <= loop_ub; i3++) {
    f->data[f->size[0] * i3] = i3;
  }

  i3 = f->size[0] * f->size[1];
  f->size[0] = 1;
  emxEnsureCapacity_real_T(f, i3);
  n = f->size[0];
  ixstart = f->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    f->data[i3] = (0.00390625 + Xwindow_im) + bandwidth * f->data[i3];
  }

  emxInit_real_T(&b_xwindow, 2);

  /*  ensemble average windows together */
  /*  take the average of all windows at each freq-band */
  /*  and divide by N*samplerate to get power spectral density */
  /*  the two is b/c Matlab's fft output is the symmetric FFT, and we did not use the redundant half (so need to multiply the psd by 2) */
  i3 = b_xwindow->size[0] * b_xwindow->size[1];
  b_xwindow->size[0] = xwindow->size[1];
  b_xwindow->size[1] = xwindow->size[0];
  emxEnsureCapacity_real_T(b_xwindow, i3);
  loop_ub = xwindow->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = xwindow->size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      b_xwindow->data[i4 + b_xwindow->size[0] * i3] = xwindow->data[i3 +
        xwindow->size[0] * i4];
    }
  }

  emxFree_real_T(&xwindow);
  c_mean(b_xwindow, XX);
  Zwindow_re = w / 2.0 * fs;
  i3 = XX->size[0] * XX->size[1];
  XX->size[0] = 1;
  emxEnsureCapacity_real_T(XX, i3);
  n = XX->size[0];
  ixstart = XX->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    XX->data[i3] /= Zwindow_re;
  }

  i3 = b_xwindow->size[0] * b_xwindow->size[1];
  b_xwindow->size[0] = ywindow->size[1];
  b_xwindow->size[1] = ywindow->size[0];
  emxEnsureCapacity_real_T(b_xwindow, i3);
  loop_ub = ywindow->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = ywindow->size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      b_xwindow->data[i4 + b_xwindow->size[0] * i3] = ywindow->data[i3 +
        ywindow->size[0] * i4];
    }
  }

  emxFree_real_T(&ywindow);
  emxInit_real_T(&b_YY, 2);
  c_mean(b_xwindow, b_YY);
  Zwindow_re = w / 2.0 * fs;
  i3 = b_YY->size[0] * b_YY->size[1];
  b_YY->size[0] = 1;
  emxEnsureCapacity_real_T(b_YY, i3);
  ixstart = b_YY->size[0];
  n = b_YY->size[1];
  loop_ub = ixstart * n;
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_YY->data[i3] /= Zwindow_re;
  }

  i3 = b_xwindow->size[0] * b_xwindow->size[1];
  b_xwindow->size[0] = zwindow->size[1];
  b_xwindow->size[1] = zwindow->size[0];
  emxEnsureCapacity_real_T(b_xwindow, i3);
  loop_ub = zwindow->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = zwindow->size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      b_xwindow->data[i4 + b_xwindow->size[0] * i3] = zwindow->data[i3 +
        zwindow->size[0] * i4];
    }
  }

  emxFree_real_T(&zwindow);
  emxInit_real_T(&ZZ, 2);
  c_mean(b_xwindow, ZZ);
  Zwindow_re = w / 2.0 * fs;
  i3 = ZZ->size[0] * ZZ->size[1];
  ZZ->size[0] = 1;
  emxEnsureCapacity_real_T(ZZ, i3);
  n = ZZ->size[0];
  ixstart = ZZ->size[1];
  loop_ub = n * ixstart;
  emxFree_real_T(&b_xwindow);
  for (i3 = 0; i3 < loop_ub; i3++) {
    ZZ->data[i3] /= Zwindow_re;
  }

  emxInit_creal_T(&b_Xwindow, 2);
  i3 = b_Xwindow->size[0] * b_Xwindow->size[1];
  b_Xwindow->size[0] = Xwindow->size[1];
  b_Xwindow->size[1] = Xwindow->size[0];
  emxEnsureCapacity_creal_T(b_Xwindow, i3);
  loop_ub = Xwindow->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = Xwindow->size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      b_Xwindow->data[i4 + b_Xwindow->size[0] * i3] = Xwindow->data[i3 +
        Xwindow->size[0] * i4];
    }
  }

  emxFree_creal_T(&Xwindow);
  d_mean(b_Xwindow, A);
  Zwindow_re = w / 2.0 * fs;
  i3 = b_Xwindow->size[0] * b_Xwindow->size[1];
  b_Xwindow->size[0] = Ywindow->size[1];
  b_Xwindow->size[1] = Ywindow->size[0];
  emxEnsureCapacity_creal_T(b_Xwindow, i3);
  loop_ub = Ywindow->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = Ywindow->size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      b_Xwindow->data[i4 + b_Xwindow->size[0] * i3] = Ywindow->data[i3 +
        Ywindow->size[0] * i4];
    }
  }

  emxFree_creal_T(&Ywindow);
  emxInit_creal_T(&b_A, 2);
  d_mean(b_Xwindow, b_A);
  Ywindow_re = w / 2.0 * fs;
  i3 = b_Xwindow->size[0] * b_Xwindow->size[1];
  b_Xwindow->size[0] = Zwindow->size[1];
  b_Xwindow->size[1] = Zwindow->size[0];
  emxEnsureCapacity_creal_T(b_Xwindow, i3);
  loop_ub = Zwindow->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_loop_ub = Zwindow->size[1];
    for (i4 = 0; i4 < b_loop_ub; i4++) {
      b_Xwindow->data[i4 + b_Xwindow->size[0] * i3] = Zwindow->data[i3 +
        Zwindow->size[0] * i4];
    }
  }

  emxFree_creal_T(&Zwindow);
  emxInit_real_T(&spread1, 2);
  emxInit_creal_T(&c_A, 2);
  d_mean(b_Xwindow, c_A);
  Ywindow_im = w / 2.0 * fs;

  /*  auto and cross displacement spectra  */
  /* [m^2/Hz] */
  /* [m^2/Hz] */
  /* [m^2/Hz] */
  /* [m^2/Hz], quadspectrum of vertical and horizontal displacements */
  /* [m^2/Hz], cospectrum of vertical and horizontal displacements */
  /* [m^2/Hz], quadspectrum of vertical and horizontal displacements */
  /* [m^2/Hz], cospectrum of vertical and horizontal displacements */
  /* [m^2/Hz], cospectrum of horizontal displacements */
  /*  check factor for circular orbits */
  i3 = spread1->size[0] * spread1->size[1];
  spread1->size[0] = 1;
  spread1->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(spread1, i3);
  loop_ub = XX->size[0] * XX->size[1];
  emxFree_creal_T(&b_Xwindow);
  for (i3 = 0; i3 < loop_ub; i3++) {
    spread1->data[i3] = XX->data[i3] + b_YY->data[i3];
  }

  rdivide(spread1, ZZ, check);

  /*  wave spectral moments  */
  /*  wave directions from Kuik et al, JPO, 1988 and Herbers et al, JTech, 2012 */
  i3 = r0->size[0] * r0->size[1];
  r0->size[0] = 1;
  r0->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(r0, i3);
  loop_ub = XX->size[0] * XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    r0->data[i3] = (XX->data[i3] + b_YY->data[i3]) * ZZ->data[i3];
  }

  emxInit_real_T(&d_A, 2);
  f_sqrt(r0);
  i3 = d_A->size[0] * d_A->size[1];
  d_A->size[0] = 1;
  d_A->size[1] = b_A->size[1];
  emxEnsureCapacity_real_T(d_A, i3);
  loop_ub = b_A->size[0] * b_A->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Xwindow_im = b_A->data[i3].im;
    if (Xwindow_im == 0.0) {
      b_n = 0.0;
    } else {
      b_n = Xwindow_im / Ywindow_re;
    }

    d_A->data[i3] = b_n;
  }

  emxFree_creal_T(&b_A);
  rdivide(d_A, r0, a1);

  /* [], would use Qxz for actual displacements */
  i3 = r0->size[0] * r0->size[1];
  r0->size[0] = 1;
  r0->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(r0, i3);
  loop_ub = XX->size[0] * XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    r0->data[i3] = (XX->data[i3] + b_YY->data[i3]) * ZZ->data[i3];
  }

  f_sqrt(r0);
  i3 = d_A->size[0] * d_A->size[1];
  d_A->size[0] = 1;
  d_A->size[1] = c_A->size[1];
  emxEnsureCapacity_real_T(d_A, i3);
  loop_ub = c_A->size[0] * c_A->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    Xwindow_im = c_A->data[i3].im;
    if (Xwindow_im == 0.0) {
      b_n = 0.0;
    } else {
      b_n = Xwindow_im / Ywindow_im;
    }

    d_A->data[i3] = b_n;
  }

  emxFree_creal_T(&c_A);
  rdivide(d_A, r0, b1);

  /* [], would use Qyz for actual displacements */
  i3 = spread1->size[0] * spread1->size[1];
  spread1->size[0] = 1;
  spread1->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(spread1, i3);
  loop_ub = XX->size[0] * XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    spread1->data[i3] = XX->data[i3] - b_YY->data[i3];
  }

  i3 = d_A->size[0] * d_A->size[1];
  d_A->size[0] = 1;
  d_A->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(d_A, i3);
  loop_ub = XX->size[0] * XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    d_A->data[i3] = XX->data[i3] + b_YY->data[i3];
  }

  rdivide(spread1, d_A, a2);
  i3 = r0->size[0] * r0->size[1];
  r0->size[0] = 1;
  r0->size[1] = A->size[1];
  emxEnsureCapacity_real_T(r0, i3);
  loop_ub = A->size[0] * A->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_n = A->data[i3].re;
    Xwindow_im = A->data[i3].im;
    if (Xwindow_im == 0.0) {
      b_n /= Zwindow_re;
    } else if (b_n == 0.0) {
      b_n = 0.0;
    } else {
      b_n /= Zwindow_re;
    }

    r0->data[i3] = 2.0 * b_n;
  }

  emxFree_creal_T(&A);
  i3 = spread1->size[0] * spread1->size[1];
  spread1->size[0] = 1;
  spread1->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(spread1, i3);
  loop_ub = XX->size[0] * XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    spread1->data[i3] = XX->data[i3] + b_YY->data[i3];
  }

  rdivide(r0, spread1, b2);

  /*  wave directions */
  /*  note that 0 deg is for waves headed towards positive x (EAST, right hand system) */
  b_atan2(b1, a1, b_YY);

  /*  [rad], 4 quadrant */
  b_atan2(b2, a2, XX);
  i3 = XX->size[0] * XX->size[1];
  XX->size[0] = 1;
  emxEnsureCapacity_real_T(XX, i3);
  n = XX->size[0];
  ixstart = XX->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    XX->data[i3] /= 2.0;
  }

  /*  [rad], only 2 quadrant */
  b_power(a1, spread1);
  b_power(b1, r0);
  i3 = spread1->size[0] * spread1->size[1];
  spread1->size[0] = 1;
  emxEnsureCapacity_real_T(spread1, i3);
  n = spread1->size[0];
  ixstart = spread1->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    spread1->data[i3] += r0->data[i3];
  }

  f_sqrt(spread1);
  i3 = spread1->size[0] * spread1->size[1];
  spread1->size[0] = 1;
  emxEnsureCapacity_real_T(spread1, i3);
  n = spread1->size[0];
  ixstart = spread1->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    spread1->data[i3] = 1.0 - spread1->data[i3];
  }

  i3 = spread1->size[0] * spread1->size[1];
  spread1->size[0] = 1;
  emxEnsureCapacity_real_T(spread1, i3);
  n = spread1->size[0];
  ixstart = spread1->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    spread1->data[i3] *= 2.0;
  }

  f_sqrt(spread1);
  i3 = r0->size[0] * r0->size[1];
  r0->size[0] = 1;
  r0->size[1] = XX->size[1];
  emxEnsureCapacity_real_T(r0, i3);
  loop_ub = XX->size[0] * XX->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    r0->data[i3] = 2.0 * XX->data[i3];
  }

  b_cos(r0);
  i3 = XX->size[0] * XX->size[1];
  XX->size[0] = 1;
  emxEnsureCapacity_real_T(XX, i3);
  n = XX->size[0];
  ixstart = XX->size[1];
  loop_ub = n * ixstart;
  for (i3 = 0; i3 < loop_ub; i3++) {
    XX->data[i3] *= 2.0;
  }

  b_cos(XX);
  i3 = d_A->size[0] * d_A->size[1];
  d_A->size[0] = 1;
  d_A->size[1] = a2->size[1];
  emxEnsureCapacity_real_T(d_A, i3);
  loop_ub = a2->size[0] * a2->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    d_A->data[i3] = 0.5 - 0.5 * (a2->data[i3] * r0->data[i3] + b2->data[i3] *
      XX->data[i3]);
  }

  emxFree_real_T(&XX);
  emxInit_real_T(&r3, 2);
  c_abs(d_A, r0);
  c_sqrt(r0, r3);

  /*  bulk parameters */
  i3 = E->size[0] * E->size[1];
  E->size[0] = 1;
  E->size[1] = ZZ->size[1];
  emxEnsureCapacity_real_T(E, i3);
  loop_ub = ZZ->size[0] * ZZ->size[1];
  emxFree_real_T(&r3);
  for (i3 = 0; i3 < loop_ub; i3++) {
    E->data[i3] = ZZ->data[i3];
  }

  emxInit_boolean_T(&eastdirs, 2);
  i3 = eastdirs->size[0] * eastdirs->size[1];
  eastdirs->size[0] = 1;
  eastdirs->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(eastdirs, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    eastdirs->data[i3] = (f->data[i3] > 0.04);
  }

  emxInit_boolean_T(&b_f, 2);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] < 0.5);
  }

  /*  frequency cutoff for wave stats, 0.4 is specific to SWIFT hull */
  end = eastdirs->size[1];
  for (n = 0; n < end; n++) {
    if (!(eastdirs->data[n] && b_f->data[n])) {
      E->data[n] = 0.0;
    }
  }

  /*  significant wave height */
  end = eastdirs->size[1] - 1;
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (eastdirs->data[n] && b_f->data[n]) {
      ixstart++;
    }
  }

  emxInit_int32_T(&r4, 2);
  i3 = r4->size[0] * r4->size[1];
  r4->size[0] = 1;
  r4->size[1] = ixstart;
  emxEnsureCapacity_int32_T(r4, i3);
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (eastdirs->data[n] && b_f->data[n]) {
      r4->data[ixstart] = n + 1;
      ixstart++;
    }
  }

  i3 = d_A->size[0] * d_A->size[1];
  d_A->size[0] = 1;
  d_A->size[1] = r4->size[1];
  emxEnsureCapacity_real_T(d_A, i3);
  loop_ub = r4->size[0] * r4->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    d_A->data[i3] = E->data[r4->data[i3] - 1];
  }

  emxFree_int32_T(&r4);
  b_n = sum(d_A) * bandwidth;
  d_sqrt(&b_n);
  Xwindow_im = 4.0 * b_n;

  /*   energy period */
  /*  peak period */
  ixstart = 1;
  n = ZZ->size[1];
  b_n = ZZ->data[0];
  b_loop_ub = 0;
  emxFree_real_T(&d_A);
  if (rtIsNaN(ZZ->data[0])) {
    end = 2;
    exitg1 = false;
    while ((!exitg1) && (end <= n)) {
      ixstart = end;
      if (!rtIsNaN(ZZ->data[end - 1])) {
        b_n = ZZ->data[end - 1];
        b_loop_ub = end - 1;
        exitg1 = true;
      } else {
        end++;
      }
    }
  }

  if (ixstart < ZZ->size[1]) {
    while (ixstart + 1 <= n) {
      if (ZZ->data[ixstart] > b_n) {
        b_n = ZZ->data[ixstart];
        b_loop_ub = ixstart;
      }

      ixstart++;
    }
  }

  emxFree_real_T(&ZZ);

  /* [~ , fpindex] = max(E); */
  Ywindow_im = 1.0 / f->data[b_loop_ub];

  /*  spectral directions */
  /*  switch from rad to deg, and CCW to CW (negate) */
  i3 = b_YY->size[0] * b_YY->size[1];
  b_YY->size[0] = 1;
  emxEnsureCapacity_real_T(b_YY, i3);
  ixstart = b_YY->size[0];
  n = b_YY->size[1];
  loop_ub = ixstart * n;
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_YY->data[i3] = -57.324840764331206 * b_YY->data[i3] + 90.0;
  }

  /*  rotate from eastward = 0 to northward  = 0 */
  end = b_YY->size[1] - 1;
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (b_YY->data[n] < 0.0) {
      ixstart++;
    }
  }

  emxInit_int32_T(&r5, 2);
  i3 = r5->size[0] * r5->size[1];
  r5->size[0] = 1;
  r5->size[1] = ixstart;
  emxEnsureCapacity_int32_T(r5, i3);
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (b_YY->data[n] < 0.0) {
      r5->data[ixstart] = n + 1;
      ixstart++;
    }
  }

  i3 = YY->size[0];
  YY->size[0] = r5->size[0] * r5->size[1];
  emxEnsureCapacity_real_T1(YY, i3);
  loop_ub = r5->size[0] * r5->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    YY->data[i3] = b_YY->data[r5->data[i3] - 1] + 360.0;
  }

  loop_ub = YY->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_YY->data[r5->data[i3] - 1] = YY->data[i3];
  }

  emxFree_int32_T(&r5);

  /*  take NW quadrant from negative to 270-360 range */
  i3 = eastdirs->size[0] * eastdirs->size[1];
  eastdirs->size[0] = 1;
  eastdirs->size[1] = b_YY->size[1];
  emxEnsureCapacity_boolean_T(eastdirs, i3);
  loop_ub = b_YY->size[0] * b_YY->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    eastdirs->data[i3] = (b_YY->data[i3] < 180.0);
  }

  end = b_YY->size[1] - 1;
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (b_YY->data[n] > 180.0) {
      ixstart++;
    }
  }

  emxInit_int32_T(&r6, 2);
  i3 = r6->size[0] * r6->size[1];
  r6->size[0] = 1;
  r6->size[1] = ixstart;
  emxEnsureCapacity_int32_T(r6, i3);
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (b_YY->data[n] > 180.0) {
      r6->data[ixstart] = n + 1;
      ixstart++;
    }
  }

  i3 = YY->size[0];
  YY->size[0] = r6->size[0] * r6->size[1];
  emxEnsureCapacity_real_T1(YY, i3);
  loop_ub = r6->size[0] * r6->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    YY->data[i3] = b_YY->data[r6->data[i3] - 1] - 180.0;
  }

  loop_ub = YY->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_YY->data[r6->data[i3] - 1] = YY->data[i3];
  }

  emxFree_int32_T(&r6);

  /*  take reciprocal such wave direction is FROM, not TOWARDS */
  end = eastdirs->size[1] - 1;
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (eastdirs->data[n]) {
      ixstart++;
    }
  }

  emxInit_int32_T(&r7, 2);
  i3 = r7->size[0] * r7->size[1];
  r7->size[0] = 1;
  r7->size[1] = ixstart;
  emxEnsureCapacity_int32_T(r7, i3);
  ixstart = 0;
  for (n = 0; n <= end; n++) {
    if (eastdirs->data[n]) {
      r7->data[ixstart] = n + 1;
      ixstart++;
    }
  }

  i3 = YY->size[0];
  YY->size[0] = r7->size[0] * r7->size[1];
  emxEnsureCapacity_real_T1(YY, i3);
  loop_ub = r7->size[0] * r7->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    YY->data[i3] = b_YY->data[r7->data[i3] - 1] + 180.0;
  }

  loop_ub = YY->size[0];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_YY->data[r7->data[i3] - 1] = YY->data[i3];
  }

  emxFree_real_T(&YY);
  emxFree_int32_T(&r7);

  /*  take reciprocal such wave direction is FROM, not TOWARDS */
  /*  directional spread */
  /*  dominant direction */
  Ywindow_re = b_YY->data[b_loop_ub];

  /*  dominant (peak) direction, use peak f */
  /*  screen for bad direction estimate,      */
  /*  pick neighboring bands */
  for (i3 = 0; i3 < 3; i3++) {
    b_n = (double)(b_loop_ub + 1) + (-1.0 + (double)i3);
    inds[i3] = (b_n > 0.0);
    b_inds[i3] = b_n;
  }

  if (all(inds)) {
    b_n = b_inds[0];
    for (end = 1; end + 1 < 4; end++) {
      if (b_inds[end] > b_n) {
        b_n = b_inds[end];
      }
    }

    if (b_n <= b_YY->size[1]) {
      for (i3 = 0; i3 < 3; i3++) {
        c_YY[i3] = b_YY->data[(int)b_inds[i3] - 1];
      }

      if (c_std(c_YY) > 45.0) {
        Ywindow_re = 9999.0;
      }
    } else {
      Ywindow_re = 9999.0;
    }
  } else {
    Ywindow_re = 9999.0;
  }

  /*  prune high frequency results */
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(E, b_f);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  emxInit_real_T(&d_YY, 2);
  nullAssignment(b_YY, b_f, d_YY);
  i3 = r0->size[0] * r0->size[1];
  r0->size[0] = 1;
  r0->size[1] = spread1->size[1];
  emxEnsureCapacity_real_T(r0, i3);
  loop_ub = spread1->size[0] * spread1->size[1];
  emxFree_real_T(&d_YY);
  emxFree_real_T(&b_YY);
  for (i3 = 0; i3 < loop_ub; i3++) {
    r0->data[i3] = 57.324840764331206 * spread1->data[i3];
  }

  emxFree_real_T(&spread1);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  emxInit_real_T(&c_f, 2);
  nullAssignment(r0, b_f, c_f);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  emxFree_real_T(&c_f);
  emxFree_real_T(&r0);
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(a1, b_f);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(b1, b_f);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(a2, b_f);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(b2, b_f);
  i3 = b_f->size[0] * b_f->size[1];
  b_f->size[0] = 1;
  b_f->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(b_f, i3);
  loop_ub = f->size[0] * f->size[1];
  for (i3 = 0; i3 < loop_ub; i3++) {
    b_f->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(check, b_f);
  i3 = eastdirs->size[0] * eastdirs->size[1];
  eastdirs->size[0] = 1;
  eastdirs->size[1] = f->size[1];
  emxEnsureCapacity_boolean_T(eastdirs, i3);
  loop_ub = f->size[0] * f->size[1];
  emxFree_boolean_T(&b_f);
  for (i3 = 0; i3 < loop_ub; i3++) {
    eastdirs->data[i3] = (f->data[i3] > 0.5);
  }

  d_nullAssignment(f, eastdirs);

  /*  quality control, with or without check factor  */
  /*    (should only test for check = unity if in deep water!) */
  /* if Tp>20 | nanmedian(check(f>.05)) > 5  |  Hs < 0.1,  */
  emxFree_boolean_T(&eastdirs);
  if ((Ywindow_im > 20.0) || (Xwindow_im < 0.0)) {
    Xwindow_im = 9999.0;
    Ywindow_im = 9999.0;
    Ywindow_re = 9999.0;

    /* E(:) = 9999;  */
    i3 = a1->size[0] * a1->size[1];
    a1->size[0] = 1;
    emxEnsureCapacity_real_T(a1, i3);
    loop_ub = a1->size[1];
    for (i3 = 0; i3 < loop_ub; i3++) {
      a1->data[a1->size[0] * i3] = 9999.0;
    }

    i3 = b1->size[0] * b1->size[1];
    b1->size[0] = 1;
    emxEnsureCapacity_real_T(b1, i3);
    loop_ub = b1->size[1];
    for (i3 = 0; i3 < loop_ub; i3++) {
      b1->data[b1->size[0] * i3] = 9999.0;
    }

    i3 = a2->size[0] * a2->size[1];
    a2->size[0] = 1;
    emxEnsureCapacity_real_T(a2, i3);
    loop_ub = a2->size[1];
    for (i3 = 0; i3 < loop_ub; i3++) {
      a2->data[a2->size[0] * i3] = 9999.0;
    }

    i3 = b2->size[0] * b2->size[1];
    b2->size[0] = 1;
    emxEnsureCapacity_real_T(b2, i3);
    loop_ub = b2->size[1];
    for (i3 = 0; i3 < loop_ub; i3++) {
      b2->data[b2->size[0] * i3] = 9999.0;
    }

    i3 = check->size[0] * check->size[1];
    check->size[0] = 1;
    emxEnsureCapacity_real_T(check, i3);
    loop_ub = check->size[1];
    for (i3 = 0; i3 < loop_ub; i3++) {
      check->data[check->size[0] * i3] = 9999.0;
    }
  }

  *Hs = Xwindow_im;
  *Tp = Ywindow_im;
  *Dp = Ywindow_re;
}

/* End of code generation (XYZwaves.cpp) */
