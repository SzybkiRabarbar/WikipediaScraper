import requests
from threading import Thread
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import time

class SearchPath():
    
    def __init__(self, start, destination) -> None:
        self.start_time = time.time()
        self.final_result = ''
        self.start = start
        self.destination = destination
        self.conn = sqlite3.connect('db\\dbSQLite.db')
        self.session = requests.Session()
        self.main()
    
    def extract_hrefs_from_content(self, content_div) -> list[str]:
        result = []
        for link in content_div.find_all('a', href=True):
            if link['href'].startswith("/wiki/") and self.filter_href(link['href']):
                result.append(link['href'].replace("/wiki/","").replace('"', '%22'))
        return result
    
    def scrap_paths(self,path: tuple[str, str]) -> list[tuple[str, str]]: #<== scrape and checking
        if not path:
            return []
        try: #<== scraping
            response = self.session.get(f"https://en.wikipedia.org/wiki/{path[1]}")
        except ConnectionError:
            return path
        soup = BeautifulSoup(response.content, "html.parser")

        content_div = soup.find('main', {'id': 'content'})
        hrefs = self.extract_hrefs_from_content(content_div)
        return [(path[0], h) for h in hrefs]
            
    def filter_href(self, link:str) -> bool: #<== check if link is valid
        for boring_site in ["File:","Category:","Help:","Portal:","Wikipedia:","Talk:","Special:","Template:","Template_talk:"]:
            if link.startswith(f"/wiki/{boring_site}"):
                return False
        for photo_site in [".jpg",".png",".svc"]:
            if link.endswith(photo_site):
                return False
        return True
    
    def fetch_path_data(self) -> tuple[list[tuple[str, str]], list]:
        paths = pd.read_sql_query(
            f'SELECT id, path FROM "{self.start} | {self.destination} | Paths" LIMIT 40',
            self.conn)
        paths_ids = paths['id'].tolist()
        paths['href_id'] = [int(path.split(',')[-1]) for path in paths['path']]
        hrefs_names = pd.read_sql_query(
            f'SELECT id as href_id, href_name FROM "{self.start} | {self.destination} | Names" WHERE id IN ({",".join([str(i) for i in paths["href_id"]])})',
            self.conn)
        paths = pd.merge(paths, hrefs_names, on="href_id")
        paths = list(map(tuple, paths[['path', 'href_name']].to_numpy()))
        return (paths, paths_ids)
    
    def filter_repeats(self, hrefs: list[tuple[str, str]]) -> list[tuple[str, str]]:
        temp = []
        content = []
        df = pd.read_sql_query(
            f'SELECT href_name FROM "{self.start} | {self.destination} | Names"',
            self.conn)
        for href in hrefs:
            if df.loc[df['href_name'] == href[1]].empty and not href[1] in temp:
                temp.append(href[1])
                content.append(href)
        return content
    
    def insert_hrefs_names_and_paths(self, hrefs: list[tuple[str, str]]) -> None:
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
        cursor = self.conn.cursor()
        cursor.execute(f'DELETE FROM "{self.start} | {self.destination} | Paths" WHERE id IN ({",".join(map(str, paths_ids))})')
        cursor.close()
        
    def main(self):
        paths, paths_ids = self.fetch_path_data()
        new_hrefs = []
        thread_list = [Thread(target=self.thread_process,args=(path, new_hrefs)) for path in paths]
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        
        # for href in new_hrefs: #TODO do poprawy sprawdzanie wyniku (dodać metode w init)
        #     if href[1] == self.destination:
        #         self.conn.close()
        #         self.final_result = href
        #         return href
        new_hrefs = self.filter_repeats(new_hrefs)
        self.insert_hrefs_names_and_paths(new_hrefs)
        self.delete_old_paths(paths_ids)
        
        self.conn.commit()
        
        print(f'Czas wykonania {time.time() - self.start_time} sek')
        
        #TODO na końcu main()
        #TODO kolenosć metod
            
    def thread_process(self, path: tuple[str, str], new_hrefs: list) -> None: #<== method executed by threads
        for new_href in self.scrap_paths(path):    
            if new_href:
                new_hrefs.append(new_href)
        
if __name__=="__main__":
    pass
    
    