/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * qrsolve.cpp
 *
 * Code generation for function 'qrsolve'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "qrsolve.h"
#include "processIMU_emxutil.h"
#include "xnrm2.h"
#include "xscal.h"
#include "ixamax.h"
#include "processIMU_rtwutil.h"

/* Function Declarations */
static void LSQFromQR(const emxArray_real_T *A, const double tau_data[], const
                      int jpvt[2], emxArray_real_T *B, int rankA, double Y[2]);

/* Function Definitions */
static void LSQFromQR(const emxArray_real_T *A, const double tau_data[], const
                      int jpvt[2], emxArray_real_T *B, int rankA, double Y[2])
{
  int i;
  int m;
  int j;
  double wj;
  for (i = 0; i < 2; i++) {
    Y[i] = 0.0;
  }

  m = A->size[0];
  for (j = 0; j < 2; j++) {
    if (tau_data[j] != 0.0) {
      wj = B->data[j];
      for (i = j + 1; i + 1 <= m; i++) {
        wj += A->data[i + A->size[0] * j] * B->data[i];
      }

      wj *= tau_data[j];
      if (wj != 0.0) {
        B->data[j] -= wj;
        for (i = j + 1; i + 1 <= m; i++) {
          B->data[i] -= A->data[i + A->size[0] * j] * wj;
        }
      }
    }
  }

  for (i = 0; i + 1 <= rankA; i++) {
    Y[jpvt[i] - 1] = B->data[i];
  }

  for (j = rankA - 1; j + 1 > 0; j--) {
    Y[jpvt[j] - 1] /= A->data[j + A->size[0] * j];
    i = 1;
    while (i <= j) {
      Y[jpvt[0] - 1] -= Y[jpvt[j] - 1] * A->data[A->size[0] * j];
      i = 2;
    }
  }
}

void qrsolve(const emxArray_real_T *A, const emxArray_real_T *B, double Y[2])
{
  emxArray_real_T *b_A;
  int i5;
  int k;
  int m;
  int i;
  int jpvt[2];
  int pvt;
  double work[2];
  double xnorm;
  double vn2[2];
  int i_i;
  int mmi;
  double vn1[2];
  emxArray_real_T *b_B;
  int ix;
  double temp2;
  int iy;
  double d9;
  double tau_data[2];
  int lastv;
  int lastc;
  boolean_T exitg2;
  int exitg1;
  emxInit_real_T(&b_A, 2);
  i5 = b_A->size[0] * b_A->size[1];
  b_A->size[0] = A->size[0];
  b_A->size[1] = 2;
  emxEnsureCapacity_real_T(b_A, i5);
  k = A->size[0] * A->size[1];
  for (i5 = 0; i5 < k; i5++) {
    b_A->data[i5] = A->data[i5];
  }

  m = A->size[0];
  for (i = 0; i < 2; i++) {
    jpvt[i] = 1 + i;
    work[i] = 0.0;
  }

  k = 1;
  for (pvt = 0; pvt < 2; pvt++) {
    xnorm = d_xnrm2(m, A, k);
    vn2[pvt] = xnorm;
    k += m;
    vn1[pvt] = xnorm;
  }

  for (i = 0; i < 2; i++) {
    i_i = i + i * m;
    mmi = (m - i) - 1;
    pvt = (i + ixamax(2 - i, vn1, i + 1)) - 1;
    if (pvt + 1 != i + 1) {
      ix = m * pvt;
      iy = m * i;
      for (k = 1; k <= m; k++) {
        xnorm = b_A->data[ix];
        b_A->data[ix] = b_A->data[iy];
        b_A->data[iy] = xnorm;
        ix++;
        iy++;
      }

      k = jpvt[pvt];
      jpvt[pvt] = jpvt[i];
      jpvt[i] = k;
      vn1[pvt] = vn1[i];
      vn2[pvt] = vn2[i];
    }

    temp2 = b_A->data[i_i];
    d9 = 0.0;
    xnorm = d_xnrm2(mmi, b_A, i_i + 2);
    if (xnorm != 0.0) {
      xnorm = rt_hypotd_snf(b_A->data[i_i], xnorm);
      if (b_A->data[i_i] >= 0.0) {
        xnorm = -xnorm;
      }

      if (std::abs(xnorm) < 1.0020841800044864E-292) {
        pvt = 0;
        do {
          pvt++;
          xscal(mmi, 9.9792015476736E+291, b_A, i_i + 2);
          xnorm *= 9.9792015476736E+291;
          temp2 *= 9.9792015476736E+291;
        } while (!(std::abs(xnorm) >= 1.0020841800044864E-292));

        xnorm = rt_hypotd_snf(temp2, d_xnrm2(mmi, b_A, i_i + 2));
        if (temp2 >= 0.0) {
          xnorm = -xnorm;
        }

        d9 = (xnorm - temp2) / xnorm;
        xscal(mmi, 1.0 / (temp2 - xnorm), b_A, i_i + 2);
        for (k = 1; k <= pvt; k++) {
          xnorm *= 1.0020841800044864E-292;
        }

        temp2 = xnorm;
      } else {
        d9 = (xnorm - b_A->data[i_i]) / xnorm;
        temp2 = 1.0 / (b_A->data[i_i] - xnorm);
        xscal(mmi, temp2, b_A, i_i + 2);
        temp2 = xnorm;
      }
    }

    tau_data[i] = d9;
    b_A->data[i_i] = temp2;
    if (i + 1 < 2) {
      temp2 = b_A->data[i_i];
      b_A->data[i_i] = 1.0;
      if (tau_data[0] != 0.0) {
        lastv = 1 + mmi;
        k = i_i + mmi;
        while ((lastv > 0) && (b_A->data[k] == 0.0)) {
          lastv--;
          k--;
        }

        lastc = 1;
        exitg2 = false;
        while ((!exitg2) && (lastc > 0)) {
          pvt = m;
          do {
            exitg1 = 0;
            if (pvt + 1 <= m + lastv) {
              if (b_A->data[pvt] != 0.0) {
                exitg1 = 1;
              } else {
                pvt++;
              }
            } else {
              lastc = 0;
              exitg1 = 2;
            }
          } while (exitg1 == 0);

          if (exitg1 == 1) {
            exitg2 = true;
          }
        }
      } else {
        lastv = 0;
        lastc = 0;
      }

      if (lastv > 0) {
        if (lastc != 0) {
          work[0] = 0.0;
          iy = 0;
          for (k = m + 1; k <= 1 + m; k += m) {
            ix = i_i;
            xnorm = 0.0;
            i5 = (k + lastv) - 1;
            for (pvt = k; pvt <= i5; pvt++) {
              xnorm += b_A->data[pvt - 1] * b_A->data[ix];
              ix++;
            }

            work[iy] += xnorm;
            iy++;
          }
        }

        if (!(-tau_data[0] == 0.0)) {
          k = m;
          iy = 0;
          pvt = 1;
          while (pvt <= lastc) {
            if (work[iy] != 0.0) {
              xnorm = work[iy] * -tau_data[0];
              ix = i_i;
              i5 = lastv + k;
              for (pvt = k; pvt + 1 <= i5; pvt++) {
                b_A->data[pvt] += b_A->data[ix] * xnorm;
                ix++;
              }
            }

            iy++;
            k += m;
            pvt = 2;
          }
        }
      }

      b_A->data[i_i] = temp2;
    }

    pvt = i + 2;
    while (pvt < 3) {
      if (vn1[1] != 0.0) {
        xnorm = std::abs(b_A->data[i + b_A->size[0]]) / vn1[1];
        xnorm = 1.0 - xnorm * xnorm;
        if (xnorm < 0.0) {
          xnorm = 0.0;
        }

        temp2 = vn1[1] / vn2[1];
        temp2 = xnorm * (temp2 * temp2);
        if (temp2 <= 1.4901161193847656E-8) {
          vn1[1] = d_xnrm2(mmi, b_A, (i + m) + 2);
          vn2[1] = vn1[1];
        } else {
          vn1[1] *= std::sqrt(xnorm);
        }
      }

      pvt = 3;
    }
  }

  pvt = 0;
  xnorm = (double)b_A->size[0] * std::abs(b_A->data[0]) * 2.2204460492503131E-16;
  while ((pvt < 2) && (!(std::abs(b_A->data[pvt + b_A->size[0] * pvt]) <= xnorm)))
  {
    pvt++;
  }

  emxInit_real_T1(&b_B, 1);
  i5 = b_B->size[0];
  b_B->size[0] = B->size[0];
  emxEnsureCapacity_real_T1(b_B, i5);
  k = B->size[0];
  for (i5 = 0; i5 < k; i5++) {
    b_B->data[i5] = B->data[i5];
  }

  LSQFromQR(b_A, tau_data, jpvt, b_B, pvt, Y);
  emxFree_real_T(&b_B);
  emxFree_real_T(&b_A);
}

int rankFromQR(const double A[4096])
{
  int r;
  double tol;
  r = 0;
  tol = 2048.0 * std::abs(A[0]) * 2.2204460492503131E-16;
  while ((r < 2) && (!(std::abs(A[r + (r << 11)]) <= tol))) {
    r++;
  }

  return r;
}

/* End of code generation (qrsolve.cpp) */
