/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xgerc.cpp
 *
 * Code generation for function 'xgerc'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "xgerc.h"

/* Function Definitions */
void xgerc(int m, int n, double alpha1, int ix0, const double y[2], double A
           [4096])
{
  int jA;
  int jy;
  int ix;
  double temp;
  int i11;
  int ijA;
  if (!(alpha1 == 0.0)) {
    jA = 2048;
    jy = 0;
    ix = 1;
    while (ix <= n) {
      if (y[jy] != 0.0) {
        temp = y[jy] * alpha1;
        ix = ix0;
        i11 = m + jA;
        for (ijA = jA; ijA + 1 <= i11; ijA++) {
          A[ijA] += A[ix - 1] * temp;
          ix++;
        }
      }

      jy++;
      jA += 2048;
      ix = 2;
    }
  }
}

/* End of code generation (xgerc.cpp) */
