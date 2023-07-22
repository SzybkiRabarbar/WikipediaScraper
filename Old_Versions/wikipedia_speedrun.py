import requests
from mediawiki import MediaWiki

wiki = MediaWiki()
seen = []

def inputs():
    starting_url = wiki.opensearch(input("Start:"), results=1)
    destination_url = wiki.opensearch(input("Destination:"), results=1)
    return [starting_url[-1][-1], destination_url[-1][-1]]

def url_list(url):
    starting_content = requests.get(url).text
    start = starting_content.find('id="content"')
    end = starting_content.find('id="mw-data-after-content"')
    raw_links = starting_content[start:end].split('href="')
    links=[]
    global seen
    for link in raw_links:
        link = link.split('"')[0]
        if link.startswith('/wiki/') and not (link.endswith('.jpg') or link.endswith('.png')):
            seen.append(link)
            links.append('https://en.wikipedia.org'+link)
    return links

def func_name(input_lst):
    
    url_lst=url_list(input_lst[0])
    iterator = url_lst[:]
    for link in iterator:
        if url_lst==iterator: url_lst.clear()
        if link==input_lst[1]: return link
        url_lst.append([link])

    n=1
    while n!=10:
        iterator = url_lst[:]
        n+=1
        for link_lst in iterator:
            if link_lst[-1]==input_lst[1]: return link_lst
        for link_lst in iterator:
            print(link_lst)
            try:
                if url_lst==iterator: url_lst.clear()
                for link in url_list(link_lst[-1]):
                    temp = link_lst[:]
                    if link in temp: continue
                    temp.append(link)
                    if link==input_lst[1]: return temp
                    url_lst.append(temp)
            except:
                continue
            
if __name__ == '__main__':
    inp = inputs()
    func = func_name(inp)
    print("Quickest path:")
    if type(func)==str:
        print(inp[0],' >>> ',func)
    else:
        print(inp[0]+' >>> '+' >>> '.join(func))
    print(len(seen),'links was scrapted')