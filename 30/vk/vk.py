# -*- coding: utf-8 -*-

from asyncio import get_event_loop
from aiohttp import ClientSession
from utils import Logger, BetterDict


logger = Logger('VKAPI')


class ApiError(Exception):
    pass


class VkApi:
    URL = 'https://api.vk.com/method/'

    def __init__(self, token, api_version='5.126', loop=None, session=None):
        self.loop = loop if loop else get_event_loop()

        self.api_version = api_version
        self.session = session if session else ClientSession()
        self.token = token

    def get_api(self):
        return VkApiMethod(self)

    async def method(self, method, values, raw=False):
        values = values.copy() if values else {}

        if 'raw' in values:
            values.pop('raw')
            raw = True

        if 'v' not in values:
            values['v'] = self.api_version

        if 'lang' not in values:
            values['lang'] = 'ru'

        values['access_token'] = values.get('access_token', self.token)

        async with self.session.post(self.URL + method, data=values) as response:
            response = await response.text()
            response = BetterDict.loads(response)
            if isinstance(response, dict):
                error = response.get('error')
                if error:
                    raise ApiError(error)
                else:
                    return response['response'] if not raw else response
            else:
                print(response)

    async def close(self):
        if not self.session.closed:
            await self.session.close()


class VkApiMethod:
    __slots__ = ('_vk', '_method')

    def __init__(self, vk, method=None):
        self._method = method
        self._vk = vk

    def __getattr__(self, method):
        return VkApiMethod(self._vk, (self._method + '.' if self._method else '') + method)

    async def __call__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                kwargs[key] = ','.join(str(i) for i in value)

            return await self._vk.method(self._method, kwargs)

