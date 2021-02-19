/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * atan2d.cpp
 *
 * Code generation for function 'atan2d'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "atan2d.h"
#include "atan21.h"
#include "processIMU_rtwutil.h"

/* Function Definitions */
void b_atan2d(const double y[2048], const double x[2048], double r[2048])
{
  int k;
  for (k = 0; k < 2048; k++) {
    r[k] = 57.295779513082323 * rt_atan2d_snf(y[k], x[k]);
  }
}

/* End of code generation (atan2d.cpp) */
