import requests
import hashlib
import hmac
import time
from typing import Dict
import pyotp
import qrcode
from os import environ, system

def generate_signature(api_secret, query_string):
    return hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def generate_qr_code():
    secret_key = pyotp.random_base32()
    uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
        name="Binance Info User",
        issuer_name='BinanceInfo'
    )
    environ["SECRET_KEY"] = secret_key
    image = qrcode.make(uri)
    image.save("qrcode.png")
    system("qrcode.png")

class BinanceInfo:
    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.secret_key = environ.get("SECRET_KEY")

    def get_account_info(self) -> Dict:
        if not self.secret_key:
            print("Register on Google Authenticator First")
            generate_qr_code()
            return
        totp = pyotp.TOTP(self.secret_key)
        while True:
            code = input("Enter code(leave empty to escape): ")
            if not code:
                return
            if totp.verify(code):
                break
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