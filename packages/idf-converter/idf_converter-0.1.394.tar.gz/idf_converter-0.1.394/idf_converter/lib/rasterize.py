# vim: ts=4:sts=4:sw=4
#
# @date 2020-09-30
#
# This file is part of IDF converter, a set of tools to convert satellite,
# in-situ and numerical model data into Intermediary Data Format, making them
# compatible with the SEAScope application.
#
# Copyright (C) 2014-2022 OceanDataLab
#
# IDF converter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# IDF converter is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IDF converter. If not, see <https://www.gnu.org/licenses/>.

"""This module contains formatter methods for operations related to the
rasterization of vector features.
"""

import typing
import numpy
import numpy.typing
import PIL.Image
import PIL.ImageDraw
import shapely.geometry

GeoTransform = typing.Tuple[float, float, float, float, float, float]


def polygons_from_coords(linear_rings: typing.List[numpy.typing.NDArray],
                         geotransform: GeoTransform,
                         nrows: int,
                         ncols: int,
                         values: typing.Optional[typing.List[int]] = None
                         ) -> numpy.typing.NDArray:
    """"""
    ulx, dx, _, uly, _, dy = geotransform
    img_type = 'L'
    dtype = 'int'
    if values is None:
        img_type = '1'
        dtype = 'bool'
        values = [1] * len(linear_rings)
    img = PIL.Image.new(img_type, (nrows, ncols), 0)
    pencil = PIL.ImageDraw.Draw(img)
    for i, linear_ring in enumerate(linear_rings):
        coords = [((_[0] - ulx) / dx,
                   (_[1] - uly) / dy) for _ in linear_ring]
        pencil.polygon(coords, fill=values[i], outline=values[i])

    raster = numpy.array(img.getdata(0), dtype=dtype).reshape((ncols, nrows))
    img.close()

    return raster


def polygons_from_shapely(shapes: typing.List[shapely.geometry.Geometry],
                          geotransform: GeoTransform,
                          nrows: int,
                          ncols: int,
                          values: typing.Optional[typing.List[int]] = None
                          ) -> numpy.typing.NDArray:
    """"""
    ulx, dx, _, uly, _, dy = geotransform
    img_type = 'L'
    dtype = 'int'
    if values is None:
        img_type = '1'
        dtype = 'bool'
        values = [1] * len(shapes)
    img = PIL.Image.new(img_type, (nrows, ncols), 0)
    pencil = PIL.ImageDraw.Draw(img)
    for i, shape in enumerate(shapes):
        # print(values[i])
        if isinstance(shape, shapely.geometry.Polygon):
            coords = shape.exterior.coords
            coords = [((_[0] - ulx) / dx,
                       (_[1] - uly) / dy) for _ in coords]
            pencil.polygon(coords, fill=values[i], outline=values[i])
        elif isinstance(shape, shapely.geometry.MultiPolygon):
            for polygon in shape.geoms:
                coords = polygon.exterior.coords
                coords = [((_[0] - ulx) / dx,
                           (_[1] - uly) / dy) for _ in coords]
                pencil.polygon(coords, fill=values[i], outline=values[i])

    raster = numpy.array(img.getdata(0), dtype=dtype).reshape((ncols, nrows))
    img.close()

    return raster
