import requests
from mediawiki import MediaWiki
from threading import Thread
from bs4 import BeautifulSoup
import time

wiki = MediaWiki()

class WikipediaSpeedrun():
    
    stop_threads=False
    answer=[]
    seen=set()
    
    def __init__(self) -> None:
        temp_input = self.user_input()
        self.start = temp_input[0]
        self.destination = temp_input[1]
        self.start_time = time.perf_counter()
        self.session = requests.Session()
    
    def user_input(self): #<==collects input and converts it to wikipedia links
        starting_url = wiki.opensearch(input("Start:"), results=1) #input("Start:")
        destination_url = wiki.opensearch(input("Destination:"), results=1) #input("Destination:")
        return (starting_url[-1][-1][24:],destination_url[-1][-1][24:])
    
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
        for link in content_div.find_all('a', href=True):
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
        all_links_container = self.get_links([self.start])
        while True:
            if self.stop_threads:
                break
            temp=[]
            
            # # Ograniczenie podstroną
            # thread_list = []
            # for link_container in all_links_container:
            #     thread_list.append(Thread(target=self.thread_process,args=(link_container,temp)))
            # for thread in thread_list:
            #     thread.start()
            # for thread in thread_list:
            #     thread.join()
            # all_links_container = temp[:]
            
            #Ograniczenie id
            thread_list = []
            for id,link_container in enumerate(all_links_container):
                if self.stop_threads:
                    break
                thread_list.append(Thread(target=self.thread_process,args=(link_container,temp)))
                if id%10==0 or id==len(all_links_container)-1:  
                    for thread in thread_list:
                        thread.start()
                    for thread in thread_list:
                        thread.join()
                    thread_list = []
            all_links_container = temp[:]        
            
            #? without thread, the slowest
            # for link_container in all_links_container:
            #     self.thread_process(link_container,temp)
            
        self.print_result()
            
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
        print(f"{time.perf_counter()-self.start_time} sec")
                 
    def test(self):
        print(self.start)
        print(self.destination)
        
if __name__=="__main__":
    speedrun = WikipediaSpeedrun()
    speedrun.main()
    #speedrun.test()
    
    