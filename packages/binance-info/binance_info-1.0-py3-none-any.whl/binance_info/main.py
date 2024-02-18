import requests
import hashlib
import hmac
import time
from typing import Dict

def generate_signature(api_secret, query_string):
    return hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

class BinanceInfo:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_account_info(self) -> Dict:
        endpoint = "/account"
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = generate_signature(self.api_secret, query_string)
        headers = {
            "X-MBX-APIKEY": self.api_key
        }
        params = {
            "timestamp": timestamp,
            "signature": signature
        }
        response = requests.get(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)
        return response.json()