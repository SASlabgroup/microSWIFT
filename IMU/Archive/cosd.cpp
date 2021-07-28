/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * cosd.cpp
 *
 * Code generation for function 'cosd'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "cosd.h"
#include "XYZwaves.h"
#include "processIMU_rtwutil.h"

/* Function Definitions */
void b_cosd(double *x)
{
  double absx;
  signed char n;
  if (!((!rtIsInf(*x)) && (!rtIsNaN(*x)))) {
    *x = rtNaN;
  } else {
    *x = rt_remd_snf(*x, 360.0);
    absx = std::abs(*x);
    if (absx > 180.0) {
      if (*x > 0.0) {
        *x -= 360.0;
      } else {
        *x += 360.0;
      }

      absx = std::abs(*x);
    }

    if (absx <= 45.0) {
      *x *= 0.017453292519943295;
      n = 0;
    } else if (absx <= 135.0) {
      if (*x > 0.0) {
        *x = 0.017453292519943295 * (*x - 90.0);
        n = 1;
      } else {
        *x = 0.017453292519943295 * (*x + 90.0);
        n = -1;
      }
    } else if (*x > 0.0) {
      *x = 0.017453292519943295 * (*x - 180.0);
      n = 2;
    } else {
      *x = 0.017453292519943295 * (*x + 180.0);
      n = -2;
    }

    if (n == 0) {
      *x = std::cos(*x);
    } else if (n == 1) {
      *x = -std::sin(*x);
    } else if (n == -1) {
      *x = std::sin(*x);
    } else {
      *x = -std::cos(*x);
    }
  }
}

void c_cosd(double x[2048])
{
  int k;
  double b_x;
  double absx;
  signed char n;
  for (k = 0; k < 2048; k++) {
    if (!((!rtIsInf(x[k])) && (!rtIsNaN(x[k])))) {
      b_x = rtNaN;
    } else {
      b_x = rt_remd_snf(x[k], 360.0);
      absx = std::abs(b_x);
      if (absx > 180.0) {
        if (b_x > 0.0) {
          b_x -= 360.0;
        } else {
          b_x += 360.0;
        }

        absx = std::abs(b_x);
      }

      if (absx <= 45.0) {
        b_x *= 0.017453292519943295;
        n = 0;
      } else if (absx <= 135.0) {
        if (b_x > 0.0) {
          b_x = 0.017453292519943295 * (b_x - 90.0);
          n = 1;
        } else {
          b_x = 0.017453292519943295 * (b_x + 90.0);
          n = -1;
        }
      } else if (b_x > 0.0) {
        b_x = 0.017453292519943295 * (b_x - 180.0);
        n = 2;
      } else {
        b_x = 0.017453292519943295 * (b_x + 180.0);
        n = -2;
      }

      if (n == 0) {
        b_x = std::cos(b_x);
      } else if (n == 1) {
        b_x = -std::sin(b_x);
      } else if (n == -1) {
        b_x = std::sin(b_x);
      } else {
        b_x = -std::cos(b_x);
      }
    }

    x[k] = b_x;
  }
}

/* End of code generation (cosd.cpp) */
