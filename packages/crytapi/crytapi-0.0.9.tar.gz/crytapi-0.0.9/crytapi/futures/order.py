class Order:
    def __init__(self, fapi):
        self.fapi = fapi

    def create(self, volume, price, contract_name, type, side):
        path = f"{self.fapi.service_path}/order"
        payload = {
            "volume": volume,
            "price": price,
            "contractName": contract_name,
            "type": type,
            "side": side,
            "open": "OPEN",
            "positionType": 1,
        }
        params = {}
        return self.fapi.client.send("POST", path, payload, params)

    def get(self, order_id, contract_name):
        path = f"{self.fapi.service_path}/order"
        payload = {}
        params = {"orderId": order_id, "contractName": contract_name}
        return self.fapi.client.send("GET", path, payload, params)

    def open_orders(self, contract_name):
        path = f"{self.fapi.service_path}/openOrders"
        payload = {}
        params = {"contractName": contract_name}
        return self.fapi.client.send("GET", path, payload, params)

    def cancel(self, order_id, contract_name):
        path = f"{self.fapi.service_path}/cancel"
        payload = {"orderId": order_id, "contractName": contract_name}
        params = {}
        return self.fapi.client.send("POST", path, payload, params)
