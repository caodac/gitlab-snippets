import json
from urllib import *

#
# retrieve marketed drugs (minus allergenic extracts) from inxight drugs
#
#url = "https://drugs.ncats.io/api/v1/substances/search?facet=Substance%20Form%2FPrincipal%20Form&facet=Development%20Status%2FPossibly%20Marketed%20Outside%20US&facet=Development%20Status%2FUS%20Approved%20Rx&facet=Development%20Status%2FUS%20Approved%20OTC"
url = "https://drugs.ncats.io/api/v1/substances/search?facet=Treatment%20Modality%2FInactive%20ingredient"

def fetch_drugs():
    skip = 0
    total = 0
    while True:
        req = urlopen (url+"&top=10&skip="+str(skip));
        content = json.loads(req.read())
        if total == 0:
            total = content['total']
        data = content['content']
        for r in data:
            if r.has_key('structure'):
                print r['structure']['smiles'],'\t',r['approvalID'],'\t',
                print r['_name']
        skip = skip + content['count']
        if skip >= total:
            break
    
if __name__ == "__main__":
    fetch_drugs ()
