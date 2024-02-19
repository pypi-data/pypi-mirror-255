from aiohttp import ClientSession

from .download import download_statistic
from .save import save_json
from .validate import validate

from redstat.redload.variables.headers import BASE_HEADER
from redstat.redload.variables.url import JSON_BASE_URL


async def download(namespace):
    name = namespace.name
    url = JSON_BASE_URL.format(name)
    async with ClientSession(headers=BASE_HEADER) as session:
        statistic = await download_statistic(session, url)
    save_json(statistic, namespace.output_file)
