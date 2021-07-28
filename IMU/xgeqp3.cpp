/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xgeqp3.cpp
 *
 * Code generation for function 'xgeqp3'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "xgeqp3.h"
#include "xnrm2.h"
#include "sqrt.h"
#include "xzlarf.h"
#include "xzlarfg.h"
#include "xswap.h"
#include "ixamax.h"

/* Function Definitions */
void xgeqp3(double A[4096], double tau[2], int jpvt[2])
{
  int i;
  int k;
  double work[2];
  int pvt;
  double temp1;
  double vn2[2];
  double vn1[2];
  int itemp;
  double temp2;
  for (i = 0; i < 2; i++) {
    jpvt[i] = 1 + i;
    work[i] = 0.0;
  }

  b_sqrt(2.2204460492503131E-16);
  k = 1;
  for (pvt = 0; pvt < 2; pvt++) {
    temp1 = xnrm2(A, k);
    vn2[pvt] = temp1;
    k += 2048;
    vn1[pvt] = temp1;
  }

  for (i = 0; i < 2; i++) {
    k = i + (i << 11);
    pvt = (i + ixamax(2 - i, vn1, i + 1)) - 1;
    if (pvt + 1 != i + 1) {
      xswap(A, 1 + (pvt << 11), 1 + (i << 11));
      itemp = jpvt[pvt];
      jpvt[pvt] = jpvt[i];
      jpvt[i] = itemp;
      vn1[pvt] = vn1[i];
      vn2[pvt] = vn2[i];
    }

    temp1 = A[k];
    tau[i] = xzlarfg(2048 - i, &temp1, A, k + 2);
    A[k] = temp1;
    if (i + 1 < 2) {
      temp1 = A[k];
      A[k] = 1.0;
      xzlarf(2048, 1, k + 1, tau[0], A, work);
      A[k] = temp1;
    }

    pvt = i + 2;
    while (pvt < 3) {
      if (vn1[1] != 0.0) {
        temp1 = std::abs(A[2048 + i]) / vn1[1];
        temp1 = 1.0 - temp1 * temp1;
        if (temp1 < 0.0) {
          temp1 = 0.0;
        }

        temp2 = vn1[1] / vn2[1];
        temp2 = temp1 * (temp2 * temp2);
        if (temp2 <= 1.4901161193847656E-8) {
          vn1[1] = b_xnrm2(2047 - i, A, i + 2050);
          vn2[1] = vn1[1];
        } else {
          d_sqrt(&temp1);
          vn1[1] *= temp1;
        }
      }

      pvt = 3;
    }
  }
}

/* End of code generation (xgeqp3.cpp) */
