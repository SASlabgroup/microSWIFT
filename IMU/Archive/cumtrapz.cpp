/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * cumtrapz.cpp
 *
 * Code generation for function 'cumtrapz'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "cumtrapz.h"

/* Function Definitions */
void cumtrapz(const double x[2048], double z[2048])
{
  double s;
  int iyz;
  double ylast;
  int k;
  s = 0.0;
  iyz = 0;
  ylast = x[0];
  z[0] = 0.0;
  for (k = 0; k < 2047; k++) {
    iyz++;
    s += (ylast + x[iyz]) / 2.0;
    ylast = x[iyz];
    z[iyz] = s;
  }
}

/* End of code generation (cumtrapz.cpp) */
