/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * mean.cpp
 *
 * Code generation for function 'mean'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "mean.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
double b_mean(const double x[2048])
{
  double y;
  int k;
  y = x[0];
  for (k = 0; k < 2047; k++) {
    y += x[k + 1];
  }

  y /= 2048.0;
  return y;
}

void c_mean(const emxArray_real_T *x, emxArray_real_T *y)
{
  int i;
  unsigned int sz[2];
  int xpageoffset;
  int k;
  if ((x->size[0] == 0) || (x->size[1] == 0)) {
    for (i = 0; i < 2; i++) {
      sz[i] = (unsigned int)x->size[i];
    }

    i = y->size[0] * y->size[1];
    y->size[0] = 1;
    y->size[1] = (int)sz[1];
    emxEnsureCapacity_real_T(y, i);
    xpageoffset = (int)sz[1];
    for (i = 0; i < xpageoffset; i++) {
      y->data[i] = 0.0;
    }
  } else {
    i = y->size[0] * y->size[1];
    y->size[0] = 1;
    y->size[1] = x->size[1];
    emxEnsureCapacity_real_T(y, i);
    for (i = 0; i + 1 <= x->size[1]; i++) {
      xpageoffset = i * x->size[0];
      y->data[i] = x->data[xpageoffset];
      for (k = 2; k <= x->size[0]; k++) {
        y->data[i] += x->data[(xpageoffset + k) - 1];
      }
    }
  }

  i = y->size[0] * y->size[1];
  y->size[0] = 1;
  emxEnsureCapacity_real_T(y, i);
  i = y->size[0];
  xpageoffset = y->size[1];
  k = x->size[0];
  xpageoffset *= i;
  for (i = 0; i < xpageoffset; i++) {
    y->data[i] /= (double)k;
  }
}

void d_mean(const emxArray_creal_T *x, emxArray_creal_T *y)
{
  int i;
  unsigned int sz[2];
  int xpageoffset;
  int k;
  double y_re;
  double y_im;
  if ((x->size[0] == 0) || (x->size[1] == 0)) {
    for (i = 0; i < 2; i++) {
      sz[i] = (unsigned int)x->size[i];
    }

    i = y->size[0] * y->size[1];
    y->size[0] = 1;
    y->size[1] = (int)sz[1];
    emxEnsureCapacity_creal_T(y, i);
    xpageoffset = (int)sz[1];
    for (i = 0; i < xpageoffset; i++) {
      y->data[i].re = 0.0;
      y->data[i].im = 0.0;
    }
  } else {
    i = y->size[0] * y->size[1];
    y->size[0] = 1;
    y->size[1] = x->size[1];
    emxEnsureCapacity_creal_T(y, i);
    for (i = 0; i + 1 <= x->size[1]; i++) {
      xpageoffset = i * x->size[0];
      y->data[i] = x->data[xpageoffset];
      for (k = 2; k <= x->size[0]; k++) {
        y->data[i].re += x->data[(xpageoffset + k) - 1].re;
        y->data[i].im += x->data[(xpageoffset + k) - 1].im;
      }
    }
  }

  i = y->size[0] * y->size[1];
  y->size[0] = 1;
  emxEnsureCapacity_creal_T(y, i);
  i = y->size[0];
  xpageoffset = y->size[1];
  k = x->size[0];
  xpageoffset *= i;
  for (i = 0; i < xpageoffset; i++) {
    y_re = y->data[i].re;
    y_im = y->data[i].im;
    if (y_im == 0.0) {
      y->data[i].re = y_re / (double)k;
      y->data[i].im = 0.0;
    } else if (y_re == 0.0) {
      y->data[i].re = 0.0;
      y->data[i].im = y_im / (double)k;
    } else {
      y->data[i].re = y_re / (double)k;
      y->data[i].im = y_im / (double)k;
    }
  }
}

double mean(const double x_data[], const int x_size[1])
{
  double y;
  int k;
  if (x_size[0] == 0) {
    y = 0.0;
  } else {
    y = x_data[0];
    for (k = 2; k <= x_size[0]; k++) {
      y += x_data[k - 1];
    }
  }

  y /= (double)x_size[0];
  return y;
}

/* End of code generation (mean.cpp) */
