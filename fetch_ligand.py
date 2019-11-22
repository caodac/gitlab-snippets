import json
from urllib import *

# A simple script to retrieve ligand structures (as SMILES format) for
# a given target.
#   Usage: python fetch_ligand.py TARGET
# where TARGET can be gene (e.g., abl1), UniProt accession (e.g., P00519),
# ENSEMBL (e.g., ENSP00000361423), etc.

pharos = 'https://pharos.nih.gov/idg/api/v1/targets/'
def fetch_ligand(target):
    req = urlopen(pharos + target)
    target = json.loads(req.read())
    #print json.dumps(target, indent=4, separators=(',', ': '))

    # retrieve ligand links for this target
    req = urlopen(pharos+'{0}'.format(target['id'])
                  +'/links(kind=ix.idg.models.Ligand)')
    link = json.loads(req.read())
    #print json.dumps(link, indent=4, separators=(',', ': '))
    
    for l in link:
        name = ""
        for p in l['properties']:
            if p['label'] == 'IDG Ligand' or p['label'] == 'IDG Drug':
                name = p['term']
                break
        
        req = urlopen(l['href']+'/properties(label=CHEMBL Canonical SMILES)')
        ligand = json.loads(req.read())
        
        print ligand[0]['text'] + '\t' + name,
        # do another pass through the properties to extract ligand activity
        for p in l['properties']:
            if p['label'] == 'Ki' or p['label'] == 'Kd' or p['label'] == 'IC50' or p['label'] == 'EC50' or p['label'] == 'AC50' or p['label'] == 'Potency':
                print '\tp' + p['label']+'={0}'.format(p['numval']),
        print
    
if __name__ == "__main__":
    import sys
    fetch_ligand(sys.argv[1])
