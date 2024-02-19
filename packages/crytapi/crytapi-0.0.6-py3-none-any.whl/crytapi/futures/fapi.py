from .order import Order


class FAPI:
    def __init__(self, api_client):
        self.client = api_client
        self.client.base_url = f"https://futuresopenapi.{self.client.base_url}"
        self.service_path = f"/fapi/{self.client.api_version}"

    @property
    def order(self):
        return Order(self)

    def ticker(self, contract_name):
        path = f"{self.service_path}/ticker"
        payload = {}
        params = {"contractName": contract_name}
        return self.client.send("GET", path, payload, params)
