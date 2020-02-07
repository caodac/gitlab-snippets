# make sure you have python 3 installed
# pip install neo4j
from neo4j import GraphDatabase
from string import Template
import json

uri = "bolt://disease.ncats.io:80"
driver = GraphDatabase.driver(uri, auth=("neo4j", ""))

def find_disease (tx, name):
    for node in tx.run("match (n:ENTITY)-[]-(d:DATA) "
                         "where {name} in n.N_Name "
                         "return id(n) as `id`,labels(n) as `labels`,d",
                         name=name.upper()):
        data = {}
        for k in node['d']:
            data[k] = node['d'][k]
        print (json.dumps(data, indent=4, separators=(',',': ')))

def show_datasources (tx):
    for node in tx.run("match(n:DATASOURCE) "
                       "return n.name as `name`, n.instances as `count` "
                       "order by n.instances desc"):
        print ('%s\t%d' % (node['name'], node['count']))

def get_all_diseases (tx, source):
    count = 0
    print ('[',end='')
    jstr = ''
    for node in tx.run("match(n:`"+source+"`)-[]-(d:DATA) return d"):
        data = {}
        for k in node['d']:
            data[k] = node['d'][k]
        if len(jstr) > 0:
            print (jstr,end=',')
        jstr = json.dumps(data, indent=4, separators=(',',': '))
        count = count+1
    if len(jstr) > 0:
        print (jstr,end='')
    print (']')

def get_direct_mappings (tx, source, target):
    query = Template('''
match (n:`$source`)-[]-(d:DATA) with n,d
   match p=(n)-[:N_Name|:I_CODE]-(m:`$target`)-[]-(e:DATA) 
     return distinct d, e
''')
    q = query.substitute(source=source,target=target)
    #print ('...%s' % q)
    for node in tx.run(q):
        print ('%d\t%s' % (node['d']['id'], node['e']['notation']))

def get_gard_omim_mappings (tx):
    print ('GARD\tOMIM')
    get_direct_mappings (tx, 'S_GARD', 'S_OMIM')

def get_gard_hpo_umls_mappings (tx):
    print ('GARD\tHPO\tUMLS')
    for row in tx.run('''
    match (n:`S_GARD`)-[]-(d:DATA) with n,d 
    match p=(n)-[:R_rel]-(:`S_HPO`)-[]-(e:DATA) 
      return distinct d.id as `GARD`, e.id as `HPO`, e.hasDbXref as `xrefs`
      order by `GARD`, `HPO`
'''):
        xrefs = row['xrefs']
        umls = ''
        if xrefs != None:
            umls = ','.join(list(filter(lambda x: x.startswith('UMLS'), xrefs)))
            
        print ('%d\t%s\t%s' % (row['GARD'], row['HPO'], umls))

if __name__ == "__main__":
    with driver.session() as session:
        #session.read_transaction(show_datasources)
        #session.read_transaction(find_disease, "nguyen syndrome")
        #session.read_transaction(get_all_diseases, 'S_GARD')
        #session.read_transaction(get_gard_omim_mappings)
        session.read_transaction(get_gard_hpo_umls_mappings)
