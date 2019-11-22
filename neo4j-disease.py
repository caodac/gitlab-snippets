# pip install neo4j
from neo4j import GraphDatabase
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
        print json.dumps(data, indent=4, separators=(',',': '))

def show_datasources (tx):
    for node in tx.run("match(n:DATASOURCE) "
                       "return n.name as `name`, n.instances as `count` "
                       "order by n.instances desc"):
        print node['name'], '\t', node['count']

def get_all_diseases (tx, source):
    count = 0
    for node in tx.run("match(n:`"+source+"`)-[]-(d:DATA) return d"):
        data = {}
        for k in node['d']:
            data[k] = node['d'][k]
        print json.dumps(data, indent=4, separators=(',',': '))
        count = count+1

if __name__ == "__main__":
    with driver.session() as session:
        #session.read_transaction(show_datasources)
        #session.read_transaction(find_disease, "nguyen syndrome")
        session.read_transaction(get_all_diseases, 'S_GARD')
