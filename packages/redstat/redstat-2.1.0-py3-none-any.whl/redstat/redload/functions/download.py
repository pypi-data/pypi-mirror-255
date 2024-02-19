from aiohttp import ClientSession


async def _get_children(session: ClientSession, url: str, params: dict) -> tuple[list, str | None]:
    async with session.get(url, params=params) as response:
        json_response = await response.json()
        json_data = json_response['data']
    return [child['data'] for child in json_data['children']], json_data['after']


async def download_statistic(session: ClientSession, url: str) -> list:
    params = {'limit': 100}
    result = []
    while True:
        children, after = await _get_children(session, url, params)
        result.extend(children)
        if after is None:
            break
        params['after'] = after
    return result
