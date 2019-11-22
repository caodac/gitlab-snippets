import mysql.connector
import sys

USER='tcrd'
HOST='tcrd.kmc.io'
DB='tcrd540'

def connect(db):
    return mysql.connector.connect(user=USER, host=HOST,
                                   database=db, buffered = True)

def fetch_drugs(db, subset):
    cursor = db.cursor(dictionary = True, buffered=True)
    query = ("select distinct e.drug,e.cmpd_chemblid,e.act_value,"
             "e.act_type,e.action_type,a.sym,a.uniprot,b.tdl,b.fam "
             "from protein a, target b, t2tc c, tdl_info d, "
             "drug_activity e where a.id=c.protein_id and "
             "b.id = c.target_id and d.protein_id=a.id and "
             "e.target_id=b.id order by e.drug, e.act_type, e.act_value desc")
    
    try:
        cursor.execute(query)
        chemblids = {}
        for r in cursor:
            chembl = r['cmpd_chemblid']
            if chembl != None:
                chemblids[r['drug']] = chembl

        cursor.execute(query)
        print "Drug,ChEMBL,Activity,ActivityType,MOA,Gene,UniProt,TDL,Family"
        for r in cursor:
            drug = r['drug']
            chembl = r['cmpd_chemblid']
            if chembl == None:
                if chemblids.has_key(drug):
                    chembl = chemblids[drug]
                else:
                    chembl = ""
            fam = r['fam']
            if fam == None:
                fam = 'Unknown'
            act = r['act_value']
            if act != None:
                act = "%.3f" % act
            else:
                act = ""
            typ = r['act_type']
            if typ == None:
                typ = ""
            else:
                typ = "p" + typ
            moa = r['action_type']
            if moa == None:
                moa = ""
            uniprot = r['uniprot']
            if subset == None or subset.has_key(uniprot):
                print ("%s,%s,%s,%s,%s,%s,%s,%s,%s" % (drug, chembl, act, typ,
                                                       moa,r['sym'], uniprot,
                                                       r['tdl'], fam))
                if subset != None:
                    subset[uniprot] = subset[uniprot] + 1
            
    except ValueError:
        pass
    cursor.close()
    

if __name__ == "__main__":
    db = connect(DB)
    subset = None
    if len(sys.argv) > 1:
        file = open(sys.argv[1], 'r')
        subset = {}
        for line in file:
            subset[line.strip()] = 0
        file.close()
        
    fetch_drugs(db, subset)
    if subset != None:
        for k in subset:
            if subset[k] == 0:
                sys.stderr.write("{}\n".format(k))
    
    db.close()
