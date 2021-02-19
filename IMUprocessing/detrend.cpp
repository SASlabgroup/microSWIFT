/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * detrend.cpp
 *
 * Code generation for function 'detrend'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "detrend.h"
#include "processIMU_emxutil.h"
#include "qrsolve.h"
#include "mldivide.h"

/* Function Definitions */
void b_detrend(emxArray_real_T *x)
{
  emxArray_real_T *a;
  int nrows;
  int ar;
  int ia;
  emxArray_real_T *C;
  double Y[2];
  unsigned int a_idx_0;
  int m;
  int br;
  int ic;
  emxInit_real_T(&a, 2);
  nrows = x->size[0];
  ar = x->size[0];
  ia = a->size[0] * a->size[1];
  a->size[0] = ar;
  a->size[1] = 2;
  emxEnsureCapacity_real_T(a, ia);
  for (ar = 1; ar <= nrows; ar++) {
    a->data[ar - 1] = (double)ar / (double)nrows;
    a->data[(ar + a->size[0]) - 1] = 1.0;
  }

  emxInit_real_T1(&C, 1);
  qrsolve(a, x, Y);
  a_idx_0 = (unsigned int)a->size[0];
  ia = C->size[0];
  C->size[0] = (int)a_idx_0;
  emxEnsureCapacity_real_T1(C, ia);
  m = a->size[0];
  ar = C->size[0];
  ia = C->size[0];
  C->size[0] = ar;
  emxEnsureCapacity_real_T1(C, ia);
  for (ia = 0; ia < ar; ia++) {
    C->data[ia] = 0.0;
  }

  ar = 0;
  while (ar <= 0) {
    for (ic = 1; ic <= m; ic++) {
      C->data[ic - 1] = 0.0;
    }

    ar = m;
  }

  br = 0;
  ar = 0;
  while (ar <= 0) {
    ar = -1;
    for (nrows = br; nrows + 1 <= br + 2; nrows++) {
      if (Y[nrows] != 0.0) {
        ia = ar;
        for (ic = 0; ic + 1 <= m; ic++) {
          ia++;
          C->data[ic] += Y[nrows] * a->data[ia];
        }
      }

      ar += m;
    }

    br += 2;
    ar = m;
  }

  emxFree_real_T(&a);
  ia = x->size[0];
  emxEnsureCapacity_real_T1(x, ia);
  ar = x->size[0];
  for (ia = 0; ia < ar; ia++) {
    x->data[ia] -= C->data[ia];
  }

  emxFree_real_T(&C);
}

void detrend(double x[2048])
{
  int i;
  static double a[4096];
  double b[2];
  double d10;
  int i9;
  for (i = 0; i < 2048; i++) {
    a[i] = ((double)i + 1.0) / 2048.0;
    a[2048 + i] = 1.0;
  }

  mldivide(a, x, b);
  for (i = 0; i < 2048; i++) {
    d10 = 0.0;
    for (i9 = 0; i9 < 2; i9++) {
      d10 += a[i + (i9 << 11)] * b[i9];
    }

    x[i] -= d10;
  }
}

/* End of code generation (detrend.cpp) */
