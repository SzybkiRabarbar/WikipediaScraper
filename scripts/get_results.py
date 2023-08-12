import sqlite3
import pandas as pd
from converter_URL_encoded_char import decode_URL

def reset_readme() -> None:
    with open("db\\README.md", mode="w") as file:
        file.writelines(["# Results","\n"])

def get_content(start: str, destination: str, path: str) -> str:
    res = ''
    df = pd.read_sql_query(
        f'SELECT id FROM "{start} | {destination} | Paths" WHERE path == "{path}"',
        conn).to_numpy().tolist()
    if df==[[1]]:
        res += "Path found" + '\n'
        res += get_route(start, destination, path) + '\n'
        res += 'Scraped 1 site' + '\n'
    elif df:
        res += "Path found" + '\n'
        res += get_route(start, destination, path) + '\n'
        res += f"Scraped {df[0][0]} sites" + '\n'
        res += f"Found {get_num_of_pages(start, destination)} uniqe sites" + '\n'
    else:
        res += 'Path not found' + '\n'
        res += get_route(start, destination, path) + '\n'
        res += f"Scraped {str(get_min_id(start, destination) - 1)} sites" + '\n'
        res += f"Found {get_num_of_pages(start, destination)} uniqe sites" + '\n'
    return res

def get_route(start: str, destination: str, path: str) -> str:
    route = pd.read_sql_query(
            f'SELECT href_name FROM "{start} | {destination} | Names" WHERE id IN ({path})',
            conn).to_numpy().tolist()
    msg = f"{readme_link(start)} > ???"
    return f"{' > '.join([readme_link(r[0]) for r in route]) if route else msg} > {readme_link(destination)}"

def readme_link(site_name: str) -> str:
    return f"[{decode_URL(site_name)}](https://en.wikipedia.org/wiki/{site_name})"

def get_min_id(start: str, destination: str) -> int:
    cursor = sqlite3.Cursor(conn)
    cursor.execute(f'SELECT MIN(id) FROM "{start} | {destination} | Paths"')
    num = cursor.fetchone()[0]
    cursor.close()
    return num

def get_num_of_pages(start: str, destination: str) -> int:
    cursor = sqlite3.Cursor(conn)
    cursor.execute(f'SELECT MAX(id) FROM "{start} | {destination} | Names"')
    num = cursor.fetchone()[0]
    cursor.close()
    return num

if __name__=="__main__":
    conn = sqlite3.connect("db\\dbSQLite.db")
    df = pd.read_sql_query(
        f"SELECT * FROM results",
        conn)
    reset_readme()
    for id, start, destination, path in df.to_numpy().tolist():
        content = []
        content.append(f'{decode_URL(start)} >> {decode_URL(destination)} \n')
        content.append('---' + '\n')
        content.append(get_content(start, destination, path))
        content.append('***' + '\n')
        
        with open("db\\README.md", mode="a") as file:
            file.writelines(content)
    conn.close()