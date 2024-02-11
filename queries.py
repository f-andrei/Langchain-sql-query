import sqlite3
import os

def get_table_names(conn):
    """
    Return a list of table names.

    Args:
        conn (sqlite3.Connection): SQLite database connection object.

    Returns:
        list: A list containing the names of all tables in the database.

    Raises:
        sqlite3.Error: If an error occurs during the execution of the SQL query.
    """
    try:
        table_names = []
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in tables.fetchall():
            table_names.append(table[0])
        return table_names
    except sqlite3.Error as e:
        print("Error while fetching table names:", e)
        return []

def get_column_names(conn, table_name):
    """
    Return a list of column names for a given table.

    Args:
        conn (sqlite3.Connection): SQLite database connection object.
        table_name (str): Name of the table for which column names are to be retrieved.

    Returns:
        list: A list containing the names of all columns in the specified table.

    Raises:
        sqlite3.Error: If an error occurs during the execution of the SQL query.
    """
    try:
        column_names = []
        columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
        for col in columns:
            column_names.append(col[1])
        return column_names
    except sqlite3.Error as e:
        print("Error while fetching column names:", e)
        return []

def get_database_info(database_path):
    """
    Return a list of dictionaries containing the table name and columns for each table in the database.

    Args:
        database_path (str): Path to the SQLite database file.

    Returns:
        list: A list of dictionaries where each dictionary contains the table name and its corresponding column names.

    Raises:
        OSError: If the specified database file does not exist.
        sqlite3.Error: If an error occurs during the execution of SQL queries.
    """
    if not os.path.isfile(database_path):
        print("Database file does not exist.")
        return []

    try:
        with sqlite3.connect(database_path) as conn:
            table_dicts = []
            for table_name in get_table_names(conn):
                columns_names = get_column_names(conn, table_name)
                table_dicts.append({"table_name": table_name, "column_name": columns_names})
            return table_dicts
    except sqlite3.Error as e:
        print("Error while fetching database info:", e)
        return []

def query_data(conn=None, query=None):
    """
    Execute a provided SQL query on the given database connection and return the results.

    Args:
        conn (sqlite3.Connection): SQLite database connection object.
        query (str): SQL query string to be executed.

    Returns:
        str: A string representation of the results of the SQL query.

    Raises:
        ValueError: If either the connection or the query is not provided.
        sqlite3.Error: If an error occurs during the execution of the SQL query.
    """
    try:
        if conn is None:
            raise ValueError("Connection is not provided.")
        if query is None:
            raise ValueError("Query is not provided.")
        results = str(conn.execute(query).fetchall())
    except sqlite3.Error as e:
        results = f"Query failed with error: {e}"
    except ValueError as ve:
        results = str(ve)
    return results
