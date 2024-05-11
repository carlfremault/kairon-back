from flask import jsonify, request
from markupsafe import escape
import ccxt
from utils.accounts import *

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
