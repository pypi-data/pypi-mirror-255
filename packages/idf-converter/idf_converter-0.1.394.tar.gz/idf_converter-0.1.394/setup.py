# vim: ts=4:sts=4:sw=4

import os
import sys
import shutil
import typing
import logging
from setuptools import setup

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.WARN)


# Check Python version
if sys.version_info < (3, 6):
    logger.error('This package is only available for Python version >= 3.6')
    sys.exit(1)

__package_name__ = 'idf_converter'

project_dir = os.path.dirname(__file__)
git_exe = shutil.which('git')
git_dir = os.path.join(project_dir, '.git')
version_file = os.path.join(project_dir, 'VERSION.txt')
readme_file = os.path.join(project_dir, 'docs', 'README.rst')
package_dir = os.path.join(project_dir, __package_name__)
init_file = os.path.join(package_dir, '__init__.py')

# Read metadata from the main __init__.py file
metadata: typing.Dict[str, typing.Any] = {}
with open(init_file, 'rt') as f:
    exec(f.read(), metadata)

# Regenerate a version file from git history
if git_exe is not None and os.path.isdir(git_dir):
    import subprocess
    gitrev = (git_exe, 'rev-list', 'HEAD', '--count')
    major, minor = metadata['__version__'].split('.')
    commits = subprocess.check_output(gitrev).decode('utf-8').strip()
    with open(version_file, 'wt') as f:
        f.write(f'{major}.{minor}.{commits}')

# Refuse to install package if version is not available
if not os.path.isfile(version_file):
    logger.error(f'Version file "{version_file}" missing.')
    logger.error('Please use a proper release of the code.')
    sys.exit(1)

with open(version_file, 'rt') as f:
    version = f.read()

with open(readme_file, 'rt') as f:
    long_description = f.read()

requirements: typing.List[str] = []
with open('requirements.txt', 'r') as f:
    lines = [x.strip() for x in f if 0 < len(x.strip())]
    requirements = [x for x in lines if x[0].isalpha()]

_pkg = __package_name__
cmds = [f'idf-converter = {_pkg}.cli:idf_converter_script']
readers = [f'sentinel3/sral/L2 = {_pkg}.readers.sentinel3_sral_l2',
           f'sentinel3/olci/L1 = {_pkg}.readers.sentinel3_olci_l1',
           f'sentinel3/olci/L2 = {_pkg}.readers.sentinel3_olci_l2',
           f'sentinel3/slstr/L1/bt = {_pkg}.readers.sentinel3_slstr_l1_bt',
           f'sentinel3/slstr/L1/rad = {_pkg}.readers.sentinel3_slstr_l1_rad',
           f'sentinel3/slstr/L2 = {_pkg}.readers.sentinel3_slstr_l2',
           f'sentinel6/p4/L2 = {_pkg}.readers.sentinel6_p4_l2',
           f'netcdf/grid/latlon = {_pkg}.readers.netcdf_grid_latlon',
           f'netcdf/grid/yx = {_pkg}.readers.netcdf_grid_yx',
           f'bremen/amsr/L3/sic = {_pkg}.readers.bremen_amsr_l3_sic',
           f'remss/L3/wind/netcdf = {_pkg}.readers.remss_l3_wind_netcdf',
           f'remss/L3/wind/bytemap = {_pkg}.readers.remss_l3_wind_bytemap',
           f'model/mfwam = {_pkg}.readers.mfwam',
           f'model/topaz4 = {_pkg}.readers.topaz4',
           f'ifremer/scat/psi-backscatter = '
           f'{_pkg}.readers.ifremer_scat_psi_backscatter',
           f'smos/miras/L2 = {_pkg}.readers.smos_miras_l2',
           f'jamstec/argo_oi/monthly = {_pkg}.readers.jamstec_argo_oi_monthly',
           f'iprc/argo_vi/monthly = {_pkg}.readers.iprc_argo_vi_monthly',
           f'roemmich-gilson/monthly = {_pkg}.readers.roemmich_gilson_monthly',
           f'metop/ascat/L2/wind = {_pkg}.readers.metop_ascat_l2_wind',
           f'metoffice/en4/analysis = {_pkg}.readers.metoffice_en4_analysis',
           f'isas/monthly = {_pkg}.readers.isas_monthly',
           f'noaa/cmorph/3-hourly = {_pkg}.readers.cmorph',
           f'woa/monthly = {_pkg}.readers.woa_monthly',
           f'sentinel1/L2/owi = {_pkg}.readers.sentinel1_l2_owi',
           f'sentinel1/L2/rvl = {_pkg}.readers.sentinel1_l2_rvl',
           f'ghrsst/l2p = {_pkg}.readers.ghrsst_l2p',
           f'osisaf/L3/sic = {_pkg}.readers.osisaf_l3_sic',
           f'cmems/drifter = {_pkg}.readers.cmems_drifter',
           f'rtofs = {_pkg}.readers.rtofs',
           f'ibtracs = {_pkg}.readers.ibtracs',
           f'sentinel1/L1 = {_pkg}.readers.sentinel1_l1',
           f'sentinel2/L1 = {_pkg}.readers.sentinel2_l1c',
           f'swot/L3 = {_pkg}.readers.swot_l3',
           ]
fmts = [f'remove_extra_lon_degrees = {_pkg}.lib.geo:remove_extra_lon_degrees',
        f'fill_1d_gaps = {_pkg}.lib.interp:fill_1d_gaps',
        f'static_common_mask = {_pkg}.lib.mask:static_common_mask',
        f'static_bands_mask = {_pkg}.lib.mask:static_bands_mask',
        f'mask_methods = {_pkg}.lib.mask:mask_methods',
        f'share_masks = {_pkg}.lib.mask:share_masks',
        f'store_as_ubytes = {_pkg}.lib.data_type:as_ubytes',
        f'store_as_float32 = {_pkg}.lib.data_type:as_float32',
        f's3_cnes_rayleigh = {_pkg}.lib.atmos_correction:s3_cnes_rayleigh',
        f'contrast_from_pct = {_pkg}.lib.scale:contrast_from_pct',
        f'stretch_extent = {_pkg}.lib.scale:stretch_extent',
        f'logscale = {_pkg}.lib.scale:logscale',
        f'limit_extrema = {_pkg}.lib.scale:limit_extrema',
        f'share_extrema = {_pkg}.lib.scale:share_extrema',
        f'extrema_methods = {_pkg}.lib.scale:extrema_methods',
        f'median_filter = {_pkg}.lib.filter:median',
        f'n2_sst_from_slstr = {_pkg}.lib.n2_sst:n2_sst_from_slstr',
        f's3_nir_bc = {_pkg}.lib.nir_bc:brightness_contrast',
        f'dir2vectors = {_pkg}.lib.vectors:from_dir',
        f'remove_vars = {_pkg}.lib.granule:remove_vars',
        f's1_experimental_radial_velocity = {_pkg}.lib.doppler:s1_radvel_exp',
        f'radial_velocity_sign = {_pkg}.lib.doppler:radial_velocity_sign',
        f'anomaly_from_clim = {_pkg}.lib.anomaly:anomaly_from_clim',
        f'compute_roughness = {_pkg}.lib.sar:compute_roughness',
        ]
setup(
    zip_safe=False,
    name=__package_name__,
    version=version,
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    url=metadata['__url__'],
    keywords=metadata['__keywords__'],
    classifiers=metadata['__classifiers__'],
    description=metadata['__description__'],
    packages=(__package_name__,
              f'{__package_name__}.lib',
              f'{__package_name__}.lib.idf',
              f'{__package_name__}.lib.idf.v1',
              f'{__package_name__}.readers'),
    license='COPYING.LESSER',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    package_data={__package_name__: ['py.typed', 'share/*.*']},
    test_suite='tests',
    python_requires='>=3.7',
    install_requires=requirements,
    setup_requires=(),
    entry_points={'console_scripts': cmds, 'idf.input.readers': readers,
                  'idf.formatters': fmts},
)
