import requests
from threading import Thread
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import time
from scripts.converter_URL_encoded_char import decode_URL

class SearchPath():
    
    def __init__(self, start, destination) -> None:
        self.start = start
        self.destination = destination
        self.conn = sqlite3.connect('db\\dbSQLite.db')
        self.session = requests.Session()
        if self.check_table_results():
            self.conn.close()
        else:
            print("Looking for route")
            self.main()
    
    def check_table_results(self) -> bool: 
        #| Checks if path was found earlier
        result = pd.read_sql_query(
            f'SELECT result FROM results WHERE start = "{self.start}" AND destination = "{self.destination}"',
            self.conn)
        if result.iloc[0]['result']:
            self.answer = result.iloc[0]['result']
            return True
        return False
    
    def fetch_path_data_from_db(self) -> tuple[list[tuple[str, str]], list[int]]: 
        #| Gets new paths from DB and transforms them into:
        #| - list with paths and the name of the last page in the each path
        #| - list with id of each path
        paths = pd.read_sql_query(
            f'SELECT id, path FROM "{self.start} | {self.destination} | Paths" LIMIT 5',
            self.conn)
        paths_ids = paths['id'].tolist()
        paths['href_id'] = [int(path.split(',')[-1]) for path in paths['path']]
        hrefs_names = pd.read_sql_query(
            f'SELECT id as href_id, href_name FROM "{self.start} | {self.destination} | Names" WHERE id IN ({",".join([str(i) for i in paths["href_id"]])})',
            self.conn)
        paths = pd.merge(paths, hrefs_names, on="href_id")
        paths = list(map(tuple, paths[['path', 'href_name']].to_numpy()))
        return (paths, paths_ids)
    
    def thread_process(self, path: tuple[str, str], new_hrefs: list) -> None:
        for new_href in self.scrap_paths(path):    
            if new_href:
                new_hrefs.append(new_href)
    
    def scrap_paths(self,path: tuple[str, str]) -> list[tuple[str, str]]: 
        #| Scraps page and returns list with paths and names of scraped page
        if not path:
            return []
        try:
            response = self.session.get(f"https://en.wikipedia.org/wiki/{path[1]}")
        except ConnectionError:
            print(f"ConnectionError: {path[1]}")
            return self.scrap_paths(path)
        soup = BeautifulSoup(response.content, "html.parser")

        content_div = soup.find('main', {'id': 'content'})
        hrefs = self.extract_hrefs_from_content(content_div)
        return [(path[0], h) for h in hrefs]
    
    def extract_hrefs_from_content(self, content_div) -> list[str]:
        #| Gets pages names from BeautifulSoup content
        result = []
        for link in content_div.find_all('a', href=True):
            if link['href'].startswith("/wiki/") and self.filter_href(link['href']):
                result.append(link['href'].replace("/wiki/","").replace('"', '%22'))
        return result
           
    def filter_href(self, link: str) -> bool:
        #| Checks if page is not namespace site or site with image
        for boring_site in ["File:", "Category:", "Help:", "Portal:", "Wikipedia:", "Talk:", "Special:", "Template:", "Template_talk:"]:
            if link.startswith(f"/wiki/{boring_site}"):
                return False
        for photo_site in [".jpg", ".png", ".svc"]:
            if link.endswith(photo_site):
                return False
        return True
    
    def filter_repeats(self, hrefs: list[tuple[str, str]]) -> list[tuple[str, str]]:
        #| Removes duplicates (Checks data in DB and data scraped in same loop)
        content = []
        df = pd.read_sql_query(
            f'SELECT href_name FROM "{self.start} | {self.destination} | Names"',
            self.conn)
        temp = set(df['href_name'].values)
        for href in hrefs:
            if not href[1] in temp:
                temp.add(href[1])
                content.append(href)
        return content
    
    def check_hrefs(self, hrefs: list[tuple[str, str]]) -> bool:
        #| Checks if destination is reached
        for href in hrefs:
            if href[1] == self.destination:
                self.save_results(href[0])
                return True
        return False
    
    def save_results(self, path: str) -> None:
        #| Append result in DB and assings result to attribute
        cursor = self.conn.cursor()
        cursor.execute(f'UPDATE results SET result = "{path}" WHERE start = "{self.start}" AND destination = "{self.destination}"')
        cursor.close()
        self.conn.commit()
        self.answer = path
    
    def insert_hrefs_names_and_paths(self, hrefs: list[tuple[str, str]]) -> None:
        #| Appends pages names and new paths to DB
        max_id = pd.read_sql_query(
            f'SELECT MAX(id) FROM "{self.start} | {self.destination} | Names"',
            self.conn).iloc[0]['MAX(id)']
        cursor = self.conn.cursor()
        for path,href_name in hrefs:
            max_id += 1
            cursor.execute(f'INSERT INTO "{self.start} | {self.destination} | Names" (id,href_name) VALUES ({max_id}, "{href_name}")')
            cursor.execute(f'INSERT INTO "{self.start} | {self.destination} | Paths" (path) VALUES ("{path},{max_id}")')
        cursor.close()
    
    def delete_old_paths(self, paths_ids: list[int]) -> None:
        #| Deletes paths what were used in current loop
        cursor = self.conn.cursor()
        cursor.execute(f'DELETE FROM "{self.start} | {self.destination} | Paths" WHERE id IN ({",".join(map(str, paths_ids))})')
        cursor.close()
                            
    def main(self) -> None:
        while True:
            print('=== === ===')
            start_timer = time.time()
            
            paths, paths_ids = self.fetch_path_data_from_db()           
            new_hrefs = []
            thread_list = [Thread(target=self.thread_process,args=(path, new_hrefs)) for path in paths]
            for thread in thread_list:
                thread.start()
            for thread in thread_list:
                thread.join()
            print(f"Found {len(new_hrefs)} sites")
            new_hrefs = self.filter_repeats(new_hrefs)
            
            if self.check_hrefs(new_hrefs):
                self.conn.close()
                return None
            
            self.insert_hrefs_names_and_paths(new_hrefs)
            self.delete_old_paths(paths_ids)
            
            self.conn.commit()
            print(f"Append {len(new_hrefs)} sites")
            print(f"{time.time() - start_timer} sec")
            
    def print_answer(self) -> None:
        print()
        conn = sqlite3.connect('db\\dbSQLite.db')
        content = []
        try:
            path = self.answer.split(',')
        except AttributeError:
            print("Path not found")
        for step in path:
            content.append(pd.read_sql_query(
                f'SELECT href_name FROM "{self.start} | {self.destination} | Names" WHERE id == "{step}"',
            conn).iloc[0]['href_name'])
        for c in content:
            print(f"https://en.wikipedia.org/wiki/{c}")
        print(f"https://en.wikipedia.org/wiki/{self.destination}\n")
        print(f"{' -> '.join([decode_URL(href) for href in content])} -> {decode_URL(self.destination)}")    