/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * xzlarf.cpp
 *
 * Code generation for function 'xzlarf'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "xzlarf.h"
#include "xgerc.h"
#include "xgemv.h"

/* Function Declarations */
static int ilazlc(int m, int n, const double A[4096]);

/* Function Definitions */
static int ilazlc(int m, int n, const double A[4096])
{
  int j;
  boolean_T exitg2;
  int ia;
  int exitg1;
  j = n;
  exitg2 = false;
  while ((!exitg2) && (j > 0)) {
    ia = 2049;
    do {
      exitg1 = 0;
      if (ia <= m + 2048) {
        if (A[ia - 1] != 0.0) {
          exitg1 = 1;
        } else {
          ia++;
        }
      } else {
        j = 0;
        exitg1 = 2;
      }
    } while (exitg1 == 0);

    if (exitg1 == 1) {
      exitg2 = true;
    }
  }

  return j;
}

void xzlarf(int m, int n, int iv0, double tau, double C[4096], double work[2])
{
  int lastv;
  int lastc;
  if (tau != 0.0) {
    lastv = m;
    lastc = iv0 + m;
    while ((lastv > 0) && (C[lastc - 2] == 0.0)) {
      lastv--;
      lastc--;
    }

    lastc = ilazlc(lastv, n, C);
  } else {
    lastv = 0;
    lastc = 0;
  }

  if (lastv > 0) {
    xgemv(lastv, lastc, C, C, iv0, work);
    xgerc(lastv, lastc, -tau, iv0, work, C);
  }
}

/* End of code generation (xzlarf.cpp) */
