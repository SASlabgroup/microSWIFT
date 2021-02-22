/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * sqrt.h
 *
 * Code generation for function 'sqrt'
 *
 */

#ifndef SQRT_H
#define SQRT_H

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
extern double b_sqrt(double x);
extern void c_sqrt(const emxArray_real_T *x, emxArray_real_T *b_x);
extern void d_sqrt(double *x);
extern void e_sqrt(double x[2048]);
extern void f_sqrt(emxArray_real_T *x);

#endif

/* End of code generation (sqrt.h) */
