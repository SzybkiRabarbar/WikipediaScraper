import sqlite3

def initialize(start: str, destination: str) -> None:
    conn = sqlite3.connect('db\\dbSQLite.db')
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE {start}___{destination}(id INTEGER PRIMARY KEY, path TEXT)")
    conn.commit()
    conn.close()