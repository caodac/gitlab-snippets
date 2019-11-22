import mysql.connector
import sys

USER='tcrd'
HOST='tcrd.kmc.io'
DB='tcrd540'
TOTALS = {}

def connect(db):
    return mysql.connector.connect(user=USER, host=HOST,
                                   database=db, buffered = True)

def parse_unigene_profiles(file):
    f = open(file, 'r')
    genes = {}
    dims = {}
    gene = None
    dim = None
    #print 'loading',file,'...'
    for line in f:
        if line[0] == '>':
            toks = line[1:].strip().split('|')
            gene = long(toks[0])
            dim = toks[1]
            if not TOTALS.has_key(dim):
                TOTALS[dim] = {}
            if not genes.has_key(gene):
                genes[gene] = {}
            if not genes[gene].has_key(dim):
                genes[gene][dim] = {}
            #print "<{}><{}>".format(gene, dim)
        else:
            toks = line.split('\t')
            counts = toks[1].split('/')
            total = int(counts[1])
            if not TOTALS[dim].has_key(toks[0]):
                TOTALS[dim][toks[0]] = total
            elif total != TOTALS[dim][toks[0]]:
                sys.stderr.write("{} != {} for {}\n"
                                 .format(total, TOTALS[dim][toks[0]], toks[0]))
            genes[gene][dim][toks[0]] = int(counts[0])
            #print "<{}><{}>".format(toks[0], toks[1])
            
    f.close()
    return genes
    
def targets_for_unigene(db, genes):
    cursor = db.cursor(dictionary = True, buffered=True)
    query = ("select c.tdl,b.uniprot,c.fam,b.sym,a.value as unigene,c.name "
             "from xref a, protein b, target c, t2tc d "
             "where a.protein_id = b.id and a.xtype='UniGene' "
             "and b.id = d.protein_id and c.id = d.target_id")

    print "UniProt\tGene\tFamily\tTDL\tName\tUniGene",
    dims = ['Developmental Stage','Body Sites','Health State']
    for d in dims:
        vals = TOTALS[d].keys()
        vals.sort()
        for v in vals:
            print "\t{}: {} ({})".format(d, v, TOTALS[d][v]),
    print
    try:
        cursor.execute(query)
        seen = {}
        for result in cursor:
            unigene = result['unigene']
            sym = result['sym']
            if None != unigene: # and not seen.has_key(sym):
                fam = result['fam']
                if None == fam:
                    fam = 'Unknown'
                    
                gene = long(unigene.split('.')[1])
                if genes.has_key(gene):
                    print result['uniprot'],"\t",sym,"\t",
                    print fam,"\t",result['tdl'],"\t",
                    print result['name'],"\t",unigene,
                    for d in dims:
                        vals = TOTALS[d].keys()
                        vals.sort()
                        for v in vals:
                            if genes[gene][d].has_key(v):
                                print "\t{}".format(genes[gene][d][v]),
                            else:
                                print "\t",
                    print
                else:
                    sys.stderr.write("No unigene EST profile for {}!\n"
                                     .format(gene))
                seen[sym] = unigene
    except ValueError:
        pass
    cursor.close()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "usage: unigene.py Hs.profiles"
        sys.exit(1)

    genes = parse_unigene_profiles(sys.argv[1])
    db = connect(DB)
    targets_for_unigene(db, genes)
    db.close()
    #import json
    #print json.dumps(TOTALS, indent=4, separators=(',',': '))
