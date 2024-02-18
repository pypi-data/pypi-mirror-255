#  SPDX-License-Identifier: GPL-3.0-or-later

"""
Module that holds miscellaneous functions and classes
"""

# This file is copied from the Rapthor repository (with minor changes):
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/lib/miscellaneous.py

import errno
import pickle
import shutil
from math import ceil, floor, modf

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Point, Polygon
from shapely.prepared import prep


def string2bool(invar):
    """
    Converts a string to a bool

    Parameters
    ----------
    invar : str
        String to be converted

    Returns
    -------
    result : bool
        Converted bool
    """
    if invar is None:
        return None
    if isinstance(invar, bool):
        return invar
    if isinstance(invar, str):
        if "TRUE" in invar.upper() or invar == "1":
            return True
        if "FALSE" in invar.upper() or invar == "0":
            return False
        raise ValueError(
            'input2bool: Cannot convert string "' + invar + '" to boolean!'
        )
    if isinstance(invar, int, float):
        return bool(invar)
    raise TypeError("Unsupported data type:" + str(type(invar)))


def string2list(invar):
    """
    Converts a string to a list

    Parameters
    ----------
    invar : str
        String to be converted

    Returns
    -------
    result : list
        Converted list
    """
    if invar is None:
        return None
    str_list = None
    if isinstance(invar, str):
        invar = invar.strip()
        if invar.startswith("[") and invar.endswith("]"):
            str_list = [f.strip(" '\"") for f in invar.strip("[]").split(",")]
        elif "," in invar:
            str_list = [f.strip(" '\"") for f in invar.split(",")]
        else:
            str_list = [invar.strip(" '\"")]
    elif isinstance(invar, list):
        str_list = [str(f).strip(" '\"") for f in invar]
    else:
        raise TypeError("Unsupported data type:" + str(type(invar)))
    return str_list


def read_vertices(filename):
    """
    Returns facet vertices stored in input file
    """
    with open(filename, "rb") as vertices_file:
        vertices = pickle.load(vertices_file)
    return vertices


def rasterize(verts, data, blank_value=0):
    """
    Rasterize a polygon into a data array

    Parameters
    ----------
    verts : list of (x, y) tuples
        List of input vertices of polygon to rasterize
    data : 2-D array
        Array into which rasterize polygon
    blank_value : int or float, optional
        Value to use for blanking regions outside the poly

    Returns
    -------
    data : 2-D array
        Array with rasterized polygon
    """
    poly = Polygon(verts)
    prepared_polygon = prep(poly)

    # Mask everything outside of the polygon plus its border (outline) with
    # zeros (inside polygon plus border are ones)
    mask = Image.new("L", (data.shape[0], data.shape[1]), 0)
    ImageDraw.Draw(mask).polygon(verts, outline=1, fill=1)
    data *= mask

    # Now check the border precisely
    mask = Image.new("L", (data.shape[0], data.shape[1]), 0)
    ImageDraw.Draw(mask).polygon(verts, outline=1, fill=0)
    masked_ind = np.where(np.array(mask).transpose())
    points = [Point(xm, ym) for xm, ym in zip(masked_ind[0], masked_ind[1])]
    outside_points = [v for v in points if prepared_polygon.disjoint(v)]
    for outside_point in outside_points:
        data[int(outside_point.y), int(outside_point.x)] = 0

    if blank_value != 0:
        data[data == 0] = blank_value

    return data


def ra2hhmmss(deg):
    """
    Convert RA coordinate (in degrees) to HH MM SS

    Parameters
    ----------
    deg : float
        The RA coordinate in degrees

    Returns
    -------
    hh : int
        The hour (HH) part
    mm : int
        The minute (MM) part
    ss : float
        The second (SS) part
    """
    deg = deg % 360
    x, hh = modf(deg / 15)  # pylint: disable=C0103
    x, mm = modf(x * 60)  # pylint: disable=C0103
    ss = x * 60  # pylint: disable=C0103

    return (int(hh), int(mm), ss)


def dec2ddmmss(deg):
    """
    Convert Dec coordinate (in degrees) to DD MM SS

    Parameters
    ----------
    deg : float
        The Dec coordinate in degrees

    Returns
    -------
    dd : int
        The degree (DD) part
    mm : int
        The arcminute (MM) part
    ss : float
        The arcsecond (SS) part
    sign : int
        The sign (+/-)
    """
    sign = -1 if deg < 0 else 1
    x, dd = modf(abs(deg))  # pylint: disable=C0103
    x, ma = modf(x * 60)  # pylint: disable=C0103
    sa = x * 60  # pylint: disable=C0103

    return (int(dd), int(ma), sa, sign)


def normalize_ra(num):
    """
    Normalize RA to be in the range [0, 360).

    Based on https://github.com/phn/angles/blob/master/angles.py

    Parameters
    ----------
    num : float
        The RA in degrees to be normalized.

    Returns
    -------
    res : float
        RA in degrees in the range [0, 360).
    """
    lower = 0.0
    upper = 360.0
    res = num
    if num > upper or num == lower:
        num = lower + abs(num + upper) % (abs(lower) + abs(upper))
    if num < lower or num == upper:
        num = upper - abs(num - lower) % (abs(lower) + abs(upper))
    res = lower if num == upper else num

    return res


def normalize_dec(num):
    """
    Normalize Dec to be in the range [-90, 90].

    Based on https://github.com/phn/angles/blob/master/angles.py

    Parameters
    ----------
    num : float
        The Dec in degrees to be normalized.

    Returns
    -------
    res : float
        Dec in degrees in the range [-90, 90].
    """
    lower = -90.0
    upper = 90.0
    res = num
    total_length = abs(lower) + abs(upper)
    if num < -total_length:
        num += ceil(num / (-2 * total_length)) * 2 * total_length
    if num > total_length:
        num -= floor(num / (2 * total_length)) * 2 * total_length
    if num > upper:
        num = total_length - num
    if num < lower:
        num = -total_length - num
    res = num

    return res


def _float_approx_equal(x, y, tol=None, rel=None):  # pylint: disable=C0103
    if tol is rel is None:
        raise TypeError(
            "cannot specify both absolute and relative errors are None"
        )
    tests = []
    if tol is not None:
        tests.append(tol)
    if rel is not None:
        tests.append(rel * abs(x))
    assert tests
    return abs(x - y) <= max(tests)


def approx_equal(x, y, *args, **kwargs):  # pylint: disable=C0103
    """
    Return True if x and y are approximately equal, otherwise False

    If x and y are floats, return True if y is within either absolute error
    tol or relative error rel of x. You can disable either the absolute or
    relative check by passing None as tol or rel (but not both).

    Parameters
    ----------
    x : float
        First value to be compared
    y : float
        Second value to be compared
    """
    if not type(x) is type(y) is float:
        # Skip checking for __approx_equal__ in the common case of two floats.
        methodname = "__approx_equal__"
        # Allow the objects to specify what they consider "approximately
        # equal", giving precedence to x. If either object has the appropriate
        # method, we pass on any optional arguments untouched.
        for a, b in ((x, y), (y, x)):  # pylint: disable=C0103
            try:
                method = getattr(a, methodname)
            except AttributeError:
                continue
            else:
                result = method(b, *args, **kwargs)
                if result is NotImplemented:
                    continue
                return bool(result)
    # If we get here without returning, then neither x nor y knows how to do an
    # approximate equal comparison (or are both floats). Fall back to a numeric
    # comparison.
    return _float_approx_equal(x, y, *args, **kwargs)


def delete_directory(dirname):
    """
    Recursively delete a directory tree, without failing if it does not exist

    Parameters
    ----------
    dirname : str
        Path of directory
    """
    try:
        shutil.rmtree(dirname)
    except OSError as e:  # pylint: disable=C0103
        if e.errno != errno.ENOENT:
            raise e
