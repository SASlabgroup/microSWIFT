/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xnrm2.h
 *
 * Code generation for function 'xnrm2'
 *
 */

#ifndef XNRM2_H
#define XNRM2_H

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
extern double b_xnrm2(int n, const double x[4096], int ix0);
extern double c_xnrm2(const double x[2048]);
extern double d_xnrm2(int n, const emxArray_real_T *x, int ix0);
extern double xnrm2(const double x[4096], int ix0);

#endif

/* End of code generation (xnrm2.h) */
