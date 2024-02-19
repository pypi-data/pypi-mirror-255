from argparse import ArgumentParser


def register_verbose_argument():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    return parser
