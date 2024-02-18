# vim: ts=4:sts=4:sw=4
#
# @author <sylvain.herledan@oceandatalab.com>
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

"""This module provides methods to handle parameters passed on the command line
and to perform the conversion of the input file to IDF format.
"""

import os
import sys
import numpy
import typing
import logging
import argparse
import warnings
import idf_converter
import idf_converter.lib
import idf_converter.writer
from pkg_resources import iter_entry_points

logger = logging.getLogger(__name__)
MainArgsResult = typing.Tuple[argparse.Namespace, typing.Any]
ComplexArgsResult = typing.Dict[str, str]
ArgsResult = typing.Dict[str, typing.Any]


class InvalidOptionsPath(ValueError):
    """Error raised when options must be read from a file that does not exist.
    """
    pass


class MalformattedInputOption(ValueError):
    """Error raised when the user provided an input option which is not in
    the key=value format."""

    def __init__(self, bad_option: str) -> None:
        self.bad_option = bad_option
        super().__init__()


class MalformattedOutputOption(ValueError):
    """Error raised when the user provided an output option which is not in
    the key=value format."""

    def __init__(self, bad_option: str) -> None:
        self.bad_option = bad_option
        super().__init__()


class FormatterMissing(ValueError):
    """Error raised when a reader requested a formatting operation that is not
    supported."""

    def __init__(self, fmt_name: str) -> None:
        self.fmt_name = fmt_name
        super(FormatterMissing, self).__init__()


class HelpRequested(Exception):
    pass


class VersionRequested(Exception):
    pass


class NoInputOptions(Exception):
    pass


class NoOutputOptions(Exception):
    pass


class NoReader(Exception):
    pass


def _get_workflow_help(reader_mod: typing.Any, idf_version: str
                       ) -> typing.Tuple[str, str]:
    """"""
    reader_input_help, reader_output_help = reader_mod.help()
    fmt = idf_converter.lib.get_idf_formatter(idf_version)
    fmt_input_help, fmt_output_help = fmt.help()
    data_model_mod = fmt.get_data_model(reader_mod.DATA_MODEL)
    idf_input_help, idf_output_help = data_model_mod.help()
    writer_input_help, writer_output_help = idf_converter.writer.help()

    input_help = f'{reader_input_help}\n{idf_input_help}\n{fmt_input_help}'
    output_help = f'{reader_output_help}\n{idf_output_help}\n{fmt_output_help}'

    input_help = f'{input_help}\n{writer_input_help}'
    output_help = f'{output_help}\n{writer_output_help}'

    # Remove empty lines
    input_help = '\n'.join([_ for _ in input_help.split('\n')
                            if 0 < len(_.strip())])
    output_help = '\n'.join([_ for _ in output_help.split('\n')
                             if 0 < len(_.strip())])

    return (input_help, output_help)


def show_help(input_readers: typing.Dict[str, typing.Any],
              main_args: argparse.Namespace) -> None:
    """
    Display help message explaining how to use the conversion command.

    Parameters
    ----------
    input_readers: dict
        TODO
    main_args: argparse.Namespace
        TODO
    """
    reader = main_args.t if main_args.t is not None else 'READER'
    print('\nUsage:\n'
          f'idf-converter -t {reader} -i key=value [key=value ...] '
          '-o key=value [key=value ...]\n[--idf-version=_version_] '
          '[--verbose] [--debug]')

    if 'READER' == reader:
        readers = '\n'.join(f'    {x}' for x in list(input_readers.keys()))
        print('\nReader\n'
              '  -t READER\tIdentifier of the reader which will extract data '
              'from the input file(s)\n\n'
              f'  Supported readers:\n{readers}\n')

        print('\nInput parameters\n'
              '  -i key=value [key=value ...]\n'
              '  -i FILE_PATH@\twhere FILE_PATH points to a text file which '
              'contains key=value pairs\n\n'
              '  Supported keys depend on the reader you choose, you can get '
              'the list\n'
              '  of the input parameters supported by a reader by using:\n\n'
              '    idf-converter -t READER -h\n')
        print('\nOutput parameters\n'
              '  -o key=value [key=value ...]\n'
              '  -o FILE_PATH@\twhere FILE_PATH points to a text file which '
              'contains key=value pairs\n\n'
              '  Supported keys depend on the reader you choose, you can get '
              'the list\n'
              '  of the output parameters supported by a reader by using:\n\n'
              '    idf-converter -t READER -h\n')
    else:
        input_help, output_help = _get_workflow_help(input_readers[reader],
                                                     main_args.idf_version)
        print('\nInput parameters\n'
              '  -i key=value [key=value ...]\n'
              '  -i FILE_PATH@\twhere FILE_PATH points to a text file which '
              'contains key=value pairs\n\n'
              f'  Supported keys are:\n{input_help}\n')

        print('\nOutput parameters\n'
              '  -o key=value [key=value ...]\n'
              '  -o FILE_PATH@\twhere FILE_PATH points to a text file which '
              'contains key=value pairs\n\n'
              f'  Supported keys are:\n{output_help}\n')

    print('\nOptions\n'
          '  -h, --help\tShow this help message and exit\n'
          '  --idf-version\tVersion of the IDF specifications that the '
          'converter will use to produce output files.\n'
          '  --verbose\tShow informational messages.\n'
          '  --debug\tShow debug messages.\n'
          '  --version\tPrint the version of the IDF converter and exit\n'
          '  --paranoid\tTreat all warnings as errors\n'
          '  --treat-numpy-errors-as-warnings\tNumerical issues detected by '
          'numpy will only display a warning message instead of raising an '
          'exception. This option is meant for debugging purpose and all the '
          'readers must be able to run without this option in production\n\n')


def parse_main_args(readers_names: typing.List[str],
                    inputs: typing.Optional[typing.List[str]] = None
                    ) -> MainArgsResult:
    """Parse generic arguments, common to all readers.

    Parameters
    ----------
    readers_names: list
        TODO

    Returns
    -------
    tuple
        TODO
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-t', nargs='?', choices=readers_names)
    parser.add_argument('-o', nargs='+', action='append')
    parser.add_argument('-h', '--help', action='store_true', default=False)
    parser.add_argument('--idf-version', choices=('1.0',), default='1.0')
    parser.add_argument('--version', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--paranoid', action='store_true', default=False)
    parser.add_argument('--treat-numpy-errors-as-warnings',
                        action='store_true', default=False)

    args, unknown = parser.parse_known_args(inputs)
    return args, unknown


def parse_reader_args(inputs: typing.List[str]
                      ) -> typing.Tuple[argparse.Namespace, typing.List[str]]:
    """Parse arguments related to input file, i.e arguments relevant for the
    data readers.

    Parameters
    ----------
    inputs: list
        TODO

    Returns
    -------
    argparse.Namespace
        TODO
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-i', nargs='+', action='append')
    args, unknown = parser.parse_known_args(inputs)
    return args, unknown


def parse_complex_list_argument(inputs: typing.Optional[typing.List[str]],
                                format_exc: typing.Any) -> ComplexArgsResult:
    """Parse command line arguments expected either as a list of key=value
    tokens, a path prefixed by the '@' symbol leading to a file that contains
    these tokens or both.

    Parameters
    ----------
    inputs: list
        TODO
    format_exc: type
        TODO

    Returns
    -------
    dict
        TODO
    """
    if inputs is None:
        return {}

    _options = [x for tokens in inputs for x in tokens]
    options_files = []
    options = []
    for _option in _options:
        if _option.endswith('@'):
            options_files.append(_option[:-1])
        else:
            options.append(_option)

    # Load options from files
    for relative_path in options_files:
        full_path = os.path.abspath(relative_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(full_path)

        with open(full_path, 'rt') as f:
            raw_text = f.read()
        file_option = raw_text.strip()
        if 0 < len(file_option):
            # Prepend option from file so that it can be overwritten by
            # the command line options
            options.insert(0, file_option)

    result = {}
    parse_opt = idf_converter.lib.parse_opt
    for opt_key, opt_value in parse_opt(' '.join(options), ' ', '='):
        result[opt_key] = opt_value

    return result


def parse_args(input_readers: typing.Dict[str, typing.Any]) -> ArgsResult:
    """Parse arguments passed on the command.

    Parameters
    ----------
    input_readers: dict
        TODO

    Returns
    -------
    dict
        TODO
    """
    _parse_complex_args = parse_complex_list_argument
    readers_names = list(input_readers.keys())

    args, extra = parse_main_args(readers_names)
    if args.help:
        show_help(input_readers, args)
        raise HelpRequested()

    if args.version:
        raise VersionRequested()

    output_options: ComplexArgsResult = {}
    if args.o is not None:
        output_options = _parse_complex_args(args.o, MalformattedOutputOption)

    reader_args, extra = parse_reader_args(extra)

    input_options: ComplexArgsResult = {}
    if reader_args.i is not None:
        input_options = _parse_complex_args(reader_args.i,
                                            MalformattedInputOption)

    # Only one extra parameter is allowed: it has to be the path of a text file
    # which contains preset options
    extra_args = None
    extra_input_options = None
    extra_output_options = None
    if 0 < len(extra):
        if not extra[0].endswith('@'):
            raise InvalidOptionsPath(extra[0])
        with open(extra[0][:-1], 'rt') as f:
            raw_text = f.read()
        extra_opts = [_.strip() for _ in raw_text.split()]
        extra_args, extra_extra = parse_main_args(readers_names, extra_opts)
        extra_reader_args, _ = parse_reader_args(extra_extra)
        extra_input_options = _parse_complex_args(extra_reader_args.i,
                                                  MalformattedInputOption)
        extra_output_options = _parse_complex_args(extra_args.o,
                                                   MalformattedOutputOption)
        # Include extra options only if they have not been defined directly
        # on the command line
        for key in extra_input_options.keys():
            if key not in input_options.keys():
                input_options[key] = extra_input_options[key]

        for key in extra_output_options.keys():
            if key not in output_options.keys():
                output_options[key] = extra_output_options[key]

    reader_type = None
    if args.t is not None:
        reader_type = args.t
    elif extra_args is not None and extra_args.t is not None:
        reader_type = extra_args.t

    if reader_type is None:
        raise NoReader()

    # Process output options
    if 0 >= len(output_options.keys()):
        raise NoOutputOptions()

    # Process input options
    if 0 >= len(input_options.keys()):
        raise NoInputOptions()

    output_options['idf_version'] = args.idf_version

    result = {'reader': reader_type,
              'output_options': output_options,
              'input_options': input_options,
              'verbose': args.verbose,
              'debug': args.debug,
              'paranoid': args.paranoid,
              'numpy_errors_are_warnings': args.treat_numpy_errors_as_warnings}

    return result


def idf_converter_script() -> None:
    """Implementation of the idf-converter command."""
    main_logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    main_logger.addHandler(handler)
    main_logger.setLevel(logging.WARN)

    # Retrieve input options help from readers
    input_readers = {}
    for reader in iter_entry_points('idf.input.readers'):
        reader_impl = reader.load()
        input_readers[reader.name] = reader_impl

    try:
        args = parse_args(input_readers)
    except (HelpRequested, VersionRequested):
        # Not an error
        sys.exit(0)
    except NoReader:
        logger.error('It is mandatory to select a reader with -t.')
        sys.exit(1)
    except NoOutputOptions:
        logger.error('It is mandatory to provide output options with -o.')
        sys.exit(1)
    except NoInputOptions:
        logger.error('It is mandatory to provide input options with -i.')
        sys.exit(1)
    except MalformattedInputOption as e:
        logger.debug(str(e))
        logger.error('Input options must follow the "key=value" format.'
                     f'The "{e.bad_option}" option you provided does not.')
        sys.exit(1)
    except MalformattedOutputOption as e:
        logger.debug(str(e))
        logger.error('Output options must follow the "key=value" format.'
                     f'The "{e.bad_option}" option you provided does not.')
        sys.exit(1)

    if args['verbose']:
        main_logger.setLevel(logging.INFO)
    if args['debug']:
        main_logger.setLevel(logging.DEBUG)

    if args['paranoid']:
        # Useful to detect the origin of FutureWarning
        logger.warning('All warnings will be treated as errors')
        warnings.filterwarnings('error')

    # Raise exceptions for all floating point issues detected by numpy
    numpy.seterr(all='raise')
    if args['numpy_errors_are_warnings'] is True:
        logger.warning('Numpy floating point errors will be treated as '
                       'warnings. Please note that this option is only meant '
                       'for debugging purpose and should not be used in '
                       'production.')
        numpy.seterr(all='warn')

    reader_impl = input_readers[args['reader']]
    result = reader_impl.read_data(args['input_options'],
                                   args['output_options'])

    try:
        for input_options, output_options, granule, formatter_jobs in result:
            logger.debug('\tRead: done')

            # Add virtual variables
            idf_converter.lib.add_virtual_variables(output_options,
                                                    formatter_jobs)

            # Remove variables that should not be saved in the IDF file
            idf_converter.lib.remove_variables(output_options, formatter_jobs)

            # Add data storage jobs
            fmt = idf_converter.lib.get_idf_formatter(granule.idf_version)
            fmt.apply_data_storage_policy(input_options, output_options,
                                          granule, formatter_jobs)

            _fmts = iter_entry_points('idf.formatters')
            formatters = {fmt.name: fmt for fmt in _fmts}
            for fmt_name, fmt_args in formatter_jobs:
                if fmt_name not in formatters:
                    logger.debug(f'Missing formatter: {fmt_name}')
                    raise FormatterMissing(fmt_name)

                fmt_method = formatters[fmt_name].load()
                result = fmt_method(input_options, output_options, granule,
                                    **fmt_args)
                input_options, output_options, granule = result
            logger.debug('\tFormat: done')

            idf_converter.writer.as_idf(input_options, output_options, granule)
            logger.debug('\tWrite: done')
    except idf_converter.lib.EarlyExit:
        sys.exit(0)

    sys.exit(0)
