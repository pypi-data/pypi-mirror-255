from asyncio import run

from .cli import parse_args
from .functions.validate import validate
from .functions import download


def main():
    namespace = parse_args()
    validate(namespace)

    if namespace.verbose:
        print(namespace)

    run(download(namespace))
