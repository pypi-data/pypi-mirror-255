from argparse import ArgumentParser


def register_name_argument():
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        'name',
        help='user/subreddit name. User starts with \'u/\' subreddit \'r/\''
    )
    return parser
