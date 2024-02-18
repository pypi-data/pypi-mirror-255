# vim: ts=4:sts=4:sw=4
#
# @date 2022-02-04
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

"""
"""

import os
import re
import typing
import logging
import datetime

import defusedxml.ElementTree as ET
import numpy
import numpy.typing
import tifffile
from scipy.interpolate import RectBivariateSpline
from scipy.stats import scoreatpercentile
import pyproj

import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult
from idf_converter.lib.types import Granule, Extrema

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'
SUPPORTED_VARIABLES = ['roughness', 'sigma0', 'incidence']
SUPPORTED_CONTRASTS = ['sea', 'ice', 'relative', 'relative_strict']


class InputPathMissing(IOError):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


class S1ProductAnnotationNotFound(IOError):
    """Error raised when the path for the S-1 product annotation file does not
    exist."""
    pass


class S1CalibrationAnnotationNotFound(IOError):
    """Error raised when the path for the S-1 calibration annotation file does
    not exist."""
    pass


class S1VariableNotSupported(ValueError):
    """Error raised when the S-1 variable is not supported."""
    pass


class S1GeolocationGridNotAsExpected(Exception):
    """Error raised when the S-1 geolocation grid is not as expected."""
    pass


class S1ProductNotKnown(ValueError):
    """Error raised when the annotated S-1 product is not known."""
    pass


class S1ModeNotKnown(ValueError):
    """Error raised when the annotated S-1 mode is not known."""
    pass


class S1ProductNotSupported(Exception):
    """Error raised when the S1 input product is not supported (IW SLC or EW
    SLC)."""
    pass


class ContrastNameNotKnown(ValueError):
    """Error raised when the contrast name is not known."""
    pass


def read_product_annotations(prod_annot_path: str
                             ) -> typing.Dict[str, typing.Any]:
    """"""
    annot = {}
    tree = ET.parse(prod_annot_path)
    ads = tree.getroot()

    # Header
    adsh = ads.find('./adsHeader')
    annot['mission'] = adsh.find('./missionId').text
    annot['product'] = adsh.find('./productType').text
    annot['polarisation'] = adsh.find('./polarisation').text
    annot['mode'] = adsh.find('./mode').text
    annot['swath'] = adsh.find('./swath').text
    annot['start_time'] = adsh.find('./startTime').text
    annot['stop_time'] = adsh.find('./stopTime').text

    # Product info
    adspi = ads.find('./generalAnnotation/productInformation')
    annot['pass'] = adspi.find('./pass').text

    # Image info
    adsii = ads.find('./imageAnnotation/imageInformation')
    range_pixel_spacing_str = adsii.find('./rangePixelSpacing').text
    annot['range_pixel_spacing'] = float(range_pixel_spacing_str)
    annot['azimuth_pixel_spacing'] = \
        float(adsii.find('./azimuthPixelSpacing').text)
    annot['incidence_angle_mid_swath'] = \
        float(adsii.find('./incidenceAngleMidSwath').text)
    annot['number_of_samples'] = int(adsii.find('./numberOfSamples').text)
    annot['number_of_lines'] = int(adsii.find('./numberOfLines').text)

    # Geolocation grid
    adsgg = ads.find('./geolocationGrid/geolocationGridPointList')
    points = adsgg.findall('./geolocationGridPoint')
    npoints = len(points)
    # azit = []
    # rant = []
    _lin = []
    _pix = []
    _lat = []
    _lon = []
    _hei = []
    _inc = []
    # elev = []
    for point in points:
        # azit.append(point.find('./azimuthTime').text)
        # rant.append(point.find('./slantRangeTime').text)
        _lin.append(point.find('./line').text)
        _pix.append(point.find('./pixel').text)
        _lat.append(point.find('./latitude').text)
        _lon.append(point.find('./longitude').text)
        _hei.append(point.find('./height').text)
        _inc.append(point.find('./incidenceAngle').text)
        # elev.append(point.find('./elevationAngle').text)
    lin = numpy.array(_lin, dtype='int32')
    pix = numpy.array(_pix, dtype='int32')
    lat = numpy.array(_lat, dtype='float32')
    lon = numpy.array(_lon, dtype='float32')
    hei = numpy.array(_hei, dtype='float32')
    inc = numpy.array(_inc, dtype='float32')
    npixels = len(numpy.where(lin == lin[0])[0])
    nlines = len(numpy.where(pix == pix[0])[0])
    if npixels * nlines != npoints:
        raise S1GeolocationGridNotAsExpected()
    shape = (nlines, npixels)
    lin = lin.reshape(shape)
    pix = pix.reshape(shape)
    chk = lin.min(axis=1) != lin.max(axis=1)
    if chk.any():
        raise S1GeolocationGridNotAsExpected()
    chk = pix.min(axis=0) != pix.max(axis=0)
    if chk.any():
        raise S1GeolocationGridNotAsExpected()
    geoloc = {}
    geoloc['line'] = lin
    geoloc['pixel'] = pix
    geoloc['latitude'] = lat.reshape(shape)
    geoloc['longitude'] = lon.reshape(shape)
    geoloc['height'] = hei.reshape(shape)
    geoloc['incidence_angle'] = inc.reshape(shape)
    linargsort = geoloc['line'][:, 0].argsort()
    if ((linargsort[1:] - linargsort[0:-1]) != 1).any():
        logging.warning('Geolocation lines are not sorted -> do sort')
        for key in geoloc.keys():
            geoloc[key] = geoloc[key][linargsort, :]
    pixargsort = geoloc['pixel'][0, :].argsort()
    if ((pixargsort[1:] - pixargsort[0:-1]) != 1).any():
        logging.warning('Geolocation pixels are not sorted -> do sort')
        for key in geoloc.keys():
            geoloc[key] = geoloc[key][:, pixargsort]
    annot['geolocation_grid'] = geoloc

    return annot


def read_calibration_annotations(cal_annot_path: str
                                 ) -> typing.Dict[str, typing.Any]:
    """"""
    annot = {}
    tree = ET.parse(cal_annot_path)
    ads = tree.getroot()

    # Look-up tables for calibration
    vectors = ads.findall('./calibrationVectorList/calibrationVector')
    # azit = []
    lin = []
    pix = []
    sig = []
    # bet = []
    # gam = []
    # dn = []
    for vector in vectors:
        # azit.append(vector.find('./azimuthTime').text)
        lin.append(vector.find('./line').text)
        pix.append(vector.find('./pixel').text.split())
        sig.append(vector.find('./sigmaNought').text.split())
        # bet.append(vector.find('./betaNought').text.split())
        # gam.append(vector.find('./gamma').text.split())
        # dn.append(vector.find('./dn').text.split())
    luts = {}
    luts['pixel'] = numpy.array(pix, dtype='int32')
    nline, npixel = luts['pixel'].shape
    lin_array = numpy.array(lin, dtype='int32')
    luts['line'] = numpy.tile(lin_array[:, numpy.newaxis], (1, npixel))
    luts['sigma0'] = numpy.array(sig, dtype='float32')
    annot['luts'] = luts

    return annot


def read_tiff(tiff_path: str) -> numpy.typing.NDArray:
    """"""
    data = tifffile.imread(tiff_path, mode='rb')
    return data


def read_tiff_as_memmap(tiff_path: str) -> numpy.typing.NDArray:
    """"""
    data = tifffile.memmap(tiff_path, mode='r')
    return data


def interpolate_grid(xval: numpy.typing.NDArray,
                     yval: numpy.typing.NDArray,
                     zval: numpy.typing.NDArray,
                     xint: numpy.typing.NDArray,
                     yint: numpy.typing.NDArray,
                     degrees: typing.Tuple[int, int] = (3, 3),
                     blocksize: int = 25000000
                     ) -> numpy.typing.NDArray:
    """"""
    # Set bbox in case of extrapolation is needed
    bbox = []
    for xyv, xyi in zip([xval, yval], [xint, yint]):
        if xyi.min() < xyv.min():
            bbox.append(xyi.min())
        else:
            bbox.append(None)
        if xyi.max() > xyv.max():
            bbox.append(xyi.max())
        else:
            bbox.append(None)
    # Interpolate with RectBivariateSpline
    # Warning: RectBivariateSpline is called with grid=True meaning that
    # xint and yint must be sorted to increasing order.
    func = RectBivariateSpline(xval, yval, zval, bbox=bbox,
                               kx=degrees[0], ky=degrees[1])
    if blocksize is None:
        values = func(xint, yint, grid=True).astype(zval.dtype)
    else:
        ny = yint.size
        nx = xint.size
        block_ny = ny
        block_nx = numpy.maximum(blocksize // block_ny, 1)
        nblock = int(numpy.ceil(nx / float(block_nx)))
        values = numpy.empty((nx, ny), dtype=zval.dtype)
        for iblock in range(nblock):
            x0 = iblock * block_nx
            x1 = numpy.minimum((iblock + 1) * block_nx, nx)
            xsli = slice(x0, x1)
            values[xsli, :] = func(xint[xsli], yint, grid=True)
    return values


def move_geoloc_height(lon: numpy.typing.NDArray,
                       lat: numpy.typing.NDArray,
                       hei: numpy.typing.NDArray,
                       inc: numpy.typing.NDArray,
                       target_height: float = 0.
                       ) -> typing.Tuple[numpy.typing.NDArray,
                                         numpy.typing.NDArray,
                                         numpy.typing.NDArray]:
    """"""
    geod = pyproj.Geod(ellps='WGS84')
    forw, back, _ = geod.inv(lon[:, :-1], lat[:, :-1], lon[:, 1:], lat[:, 1:])
    forw = numpy.hstack((forw, forw[:, [-1]]))
    back = numpy.hstack((back[:, [0]], back))
    mvdist = (target_height - hei) / numpy.tan(numpy.deg2rad(inc))
    mvforw = forw
    indneg = numpy.where(mvdist < 0)
    mvdist[indneg] = -mvdist[indneg]
    mvforw[indneg] = back[indneg]
    _lon, _lat, _ = geod.fwd(lon, lat, mvforw, mvdist)
    _hei = numpy.full_like(hei, target_height)
    return _lon, _lat, _hei


def s1_extrema(var_dict: typing.Dict[str, typing.Any],
               default_min: float,
               default_max: float) -> Extrema:
    """"""
    shp = var_dict['array'].shape
    noborder = (slice(int(shp[0] * 0.05), int(shp[0] * 0.95)),
                slice(int(shp[1] * 0.1), int(shp[1] * 0.9)))
    _min = scoreatpercentile(var_dict['array'][noborder], 0.1)
    _max = scoreatpercentile(var_dict['array'][noborder], 99.9)
    return _min, _max


def s1_extrema_strict(var_dict: typing.Dict[str, typing.Any],
                      default_min: float,
                      default_max: float) -> Extrema:
    """"""
    _min = var_dict['array'].min()
    _max = var_dict['array'].max()
    return _min, _max


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    supp_vars = ', '.join(SUPPORTED_VARIABLES)
    supp_ctst = ', '.join(SUPPORTED_CONTRASTS)
    inp = ('    path\tPath of the input file',
           '    variables\tComma-separated list of variable identifiers to'
           ' extract from the input file. Identifiers of supported variables'
           ' are {}.'.format(supp_vars),
           '    variable_overrides_VAR\tDefinition of variable attributes'
           ' that are either missing or erroneous in the input file.'
           ' VAR is the identifier of the variable and the value of this'
           ' option is a comma-separated list of key:value. For instance'
           ' here, variable_overrides_roughness=valid_max:3 allows to'
           ' directly set valid_max of roughness variable.',
           '    contrast\tStrategy to automatically set valid_min/valid_max'
           ' of roughness variable. Supported contrasts are'
           ' {}.'.format(supp_ctst),
           '    spacing\tComma-separated list (length 2) of extraction spacing'
           ' in pixel. For instance, spacing=4,3 gives a downsampled version'
           ' by 4 in azimuth and by 3 in range.',
           '    mspacing\tComma-separated list (length 2) of extraction'
           ' spacing in meter. For instance, mspacing=100,50 gives a'
           ' downsampled version with 100m spacing in azimuth and 50m spacing'
           ' in range. Ignored if spacing is given.',
           )
    out = ('',)
    return ('\n'.join(inp), '\n'.join(out))


def set_extrema(granule: Granule,
                vars_id: typing.Sequence[str],
                annot: typing.Dict[str, typing.Any],
                contrast: typing.Optional[str],
                float_variables: typing.Sequence[str]
                ) -> typing.Optional[str]:
    """"""
    # Sigma0
    if 'sigma0' in vars_id:
        vmin = granule.vars['sigma0']['valid_min']
        vmax = granule.vars['sigma0']['valid_max']
        if vmin is None or vmax is None:
            if 'sigma0' not in float_variables:
                _vmin, _vmax = s1_extrema(granule.vars['sigma0'], 0., 0.)
            else:
                _vmin, _vmax = s1_extrema_strict(granule.vars['sigma0'],
                                                 0., 0.)
            if vmin is None:
                granule.vars['sigma0']['valid_min'] = _vmin
            if vmax is None:
                granule.vars['sigma0']['valid_max'] = _vmax
    # Incidence
    if 'incidence' in vars_id:
        vmin = granule.vars['incidence']['valid_min']
        vmax = granule.vars['incidence']['valid_max']
        if vmin is None:
            _vmin = granule.vars['incidence']['array'].min()
            granule.vars['incidence']['valid_min'] = _vmin
        if vmax is None:
            _vmax = granule.vars['incidence']['array'].max()
            granule.vars['incidence']['valid_max'] = _vmax
    # Roughness
    if 'roughness' in vars_id:
        vmin = granule.vars['roughness']['valid_min']
        vmax = granule.vars['roughness']['valid_max']
        if vmin is not None and vmax is not None:  # user choice
            # Nothing to do but we don't want contrast='relative' or
            # contrast='relative_strict'.
            # (otherwise it will trigger a transform)
            contrast = None
        else:  # default vmin and/or vmax based on contrast string
            if contrast is None:  # default contrast string
                if 'sea_surface_roughness' in float_variables:
                    contrast = 'relative_strict'
                elif annot['mode'] == 'WV':
                    contrast = 'relative'
                else:
                    contrast = 'sea'
            else:
                if contrast not in SUPPORTED_CONTRASTS:
                    raise ContrastNameNotKnown()
            if contrast == 'relative':
                # a transform will be added for vmin/vmax computation
                pass
            elif contrast == 'relative_strict':
                # a transform will be added for vmin/vmax computation
                pass
            elif contrast == 'sea':
                if annot['polarisation'] == 'VV':
                    if vmin is None:
                        vmin = 0.
                    if vmax is None:
                        vmax = 2.
                elif annot['polarisation'] == 'HH':
                    if vmin is None:
                        vmin = 0.
                    if vmax is None:
                        vmax = 2.5
                else:
                    if vmin is None:
                        vmin = 1.
                    if vmax is None:
                        vmax = 3.
            elif contrast == 'ice':
                if annot['polarisation'] in ['HH', 'VV']:
                    if vmin is None:
                        vmin = 0.
                    if vmax is None:
                        vmax = 3.5
                else:
                    if vmin is None:
                        vmin = 1.
                    if vmax is None:
                        vmax = 5.
            else:
                raise ContrastNameNotKnown()
            granule.vars['roughness']['valid_min'] = vmin
            granule.vars['roughness']['valid_max'] = vmax
    return contrast


def read_data(input_opts: InputOptions,
              output_opts: OutputOptions
              ) -> typing.Iterator[ReaderResult]:
    """Read input file, extract data and metadata, store them in a Granule
    object then prepare formatting instructions to finalize the conversion to
    IDF format.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule, list)
        A tuple which contains four elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the extracted information
          has been stored

        - a :obj:list of :obj:dict describing the formatting operations that
          the converter must perform before serializing the result in IDF
          format
    """
    # Get inputs
    _tiff_path = input_opts.get('path', None)
    if _tiff_path is None:
        raise InputPathMissing()
    tiff_path = os.path.normpath(_tiff_path)

    _vars_id = input_opts.get('variables', None)
    if _vars_id is None:
        vars_id = ['roughness']  # Default
    else:
        _vars_id = _vars_id.split(',')
        for var in _vars_id:
            if var not in SUPPORTED_VARIABLES:
                raise S1VariableNotSupported()
        vars_id = []
        for var in SUPPORTED_VARIABLES:
            if var in _vars_id:
                vars_id.append(var)

    contrast = input_opts.get('contrast', None)
    spacing = input_opts.get('spacing', None)
    if spacing is not None:
        spacing = numpy.array(spacing.split(','), dtype='int32')
    mspacing = input_opts.get('mspacing', None)
    if mspacing is not None:
        mspacing = numpy.array(mspacing.split(','), dtype='float32')

    # Init granule
    variables: typing.Dict[str, typing.Dict[str, typing.Any]] = {}
    if 'roughness' in vars_id:
        variables['roughness'] = {'name': 'sea_surface_roughness',
                                  'long_name': 'sea surface roughness',
                                  # 'units': '', # dimensionless
                                  'valid_min': None,
                                  'valid_max': None,
                                  'options': {}}
    if 'sigma0' in vars_id or 'roughness' in vars_id:
        variables['sigma0'] = {'name': 'sigma0',
                               'long_name': 'normalized radar cross-section',
                               # 'units': '', # dimensionless
                               'valid_min': None,
                               'valid_max': None,
                               'options': {}}
    if 'incidence' in vars_id or 'roughness' in vars_id:
        variables['incidence'] = {'name': 'incidence',
                                  'long_name': 'incidence angle',
                                  'units': 'degrees',
                                  'valid_min': None,
                                  'valid_max': None,
                                  'options': {}}
    variables['lat'] = {'units': 'degrees_north',
                        'options': {}}
    variables['lon'] = {'units': 'degrees_east',
                        'options': {}}

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    granule.vars = variables
    idf_converter.lib.apply_var_overrides(input_opts, granule)

    # Check existance of required files
    tiff_dir, tiff_bname = os.path.split(tiff_path)
    annot_dir = os.path.join(os.path.dirname(tiff_dir), 'annotation')
    xml_bname = tiff_bname.replace('.tiff', '.xml')

    prod_annot_path = os.path.join(annot_dir, xml_bname)
    if not os.path.exists(prod_annot_path):
        raise S1ProductAnnotationNotFound()

    cal_annot_path = os.path.join(annot_dir, 'calibration',
                                  'calibration-{}'.format(xml_bname))
    if not os.path.exists(cal_annot_path):
        raise S1CalibrationAnnotationNotFound()

    # Read relevant annotations
    annot = read_product_annotations(prod_annot_path)
    annot.update(read_calibration_annotations(cal_annot_path))

    # Set downsampling factor
    # - grd_spacing is product ground spacing in meter
    # - spacing is target spacing in pixel (ie downsampling factor)
    # - mspacing is target spacing in meter
    azi_grd_spacing = annot['azimuth_pixel_spacing']
    ran_grd_spacing = annot['range_pixel_spacing']
    if annot['product'] == 'SLC':
        incmid = numpy.deg2rad(annot['incidence_angle_mid_swath'])
        ran_grd_spacing = ran_grd_spacing / numpy.sin(incmid)
    grd_spacing = numpy.array([azi_grd_spacing, ran_grd_spacing])
    if spacing is not None:  # user choice
        pass
    elif mspacing is not None:  # user choice
        spacing = (mspacing / grd_spacing).round().astype('int32')
    else:  # default
        if annot['product'] == 'GRD':
            spacing = numpy.array([2, 2])
        elif annot['product'] == 'SLC':
            if annot['mode'] == 'WV':
                mspacing = numpy.array([15., 15.])  # meters
            elif re.match(r'^S[1-6]$', annot['mode']) is not None:
                mspacing = numpy.array([15., 15.])  # meters
            elif annot['mode'] == 'IW':
                raise S1ProductNotSupported()
            elif annot['mode'] == 'EW':
                raise S1ProductNotSupported()
            else:
                raise S1ModeNotKnown()
            spacing = (mspacing / grd_spacing).round().astype('int32')
        else:
            raise S1ProductNotKnown()
    mspacing = spacing * grd_spacing
    frshp = numpy.array([annot['number_of_lines'],
                         annot['number_of_samples']])  # full res shape
    _frshp = frshp - numpy.mod(frshp, spacing)
    dshp = (_frshp / spacing).astype('int32')  # downsampled shape
    fullres_nrow = int(_frshp[0])
    fullres_ncell = int(_frshp[1])
    nrow = int(dshp[0])
    ncell = int(dshp[1])
    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    # Get sigma0
    if 'sigma0' in granule.vars:
        # - Read digital number stored in tiff file and downsample it
        # -- blocksize version
        # tiff memmap is called at each iteration, otherwise memory usage
        # increases up to the tiff size.
        sigma0 = numpy.empty((nrow, ncell), dtype='float32')
        blocksize = 50000000
        block_ncell = fullres_ncell
        block_nrow = numpy.maximum(blocksize // block_ncell, spacing[0])
        block_nrow -= block_nrow % spacing[0]
        nblock = int(numpy.ceil(fullres_nrow / float(block_nrow)))
        for iblock in range(nblock):
            fr_row0 = iblock * block_nrow
            fr_row1 = numpy.minimum((iblock + 1) * block_nrow, fullres_nrow)
            fr_sli = (slice(fr_row0, fr_row1), slice(0, fullres_ncell))
            row0 = int(fr_row0 / spacing[0])
            row1 = int(fr_row1 / spacing[0])
            sli = (slice(row0, row1), slice(0, ncell))
            rshp = (row1 - row0, spacing[0], ncell, spacing[1])
            dnum: numpy.typing.NDArray
            try:
                dnum = read_tiff_as_memmap(tiff_path)
            except ValueError:
                dnum = read_tiff(tiff_path)
            _sigma0 = numpy.abs(dnum[fr_sli]).astype('float32') ** 2.
            _sigma0 = _sigma0.reshape(rshp).mean(-1).mean(1)
            sigma0[sli] = _sigma0
        # -- non blocksize version
        # sigma0 = numpy.abs(read_tiff(tiff_path)).astype('float32') ** 2.
        # if spacing.max() > 1:
        #     rshp = (nrow, spacing[0], ncell, spacing[1])
        #     frsli = (slice(0, _frshp[0]), slice(0, _frshp[1]))
        #     sigma0 = sigma0[frsli].reshape(rshp).mean(-1).mean(1)
        # - Calibrate sigma0
        # Warning: xint and yint must be sorted to increasing order
        xint = numpy.arange(nrow) * spacing[0] + (spacing[0] - 1) / 2.
        yint = numpy.arange(ncell) * spacing[1] + (spacing[1] - 1) / 2.
        xval = annot['luts']['line'][:, 0]
        yval = annot['luts']['pixel'][0, :]
        zval = annot['luts']['sigma0']
        lut_sigma0 = interpolate_grid(xval, yval, zval, xint, yint,
                                      degrees=(1, 1), blocksize=25000000)
        sigma0 /= lut_sigma0 ** 2.
        del lut_sigma0
        granule.vars['sigma0']['array'] = sigma0

    # Get incidence angle
    if 'incidence' in granule.vars:
        # Warning: xint and yint must be sorted to increasing order
        xint = numpy.arange(nrow) * spacing[0] + (spacing[0] - 1) / 2.
        yint = numpy.arange(ncell) * spacing[1] + (spacing[1] - 1) / 2.
        xval = annot['geolocation_grid']['line'][:, 0]
        yval = annot['geolocation_grid']['pixel'][0, :]
        zval = annot['geolocation_grid']['incidence_angle']
        inc_angle = interpolate_grid(xval, yval, zval, xint, yint,
                                     degrees=(1, 3), blocksize=25000000)
        granule.vars['incidence']['array'] = inc_angle

    # Set valid_min / valid_max
    _float_variables = output_opts.get('use_float32_values', '')
    float_variables = [_.strip() for _ in _float_variables.split(',')
                       if 0 < len(_.strip())]
    contrast = set_extrema(granule, vars_id, annot, contrast, float_variables)

    # Geolocation
    # - Move geoloc to 0 height
    geoloc = annot['geolocation_grid']
    lon = geoloc['longitude']
    lat = geoloc['latitude']
    hei = geoloc['height']
    inc = geoloc['incidence_angle']
    lon, lat, hei = move_geoloc_height(lon, lat, hei, inc, 0.)
    if lon.min() < -135 and lon.max() > 135:
        lon[numpy.where(lon < 0)] += 360.
    granule.vars['lat']['array'] = lat
    granule.vars['lon']['array'] = lon
    # - Settings for compute_gcps() method in swath module
    ngeorow = lat.shape[0]
    ngeocell = lat.shape[1]
    gcp_distribution = {}
    gcp_distribution['geoloc_row'] = numpy.arange(ngeorow)
    gcp_distribution['geoloc_cell'] = numpy.arange(ngeocell)
    gcp_distribution['input_row'] = (geoloc['line'][:, 0] + 0.5) / spacing[0]
    gcp_distribution['input_cell'] = (geoloc['pixel'][0, :] + 0.5) / spacing[1]
    dst_lin = numpy.linspace(0, nrow, num=ngeorow - 1, endpoint=False)
    gcp_distribution['output_row'] = dst_lin.round().astype('int32')
    dst_pix = numpy.linspace(0, ncell, num=ngeocell - 1, endpoint=False)
    gcp_distribution['output_cell'] = dst_pix.round().astype('int32')
    output_opts['gcp_distribution'] = gcp_distribution
    input_opts['geoloc_at_pixel_center'] = 'false'

    # Metadata
    safe_dir = os.path.dirname(os.path.dirname(tiff_path))
    safe_name = os.path.splitext(os.path.basename(safe_dir))[0]
    pid = safe_name.split('_')[-1]
    granule_name = '{}-{}'.format(os.path.splitext(tiff_bname)[0], pid)

    time_fmt = '%Y-%m-%dT%H:%M:%S.%f'
    start_time = datetime.datetime.strptime(annot['start_time'], time_fmt)
    stop_time = datetime.datetime.strptime(annot['stop_time'], time_fmt)

    platform = annot['mission'].replace('S1', 'Sentinel-1')

    granule.meta['idf_granule_id'] = granule_name
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = mspacing.min()
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_time
    granule.meta['time_coverage_end'] = stop_time
    granule.meta['institution'] = 'ESA'
    granule.meta['platform'] = platform
    granule.meta['platform_type'] = 'leo satellite'
    granule.meta['sensor'] = 'C-SAR'
    granule.meta['sensor_type'] = 'sar'
    granule.meta['sensor_mode'] = annot['mode']
    granule.meta['sensor_swath'] = annot['swath']
    granule.meta['sensor_polarisation'] = annot['polarisation']
    granule.meta['sensor_pass'] = annot['pass']
    granule.meta['safe_name'] = safe_name

    # Transforms
    transforms = []
    # - SAR roughness computation
    if 'roughness' in vars_id:
        transforms.append(('compute_roughness',
                           {'targets': ('roughness',),
                            'sigma0_var_id': 'sigma0',
                            'incidence_var_id': 'incidence',
                            'polarisation': annot['polarisation']}))
    # - SAR roughness relative valid_min / valid_max
    if 'roughness' in vars_id and contrast == 'relative':
        methods = {'roughness': s1_extrema}
        min_values = {'roughness': 0.}
        max_values = {'roughness': 0.}
        transforms.append(('extrema_methods', {'targets': ('roughness',),
                                               'methods': methods,
                                               'min_values': min_values,
                                               'max_values': max_values}))
    elif 'roughness' in vars_id and contrast == 'relative_strict':
        methods = {'roughness': s1_extrema_strict}
        min_values = {'roughness': 0.}
        max_values = {'roughness': 0.}
        transforms.append(('extrema_methods', {'targets': ('roughness',),
                                               'methods': methods,
                                               'min_values': min_values,
                                               'max_values': max_values}))
    # - masking sigma0 and roughness
    if 'roughness' in vars_id or 'sigma0' in vars_id:
        mask = granule.vars['sigma0']['array'] == 0
        if mask.max() == True:  # noqa: E712
            targets = [vid for vid in vars_id
                       if vid in ['roughness', 'sigma0']]
            transforms.append(('static_common_mask', {'targets': targets,
                                                      'mask': mask}))
    # - Remove variables
    to_remove = []
    if 'sigma0' in granule.vars and 'sigma0' not in vars_id:
        to_remove.append('sigma0')
    if 'incidence' in granule.vars and 'incidence' not in vars_id:
        to_remove.append('incidence')
    if len(to_remove) > 0:
        transforms.append(('remove_vars', {'targets': to_remove}))

    output_opts['__export'] = vars_id

    yield input_opts, output_opts, granule, transforms
