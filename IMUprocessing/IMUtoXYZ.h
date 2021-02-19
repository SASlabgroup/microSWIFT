/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * IMUtoXYZ.h
 *
 * Code generation for function 'IMUtoXYZ'
 *
 */

#ifndef IMUTOXYZ_H
#define IMUTOXYZ_H

/* Include files */
#include <cmath>
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_defines.h"
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "processIMU_types.h"

/* Function Declarations */
extern void IMUtoXYZ(double ax[2048], double ay[2048], double az[2048], const
                     double gx[2048], const double gy[2048], const double gz
                     [2048], double mx[2048], double my[2048], double mz[2048],
                     double mxo, double myo, double Wd, double fs, double x[2048],
                     double y[2048], double z[2048], double roll[2048], double
                     pitch[2048], double yaw[2048], double heading[2048]);

#endif

/* End of code generation (IMUtoXYZ.h) */
