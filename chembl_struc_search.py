from __future__ import print_function
import json
import sys
import urllib

reload(sys)
sys.setdefaultencoding('utf8')

base = "https://tripod.nih.gov/chembl-v23/compounds"
def fetch (url):
    req = urllib.urlopen(url)
    buf = req.read()
    if buf == None or len(buf) == 0:
        return None
    return json.loads(buf)

def getpmid (json):
    return str(json['pubmedId'])

def search (file):
    with open (file, 'r') as f:
        header = None
        lines = 0
        for line in f:
            line = line.strip()
            toks = line.split('\t')
            if header == None:
                header = toks
            else:
                smiles = (toks[0].strip()
                          .replace("#", "%23").replace("+", "%2B")
                          .replace("[", "%5b").replace("]", "%5d"))
                url = base+'/'+smiles+'/sub?format=pubmed&max=100'
                print ('searching for {0}...{1}'.format(toks[1], url),
                       file=sys.stderr)
                data = fetch (url)
                search = "sub"
                if data == None:
                    cutoff = 0.85
                    url = (base+'/'+smiles
                           +'/sim?format=pubmed&max=100&cutoff={0}'.format(cutoff))
                    search = 'sim:{0}'.format(cutoff)
                    data = fetch (url)

                if type(data) == list:
                    pubs = '|'.join(map(getpmid, data))
                    print ('{0}\t{1}\t{2}'.format(line, search, pubs))
                elif type(data) == dict:
                    print ('{0}\t{1}\t{2}'.format(line, search,
                                                  data['pubmedId']))
                else:
                    print ('{0}\t{1}\tNo Match'.format(line, search))
                lines = lines + 1
                    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print ("usage: {0} SMILES_FILES...".format(sys.argv[0]))
        sys.exit(1)
    for i in range(1, len(sys.argv)):
        search (sys.argv[i])
        
