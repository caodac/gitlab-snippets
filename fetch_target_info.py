import mysql.connector
import sys

USER='tcrd'
HOST='tcrd.kmc.io'
DB='tcrd540'

def connect(db):
    return mysql.connector.connect(user=USER, host=HOST,
                                   database=db, buffered = True)

def fetch_target_info(db):
    cursor = db.cursor(dictionary = True, buffered=True)

    query = ("select a.sym,b.tdl,a.uniprot,b.fam,"
             "d.integer_value as pubmed,b.name "
             "from protein a, target b, t2tc c, tdl_info d "
             "where a.id=c.protein_id and b.id = c.target_id "
             "and d.protein_id = a.id and d.itype = 'NCBI Gene PubMed Count' "
             "and b.tdl in ('Tbio','Tdark') "
#             "limit 100"
    )
    try:
        cursor.execute(query)
        print "Gene\tTDL\tUniProt\tFamily\tPubMedCount\tName"
        for r in cursor:
            fam = r['fam']
            if fam == None:
                fam = 'Unknown'
            print r['sym'],"\t",r['tdl'],"\t",r['uniprot'],"\t",
            print fam,"\t",r['pubmed'],"\t",r['name']
    except ValueError:
        pass
    cursor.close()

if __name__ == "__main__":
    db = connect(DB)
    fetch_target_info(db)
    db.close()
