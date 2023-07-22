import pandas as pd
from wiki_speedrun_test_threads_n import WikipediaSpeedrun

thread_limit = [x for x in range(5,201,5)]
sites = [("Ozimek Suspension Bridge","Diesel fuel"),
         ("Poland","Szczecin Cathedral"),
         ("Music","Tank"),
         ("Python","C++")]

data = {'thread_limit':[],
        'sites':[],
        'time':[]}

path_data = {"start":[],
             "destination":[]}

for s in sites:
    path_data["start"].append(s[0])
    path_data["destination"].append(s[1])

def generate_append_data(data:dict[str,list])->None:
    for s in sites:
        for limit in thread_limit:
            data["thread_limit"].append(limit)
            data["sites"].append('|'.join(s))
            data["time"].append(WikipediaSpeedrun(limit,s).main()[0])

def data_to_csv(data,path):
    df = pd.DataFrame(data)
    df.to_csv(f'.\\Test\\{path}.csv',mode="a",index=False,header=False)
    
data_to_csv(path_data,"path")