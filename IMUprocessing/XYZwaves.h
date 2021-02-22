/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * XYZwaves.h
 *
 * Code generation for function 'XYZwaves'
 *
 */

#ifndef XYZWAVES_H
#define XYZWAVES_H

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
extern void XYZwaves(const double x[2048], const double y[2048], const double z
                     [2048], double fs, double *Hs, double *Tp, double *Dp,
                     emxArray_real_T *E, emxArray_real_T *f, emxArray_real_T *a1,
                     emxArray_real_T *b1, emxArray_real_T *a2, emxArray_real_T
                     *b2, emxArray_real_T *check);

#endif

/* End of code generation (XYZwaves.h) */
