/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * mean.h
 *
 * Code generation for function 'mean'
 *
 */

#ifndef MEAN_H
#define MEAN_H

/* Include files */
#include <cmath>
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_defines.h"
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "processIMU_types.h"

/* Function Declarations */
extern double b_mean(const double x[2048]);
extern void c_mean(const emxArray_real_T *x, emxArray_real_T *y);
extern void d_mean(const emxArray_creal_T *x, emxArray_creal_T *y);
extern double mean(const double x_data[], const int x_size[1]);

#endif

/* End of code generation (mean.h) */
