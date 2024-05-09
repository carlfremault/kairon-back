DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS markets;

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    account_name TEXT NOT NULL,
    exchange_name TEXT NOT NULL,
	public_key TEXT NOT NULL,
	private_key TEXT NOT NULL
);

CREATE TABLE markets (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	market_name TEXT NOT NULL,
	account_id INTEGER,
	FOREIGN KEY (account_id) REFERENCES accounts(id)
);
	