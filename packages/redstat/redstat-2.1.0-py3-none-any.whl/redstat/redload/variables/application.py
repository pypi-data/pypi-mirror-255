from importlib.metadata import PackageNotFoundError, metadata

APPLICATION_NAME = 'redstat'
APPLICATION_METADATA = metadata(APPLICATION_NAME)

try:
    APPLICATION_VERSION = APPLICATION_METADATA.get('version')
    APPLICATION_AUTHOR = APPLICATION_METADATA.get('author')
except PackageNotFoundError:
    APPLICATION_VERSION = '0.0.1'
