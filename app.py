from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import ccxt
from markupsafe import escape

app = Flask(__name__)
CORS(app, resources=r"/api/*")


def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.after_request
def after_request(response):
    return add_cors_headers(response)


def get_db_connection():
    conn = sqlite3.connect("kairon.db")
    conn.row_factory = sqlite3.Row
    return conn


# EXCHANGES


@app.route("/api/exchanges")
def get_exchanges():
    return jsonify(ccxt.exchanges)


def verify_exchange_credentials(exchange_name, public_key, private_key):
    exchange = getattr(ccxt, exchange_name)(
        {"apiKey": public_key, "secret": private_key}
    )
    try:
        account_info = exchange.fetch_balance()
    except:
        return False
    return True


# ACCOUNTS


@app.route("/api/accounts")
def get_accounts():
    db = get_db_connection()
    cursor = db.execute("SELECT id, account_name, exchange_name FROM accounts")
    accounts = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(accounts)


@app.route("/api/accounts", methods=["POST"])
def add_account():
    new_account = request.get_json()
    account_name = new_account["account_name"]
    exchange_name = new_account["exchange_name"]
    public_key = new_account["public_key"]
    private_key = new_account["private_key"]

    if verify_exchange_credentials(exchange_name, public_key, private_key) is True:
        db = get_db_connection()
        db.execute(
            "INSERT INTO accounts (account_name, exchange_name, public_key, private_key) VALUES (?, ?, ? , ?)",
            (account_name, exchange_name, public_key, private_key),
        )
        db.commit()
        db.close()
        response = jsonify("")
        return response, 204
    else:
        return jsonify("Invalid credentials"), 400


def get_account_info(id):
    db = get_db_connection()
    cursor = db.execute(
        "SELECT exchange_name, public_key, private_key FROM accounts WHERE id = ?", (id)
    )
    info = [dict(row) for row in cursor.fetchall()]
    db.close()
    return info


# MARKETS


binance_markets_cache = None
kucoin_markets_cache = None


def get_binance_markets():
    global binance_markets_cache
    if binance_markets_cache is None:
        binance = ccxt.binance()
        markets = binance.load_markets()
        binance_markets_cache = markets
    return binance_markets_cache


def get_kucoin_markets():
    global kucoin_markets_cache
    if kucoin_markets_cache is None:
        kucoin = ccxt.kucoin()
        markets = kucoin.load_markets()
        kucoin_markets_cache = markets
    return kucoin_markets_cache


exchange_market_functions = {
    "binance": get_binance_markets,
    "kucoin": get_kucoin_markets,
}


@app.route("/api/markets/<id>/all")
def get_all_exchange_markets(id):
    if id == "undefined":
        return jsonify([])

    escaped_id = escape(id)
    account_info = get_account_info(escaped_id)
    exchange_name = account_info[0]["exchange_name"]

    market_function = exchange_market_functions.get(exchange_name)
    if market_function:
        markets = market_function()
        return jsonify(markets)

    return jsonify([])


@app.route("/api/markets")
def get_markets():
    db = get_db_connection()
    cursor = db.execute(
        "SELECT market_name, account_name, exchange_name FROM markets INNER JOIN accounts ON markets.account_id = accounts.id"
    )
    markets = [dict(row) for row in cursor.fetchall()]
    for market in markets:
        if market["exchange_name"] == "binance":
            exchange = ccxt.binance()
        elif market["exchange_name"] == "kucoin":
            exchange = ccxt.kucoin()
        ticker = exchange.fetch_ticker(market["market_name"])
        market_data = {
            "market_name": market["market_name"],
            "price": ticker["last"],
            "account_name": market["account_name"],
        }
        market.update(market_data)

    db.close()
    return jsonify(markets)


@app.route("/api/markets", methods=["POST"])
def add_market():
    new_market = request.get_json()
    account_id = new_market["account_id"]
    market_name = new_market["market_name"]

    db = get_db_connection()
    db.execute(
        "INSERT INTO markets (account_id, market_name) VALUES (?, ?)",
        (account_id, market_name),
    )
    db.commit()
    db.close()
    response = jsonify("")
    return response, 204
