from .base import BaseClient
from .spot.sapi import SAPI
from .futures.fapi import FAPI
from .service.api import Service


class Client(BaseClient):
    def __init__(self, base_url=None, api_key=None, secret_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_version = "v1"

    @property
    def sapi(self):
        return SAPI(self)

    @property
    def fapi(self):
        return FAPI(self)

    @property
    def service(self):
        return Service(self)
