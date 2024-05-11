from flask import jsonify, request
from markupsafe import escape
import ccxt
from utils.accounts import *

binance_markets_cache = None
kucoin_markets_cache = None


def load_exchange_markets(exchange_name, markets_cache):
    try:
        exchange = getattr(ccxt, exchange_name.lower())()
        markets = exchange.load_markets()
        markets_cache = markets
        return markets_cache
    except Exception as e:
        error_message = f"Error fetching {exchange_name} markets: {e}"
        return jsonify({"error": error_message}), 500


def get_binance_markets():
    global binance_markets_cache
    if binance_markets_cache is None:
        binance_markets_cache = load_exchange_markets("binance", binance_markets_cache)
    return binance_markets_cache


def get_kucoin_markets():
    global kucoin_markets_cache
    if kucoin_markets_cache is None:
        kucoin_markets_cache = load_exchange_markets("kucoin", kucoin_markets_cache)
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
    try:
        markets = fetch_data(
            "SELECT market_name, account_name, exchange_name FROM markets INNER JOIN accounts ON markets.account_id = accounts.id"
        )

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

        return jsonify(markets)
    except Exception as e:
        error_message = f"Error fetching markets: {e}"
        return jsonify({"error": error_message}), 500


def add_market():
    new_market = request.get_json()
    account_id = new_market["account_id"]
    market_name = new_market["market_name"]

    try:
        execute_query(
            "INSERT INTO markets (account_id, market_name) VALUES (?, ?)",
            (account_id, market_name),
        )
        return jsonify(""), 204
    except Exception as e:
        error_message = f"Error adding market: {e}"
        return jsonify({"error": error_message}), 500
