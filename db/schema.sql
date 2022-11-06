CREATE TABLE IF NOT EXISTS GROCERIES (
    "ID"            INTEGER PRIMARY KEY AUTOINCREMENT,
    "NAME"          TEXT NOT NULL,
    "SHOPPING_LIST" BOOLEAN DEFAULT 1,
    "SHOPPING_CART" BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS LASTUPDATE (
    "TS"  timestamp
);

INSERT INTO LASTUPDATE (TS) VALUES (0);
