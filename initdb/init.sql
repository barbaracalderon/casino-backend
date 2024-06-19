\c casino;


CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    balance FLOAT DEFAULT 0.0
);


CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    txn_uuid VARCHAR(255) UNIQUE NOT NULL,
    player_id INTEGER NOT NULL REFERENCES players(id),
    value_bet FLOAT DEFAULT 0.0,
	value_win FLOAT DEFAULT 0.0,
    rolled_back BOOLEAN DEFAULT FALSE
);