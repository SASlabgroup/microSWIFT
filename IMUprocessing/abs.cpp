/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * abs.cpp
 *
 * Code generation for function 'abs'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "abs.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
void b_abs(const double x[2048], double y[2048])
{
  int k;
  for (k = 0; k < 2048; k++) {
    y[k] = std::abs(x[k]);
  }
}

void c_abs(const emxArray_real_T *x, emxArray_real_T *y)
{
  int k;
  k = y->size[0] * y->size[1];
  y->size[0] = 1;
  y->size[1] = x->size[1];
  emxEnsureCapacity_real_T(y, k);
  for (k = 0; k + 1 <= x->size[1]; k++) {
    y->data[k] = std::abs(x->data[k]);
  }
}

/* End of code generation (abs.cpp) */
