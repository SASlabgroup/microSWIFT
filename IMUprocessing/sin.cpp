/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * sin.cpp
 *
 * Code generation for function 'sin'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "sin.h"

/* Function Definitions */
void b_sin(emxArray_real_T *x)
{
  int nx;
  int k;
  nx = x->size[1];
  for (k = 0; k + 1 <= nx; k++) {
    x->data[k] = std::sin(x->data[k]);
  }
}

/* End of code generation (sin.cpp) */
