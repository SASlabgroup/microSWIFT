/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xswap.cpp
 *
 * Code generation for function 'xswap'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "xswap.h"

/* Function Definitions */
void xswap(double x[4096], int ix0, int iy0)
{
  int ix;
  int iy;
  int k;
  double temp;
  ix = ix0 - 1;
  iy = iy0 - 1;
  for (k = 0; k < 2048; k++) {
    temp = x[ix];
    x[ix] = x[iy];
    x[iy] = temp;
    ix++;
    iy++;
  }
}

/* End of code generation (xswap.cpp) */
