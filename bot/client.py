import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("client")


class BinanceClientError(Exception):
    """Raised when Binance API returns an error response."""
    pass


def _make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = _make_session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, path: str, signed: bool = False, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        params = kwargs.get("params", {})

        if signed:
            params = self._sign(params)
            kwargs["params"] = params

        logger.debug("REQUEST  %s %s | params=%s", method.upper(), path, {
            k: v for k, v in params.items() if k != "signature"
        })

        try:
            resp = self.session.request(method, url, timeout=10, **kwargs)
        except requests.ConnectionError as e:
            logger.error("Network error: %s", e)
            raise BinanceClientError(f"Network error: {e}") from e
        except requests.Timeout:
            logger.error("Request timed out for %s %s", method, path)
            raise BinanceClientError("Request timed out. Check your connection.")

        logger.debug("RESPONSE %s %s | status=%s body=%s", method.upper(), path,
                     resp.status_code, resp.text[:500])

        try:
            data = resp.json()
        except ValueError:
            logger.error("Non-JSON response: %s", resp.text)
            raise BinanceClientError(f"Unexpected response: {resp.text}")

        # Binance error responses have a negative integer "code" field
        if isinstance(data, dict) and "code" in data and isinstance(data["code"], int) and data["code"] < 0:
            msg = data.get("msg", "Unknown API error")
            logger.error("API error code=%s msg=%s", data["code"], msg)
            raise BinanceClientError(f"API error {data['code']}: {msg}")

        if resp.status_code >= 400:
            logger.error("HTTP error status=%s body=%s", resp.status_code, resp.text[:200])
            raise BinanceClientError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        return data

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        return self._request("GET", "/fapi/v2/account", signed=True, params={})

    def place_order(self, **order_params) -> dict:
        return self._request("POST", "/fapi/v1/order", signed=True, params=order_params)
