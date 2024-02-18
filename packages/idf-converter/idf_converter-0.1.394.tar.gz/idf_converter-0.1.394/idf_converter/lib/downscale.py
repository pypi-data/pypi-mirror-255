# vim: ts=4:sts=4:sw=4
#
# @date 2019-09-25
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

import os
import numpy
import typing
import logging
import netCDF4

logger = logging.getLogger(__name__)

DIMNAMES = ['lat', 'lon', 'y', 'x', 'row', 'cell']
DIMGCPNAMES = ['{}_gcp'.format(dimname) for dimname in DIMNAMES]
VARGCPNAMES = ['lat_gcp', 'lon_gcp']
VARINDEXGCPNAMES = ['index_{}_gcp'.format(dimname) for dimname in DIMNAMES]


class MultiTimeGranuleError(ValueError):
    """Error raised when the input IDF file contains more than one time value.
    Note: downscaling is not supported for time-dependent data model."""
    pass


class UnknownDimension(ValueError):
    """Error raised when a dimension of the input file is neither a temporal,
    a spatial or a GCP dimension."""
    def __init__(self, dim_name: str) -> None:
        """"""
        self.dim_name = dim_name


class MaskedValuesFound(ValueError):
    """Error raised when masked values are found in the data array before it is
    assigned to a variable in the output file. At this point the data array
    should contain fill/missing values instead of masked ones."""
    pass


class DownscaleFactorNotSupported(ValueError):
    """Error raised when the downscale factor is so big that it would not be
    possible to define a standard data type for storing the count of valid
    data (i.e. risk of overflowing uint64 data type)."""
    def __init__(self, factor: int) -> None:
        """"""
        self.factor = factor


class IncompatibleVariableShape(ValueError):
    """Error raised when the shape of the input variable does not count exactly
    three axes, which is the shape expected for geophysical variables in IDF
    files. It means that the downscaling method does not support extra
    dimensions such as depth or (k, phi)."""
    def __init__(self, name: str, shape: typing.Tuple[int]) -> None:
        """"""
        self.var_name = name
        self.var_shape = shape


class InvalidGCPIndexShape(ValueError):
    """Error raised when a GCP index variable from the input file has more than
    one dimension, which should never happen."""
    def __init__(self, name: str, shape: typing.Tuple[int]) -> None:
        """"""
        self.var_name = name
        self.var_shape = shape


class MaxGCPIndexDoesNotMatchGCPDimension(ValueError):
    """Error raised if the max value stored in the GCP index variable for an
    axis will not match the size of the dimension associated with this axis."""
    def __init__(self, name: str, dim_name: str, max_value: int,
                 dim_size: int) -> None:
        """"""
        self.var_name = name
        self.dim_name = dim_name
        self.dim_size = dim_size
        self.max_value = max_value


def downscale(idf_path: str,
              output_dir: typing.Optional[str] = None,
              min_factor: typing.Optional[int] = None,
              max_factor: typing.Optional[int] = None) -> None:
    """
    """
    if output_dir is None:
        output_dir = os.path.dirname(idf_path)

    os.makedirs(output_dir, exist_ok=True)

    input_idf = netCDF4.Dataset(idf_path, 'r')
    input_factor = input_idf.idf_subsampling_factor
    if min_factor is None:
        min_factor = input_factor + 1
    if max_factor is None:
        max_factors = []
        # compute how many times each dimension can be subsampled
        for input_dim_name, input_dim in input_idf.dimensions.items():
            if input_dim_name in DIMGCPNAMES:
                float_factor = numpy.log(len(input_dim) - 1) / numpy.log(2.)
                _factor = numpy.ceil(float_factor).astype('int')
                max_factors.append(input_factor + _factor)
        max_factor = max(max_factors)

    for factor in range(min_factor, max_factor + 1):
        downfactor = 2 ** (factor - input_factor)
        fname = '{}_idf_{:02d}.nc'.format(input_idf.idf_granule_id, factor)
        output_path = os.path.join(output_dir, fname)
        output_idf = netCDF4.Dataset(output_path, 'w', format='NETCDF4')

        # Dimensions
        for input_dim_name, input_dim in input_idf.dimensions.items():
            if 'time' == input_dim_name:
                if len(input_dim) != 1:
                    raise MultiTimeGranuleError
                if input_dim.isunlimited():
                    output_dim = output_idf.createDimension(input_dim_name,
                                                            None)
                else:
                    output_dim = output_idf.createDimension(input_dim_name,
                                                            len(input_dim))
            elif input_dim_name in DIMNAMES:
                _dimlen = len(input_dim) / float(downfactor)
                dimlen = numpy.ceil(_dimlen).astype('int32')
                output_dim = output_idf.createDimension(input_dim_name, dimlen)  # noqa
            elif input_dim_name in DIMGCPNAMES:
                _dimlen = (len(input_dim) - 1) / float(downfactor)
                dimlen = numpy.ceil(_dimlen).astype('int32') + 1
                output_dim = output_idf.createDimension(input_dim_name, dimlen)  # noqa
            else:
                raise UnknownDimension(input_dim_name)

        # Variables
        for input_var_name, input_var in input_idf.variables.items():
            _filters = input_var.filters()
            zlib = _filters.get('zlib', True)
            complevel = _filters.get('complevel', 4)
            shuffle = _filters.get('shuffle', True)
            fletcher32 = _filters.get('fletcher32', False)
            contiguous = ('contiguous' == input_var.chunking())
            endian = input_var.endian()
            lsd = input_var.quantization()

            # Cannot use the same chunking as the original for the downscaled
            # IDF files as the dimensions have different sizes
            chunksizes = None

            if '_FillValue' in input_var.ncattrs():
                fvalue = input_var._FillValue
                output_var = output_idf.createVariable(
                                                input_var_name,
                                                input_var.datatype,
                                                input_var.dimensions,
                                                zlib=zlib,
                                                complevel=complevel,
                                                shuffle=shuffle,
                                                fletcher32=fletcher32,
                                                contiguous=contiguous,
                                                chunksizes=chunksizes,
                                                least_significant_digit=lsd,
                                                endian=endian,
                                                fill_value=fvalue)
            else:
                output_var = output_idf.createVariable(
                                                input_var_name,
                                                input_var.datatype,
                                                input_var.dimensions,
                                                zlib=zlib,
                                                complevel=complevel,
                                                shuffle=shuffle,
                                                fletcher32=fletcher32,
                                                contiguous=contiguous,
                                                chunksizes=chunksizes,
                                                least_significant_digit=lsd,
                                                endian=endian)

            for attrname in input_var.ncattrs():
                if '_FillValue' == attrname:
                    continue
                output_var.setncattr(attrname, input_var.getncattr(attrname))
            if input_var_name == 'time':
                output_var[:] = input_var[:]
            elif (input_var_name == 'crs') and 'y_gcp' in input_idf.dimensions:
                output_var[:] = input_var[:]
            elif input_var_name in VARGCPNAMES:
                subind = []
                for idim in range(len(input_var.shape)):
                    _subind = numpy.arange(0, input_var.shape[idim],
                                           downfactor)
                    if numpy.mod(input_var.shape[idim] - 1, downfactor) != 0:
                        _subind = numpy.append(_subind,
                                               input_var.shape[idim] - 1)
                    _shape = numpy.ones(len(input_var.shape)).astype('int32')
                    _shape[idim] = -1
                    subind.append(_subind.reshape(_shape))
                output_var[:] = input_var[:][tuple(subind)]
            elif input_var_name in VARINDEXGCPNAMES:
                if len(input_var.shape) > 1:
                    raise InvalidGCPIndexShape(input_var_name, input_var.shape)
                subind = numpy.arange(0, input_var.shape[0], downfactor)
                if numpy.mod(input_var.shape[0] - 1, downfactor) != 0:
                    subind = numpy.append(subind, input_var.shape[0] - 1)
                # ceil may be needed for last index (not necessarily modulo
                # downfactor)
                output = numpy.ceil(input_var[subind] / float(downfactor))
                output = output.astype(output_var.datatype)
                dimname = input_var.dimensions[0].split('_')[0]
                dimsize = len(output_idf.dimensions[dimname])
                if output[-1] != dimsize:
                    raise MaxGCPIndexDoesNotMatchGCPDimension(input_var_name,
                                                              dimname,
                                                              output[-1],
                                                              dimsize)

                output_var[:] = output
            else:
                if len(input_var.shape) != 3:
                    raise IncompatibleVariableShape(input_var_name,
                                                    input_var.shape)
                # We let netCDF4 auto masking when reading input
                # but for the rest we take care of it.
                # Some strange behaviors:
                # - auto scaling input: it appears float64 are used internally
                # even when scale_factor and add_offset are float32
                # - auto masking output (with auto scaling off): masked values
                #   are not replaced by _FillValue
                input_var.set_auto_mask(True)
                input_var.set_auto_scale(False)
                output_var.set_auto_maskandscale(False)
                # Datatype down_type is used for downsampling (ie averaging)
                # Datatype cnt_type is used for counting valid data
                down_dtype = 'float32'
                if downfactor < 2 ** 4:
                    cnt_dtype = 'uint8'
                elif downfactor < 2 ** 8:
                    cnt_dtype = 'uint16'
                elif downfactor < 2 ** 16:
                    cnt_dtype = 'uint32'
                elif downfactor < 2 ** 32:
                    cnt_dtype = 'uint64'
                else:
                    raise DownscaleFactorNotSupported(downfactor)
                # Read input
                dshape = output_var.shape[1:]
                fshape = (dshape[0] * downfactor, dshape[1] * downfactor)
                rshape = (dshape[0], downfactor, dshape[1], downfactor)
                output = numpy.ma.MaskedArray(numpy.zeros(fshape,
                                                          dtype=down_dtype),
                                              mask=numpy.ones(fshape,
                                                              dtype='bool'))
                input_slice = (slice(None, input_var.shape[1]),
                               slice(None, input_var.shape[2]))
                output[input_slice] = input_var[0, :, :]
                # Average in blocks of size downfactor x downfactor
                # (we avoid .mean() function which does not seem to respect
                # dtype and uses float64)
                output = output.reshape(rshape)
                output_mask = numpy.ma.getmaskarray(output)
                cnt_valid = (~output_mask).sum(axis=(1, 3), dtype=cnt_dtype)
                output = output.sum(axis=(1, 3), dtype=down_dtype)
                # (output should be masked where cnt_valid=0)
                try:
                    output /= cnt_valid
                except FloatingPointError:
                    # Save sign and detect where log scale can be used
                    sign = numpy.sign(output)
                    abs_output = numpy.abs(output)
                    ok_mask = (cnt_valid > 0) & (abs_output > 0)
                    ok_ind = numpy.where(ok_mask)

                    # Perform division in log space
                    output[ok_ind] = numpy.log(abs_output[ok_ind])
                    output[ok_ind] -= numpy.log(cnt_valid[ok_ind])

                    # Switch back to linear space and restore sign
                    output[ok_ind] = sign[ok_ind] * numpy.exp(output[ok_ind])

                if numpy.issubdtype(output_var.dtype, numpy.integer):
                    output = output.round().astype(output_var.dtype)
                else:
                    output = output.astype(output_var.dtype)

                # Update mask in order to mask where too few valid points
                exist_mask = numpy.zeros(fshape, dtype='bool')
                exist_mask[:input_var.shape[1], :input_var.shape[2]] = True
                cnt_exist = exist_mask.reshape(rshape).sum(axis=(1, 3),
                                                           dtype=cnt_dtype)
                del exist_mask
                output.mask = cnt_valid < (cnt_exist / 2.)
                del cnt_valid, cnt_exist
                # Put into netCDF4 variable
                if 'missing_value' in output_var.ncattrs():
                    output = output.filled(output_var.missing_value)
                elif '_FillValue' in output_var.ncattrs():
                    output = output.filled(output_var._FillValue)
                else:
                    if numpy.ma.is_masked(output):
                        raise MaskedValuesFound()
                output_var[0, :, :] = output

        # Global attributes
        for attrname in input_idf.ncattrs():
            if 'idf_subsampling_factor' == attrname:
                attrvalue = numpy.int32(factor)
            elif 'idf_spatial_resolution' == attrname:
                attrvalue = input_idf.getncattr(attrname) * downfactor
            else:
                attrvalue = input_idf.getncattr(attrname)
            output_idf.setncattr(attrname, attrvalue)
        output_idf.close()
    input_idf.close()
