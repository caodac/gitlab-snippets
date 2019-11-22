import urllib.request as req
import json
import sys
import os

if __name__ == "__main__":
    PRIVATE_TOKEN = os.environ['PRIVATE_TOKEN']
    url = req.Request('https://spotlite.nih.gov/api/v4/snippets',
                      headers = {'PRIVATE-TOKEN': PRIVATE_TOKEN})
    res = req.urlopen(url)
    if 200 == res.status:
        json = json.loads(res.read())
        for snippet in json:
            file = snippet['file_name']
            print ('-- %s' % (file))
            url = req.Request(snippet['raw_url'],
                            headers={'PRIVATE-TOKEN': PRIVATE_TOKEN})
            res = req.urlopen(url)
            if 200 == res.status:
                with open(file, 'w') as f:
                    f.write(res.read().decode('utf-8'))

