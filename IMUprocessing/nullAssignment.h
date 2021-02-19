/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * nullAssignment.h
 *
 * Code generation for function 'nullAssignment'
 *
 */

#ifndef NULLASSIGNMENT_H
#define NULLASSIGNMENT_H

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
extern void b_nullAssignment(emxArray_creal_T *x, const emxArray_int32_T *idx);
extern void c_nullAssignment(emxArray_creal_T *x);
extern void d_nullAssignment(emxArray_real_T *x, const emxArray_boolean_T *idx);
extern void nullAssignment(const emxArray_real_T *x, const emxArray_boolean_T
  *idx, emxArray_real_T *b_x);

#endif

/* End of code generation (nullAssignment.h) */
