import json
from urllib import *

pharos = 'https://pharos.nih.gov/idg/api/v1/targets/'
def fetch_collection():
    req = urlopen(pharos + 'Collection/termvec')
    termvec = json.loads(req.read())
    for t in termvec['terms']:
        docs = termvec['terms'][t]['docs'];
        for d in docs:
            req = urlopen(pharos+str(d)+'/$gene')
            print t+','+req.read()

    
if __name__ == "__main__":
    import sys
    fetch_collection()
