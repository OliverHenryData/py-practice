

import sqlite3
from pathlib import Path
DB_PATH = Path("practice_trades.db")


def connect_db(db_path : Path, timeout : int = 5) -> sqlite3.Connection:
    """
    Connect to SQLite db file. Creates file if not existing.
    args:
        timeout = 5, wait up to 5 seconds in db locked
    
    """

    connection = sqlite3.connect(db_path,timeout=timeout)
    return connection

# SQLite is a bit different from PostgreSQL/MySQL. It mainly uses storage classes:

# NULL     = no value
# INTEGER  = whole numbers
# REAL     = floating-point numbers
# TEXT     = strings
# BLOB     = raw binary data

# i.e
# id INTEGER
# price REAL
# symbol TEXT
# raw_data BLOB
# missing_value NULL

# Other data types accepted but mapped to above internals
# VARCHAR(20) treated as TEXT,  BOOLEAN treated as 0,1 integefer
# DATE, DATETIME, can be stored as TEXT INTEGER OR REAL depending on design
# DECIMAL(10, 2)
# FLOAT, DOUBLE

# SQLite accepts many of these, but internally it maps them into its looser type system.

# CONSTRAINTS
# UNIQUE no duplicates in this column
# PRIMARY KEY main unique row id

#FOREIGN KEY (...) links this table to another
def drop_trades_table(connection: sqlite3.Connection) -> None:
    """
    Delete the trades table completely.

    DROP TABLE removes:
    - the table
    - all rows inside it
    - the schema definition

    This is different from DELETE FROM trades, which deletes rows but leaves
    the table structure intact.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        DROP TABLE IF EXISTS trades
        """
    )

    connection.commit()

def list_tables(connection: sqlite3.Connection) -> list[tuple]:
    """
    List all tables in the SQLite database.

    sqlite_master is SQLite's internal metadata table.
    It stores information about tables, indexes, views, triggers, etc.

    We filter for type = 'table' to see user/database tables.
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    )

    return cursor.fetchall()

def create_table(connection: sqlite3.Connection) -> None:
    """
    Create a table if one does not already exist.

    Conceptual model:

    connection = open link to db file.
    cursor = object used to send SQL commands via connection
    execute = send one command to db engine
    commit = makes db change permanent

    """

    #cursor is like a db cmnd runner created via open connection
    #connection "owns" actual db session
    #cursor executes sql statements
    cursor = connection.cursor()

    #create table changes database schema
    #"schema" means db structures tables,cols,constraints
    # IF NOT Exists means leave as is

    #schema is essentially 
    #column_name TYPE constraints default

    #
    #id            = column name
    #INTEGER       = whole number type
    #PRIMARY KEY   = unique row identifier
    #AUTOINCREMENT = SQLite automatically gives each new row the next id

    #usually id not manually inserted sqlite fills it
    # NOT NUll every row must have it
    # CHECK only allow certain values

    #SQLite does not have a strict separate boolean type 
    # like some databases, so people often use:

    print("In create table.")
    cursor.execute("""

    CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL, 
        side TEXT NOT NULL CHECK (side in ('BUY','SELL')),
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        entry_price REAL NOT NULL,
        exit_price REAL CHECK (exit_price IS NULL OR exit_price > 0),
        is_closed integer NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )

    """)

    connection.commit() #finalizes and saves changes
    #without commit change may not be permanetly saved 

    print("Created table")

def is_database_locked(db_path: Path) -> bool:
    """
    Basic lock check.

    SQLite locks usually happen when another connection/process has an open write
    transaction, this tries to briefly obtain a write lock.

    Begin IMMEDIATE tries to start a write transaction immediately.
    if another write holds the database sqlite3.OperationError may be raised

    """

    try:
        connection = sqlite3.connect(db_path, timeout=1) # try obtain connection
        cursor = connection.cursor()
        cursor.execute("Begin Immediate")
        connection.rollback()
        connection.close()
        return False

    except sqlite3.OperationalError as error:
        if "locked" in str(error).lower():
            return True
        raise 

def delete_trade(connection: sqlite3.Connection, trade_id : int) -> None:
    """
    Delete one trade by primary key
    """
    cursor = connection.cursor()
    cursor.exectute(
        """
        DELETE FROM trades
        where id = ?
        """, (trade_id),

    )
    connection.commit()

def insert_trade(
        connection: sqlite3.Connection,
        symbol: str,
        side:str,
        quantity:int,
        entry_price: float,
        exit_price : float | None = None,
        is_closed: int = 0,
) -> None:
    """
    Insert one trade into trades table, is an Insert Query
    SQL Statement contains placeholders ?:
        VALUES (?,?,?,?,?,?)
        these are parameter placeholders.

        good: cursor.execute(".. WHERE id = ?", (trade_id,))
        bad: cursor.execute(f"... WHERE id = {trade_id}") < allows sqlinjections

    """

    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT into trades (
            symbol, side, quantity, entry_price, exit_price, is_closed
        )
        VALUES (?,?,?,?,?,?)
        """,
        (symbol,side,quantity,entry_price,exit_price, is_closed)
    )
    #INSERT changes database, still need to commit
    connection.commit()

def get_trade_by_id(connection : sqlite3.Connection, trade_id : int) -> tuple | None:
    """
        Retrieve one trade via primary key.
        The id column is the primary key, so each id identifies one row
        fetchone() gets one row from query result
        if no matching row returns None
    """
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            symbol,
            side,
            quantity,
            entry_price,
            exit_price,
            is_closed,
            created_at

        FROM trades
        WHERE id = ?
        """,
        (trade_id,),
    )

    row = cursor.fetchone()
    return row

def get_all_trades(connection : sqlite3.Connection) -> list[tuple]:

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            symbol,
            side,
            quantity,
            entry_price,
            exit_price,
            is_closed,
            created_at

        FROM trades
        ORDER BY id
        """)
    rows = cursor.fetchall()
        
    return rows

def get_closed_trade_pnl(connection: sqlite3.Connection) -> list[tuple]:
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            id,symbol,side,quantity,entry_price,exit_price,
            CASE
                WHEN side = 'BUY' THEN (exit_price - exit_price) * quantity
                WHEN side = 'SELL' THEN (entry_price-exit_price)*quantity
            END as pnl
                   
        FROM trades
        WHERE is_closed = 1
        ORDER BY pnl DESC
        """)
    rows = cursor.fetchall()
    return rows

def update_trade_exit(
    connection: sqlite3.Connection,
    trade_id: int,
    exit_price: float) -> None:

    cursor = connection.cursor()

    #pattern 
    #     UPDATE table_name
        # SET
        #     column_1 = value_1,
        #     column_2 = value_2,
        #     column_3 = value_3
        # WHERE some_column = some_value

    cursor.execute("""
        UPDATE trades
        SET
            exit_price = ?,
            is_closed = 1
        WHERE id = ?

    """, (exit_price,trade_id),)

    connection.commit()



def print_rows(title: str, rows : list[tuple]) -> None:
    print(f"\n{title}")
    for row in rows:
        print(row)


def main():
    
    print("Running SQL refresher code")

    connection = connect_db(DB_PATH)

    try:

        list_tables(connection)
        drop_trades_table(connection)

        create_table(connection)
        insert_trade(connection, "BTCUSD", "BUY",2, 65000.0,66000.0,1)
        insert_trade(connection, "ETHUSD", "SELL", 5, 3500.0, 3400.0, 1)
        insert_trade(connection, "XAUUSD", "BUY", 10, 2300.0)

        all_trades = get_all_trades(connection)
        print_rows("All trades:", all_trades)

        update_trade_exit(connection, trade_id=3, exit_price=2350.0)

        updated_trade = get_trade_by_id(connection, trade_id=3)
        print("\nTrade 3 after update:")
        print(updated_trade)

        all_trades = get_all_trades(connection)
        print_rows("All trades after update:", all_trades)
        print(f"\nDatabase locked? {is_database_locked(DB_PATH)}")


    except sqlite3.Error as error:
        connection.rollback() #rollback cancel any uncomitted change in db 
        print(f"Database error: {error}")

    finally:
        #always runs and closes the connection so another process can use it
        connection.close()
        print("\nConnection has been closed.")

    


if __name__ == "__main__":
    main()