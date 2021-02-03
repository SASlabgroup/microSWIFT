/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * nullAssignment.cpp
 *
 * Code generation for function 'nullAssignment'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "nullAssignment.h"
#include "processIMU_emxutil.h"

/* Function Definitions */
void b_nullAssignment(emxArray_creal_T *x, const emxArray_int32_T *idx)
{
  int nrowx;
  int ncolx;
  emxArray_boolean_T *b;
  int nrows;
  int j;
  int i;
  int loop_ub;
  emxArray_creal_T *b_x;
  nrowx = x->size[0];
  ncolx = x->size[1];
  if (idx->size[1] == 1) {
    nrows = x->size[0] - 1;
    for (j = 0; j + 1 <= ncolx; j++) {
      for (i = idx->data[0]; i < nrowx; i++) {
        x->data[(i + x->size[0] * j) - 1] = x->data[i + x->size[0] * j];
      }
    }
  } else {
    emxInit_boolean_T(&b, 2);
    j = b->size[0] * b->size[1];
    b->size[0] = 1;
    b->size[1] = x->size[0];
    emxEnsureCapacity_boolean_T(b, j);
    loop_ub = x->size[0];
    for (j = 0; j < loop_ub; j++) {
      b->data[j] = false;
    }

    for (loop_ub = 1; loop_ub <= idx->size[1]; loop_ub++) {
      b->data[idx->data[loop_ub - 1] - 1] = true;
    }

    nrows = 0;
    for (loop_ub = 1; loop_ub <= b->size[1]; loop_ub++) {
      nrows += b->data[loop_ub - 1];
    }

    nrows = x->size[0] - nrows;
    i = 0;
    for (loop_ub = 1; loop_ub <= nrowx; loop_ub++) {
      if ((loop_ub > b->size[1]) || (!b->data[loop_ub - 1])) {
        for (j = 0; j + 1 <= ncolx; j++) {
          x->data[i + x->size[0] * j] = x->data[(loop_ub + x->size[0] * j) - 1];
        }

        i++;
      }
    }

    emxFree_boolean_T(&b);
  }

  if (1 > nrows) {
    loop_ub = 0;
  } else {
    loop_ub = nrows;
  }

  emxInit_creal_T(&b_x, 2);
  nrows = x->size[1];
  j = b_x->size[0] * b_x->size[1];
  b_x->size[0] = loop_ub;
  b_x->size[1] = nrows;
  emxEnsureCapacity_creal_T(b_x, j);
  for (j = 0; j < nrows; j++) {
    for (i = 0; i < loop_ub; i++) {
      b_x->data[i + b_x->size[0] * j] = x->data[i + x->size[0] * j];
    }
  }

  j = x->size[0] * x->size[1];
  x->size[0] = b_x->size[0];
  x->size[1] = b_x->size[1];
  emxEnsureCapacity_creal_T(x, j);
  loop_ub = b_x->size[1];
  for (j = 0; j < loop_ub; j++) {
    nrows = b_x->size[0];
    for (i = 0; i < nrows; i++) {
      x->data[i + x->size[0] * j] = b_x->data[i + b_x->size[0] * j];
    }
  }

  emxFree_creal_T(&b_x);
}

void c_nullAssignment(emxArray_creal_T *x)
{
  int nrowx;
  int ncolx;
  int j;
  int i;
  emxArray_creal_T *b_x;
  nrowx = x->size[0] - 1;
  ncolx = x->size[1];
  for (j = 0; j + 1 <= ncolx; j++) {
    for (i = 1; i <= nrowx; i++) {
      x->data[(i + x->size[0] * j) - 1] = x->data[i + x->size[0] * j];
    }
  }

  if (1 > nrowx) {
    ncolx = 0;
  } else {
    ncolx = nrowx;
  }

  emxInit_creal_T(&b_x, 2);
  nrowx = x->size[1];
  j = b_x->size[0] * b_x->size[1];
  b_x->size[0] = ncolx;
  b_x->size[1] = nrowx;
  emxEnsureCapacity_creal_T(b_x, j);
  for (j = 0; j < nrowx; j++) {
    for (i = 0; i < ncolx; i++) {
      b_x->data[i + b_x->size[0] * j] = x->data[i + x->size[0] * j];
    }
  }

  j = x->size[0] * x->size[1];
  x->size[0] = b_x->size[0];
  x->size[1] = b_x->size[1];
  emxEnsureCapacity_creal_T(x, j);
  ncolx = b_x->size[1];
  for (j = 0; j < ncolx; j++) {
    nrowx = b_x->size[0];
    for (i = 0; i < nrowx; i++) {
      x->data[i + x->size[0] * j] = b_x->data[i + b_x->size[0] * j];
    }
  }

  emxFree_creal_T(&b_x);
}

void d_nullAssignment(emxArray_real_T *x, const emxArray_boolean_T *idx)
{
  int nxin;
  int k0;
  int k;
  int nxout;
  nxin = x->size[1];
  k0 = 0;
  for (k = 1; k <= idx->size[1]; k++) {
    k0 += idx->data[k - 1];
  }

  nxout = x->size[1] - k0;
  k0 = -1;
  for (k = 1; k <= nxin; k++) {
    if ((k > idx->size[1]) || (!idx->data[k - 1])) {
      k0++;
      x->data[k0] = x->data[k - 1];
    }
  }

  k0 = x->size[0] * x->size[1];
  if (1 > nxout) {
    x->size[1] = 0;
  } else {
    x->size[1] = nxout;
  }

  emxEnsureCapacity_real_T(x, k0);
}

void nullAssignment(const emxArray_real_T *x, const emxArray_boolean_T *idx,
                    emxArray_real_T *b_x)
{
  int i8;
  int loop_ub;
  i8 = b_x->size[0] * b_x->size[1];
  b_x->size[0] = 1;
  b_x->size[1] = x->size[1];
  emxEnsureCapacity_real_T(b_x, i8);
  loop_ub = x->size[0] * x->size[1];
  for (i8 = 0; i8 < loop_ub; i8++) {
    b_x->data[i8] = x->data[i8];
  }

  d_nullAssignment(b_x, idx);
}

/* End of code generation (nullAssignment.cpp) */
