/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xgemv.cpp
 *
 * Code generation for function 'xgemv'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "xgemv.h"

/* Function Definitions */
void xgemv(int m, int n, const double A[4096], const double x[4096], int ix0,
           double y[2])
{
  int ix;
  double c;
  int ia;
  if (n != 0) {
    y[0] = 0.0;
    ix = ix0;
    c = 0.0;
    for (ia = 2049; ia <= m + 2048; ia++) {
      c += A[ia - 1] * x[ix - 1];
      ix++;
    }

    y[0] += c;
  }
}

/* End of code generation (xgemv.cpp) */
