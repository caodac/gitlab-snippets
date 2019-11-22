import mysql.connector
import sys

USER='tcrd'
HOST='tcrd.kmc.io'
DB='tcrd540'

def connect(db):
    return mysql.connector.connect(user=USER, host=HOST,
                                   database=db, buffered = True)

def targets_for_disease(db, diseases):
    cursor = db.cursor(dictionary = True, buffered=True)

    query = ("select c.name,c.tdl,c.fam,d.uniprot,d.sym,a.did,a.dtype "
             "from disease a, t2tc b, target c, protein d "
             "where a.target_id = b.target_id and b.target_id = c.id "
             "and b.protein_id = d.id and c.tdl in ('Tchem','Tclin') "
             "and a.name = %(disease)s")
    print "Disease\tDiseaseSource\tDiseaseId\tUniProt\tGene\tTDL\tFamily"
    for d in diseases:
        try:        
            cursor.execute(query, {'disease':d})
            if cursor.rowcount > 0:
                for result in cursor:
                    fam = result['fam']
                    if fam == None:
                        fam = 'Unknown'
                    did = result['did']
                    if did == None:
                        did = ''
                    print d,"\t",result['dtype'],"\t",did,"\t",
                    print result['uniprot'],"\t",result['sym'],"\t",
                    print result['tdl'],"\t",fam
        except ValueError:
            pass
    cursor.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage:",sys.argv[0],"DISEASES..."
        sys.exit(1)
        
    db = connect(DB)
    targets_for_disease(db, sys.argv[1:len(sys.argv)])
    db.close()
