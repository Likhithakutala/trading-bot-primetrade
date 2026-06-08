# Trading Bot — Binance Futures Testnet

A lightweight Python CLI tool to place orders on the Binance Futures USDT-M Testnet. Supports MARKET, LIMIT, and STOP_MARKET order types with structured logging and clean error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Binance REST client (auth, signing, HTTP)
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # Input validation
│   └── logging_config.py   # Logging setup (file + console)
├── cli.py                   # CLI entry point (argparse)
├── logs/                    # Log files (auto-created)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Click **API Key** → generate a new key pair
4. Copy the API Key and Secret

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Export credentials

```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

---

## How to Run

### Place a MARKET order

```bash
# Buy 0.001 BTC at market price
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Sell 0.001 BTC at market price
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Place a LIMIT order

```bash
# Sell 0.001 BTC at $110,000 (resting limit, GTC)
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 110000

# Buy with custom time-in-force
python cli.py --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.01 --price 3000 --tif IOC
```

### Place a STOP_MARKET order (bonus)

```bash
# Trigger a market buy if price drops to $100,000
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 100000
```

### Help

```bash
python cli.py --help
```

---

## Sample Output

```
──────────────────────────────────────────────────
  ORDER REQUEST
──────────────────────────────────────────────────
  symbol        : BTCUSDT
  side          : BUY
  order_type    : MARKET
  quantity      : 0.001
──────────────────────────────────────────────────

──────────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────────
  orderId       : 4061880982
  symbol        : BTCUSDT
  side          : BUY
  type          : MARKET
  status        : FILLED
  origQty       : 0.001
  executedQty   : 0.001
  avgPrice      : 104823.10
──────────────────────────────────────────────────

  ✅  Order placed successfully! (orderId: 4061880982)
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` automatically.

- **File**: DEBUG level — full request params, response bodies, errors
- **Console**: INFO level — concise status messages

---

## Assumptions

- Uses Binance Futures **USDT-M Testnet** only (`https://testnet.binancefuture.com`)
- Credentials are passed via environment variables (not hardcoded)
- Default time-in-force for LIMIT orders is `GTC` (Good Till Cancelled)
- No real money is involved — testnet only
