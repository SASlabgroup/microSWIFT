/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * power.cpp
 *
 * Code generation for function 'power'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "power.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
void b_power(const emxArray_real_T *a, emxArray_real_T *y)
{
  int unnamed_idx_1;
  int k;
  unnamed_idx_1 = a->size[1];
  k = y->size[0] * y->size[1];
  y->size[0] = 1;
  y->size[1] = a->size[1];
  emxEnsureCapacity_real_T(y, k);
  for (k = 0; k + 1 <= unnamed_idx_1; k++) {
    y->data[k] = a->data[k] * a->data[k];
  }
}

void power(const double a[2048], double y[2048])
{
  int k;
  for (k = 0; k < 2048; k++) {
    y[k] = a[k] * a[k];
  }
}

/* End of code generation (power.cpp) */
