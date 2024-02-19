import aiohttp

from .base import BaseClient


class AsyncClient(BaseClient):
    def __init__(self, base_url=None, api_key=None, secret_key=None):
        super().__init__(base_url, api_key=api_key, secret_key=secret_key)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        headers = self._prepare_headers()
        self.session.headers.update(headers)
        return self

    async def __aexit__(self):
        await self.close_connection()

    async def close_connection(self):
        if self.session:
            assert self.session
            await self.session.close()

    async def send(self, method, uri, **kwargs):
        async with self.session.request(method, uri, **kwargs) as response:
            return await response
