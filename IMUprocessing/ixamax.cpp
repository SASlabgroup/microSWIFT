/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * ixamax.cpp
 *
 * Code generation for function 'ixamax'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "ixamax.h"

/* Function Definitions */
int ixamax(int n, const double x[2], int ix0)
{
  int idxmax;
  idxmax = 1;
  if ((n > 1) && (std::abs(x[1]) > std::abs(x[ix0 - 1]))) {
    idxmax = 2;
  }

  return idxmax;
}

/* End of code generation (ixamax.cpp) */
