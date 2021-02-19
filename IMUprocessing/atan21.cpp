/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * atan21.cpp
 *
 * Code generation for function 'atan21'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "atan21.h"
#include "processIMU_emxutil.h"
#include "processIMU_rtwutil.h"

/* Function Definitions */
void b_atan2(const emxArray_real_T *y, const emxArray_real_T *x, emxArray_real_T
             *r)
{
  int c;
  int k;
  if (y->size[1] <= x->size[1]) {
    c = y->size[1];
  } else {
    c = x->size[1];
  }

  k = r->size[0] * r->size[1];
  r->size[0] = 1;
  r->size[1] = c;
  emxEnsureCapacity_real_T(r, k);
  for (k = 0; k + 1 <= c; k++) {
    r->data[k] = rt_atan2d_snf(y->data[k], x->data[k]);
  }
}

/* End of code generation (atan21.cpp) */
