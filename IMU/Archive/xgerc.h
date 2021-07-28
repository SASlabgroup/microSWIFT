/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xgerc.h
 *
 * Code generation for function 'xgerc'
 *
 */

#ifndef XGERC_H
#define XGERC_H

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
extern void xgerc(int m, int n, double alpha1, int ix0, const double y[2],
                  double A[4096]);

#endif

/* End of code generation (xgerc.h) */
