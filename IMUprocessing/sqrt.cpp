/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * sqrt.cpp
 *
 * Code generation for function 'sqrt'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "sqrt.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
double b_sqrt(double x)
{
  double b_x;
  b_x = x;
  d_sqrt(&b_x);
  return b_x;
}

void c_sqrt(const emxArray_real_T *x, emxArray_real_T *b_x)
{
  int i7;
  int loop_ub;
  i7 = b_x->size[0] * b_x->size[1];
  b_x->size[0] = 1;
  b_x->size[1] = x->size[1];
  emxEnsureCapacity_real_T(b_x, i7);
  loop_ub = x->size[0] * x->size[1];
  for (i7 = 0; i7 < loop_ub; i7++) {
    b_x->data[i7] = x->data[i7];
  }

  f_sqrt(b_x);
}

void d_sqrt(double *x)
{
  *x = std::sqrt(*x);
}

void e_sqrt(double x[2048])
{
  int k;
  for (k = 0; k < 2048; k++) {
    x[k] = std::sqrt(x[k]);
  }
}

void f_sqrt(emxArray_real_T *x)
{
  int nx;
  int k;
  nx = x->size[1];
  for (k = 0; k + 1 <= nx; k++) {
    x->data[k] = std::sqrt(x->data[k]);
  }
}

/* End of code generation (sqrt.cpp) */
