from mediawiki import MediaWiki

wiki = MediaWiki()

def get_directions() -> list[str]:
    starting_url = wiki.opensearch(input("Start:"), results=1)
    destination_url = wiki.opensearch(input("Destination:"), results=1)
    return [starting_url[-1][-1], destination_url[-1][-1]]
if __name__=='__main__':
    p = get_directions()
    print(p)