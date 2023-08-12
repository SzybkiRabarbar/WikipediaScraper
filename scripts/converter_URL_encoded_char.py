import urllib.parse

def decode_URL(name: str) -> str:
    return urllib.parse.unquote(name).replace('_', ' ')