#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot
CLI entry point — run with: python cli.py --help
"""

import argparse
import json
import os
import sys

from bot import (
    BinanceFuturesClient, BinanceClientError,
    place_market_order, place_limit_order, place_stop_market_order,
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price, validate_stop_price,
    ValidationError, setup_logger,
)

logger = setup_logger("cli")

# ── helpers ──────────────────────────────────────────────────────────────────

def _print_summary(label: str, data: dict) -> None:
    print(f"\n{'─'*50}")
    print(f"  {label}")
    print(f"{'─'*50}")
    for k, v in data.items():
        if v is not None and v != "":
            print(f"  {k:<14}: {v}")
    print(f"{'─'*50}\n")


def _get_credentials() -> tuple[str, str]:
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        print(
            "\n[ERROR] API credentials not found.\n"
            "Export them before running:\n"
            "$env:BINANCE_API_KEY="your_key\n"
	    "$env:BINANCE_API_SECRET="your_secret"\n"
        )
        sys.exit(1)
    return api_key, api_secret


# ── argument parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

  # Stop-Market BUY (bonus order type)
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 60000

Credentials are read from environment variables:
  BINANCE_API_KEY
  BINANCE_API_SECRET
""",
    )
    parser.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True, help="BUY or SELL")
    parser.add_argument("--type",       required=True, dest="order_type",
                        help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--quantity",   required=True, help="Order quantity")
    parser.add_argument("--price",      default=None,  help="Limit price (required for LIMIT)")
    parser.add_argument("--stop-price", default=None,  dest="stop_price",
                        help="Stop trigger price (required for STOP_MARKET)")
    parser.add_argument("--tif",        default="GTC",
                        help="Time-in-force for LIMIT orders (default: GTC)")
    return parser


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # ── validate inputs ──
    try:
        symbol     = validate_symbol(args.symbol)
        side       = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity   = validate_quantity(args.quantity)

        if order_type == "LIMIT":
            if not args.price:
                parser.error("--price is required for LIMIT orders.")
            price = validate_price(args.price)

        if order_type == "STOP_MARKET":
            if not args.stop_price:
                parser.error("--stop-price is required for STOP_MARKET orders.")
            stop_price = validate_stop_price(args.stop_price)

    except ValidationError as e:
        print(f"\n[VALIDATION ERROR] {e}\n")
        logger.warning("Validation failed: %s", e)
        sys.exit(1)

    # ── print request summary ──
    req_summary = {
        "symbol":     symbol,
        "side":       side,
        "order_type": order_type,
        "quantity":   quantity,
    }
    if order_type == "LIMIT":
        req_summary["price"] = price
        req_summary["timeInForce"] = args.tif
    if order_type == "STOP_MARKET":
        req_summary["stop_price"] = stop_price

    _print_summary("ORDER REQUEST", req_summary)
    logger.info("Order request: %s", json.dumps(req_summary))

    # ── connect and place ──
    api_key, api_secret = _get_credentials()
    client = BinanceFuturesClient(api_key, api_secret)

    try:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price, args.tif)
        elif order_type == "STOP_MARKET":
            result = place_stop_market_order(client, symbol, side, quantity, stop_price)

        _print_summary("ORDER RESPONSE", result)
        print(f"  ✅  Order placed successfully! (orderId: {result['orderId']})\n")
        logger.info("Order placed successfully. orderId=%s", result["orderId"])

    except BinanceClientError as e:
        print(f"\n  ❌  Order failed: {e}\n")
        logger.error("Order failed: %s", e)
        sys.exit(1)
    except Exception as e:
        print(f"\n  ❌  Unexpected error: {e}\n")
        logger.exception("Unexpected error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
