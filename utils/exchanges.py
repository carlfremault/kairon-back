import ccxt


def verify_exchange_credentials(exchange_name, public_key, private_key):
    exchange = getattr(ccxt, exchange_name)(
        {"apiKey": public_key, "secret": private_key}
    )
    try:
        account_info = exchange.fetch_balance()
    except:
        return False
    return True
