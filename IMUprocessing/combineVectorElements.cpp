/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * combineVectorElements.cpp
 *
 * Code generation for function 'combineVectorElements'
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "processIMU.h"
#include "combineVectorElements.h"

/* Function Definitions */
double combineVectorElements(const double x[2048])
{
  double y;
  int k;
  y = x[0];
  for (k = 0; k < 2047; k++) {
    y += x[k + 1];
  }

  return y;
}

/* End of code generation (combineVectorElements.cpp) */
