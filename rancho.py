import json
import sys

conditions = [
    'ConditionName',
    'ConditionUri',
    'ConditionComment',
    'isConditionDoImprecise',
    'ConditionDoId',
    'ConditionDoValue',
    'isConditionMeshImprecise',
    'ConditionMeshId',
    'ConditionMeshValue',
    'ConditionManualProductName',
    'ConditionProductName',
    'ConditionProductDate',
    'HighestPhase',
    'HighestPhaseUri',
    'HighestPhaseComment',
    'ConditionFdaUse',
    'FdaUseURI',
    'FdaUseComment',
    'OfflabelUse',
    'OfflabelUseUri',
    'OfflabelUseComment',
    'ClinicalTrial',
    'TreatmentModality'
    ]

targets = [
    'PrimaryTargetId',
    'PrimaryTargetLabel',
    'PrimaryTargetType',
    'PrimaryTargetUri',
    'PrimaryTargetGeneId',
    'PrimaryTargetGeneSymbol',
    'PrimaryTargetOrganism',
    'PrimaryTargetComment',
    'PrimaryPotencyType',
    'PrimaryPotencyValue',
    'PrimaryPotencyDimensions',
    'PrimaryPotencyTypeOther',
    'PrimaryPotencyUri',
    'PrimaryPotencyComment',
    'TargetPharmacology'
    ]

def rancho (file):
    import csv
    with open (file, 'rb') as file:
        reader = csv.reader(file,dialect='excel-tab')
        header = reader.next()
        line = 0
        p = None
        print '[',
        for row in reader:
            #print '--- record {0} ---'.format(line)
            d = {}
            c = {} # condition
            t = {} # target
            for i in range(0,len(header)):
                name = header[i]
                    
                if i < len(row):
                    r = row[i].strip()
                    if r != '':
                        x = d
                        if name in conditions:
                            x = c
                        elif name in targets:
                            x = t
                        
                        vals = r.split('|')
                        if len(vals) > 1:
                            numeric = []
                            for v in vals:
                                if not v.isdigit():
                                    break
                                else:
                                    numeric.append(long(v))
                            if len(numeric) == len(vals):
                                x[name] = numeric
                            else:
                                x[name] = vals
                        elif name == 'Unii':
                            unii = []
                            for v in r.split(';'):
                                unii.append(v.strip())
                            if len(unii) > 1:
                                x[name] = unii
                            else:
                                x[name] = r
                        else:
                            if r.lower() == 'false':
                                x[name] = False
                            elif r.lower() == 'true':
                                x[name] = True
                            elif r.isdigit():
                                x[name] = long(r)
                            elif r.lower() != 'null' and r.lower() != 'unknown':
                                x[name] = r
            if not d.has_key('CompoundName'):
                sys.stderr.write(('{0}: No CompoundName: '+'|'.join(row)+'\n').format(line))
                continue
            
            if c.has_key('ConditionName') or c.has_key('ConditionMeshValue') or c.has_key('ConditionDoValue'):
                d['conditions'] = [c]
            if t.has_key('PrimaryTargetId'):
                d['targets'] = [t]
            if d['Connected'] and len(t) > 0:
                c['target'] = t
            del d['Connected']
            #print json.dumps(d, indent=4, separators=(',',': '))
            
            if p != None:
                #print '^^^^^^^^^^^^^^^^^^^'                
                if p['CompoundName'] == d['CompoundName']:
                    if p.has_key('conditions') and len(c) > 0:
                        p['conditions'].append(c)
                    if p.has_key('targets') and len(t) > 0:
                        p['targets'].append(t)
                    d = p
                else:
                    print json.dumps(p, indent=4, separators=(',',': '))+','

            line = line + 1
            p = d
            
        if p != None:
            print json.dumps(p, indent=4, separators=(',',': '))
        print ']'
            
if __name__ == "__main__":
    import sys
    rancho(sys.argv[1])
