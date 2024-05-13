from .db import *


def get_account_info(id):
    info = fetch_data(
        "SELECT exchange_name, public_key, private_key FROM accounts WHERE id = ?", (id)
    )
    return info
