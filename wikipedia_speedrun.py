from mediawiki import MediaWiki
import sqlite3
import pandas as pd
from scripts.initializer import initialize

wiki = MediaWiki()

def get_directions() -> list[str]:
    starting_url = wiki.opensearch(input("Start:"), results=1)
    destination_url = wiki.opensearch(input("Destination:"), results=1)
    return [starting_url[-1][-1], destination_url[-1][-1]]

if __name__=="__main__":
    #inputs = [i.replace('https://en.wikipedia.org/wiki/','') for i in get_directions()]
    inputs = ['Poland', 'Japan']
    conn = sqlite3.connect('db\\dbSQLite.db')
    df = pd.read_sql_query("SELECT * FROM results", conn, index_col='id')
    if not df.loc[(df['start'] == inputs[0]) & (df['destination'] == inputs[1])].empty:
        print("exist")
    else:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO results (start, destination, result) VALUES ('{inputs[0]}', '{inputs[1]}', '')")
        conn.commit()
        initialize(inputs[0], inputs[1])
    conn.close()

# TODO nowy scraper i podłączenie z nim 