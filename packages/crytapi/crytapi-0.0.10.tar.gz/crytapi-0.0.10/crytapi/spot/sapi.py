from .order import Order


class SAPI:
    def __init__(self, api_client):
        self.client = api_client
        self.client.base_url = f"https://openapi.{self.client.base_url}"
        self.service_path = f"/sapi/{self.client.api_version}"

    @property
    def order(self):
        return Order(self)

    def ticker(self, symbol):
        path = f"{self.service_path}/ticker"
        payload = {}
        params = {"symbol": symbol}
        return self.client.send("GET", path, payload, params)
