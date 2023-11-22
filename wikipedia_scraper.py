from mediawiki import MediaWiki
import sqlite3
import pandas as pd
from scripts.scraper import SearchPath
from scripts.converter_URL_encoded_char import decode_URL

wiki = MediaWiki()

def initialize(start: str, destination: str, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO results (start, destination, result) VALUES ('{start}', '{destination}', '')")
    cursor.execute(f"CREATE TABLE '{start} | {destination} | Paths' (id INTEGER PRIMARY KEY, path TEXT)")
    cursor.execute(f"CREATE TABLE '{start} | {destination} | Names' (id INTEGER PRIMARY KEY, href_name TEXT)")
    cursor.execute(f"INSERT INTO '{start} | {destination} | Names' (href_name) VALUES ('{start}')")
    cursor.execute(f"INSERT INTO '{start} | {destination} | Paths' (path) VALUES ('1')")
    conn.commit()
    print("New Route Created")

def get_directions() -> list[str]:
    starting_url = wiki.opensearch(input("Start:"), results=1)
    destination_url = wiki.opensearch(input("Destination:"), results=1)
    return [i.replace('https://en.wikipedia.org/wiki/','') for i in [starting_url[-1][-1], destination_url[-1][-1]]]

if __name__=="__main__":
    start, destination = get_directions()
    print(f'\n{decode_URL(start)} -> {decode_URL(destination)}')
    
    conn = sqlite3.connect('db\\dbSQLite.db')
    df = pd.read_sql_query("SELECT * FROM results", conn, index_col='id')
    if df.loc[(df['start'] == start) & (df['destination'] == destination)].empty:
        initialize(start, destination, conn)
    conn.close()
    
    scraper = SearchPath(start, destination)
    scraper.print_answer()