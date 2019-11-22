import json
from urllib import *

pharos = 'https://pharos.nih.gov/idg/api/v1/targets/search'
def fetch_targets():
    skip = 0
    top = 20
    total = None
    print 'Acc\tGene\tFamily\tName'
    while True:
        req = urlopen(pharos + '?facet=IDG+Development+Level/Tchem&top='
                      +str(top)+'&skip='+str(skip))
        data = json.loads(req.read())
        if total == None:
            total = data['total']
        for t in data['content']:
            print t['accession']+'\t'+t['gene']+'\t'+t['idgFamily']+'\t'+t['name']
        count = data['count']
        skip = skip + count
        if skip >= total:
            break
    return skip
    
if __name__ == "__main__":
    import sys
    count = fetch_targets()
    ##print '### {0} target(s)'.format(count)
