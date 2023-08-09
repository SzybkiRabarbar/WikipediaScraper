from mediawiki import MediaWiki
import sqlite3
import pandas as pd
from scripts.scraper import SearchPath

wiki = MediaWiki()

def initialize(start: str, destination: str, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO results (start, destination, result) VALUES ('{start}', '{destination}', '')")
    cursor.execute(f"CREATE TABLE '{start} | {destination} | Paths' (id INTEGER PRIMARY KEY, path TEXT)")
    cursor.execute(f"CREATE TABLE '{start} | {destination} | Names' (id INTEGER PRIMARY KEY, href_name TEXT)")
    cursor.execute(f"INSERT INTO '{start} | {destination} | Names' (href_name) VALUES ('{start}')")
    cursor.execute(f"INSERT INTO '{start} | {destination} | Paths' (path) VALUES ('1')")
    conn.commit()

def get_directions() -> list[str]:
    starting_url = wiki.opensearch(input("Start:"), results=1)
    destination_url = wiki.opensearch(input("Destination:"), results=1)
    return [starting_url[-1][-1], destination_url[-1][-1]]

if __name__=="__main__":
    # start, destination = [i.replace('https://en.wikipedia.org/wiki/','') for i in get_directions()]
    start, destination = 'Poland', 'Japan'
    conn = sqlite3.connect('db\\dbSQLite.db')
    df = pd.read_sql_query("SELECT * FROM results", conn, index_col='id')
    if df.loc[(df['start'] == start) & (df['destination'] == destination)].empty:
        print("NEW PATH")
        initialize(start, destination, conn)
    conn.close()
    res = SearchPath(start, destination)
    print(res.final_result)
