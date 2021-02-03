/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * abs.h
 *
 * Code generation for function 'abs'
 *
 */

#ifndef ABS_H
#define ABS_H

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
extern void b_abs(const double x[2048], double y[2048]);
extern void c_abs(const emxArray_real_T *x, emxArray_real_T *y);

#endif

/* End of code generation (abs.h) */
