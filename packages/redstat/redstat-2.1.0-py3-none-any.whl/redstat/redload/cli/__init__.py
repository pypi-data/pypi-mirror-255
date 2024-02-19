from argparse import ArgumentParser


from redstat.redload.cli.arguments.positional import register_name_argument

from redstat.shared_resources.cli.arguments.optional.verbose import register_verbose_argument
from redstat.shared_resources.cli.arguments.optional.output import register_output_file_argument


def parse_args():
    root_parents = [
        register_name_argument(),
        register_output_file_argument(),
        register_verbose_argument()
    ]
    default_parser = ArgumentParser(
        description='Cli tool for download statistic about user/subreddit',
        parents=root_parents
    )
    return default_parser.parse_args()

