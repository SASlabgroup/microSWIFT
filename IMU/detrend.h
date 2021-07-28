/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * detrend.h
 *
 * Code generation for function 'detrend'
 *
 */

#ifndef DETREND_H
#define DETREND_H

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
extern void b_detrend(emxArray_real_T *x);
extern void detrend(double x[2048]);

#endif

/* End of code generation (detrend.h) */
