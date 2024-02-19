class Order:
    def __init__(self, sapi):
        self.sapi = sapi

    def create(self, price, side, symbol, type, volume):
        path = f"{self.sapi.service_path}/order"
        payload = {
            "price": price,
            "side": side,
            "symbol": symbol,
            "type": type,
            "volume": volume,
        }
        params = {}
        return self.sapi.client.send("POST", path, payload, params)

    def get(self, order_id, symbol):
        path = f"{self.sapi.service_path}/order"
        payload = {}
        params = {"orderId": order_id, "symbol": symbol}
        return self.sapi.client.send("GET", path, payload, params)

    def open_orders(self, symbol, limit=100):
        path = f"{self.sapi.service_path}/openOrders"
        payload = {}
        params = {"symbol": symbol, "limit": limit}
        return self.sapi.client.send("GET", path, payload, params)

    def cancel(self, order_id, symbol):
        path = f"{self.sapi.service_path}/cancel"
        payload = {"orderId": order_id, "symbol": symbol}
        params = {}
        return self.sapi.client.send("POST", path, payload, params)
