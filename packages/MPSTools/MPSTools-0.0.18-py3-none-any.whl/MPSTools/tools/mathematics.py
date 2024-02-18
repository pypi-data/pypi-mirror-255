#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy


def get_rho_gradient(mesh: numpy.ndarray, coordinate_system) -> numpy.ndarray:
    """
    Gets the gradient in the rho component axis (polar coordinate).
    Equation is given as:
    .. math:
        \\partial{f}{r} &= \\partial{f}{x} \\partial{x}{r} \\partial{f}{y} \\partial{y}{r} \\
        \\partial{f}{r} &= \\partial{f}{x} \\cos(\theta) \\partial{f}{y} \\sin(\theta)


    :param      mesh:             The mesh
    :type       mesh:             numpy.ndarray
    :param      coordinate_system:  The coordinates axis
    :type       coordinate_system:  Axis

    :returns:   The rho gradient.
    :rtype:     numpy.ndarray
    """
    y_gradient, x_gradient = gradientO4(
        mesh,
        coordinate_system.dx,
        coordinate_system.dy
    )

    theta_mesh = numpy.arctan2(coordinate_system.y_mesh.astype('float'), coordinate_system.x_mesh.astype('float'))

    gradient = (x_gradient * numpy.cos(theta_mesh) + y_gradient * numpy.sin(theta_mesh))

    return gradient


# 4th order accurate gradient function based on 2nd order version from http://projects.scipy.org/scipy/numpy/browser/trunk/numpy/lib/function_base.py
def gradientO4(f, *varargs) -> tuple:
    """Calculate the fourth-order-accurate gradient of an N-dimensional scalar function.
    Uses central differences on the interior and first differences on boundaries
    to give the same shape.
    Inputs:
      f -- An N-dimensional array giving samples of a scalar function
      varargs -- 0, 1, or N scalars giving the sample distances in each direction
    Outputs:
      N arrays of the same shape as f giving the derivative of f with respect
       to each dimension.
    """
    N = len(f.shape)  # number of dimensions
    n = len(varargs)
    dx = list(varargs)

    # use central differences on interior and first differences on endpoints

    outvals = []

    # create slice objects --- initially all are [:, :, ..., :]
    slice0 = [slice(None)] * N
    slice1 = [slice(None)] * N
    slice2 = [slice(None)] * N
    slice3 = [slice(None)] * N
    slice4 = [slice(None)] * N

    otype = f.dtype.char
    if otype not in ['f', 'd', 'F', 'D']:
        otype = 'd'

    for axis in range(N):
        # select out appropriate parts for this dimension
        out = numpy.zeros(f.shape, f.dtype.char)

        slice0[axis] = slice(2, -2)
        slice1[axis] = slice(None, -4)
        slice2[axis] = slice(1, -3)
        slice3[axis] = slice(3, -1)
        slice4[axis] = slice(4, None)
        # 1D equivalent -- out[2:-2] = (f[:4] - 8*f[1:-3] + 8*f[3:-1] - f[4:])/12.0
        out[tuple(slice0)] = (f[tuple(slice1)] - 8.0 * f[tuple(slice2)] + 8.0 * f[tuple(slice3)] - f[tuple(slice4)]) / 12.0

        slice0[axis] = slice(None, 2)
        slice1[axis] = slice(1, 3)
        slice2[axis] = slice(None, 2)
        # 1D equivalent -- out[0:2] = (f[1:3] - f[0:2])
        out[tuple(slice0)] = (f[tuple(slice1)] - f[tuple(slice2)])

        slice0[axis] = slice(-2, None)
        slice1[axis] = slice(-2, None)
        slice2[axis] = slice(-3, -1)
        # 1D equivalent -- out[-2:] = (f[-2:] - f[-3:-1])
        out[tuple(slice0)] = (f[tuple(slice1)] - f[tuple(slice2)])

        # divide by step size
        outvals.append(out / dx[axis])

        # reset the slice object in this dimension to ":"
        slice0[axis] = slice(None)
        slice1[axis] = slice(None)
        slice2[axis] = slice(None)
        slice3[axis] = slice(None)
        slice4[axis] = slice(None)

    if N == 1:
        return outvals[0]
    else:
        return outvals
