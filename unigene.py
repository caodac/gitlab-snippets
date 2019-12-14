import mysql.connector
import sys

USER='tcrd'
HOST='tcrd.ncats.io'
DB='tcrd610'
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
            gene = int(toks[0])
            dim = toks[1]
            if not dim in TOTALS:
                TOTALS[dim] = {}
            if not gene in genes:
                genes[gene] = {}
            if not dim in genes[gene]:
                genes[gene][dim] = {}
            #print "<{}><{}>".format(gene, dim)
        else:
            toks = line.split('\t')
            counts = toks[1].split('/')
            total = int(counts[1])
            if not toks[0] in TOTALS[dim]:
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
    query = """select c.tdl,b.uniprot,c.fam,b.sym as human_gene, 
a.symbol as mouse_gene,a.geneid as mouse_gene_id
from protein b, target c, t2tc d 
left join ortholog a on d.protein_id=a.protein_id and a.species='mouse'
where b.id = d.protein_id and c.id = d.target_id"""

    print ("UniProt\tHumanGene\tFamily\tTDL\tMouseGene\tMouseGeneID",end='')
#    dims = ['Developmental Stage','Body Sites','Health State']
    dims = ['Developmental Stage','Body Sites']
    for d in dims:
        sorted(TOTALS[d])
        vals = TOTALS[d].keys()
        for v in vals:
            print ("\t{}: {} ({})".format(d, v, TOTALS[d][v]), end='')
    print ('')
    try:
        cursor.execute(query)
        seen = {}
        for result in cursor:
            unigene = result['mouse_gene']
            gene = result['mouse_gene_id']
            sym = result['human_gene']
            if None != unigene: # and not seen.has_key(sym):
                fam = result['fam']
                if None == fam:
                    fam = 'Unknown'
                    
                #gene = int(unigene.split('.')[1])
                if gene in genes:
                    print ('%s\t"%s"\t%s\t%s\t"%s"\t%d' %
                           (result['uniprot'],sym,fam,result['tdl'],
                            unigene,gene), end='')
                    for d in dims:
                        sorted(TOTALS[d])
                        vals = TOTALS[d].keys()
                        for v in vals:
                            if v in genes[gene][d]:
                                print ("\t{}".format(genes[gene][d][v]),end='')
                            else:
                                print ("\t",end='')
                    print ('')
                else:
                    print("No unigene EST profile for %s!" % (gene), file=sys.stderr)
                seen[sym] = unigene
    except ValueError:
        pass
    cursor.close()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print ("usage: unigene.py Mm.profiles")
        sys.exit(1)

    genes = parse_unigene_profiles(sys.argv[1])
    db = connect(DB)
    targets_for_unigene(db, genes)
    db.close()
    #import json
    #print json.dumps(TOTALS, indent=4, separators=(',',': '))
