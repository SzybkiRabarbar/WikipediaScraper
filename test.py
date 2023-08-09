from mediawiki import MediaWiki

wiki = MediaWiki()

def get_directions() -> list[str]:
    starting_url = wiki.opensearch(input("Start:"), results=1)
    destination_url = wiki.opensearch(input("Destination:"), results=1)
    return [starting_url[-1][-1], destination_url[-1][-1]]
if __name__=='__main__':
    l = [1,2,3,4,5,6,7,8,9]
    r = map(str, l)
    print(','.join(r))