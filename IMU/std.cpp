/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * std.cpp
 *
 * Code generation for function 'std'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "std.h"
#include "xnrm2.h"
#include "combineVectorElements.h"

/* Function Definitions */
double b_std(const double x[2048])
{
  double xbar;
  int k;
  double absdiff[2048];
  xbar = combineVectorElements(x) / 2048.0;
  for (k = 0; k < 2048; k++) {
    absdiff[k] = std::abs(x[k] - xbar);
  }

  return c_xnrm2(absdiff) / 45.243784103454473;
}

double c_std(const double x[3])
{
  double y;
  double xbar;
  int k;
  double scale;
  double absdiff;
  double t;
  xbar = x[0];
  for (k = 0; k < 2; k++) {
    xbar += x[k + 1];
  }

  xbar /= 3.0;
  y = 0.0;
  scale = 3.3121686421112381E-170;
  for (k = 0; k < 3; k++) {
    absdiff = std::abs(x[k] - xbar);
    if (absdiff > scale) {
      t = scale / absdiff;
      y = 1.0 + y * t * t;
      scale = absdiff;
    } else {
      t = absdiff / scale;
      y += t * t;
    }
  }

  y = scale * std::sqrt(y);
  y /= 1.4142135623730951;
  return y;
}

/* End of code generation (std.cpp) */
