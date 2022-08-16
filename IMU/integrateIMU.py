"""
Author: @jacobrdavis

A collection of functions for IMU integration.

Contents:
    - demean(x)
    - tupleset(t, i, value)
    - cumtrapz(y, x=None, dx=1.0, axis=-1, initial=None)
    - integrate_acc(a,t,filt) [main]

Log:
    - Aug 2022, J.Davis: created integrateIMU.py
"""
import numpy as np
from numpy import add, diff, asarray

def demean(x):
    """
    Helper function to demean an array

    Input:
        - x, array of values to be demeaned

    Output:
        - x_demean, array of demeaned input values
    """
    x_demean = x - np.mean(x)
    return x_demean

def tupleset(t, i, value):
    """
    Helper function to create tuple set for cumtrapz
    """
    l = list(t)
    l[i] = value
    return tuple(l)

def cumtrapz(y, x=None, dx=1.0, axis=-1, initial=None):
    """
    Cumulatively integrate y(x) using the composite trapezoidal rule.

    Parameters
    ----------
    y : array_like
        Values to integrate.
    x : array_like, optional
        The coordinate to integrate along.  If None (default), use spacing `dx`
        between consecutive elements in `y`.
    dx : int, optional
        Spacing between elements of `y`.  Only used if `x` is None.
    axis : int, optional
        Specifies the axis to cumulate.  Default is -1 (last axis).
    initial : scalar, optional
        If given, uses this value as the first value in the returned result.
        Typically this value should be 0.  Default is None, which means no
        value at ``x[0]`` is returned and `res` has one element less than `y`
        along the axis of integration.

    Returns
    -------
    res : ndarray
        The result of cumulative integration of `y` along `axis`.
        If `initial` is None, the shape is such that the axis of integration
        has one less value than `y`.  If `initial` is given, the shape is equal
        to that of `y`.

    See Also
    --------
    numpy.cumsum, numpy.cumprod
    quad: adaptive quadrature using QUADPACK
    romberg: adaptive Romberg quadrature
    quadrature: adaptive Gaussian quadrature
    fixed_quad: fixed-order Gaussian quadrature
    dblquad: double integrals
    tplquad: triple integrals
    romb: integrators for sampled data
    ode: ODE integrators
    odeint: ODE integrators

    Examples
    --------
    >>> from scipy import integrate
    >>> import matplotlib.pyplot as plt
    >>> x = np.linspace(-2, 2, num=20)
    >>> y = x
    >>> y_int = integrate.cumtrapz(y, x, initial=0)
    >>> plt.plot(x, y_int, 'ro', x, y[0] + 0.5 * x**2, 'b-')
    >>> plt.show()
    """
    y = asarray(y)
    if x is None:
        d = dx
    else:
        x = asarray(x)
        if x.ndim == 1:
            d = diff(x)
            # reshape to correct shape
            shape = [1] * y.ndim
            shape[axis] = -1
            d = d.reshape(shape)
        elif len(x.shape) != len(y.shape):
            raise ValueError("If given, shape of x must be 1-d or the "
                    "same as y.")
        else:
            d = diff(x, axis=axis)

        if d.shape[axis] != y.shape[axis] - 1:
            raise ValueError("If given, length of x along axis must be the "
                             "same as y.")

    nd = len(y.shape)
    slice1 = tupleset((slice(None),)*nd, axis, slice(1, None))
    slice2 = tupleset((slice(None),)*nd, axis, slice(None, -1))
    res = add.accumulate(d * (y[slice1] + y[slice2]) / 2.0, axis)

    if initial is not None:
        if not np.isscalar(initial):
            raise ValueError("`initial` parameter should be a scalar.")

        shape = list(res.shape)
        shape[axis] = 1
        res = np.concatenate([np.ones(shape, dtype=res.dtype) * initial, res],
                             axis=axis)

    return res

def integrate_acc(a,t,filt):
    """
    Helper function to perform double integration of acceleration values

    Input:
        - a, acceleration array
        - t, time array
        - filt, filter function (e.g. lambda function)

    Output:
        - x_demean, array of demeaned input values

    TODO:
        - validate 30 s window -> increase to 120s?
    """
    
    # determine 30 second window to zero out after filtering
    fs = np.mean(np.diff(t))**(-1)
    zeroPts = int(np.round(30*fs))

    ai = a.copy()
    ai[:zeroPts] = 0 # zero initial oscillations from filtering
    ai = demean(ai) #IMU.acc(:,i) - 10.025;

    vi = cumtrapz(y=ai,x=t,initial=0)  # [m/s]
    vi = filt(vi)
    vi[:zeroPts] = 0
    vi = demean(vi) 

    pi = cumtrapz(y=vi,x=t,initial=0)  # [m/s]
    pi = filt(pi)
    pi[:zeroPts] = 0
    pi = demean(pi) 

    return ai,vi,pi


    