import hashlib


class Service:
    def __init__(self, api_client):
        self.client = api_client
        self.client.base_url = f"https://service.{self.client.base_url}"

    def get_signature(self, app_key, api_key, api_secret, uid, app_secret):
        string = f"apiKey{api_key}appKey{app_key}secret{api_secret}uid{uid}{app_secret}"
        return hashlib.md5(string.encode("utf-8")).hexdigest()

    def get_exchange_token(self, app_key, api_key, api_secret, uid, app_secret):
        path = "/platformapi/chainup/open/user/getExchangeToken"
        payload = {
            "appKey": app_key,
            "apiKey": api_key,
            "secret": api_secret,
            "uid": uid,
            "sign": self.get_signature(app_key, api_key, api_secret, uid, app_secret),
        }
        params = {}
        response = self.client.send("POST", path, payload, params)
        return response.json()["data"]["token"]
