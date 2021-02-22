/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * var.cpp
 *
 * Code generation for function 'var'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "var.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
void var(const emxArray_real_T *x, double y_data[], int y_size[2])
{
  int environment_idx_0;
  int loop_ub;
  unsigned int szy[2];
  int nx;
  int p;
  emxArray_real_T *xv;
  int outsize_idx_0;
  int n;
  int b_environment_idx_0;
  double xbar;
  double yv;
  double t;
  environment_idx_0 = x->size[0];
  for (loop_ub = 0; loop_ub < 2; loop_ub++) {
    szy[loop_ub] = (unsigned int)x->size[loop_ub];
  }

  y_size[0] = 1;
  y_size[1] = (int)szy[1];
  loop_ub = (int)szy[1];
  if (0 <= loop_ub - 1) {
    memset(&y_data[0], 0, (unsigned int)(loop_ub * (int)sizeof(double)));
  }

  nx = x->size[0];
  p = 0;
  emxInit_real_T1(&xv, 1);
  if (1 <= x->size[1]) {
    outsize_idx_0 = nx;
    n = environment_idx_0;
  }

  while (p + 1 <= x->size[1]) {
    b_environment_idx_0 = p * nx + 1;
    loop_ub = xv->size[0];
    xv->size[0] = outsize_idx_0;
    emxEnsureCapacity_real_T1(xv, loop_ub);
    for (loop_ub = 0; loop_ub < outsize_idx_0; loop_ub++) {
      xv->data[loop_ub] = 0.0;
    }

    for (loop_ub = -1; loop_ub + 2 <= nx; loop_ub++) {
      xv->data[loop_ub + 1] = x->data[b_environment_idx_0 + loop_ub];
    }

    xbar = xv->data[0];
    for (loop_ub = 2; loop_ub <= n; loop_ub++) {
      xbar += xv->data[loop_ub - 1];
    }

    xbar /= (double)environment_idx_0;
    yv = 0.0;
    for (loop_ub = 1; loop_ub <= n; loop_ub++) {
      t = xv->data[loop_ub - 1] - xbar;
      yv += t * t;
    }

    yv /= (double)environment_idx_0 - 1.0;
    y_data[p] = yv;
    p++;
  }

  emxFree_real_T(&xv);
}

/* End of code generation (var.cpp) */
