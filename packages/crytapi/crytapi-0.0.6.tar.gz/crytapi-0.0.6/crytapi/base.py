import json
import requests
import time
import hashlib
import hmac
from urllib.parse import urlparse, urlencode


from .version import __version__


class BaseClient:
    def __init__(self, base_url=None, api_key=None, secret_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = None

    def prepare_url(self, path, params):
        full_url = self.base_url + path
        if params:
            full_url += "?" + urlencode(params)
        return full_url

    @staticmethod
    def prepare_payload(payload):
        return json.dumps(payload)

    def prepare_headers(self, sign, timestamp):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"Python CRYT API Client/{__version__}",
            "X-CH-APIKEY": self.api_key,
            "X-CH-SIGN": sign,
            "X-CH-TS": str(timestamp),
        }
        return headers

    def prepare_message(self, method, url, payload, timestamp):
        message = str(timestamp) + method + url.path
        if method == "GET":
            message += "?" + url.query
        if method == "POST":
            message += payload
        return message

    def prepare_sign(self, message):
        secret_key = bytes(self.secret_key, "utf-8")
        message = bytes(message, "utf-8")
        signature = hmac.new(secret_key, message, hashlib.sha256)
        return signature.hexdigest()

    def send(self, method, path, payload, params=None):
        url = self.prepare_url(path, params)
        payload = self.prepare_payload(payload)
        timestamp = int(time.time() * 1000)
        message = self.prepare_message(method, urlparse(url), payload, timestamp)
        sign = self.prepare_sign(message)
        headers = self.prepare_headers(sign, timestamp)
        res = requests.request(method, url, data=payload, headers=headers)
        return res
