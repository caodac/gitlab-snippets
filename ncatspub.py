from __future__ import print_function
import json
import sys
from urllib import *

reload(sys)
sys.setdefaultencoding('utf8')

puburl = "https://publications.ncats.nih.gov/api/v1/publications/search?facet=Program/NCGC&facet=Program/Tox21&facet=Program/TRND&facet=Program/ADST&facet=Program/SCTF&facet=Program/ChemTech&view=full"

if __name__ == "__main__":
    top = 50
    skip = 0
    print ("PMID\tTitle\tNCATS Authors")
    while True:
        req = urlopen(puburl+'&top={0}&skip={1}'.format(top, skip))
        pub = json.loads(req.read())
        id = pub['id']
        for p in pub['content']:
            try:
                authors = []
                for a in p['authors']:
                    if a['author'].has_key('ncatsEmployee'):
                        authors.append(a['author']['username'])
                print (u"{0}\t{1}\t{2}".format(p['pmid'], p['title'],
                                               ' '.join(authors)))
            except UnicodeEncodeError:
                print (str(p['pmid'])+'\t'+p['title'], file=sys.stderr)
        count = len (pub['content'])
        skip = skip + count
        if count < top:
            break
    print (str(skip)+" publications!", file=sys.stderr)
