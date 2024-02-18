import ssl
import hmac
import json
import time
import hashlib
import requests
import datetime

import threading
from websockets.sync.client import connect


class ZerocapWebsocketClient:
    def __init__(self, api_key: str, api_secret: str, env: str='prod'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.websocket = None
        if env == 'development':
            self.base_url = "wss://dma-ws.defi.wiki/v2"
            self.http_url = "https://dma-api.defi.wiki/v2/orders"
        elif env == 'uat':
            self.base_url = "wss://dma-uat-ws.defi.wiki/v2"
            self.http_url = "https://dma-uat-api.defi.wiki/v2/orders"
        elif env == 'prod':
            self.base_url = "wss://dma-ws.zerocap.com/v2"
            self.http_url = "https://dma-api.zerocap.com/v2/orders"
        elif env == 'sandbox':
            self.base_url = "wss://sandbox-ws.zerocap.com/v2"
            self.http_url = "https://sandbox-api.zerocap.com/v2/orders"
        else:
            self.base_url = "*"
            self.http_url = "*"
        # self.signature = self.hashing()
        # self.verify_identity()
        
    def verify_identity(self):
        timestamp = int(time.time())
        headers = {'Content-Type': 'application/json'}
        data = {"api_key": self.api_key, "signature": self.hashing(timestamp)}
        url = f"{self.http_url}/api_key_signature_valid"
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code != 200 or response.json().get('status_code') != 200:
            raise Exception("Authentication failed")
        
    def hashing(self, timestamp):
        return hmac.new(
            self.api_secret.encode("utf-8"), str(timestamp).encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def close(self):
        try:
            if self.websocket:
                self.websocket.close()
        except:
            pass
        return

    def recv(self, websocket):
        return json.loads(websocket.__next__())

    def send(self, message: json):
        try:
            self.websocket.send(json.dumps(message))
        except Exception as e:
            raise Exception(e)

    def test_send_heartbeat(self):
        while True:
            time.sleep(5)
            if not self.websocket:
                continue
            try:
                self.websocket.send(json.dumps({"type": "message", "message": "ping"}))
            except Exception as e:
                raise Exception(e)
        return

    def create_connection(self, timestamp: int = 0):
        if not timestamp:
            timestamp = int(time.time())

        try:
            threading.Thread(target=self.test_send_heartbeat).start()

            with connect(self.base_url,
                         additional_headers={"api-key": self.api_key, "signature": self.hashing(timestamp), "timestamp": str(timestamp)}
                         ) as self.websocket:
                while True:
                    yield self.websocket.recv()

        except Exception as e:
            self.close()
            raise Exception(e)


class ZerocapRestClient:
    def __init__(self, api_key: str, api_secret: str, env: str='prod'):
        self.api_key = api_key
        self.api_secret = api_secret
        # signature = self.encryption_api_key()
        if env == 'development':
            self.base_url = "https://dma-api.defi.wiki/v2/orders"
            self.api_base_url = "https://dma-api.defi.wiki/v2"
        elif env == 'uat':
            self.base_url = "https://dma-uat-api.defi.wiki/v2/orders"
            self.api_base_url = "https://dma-uat-api.defi.wiki/v2"
        elif env == 'prod':
            self.base_url = "https://dma-api.zerocap.com/v2/orders"
            self.api_base_url = "https://dma-api.zerocap.com/v2"
        elif env == 'sandbox':
            self.base_url = "https://sandbox-api.zerocap.com/v2/orders"
            self.api_base_url = "https://sandbox-api.zerocap.com/v2"
        else:
            self.base_url = ''
            self.api_base_url = ''
        # url = f"{self.base_url}/api_key_signature_valid"
        # headers = {
        #     'Content-Type': 'application/json',
        # }
        # data = {
        #     "api_key": self.api_key,
        #     "signature": signature,
        # }
        # response = requests.post(url, data=json.dumps(data), headers=headers)
        # check_pass = False
        #
        # if response.status_code == 200:
        #     result = response.json()
        #     if result["status_code"] ==200:
        #         check_pass = True
        #
        # if not check_pass:
        #     raise Exception("ZerocapRestClient init fail")
        
    def hashing(self, timestamp):
        return hmac.new(
            self.api_secret.encode("utf-8"), str(timestamp).encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def encryption_api_key(self, timestamp):
        signature = self.hashing(timestamp)
        return signature

    def create_order(
        self,
        symbol: str, 
        side: str, 
        type: str, 
        amount: str,
        coinroutes_customer_id: int=0,
        price: str = "0",
        client_order_id: str = "",
        timestamp: int = 0,
    ):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            raise Exception("Create Order Api Key error")

        url = f"{self.base_url}/create_order"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }
        data = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "amount": amount,
            "price": price,
            'coinroutes_customer_id': coinroutes_customer_id,
            "client_order_id": client_order_id,
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def fetch_order(
        self, id: str,
        timestamp: int = 0,
    ):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            raise Exception("Fetch Order Api Key error")

        url = f"{self.base_url}/fetch_order"
        headers = {
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }
        data = {
            "id": id,
        }
        response = requests.get(url, params=data, headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def fetch_orders(
        self,
        start_datetime: int=0,
        end_datetime: int=0,
        symbol: str='',
        page: int=1,
        limit: int=500,
        ids: str="",
        status: str="",
        sort_order: str="desc",
        order_type: str="",
        side: str="",
        timestamp: int = 0,
    ):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            return "Fetch Orders Api Key error"

        url = f"{self.base_url}/fetch_orders"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }
        data = {
            "symbol": symbol,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "page": page,
            "ids": ids,
            "status": status,
            "sort_order": sort_order,
            "order_type": order_type,
            "side": side,
            "limit": limit,
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def get_balances(self, timestamp: int = 0):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            return "GetBalances Api Key error"

        url = f"{self.base_url}/get_balances"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def request_for_quote(self, symbol: str = "",
                          side: str = "",
                          quantity: str = "",
                          client_order_id: str = "",
                          timestamp: int = 0):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            return "RequestForQuote Api Key error"

        url = f"{self.base_url}/request_for_quote"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }

        data = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "client_order_id": client_order_id
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def get_instruments(self, timestamp: int = 0):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            return "GetInstruments Api Key error"

        url = f"{self.base_url}/get_instruments"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def get_transfers(self, start_datetime: int = 0,
                      end_datetime: int = 0,
                      asset_id: str = "",
                      type: str = "",
                      page: int = 1,
                      limit: int = 20,
                      sort_order: str = "desc",
                      timestamp: int = 0):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            return "Get Transfer Api Key error"

        url = f"{self.base_url}/get_transfers"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }

        data = {
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "asset_id": asset_id,
            "type": type,
            "page": page,
            "limit": limit,
            "sort_order": sort_order
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)

    def get_time(self, timestamp: int = 0):
        if not timestamp:
            timestamp = int(time.time())
        signature = self.encryption_api_key(timestamp)
        if signature == "fail":
            raise Exception("Create Order Api Key error")

        url = f"{self.api_base_url}/systems/get_time"
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
            'signature': signature,
            "timestamp": str(timestamp),
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            raise Exception(response.text)
