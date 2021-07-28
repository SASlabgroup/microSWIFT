/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * processIMU.h
 *
 * Code generation for function 'processIMU'
 *
 */

#ifndef PROCESSIMU_H
#define PROCESSIMU_H

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
extern void processIMU(double ax[2048], double ay[2048], double az[2048], double
  gx[2048], double gy[2048], double gz[2048], double mx[2048], double my[2048],
  double mz[2048], double mxo, double myo, double mzo, double Wd, double fs,
  double *Hs, double *Tp, double *Dp, emxArray_real_T *E, emxArray_real_T *f,
  emxArray_real_T *a1, emxArray_real_T *b1, emxArray_real_T *a2, emxArray_real_T
  *b2, emxArray_real_T *check);

#endif

/* End of code generation (processIMU.h) */
