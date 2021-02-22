/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * rdivide.cpp
 *
 * Code generation for function 'rdivide'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "rdivide.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
void rdivide(const emxArray_real_T *x, const emxArray_real_T *y, emxArray_real_T
             *z)
{
  int i6;
  int loop_ub;
  i6 = z->size[0] * z->size[1];
  z->size[0] = 1;
  z->size[1] = x->size[1];
  emxEnsureCapacity_real_T(z, i6);
  loop_ub = x->size[0] * x->size[1];
  for (i6 = 0; i6 < loop_ub; i6++) {
    z->data[i6] = x->data[i6] / y->data[i6];
  }
}

/* End of code generation (rdivide.cpp) */
