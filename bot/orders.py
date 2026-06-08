from typing import Optional

from .client import BinanceFuturesClient
from .logging_config import setup_logger

logger = setup_logger("orders")


def _summarise(response: dict) -> dict:
    """Extract the most useful fields from a raw order response."""
    return {
        "orderId":     response.get("orderId"),
        "symbol":      response.get("symbol"),
        "side":        response.get("side"),
        "type":        response.get("type"),
        "status":      response.get("status"),
        "origQty":     response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "avgPrice":    response.get("avgPrice"),
        "price":       response.get("price"),
        "stopPrice":   response.get("stopPrice"),
        "timeInForce": response.get("timeInForce"),
        "updateTime":  response.get("updateTime"),
    }


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
) -> dict:
    logger.info("Placing MARKET %s order | symbol=%s qty=%s", side, symbol, quantity)
    params = dict(symbol=symbol, side=side, type="MARKET", quantity=quantity)
    raw = client.place_order(**params)
    result = _summarise(raw)
    logger.info("MARKET order placed | orderId=%s status=%s executedQty=%s avgPrice=%s",
                result["orderId"], result["status"], result["executedQty"], result["avgPrice"])
    return result


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    time_in_force: str = "GTC",
) -> dict:
    logger.info("Placing LIMIT %s order | symbol=%s qty=%s price=%s tif=%s",
                side, symbol, quantity, price, time_in_force)
    params = dict(
        symbol=symbol, side=side, type="LIMIT",
        quantity=quantity, price=price, timeInForce=time_in_force,
    )
    raw = client.place_order(**params)
    result = _summarise(raw)
    logger.info("LIMIT order placed | orderId=%s status=%s price=%s qty=%s",
                result["orderId"], result["status"], result["price"], result["origQty"])
    return result


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
    stop_price: str,
) -> dict:
    """Bonus: Stop-Market order — triggers a market order when stopPrice is hit."""
    logger.info("Placing STOP_MARKET %s order | symbol=%s qty=%s stopPrice=%s",
                side, symbol, quantity, stop_price)
    params = dict(
        symbol=symbol, side=side, type="STOP_MARKET",
        quantity=quantity, stopPrice=stop_price,
    )
    raw = client.place_order(**params)
    result = _summarise(raw)
    logger.info("STOP_MARKET order placed | orderId=%s status=%s stopPrice=%s",
                result["orderId"], result["status"], result["stopPrice"])
    return result
