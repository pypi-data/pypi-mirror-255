#  SPDX-License-Identifier: GPL-3.0-or-later
# Rapthor: LOFAR DDE Pipeline
# Copyright (C) 2023, Team Rapthor
# https://git.astron.nl/RD/rapthor/-/blob/master/LICENSE

"""
Module that holds functions and classes related to faceting
"""

# This file is copied from the Rapthor repository (with minor changes):
# https://git.astron.nl/RD/rapthor/-/tree/master/rapthor/lib/facet.py
# pylint: skip-file

import numpy as np
import scipy as sp

from ska_sdp_wflow_low_selfcal.pipeline.support.miscellaneous import (
    make_wcs,
    radec2xy,
    xy2radec,
)


def make_facet_polygons(ra_cal, dec_cal, ra_mid, dec_mid, width_ra, width_dec):
    """
    Makes a Voronoi tessellation and returns the resulting facet centers
    and polygons

    Parameters
    ----------
    ra_cal : array
        RA values in degrees of calibration directions
    dec_cal : array
        Dec values in degrees of calibration directions
    ra_mid : float
        RA in degrees of bounding box center
    dec_mid : float
        Dec in degrees of bounding box center
    width_ra : float
        Width of bounding box in RA in degrees, corrected to Dec = 0
    width_dec : float
        Width of bounding box in Dec in degrees

    Returns
    -------
    facet_points, facet_polys : list of tuples, list of arrays
        List of facet points (centers) as (RA, Dec) tuples in degrees and
        list of facet polygons (vertices) as [RA, Dec] arrays in degrees
        (each of shape N x 2, where N is the number of vertices in a given
        facet)
    """
    # Build the bounding box corner coordinates
    if width_ra <= 0.0 or width_dec <= 0.0:
        raise ValueError("The RA/Dec width cannot be zero or less")
    wcs_pixel_scale = 20.0 / 3600.0  # 20"/pixel
    wcs = make_wcs(ra_mid, dec_mid, wcs_pixel_scale)
    x_cal, y_cal = radec2xy(wcs, ra_cal, dec_cal)
    x_mid, y_mid = radec2xy(wcs, [ra_mid], [dec_mid])
    width_x = width_ra / wcs_pixel_scale / 2.0
    width_y = width_dec / wcs_pixel_scale / 2.0
    bounding_box = np.array(
        [
            x_mid[0] - width_x,
            x_mid[0] + width_x,
            y_mid[0] - width_y,
            y_mid[0] + width_y,
        ]
    )

    # Tessellate and convert resulting facet polygons from (x, y) to (RA, Dec)
    vor = voronoi(np.stack((x_cal, y_cal)).T, bounding_box)
    facet_polys = []
    for region in vor.filtered_regions:
        vertices = vor.vertices[region + [region[0]], :]
        ra, dec = xy2radec(wcs, vertices[:, 0], vertices[:, 1])
        vertices = np.stack((ra, dec)).T
        facet_polys.append(vertices)
    facet_points = []
    for point in vor.filtered_points:
        ra, dec = xy2radec(wcs, [point[0]], [point[1]])
        facet_points.append((ra[0], dec[0]))

    return facet_points, facet_polys


def in_box(cal_coords, bounding_box):
    """
    Checks if coordinates are inside the bounding box

    Parameters
    ----------
    cal_coords : array
        Array of x, y coordinates
    bounding_box : array
        Array defining the bounding box as [minx, maxx, miny, maxy]

    Returns
    -------
    inside : array
        Bool array with True for inside and False if not
    """
    return np.logical_and(
        np.logical_and(
            bounding_box[0] <= cal_coords[:, 0],
            cal_coords[:, 0] <= bounding_box[1],
        ),
        np.logical_and(
            bounding_box[2] <= cal_coords[:, 1],
            cal_coords[:, 1] <= bounding_box[3],
        ),
    )


def voronoi(cal_coords, bounding_box):
    """
    Produces a Voronoi tessellation for the given coordinates and bounding box

    Parameters
    ----------
    cal_coords : array
        Array of x, y coordinates
    bounding_box : array
        Array defining the bounding box as [minx, maxx, miny, maxy]

    Returns
    -------
    vor : Voronoi object
        The resulting Voronoi object
    """
    eps = 1e-6

    # Select calibrators inside the bounding box
    i = in_box(cal_coords, bounding_box)

    # Mirror points
    points_center = cal_coords[i, :]
    points_left = np.copy(points_center)
    points_left[:, 0] = bounding_box[0] - (points_left[:, 0] - bounding_box[0])
    points_right = np.copy(points_center)
    points_right[:, 0] = bounding_box[1] + (
        bounding_box[1] - points_right[:, 0]
    )
    points_down = np.copy(points_center)
    points_down[:, 1] = bounding_box[2] - (points_down[:, 1] - bounding_box[2])
    points_up = np.copy(points_center)
    points_up[:, 1] = bounding_box[3] + (bounding_box[3] - points_up[:, 1])
    points = np.append(
        points_center,
        np.append(
            np.append(points_left, points_right, axis=0),
            np.append(points_down, points_up, axis=0),
            axis=0,
        ),
        axis=0,
    )

    # Compute Voronoi, sorting the output regions to match the order of the
    # input coordinates
    vor = sp.spatial.Voronoi(points)
    sorted_regions = np.array(vor.regions, dtype=object)[
        np.array(vor.point_region)
    ]
    vor.regions = sorted_regions.tolist()

    # Filter regions
    regions = []
    for region in vor.regions:
        flag = True
        for index in region:
            if index == -1:
                flag = False
                break
            else:
                x = vor.vertices[index, 0]
                y = vor.vertices[index, 1]
                if not (
                    bounding_box[0] - eps <= x
                    and x <= bounding_box[1] + eps
                    and bounding_box[2] - eps <= y
                    and y <= bounding_box[3] + eps
                ):
                    flag = False
                    break
        if region and flag:
            regions.append(region)
    vor.filtered_points = points_center
    vor.filtered_regions = regions

    return vor


def make_ds9_region_file(center_coords, facet_polygons, outfile, names=None):
    """
    Make a ds9 region file for given polygons and centers

    Parameters
    ----------
    center_coords : list of tuples
        List of (RA, Dec) of the facet center coordinates
    facet_polygons : list of arrays
        List of [RA, Dec] arrays of the facet vertices (each of shape N x 2,
        where N is the number of vertices in a given facet)
    outfile : str
        Name of output region file
    names : list, optional
        List of names of the facets
    """
    lines = []
    lines.append(
        "# Region file format: DS9 version 4.0\nglobal color=green "
        'font="helvetica 10 normal" select=1 highlite=1 edit=1 '
        "move=1 delete=1 include=1 fixed=0 source=1\nfk5\n"
    )
    if names is None:
        names = [None] * len(center_coords)
    if not (len(names) == len(center_coords) == len(facet_polygons)):
        raise ValueError(
            "Input lists of facet coordinates, vertices, and names "
            "must have the same length"
        )
    for name, center_coord, vertices in zip(
        names, center_coords, facet_polygons
    ):
        radec_list = []
        RAs = vertices.T[0]
        Decs = vertices.T[1]
        for ra, dec in zip(RAs, Decs):
            radec_list.append("{0}, {1}".format(ra, dec))
        lines.append("polygon({0})\n".format(", ".join(radec_list)))
        if name is None:
            lines.append(
                "point({0}, {1})\n".format(center_coord[0], center_coord[1])
            )
        else:
            lines.append(
                "point({0}, {1}) # text={2}\n".format(
                    center_coord[0], center_coord[1], name
                )
            )

    with open(outfile, "w") as f:
        f.writelines(lines)
