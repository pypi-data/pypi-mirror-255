from argparse import ArgumentParser

from redstat.shared_resources.cli.arguments.types import output_file_type, output_dir_type


def register_output_file_argument():
    default_value = 'result.json'
    help_message = f'output file (default: {default_value!r})'
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-of', '--output_file', help=help_message, type=output_file_type, default=default_value)
    return parser


def register_output_dir_argument():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-od', '--output_dir', help='output dir', type=output_dir_type)
    return parser
