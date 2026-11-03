# Signal Alert Pipeline

A small project that takes trading signals, saves them, sends them to Telegram, and later checks whether each signal hit its target or its stop.

I built it to learn how a real alert system fits together: a web API, a database, a chat bot, and a script that follows up on the results. It works end to end, but it is a learning project, not a trading system. Please read the [Limitations](#limitations) section before trusting any numbers it produces.

## What it does

1. **Receives a signal.** Anything that can send an HTTP request can post a JSON signal to the `/webhook` endpoint (MetaTrader 5, TradingView, a Python script, or `curl`).
2. **Checks it.** The secret token has to match, and the JSON has to have the right fields. Anything else is rejected.
3. **Saves it.** Signals go into a SQLite database. If the same `signal_id` arrives twice, the second one is ignored, so a retry will not send a double alert.
4. **Sends it to Telegram.** This happens in the background, so the API answers right away even if Telegram is slow.
5. **Follows up.** A separate script looks at the live price and marks each signal as `target_hit` or `stop_hit`.
6. **Reports.** Another script prints a short summary: wins, losses, win rate, and total profit and loss in percent.

```
Sender (MT5 / TradingView / script)
        |  POST /webhook  (JSON + secret)
        v
   FastAPI app  -->  SQLite database
        |
        +--> Telegram alert (background task)

scripts/track_outcomes.py  -->  checks live prices, updates results
scripts/generate_report.py -->  prints win rate and total PnL
```

## Tech stack

- Python 3.10 or newer
- FastAPI and Uvicorn (the web API)
- Pydantic (input validation)
- SQLAlchemy and SQLite (storage)
- httpx (Telegram and Binance requests)
- yfinance (forex prices from Yahoo Finance)
- pytest (tests)

## Getting started

### 1. Download and install

```bash
git clone https://github.com/amir-mirshahi/signal-alert-pipeline.git
cd signal-alert-pipeline

python -m venv venv
# Windows (PowerShell):  .\venv\Scripts\Activate.ps1
# macOS / Linux:         source venv/bin/activate

pip install -r requirements.txt
```

### 2. Create your `.env` file

Copy `.env.example` to `.env` and fill it in:

```
WEBHOOK_SECRET=put-a-long-random-string-here
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
DATABASE_URL=sqlite:///./signals.db
```

- `WEBHOOK_SECRET` is required and must be at least 16 characters. The app will refuse to start without it. You can generate one with:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- The Telegram values are optional. If you leave them out, alerts are printed to the console instead, which is handy for trying things out.
- To get a bot token, talk to [@BotFather](https://t.me/BotFather) in Telegram. To find your chat ID, send your bot a message and open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`.
- Never commit your `.env` file. It is already listed in `.gitignore`.

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. FastAPI also gives you an interactive page at `http://127.0.0.1:8000/docs`.

### 4. Send a test signal

With the server running, open a second terminal and run:

```bash
python scripts/send_fake_signal.py
```

It sends a valid signal, a duplicate, one with a wrong token, and one with a bad format, so you can see each case being handled.

You can also send one by hand:

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_SECRET" \
  -d '{
    "schema": "1.0",
    "source": "curl",
    "indicator_version": "1.0.0",
    "signal_id": "demo-1",
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "bar_time": "2025-01-01T00:00:00Z",
    "type": "entry",
    "direction": "long",
    "entry": 42000.0,
    "stop": 41000.0,
    "target": 44000.0
  }'
```

A good answer looks like `{"status": "accepted", "signal_id": "demo-1"}`. Sending the same `signal_id` again returns `"duplicate"`.

## The signal format

| Field | Required | Notes |
|---|---|---|
| `schema` | yes | Version of the format, for example `"1.0"` |
| `source` | yes | Where it came from (`mt5`, `tradingview`, ...) |
| `indicator_version` | yes | Version of whatever produced the signal |
| `signal_id` | yes | Must be unique. Used to block duplicates |
| `symbol` | yes | For example `BTCUSDT` or `EURUSD` |
| `timeframe` | yes | One of `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d` |
| `bar_time` | yes | Time of the candle, ISO format |
| `type` | yes | `entry`, `exit`, `update` or `alert` |
| `direction` | yes | `long` or `short` |
| `entry`, `stop`, `target` | no | Needed if you want the outcome tracked |
| `notes` | no | Free text, up to 1000 characters |

Unknown fields are rejected on purpose, so typos do not slip through quietly.

## Tracking results and reports

```bash
python scripts/track_outcomes.py     # checks pending signals against the live price
python scripts/generate_report.py    # prints wins, losses, win rate, total PnL
python scripts/view_db.py            # prints what is in the database
```

Run the tracker whenever you want fresh results (for example from a scheduler). Only `entry` signals with an entry, a stop and a target are tracked. Others are skipped.

Prices come from Binance for symbols with `USDT` or `BTC` in the name, and from Yahoo Finance for everything else (it looks up `<SYMBOL>=X`, like `EURUSD=X`).

## Using it with MetaTrader 5

The `mt5/` folder has an MQL5 script that posts signals to the webhook. In MT5, go to **Tools, Options, Expert Advisors**, tick "Allow WebRequest for listed URL", and add the address of your server. MT5 blocks web requests until you do this.

## Running the tests

```bash
pytest
```

The tests use an in-memory database and a fake Telegram sender, so they never touch your real data or send real messages. They cover a valid signal, duplicates, a wrong token, and a badly formatted payload.

## Project layout

```
app/
  config.py      settings from .env (refuses to start without a secret)
  database.py    database connection
  models.py      the Signal table
  schemas.py     what a valid signal looks like
  security.py    secret token check
  telegram.py    sends alerts, retries if Telegram fails
  main.py        the /webhook endpoint
scripts/         tracker, report, test sender, database viewer
mt5/             MQL5 sender for MetaTrader 5
tests/           pytest tests
```

## Security notes

- The secret is compared with `hmac.compare_digest`, which avoids leaking information through response timing.
- The secret can be sent as an `X-Webhook-Secret` header or as a `?token=` URL parameter. The URL option exists because TradingView cannot send custom headers. The downside is that URLs can end up in server logs, so use the header whenever your sender allows it.
- Keep your bot token and webhook secret out of Git and out of screenshots.

## Limitations

This is a learning project, and I would rather be upfront about what it does not do:

- **Results are simulated, not real trades.** There are no fees, spreads, slippage, or partial fills. Real results would be worse.
- **The tracker only looks at the price at the moment it runs.** If price touched your stop and came back between two runs, it will not notice. A better version would read the candles since the signal and check each high and low.
- **It assumes you got in at the entry price**, even if the market never reached it.
- **Forex prices come from Yahoo Finance.** Those can be delayed or missing, and some symbols (gold, for instance) may not map correctly. A skipped symbol just stays `pending`.
- **Profit and loss is in percent only.** There is no position sizing and no risk-to-reward ratio yet.
- **SQLite and a single server** are fine for one person, but they are not built for heavy traffic.
- **Timestamps** are stored without time zone information in SQLite.

None of this is financial advice. Do not trade real money based on this project's results.

## Ideas for later

- Check candles instead of a single price, and add an entry-hit state.
- Add risk-to-reward, drawdown, and profit factor to the report.
- Run the tracker automatically on a schedule.
- Support MetaTrader 5 prices directly, so forex and gold can be tracked properly.
- Docker setup and automatic tests on every push (GitHub Actions).
