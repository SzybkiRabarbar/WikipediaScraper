import requests
from threading import Thread
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd

class SearchPath():
    
    stop_threads=False
    answer=[]
    seen=set()
    
    def __init__(self, start, destination) -> None:
        self.start = start
        self.destination = destination
        self.conn = sqlite3.connect('db\\dbSQLite.db')
        self.session = requests.Session()
        self.main()
    
    def get_links(self,path): #<== scrape and checking
        result = []
        if not path or self.stop_threads or path[-1] in self.seen:
            return result
        self.seen.add(path[-1])
        try: #<== scraping
            response = self.session.get(f"https://en.wikipedia.org{path[-1]}")
        except ConnectionError:
            return path
        data = response.content
        soup = BeautifulSoup(data, "html.parser")

        content_div = soup.find('main', {'id': 'content'})
        for link in content_div.find_all('a', href=True): # TODO Przerobić na osobną funckję
            if link['href'].startswith("/wiki/") and self.filter_link(link['href']):
                if self.stop_threads:
                    return result
                elif self.destination==link['href']: #<== check if link is destination
                    self.stop_threads = True
                    self.answer.append(path)
                elif not link['href'] in path:
                    temp = path[:]
                    temp.append(link['href'])
                    result.append(temp)
        return result
            
    def filter_link(self,link:str): #<== check if link is valid
        for boring_site in ["File:","Category:","Help:","Portal:","Wikipedia:","Talk:","Special:","Template:"]:
            if link.startswith(f"/wiki/{boring_site}"):
                return False
        for photo_site in [".jpg",".png",".svc"]:
            if link.endswith(photo_site):
                return False
        return True
    
    def main(self):
        paths = pd.read_sql_query(
            f"SELECT id, path FROM '{self.start} | {self.destination} | Paths' LIMIT 3",
            self.conn)
        #print(paths.info())
        paths_ids = paths['id'].tolist()
        print('paths_id =',paths_ids)
        paths['href_id'] = [path.split(',')[-1] for path in paths['path']]
        print(paths)
        hrefs_names = pd.read_sql_query(
            f"SELECT id, href_name FROM '{self.start} | {self.destination} | Names' WHERE id IN ({','.join(paths['href_id'].tolist())})",
            self.conn)
        #TODO połaczyć oba df ale href_name w odpowiedniej kolejności
        #TODO pomyśleć jak program ma przekazywać ścieżke dla poszczególnego href_name (dodać do df paths href_id i href_name?
        
        # href_name = pd.read_sql_query(
        #     f"SELECT href_name FROM '{self.start} | {self.destination} | Names' WHERE id == {href_id}",
        #     conn)
        # href_name = href_name.iloc[0]['href_name']
        #TODO INSERT nowych href_name
        #TODO INSERT nowych paths
        #TODO usuwanie z bazy paths_ids
        #TODO dodać Commit
        #TODO na końcu main()
        
        ##
        # all_links_container = self.get_links([self.start])
        # while True:
        #     if self.stop_threads:
        #         break
        #     temp=[]
        #     thread_list = []
        #     for id,link_container in enumerate(all_links_container):
        #         if self.stop_threads:
        #             break
        #         thread_list.append(Thread(target=self.thread_process,args=(link_container,temp)))
        #         if id%10==0 or id==len(all_links_container)-1:  
        #             for thread in thread_list:
        #                 thread.start()
        #             for thread in thread_list:
        #                 thread.join()
        #             thread_list = []
        #     all_links_container = temp[:]
        # self.print_result()
            
    def thread_process(self,link_container,temp): #<== method executed by threads
        print(link_container)
        for link in self.get_links(link_container):    
            if link:
                temp.append(link)
    
    def print_result(self):
        print()
        for a in self.answer[0]:
            print(f"https://en.wikipedia.org{a}")
        print(f"https://en.wikipedia.org{self.destination}")
        print()
        print(f"{' => '.join(a.replace('/wiki/','') for a in self.answer[0])} => {self.destination.replace('/wiki/','')}")
                 
    def test(self):
        print(self.start)
        print(self.destination)
        
if __name__=="__main__":
    pass
    
    