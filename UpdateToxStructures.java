import java.io.*;
import java.util.*;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.sql.*;

import chemaxon.struc.*;
import chemaxon.formats.*;
import lychi.SaltIdentifier;
import lychi.LyChIStandardizer;

public class UpdateToxStructures {
    static {
        try {
            Class.forName("oracle.jdbc.driver.OracleDriver");
        }
        catch (Exception ex) {
            ex.printStackTrace();
        }        
    }

    public static void main (String[] argv) throws Exception {
        if (argv.length == 0) {
            System.err.println("Usage: UpdateToxStructures SDF...");
            System.exit(1);
        }

        Connection con = DriverManager.getConnection
            ("jdbc:oracle:thin:registry/ncgc@lederman.ncats.nih.gov:1521:probedb");
        PreparedStatement pstm = con.prepareStatement
            ("update ncgc_sample set smiles_iso = ? where sample_id = ?");

        LyChIStandardizer lychi = new LyChIStandardizer ();     
        SaltIdentifier salt = SaltIdentifier.getInstance();
        
        System.out.println("Tox21_ID,NCGC,ParentExactMass,FullMass,ParentFormula,PARENT_SMILES,FullFormula,FULL_SMILES");
        for (String a : argv) {
            MolImporter mi = new MolImporter (a);
            for (Molecule m = new Molecule (); mi.read(m); ) {
                String ncgc = m.getProperty("ncgc_id");
                String[] syns =
                    m.getProperty("PUBCHEM_SUBSTANCE_SYNONYM").split("\n");
                for (String s : syns) {
                    if (s.startsWith("Tox21")) {
                        System.out.print(s);
                        break;
                    }
                }
                System.out.print(","+ncgc);
                double fullMass = m.getMass();
                double exactMass = m.getExactMass();
                String fullFormula = m.getFormula();
                String fullSmiles = m.toFormat("smiles:q");

                Molecule[] frags = m.convertToFrags();
                if (frags.length > 1) {
                    List<Molecule> moieties = new ArrayList<Molecule>();
                    double pExact = 0.;
                    Molecule largest = null;
                    for (Molecule f : frags) {
                        Molecule moiety = f.cloneMolecule();
                        lychi.standardize(f);
                        if (!salt.isSaltOrSolvent(f)
                            /*|| LyChIStandardizer.containsMetal(f)*/) {
                            pExact += moiety.getExactMass();
                            Molecule orig = moiety.cloneMolecule();
                            if (!LyChIStandardizer.normalize(moiety))
                                moiety = orig;
                            moieties.add(moiety);
                        }
                        else if (largest == null
                                 || (moiety.getMass() > largest.getMass())) {
                            largest = moiety;
                        }
                    }
                    
                    //assert !moieties.isEmpty(): ncgc+": empty parent!";
                    if (moieties.isEmpty()) {
                        moieties.add(largest);
                    }
                    else if (moieties.size() > 1) {
                        Collections.sort(moieties, new Comparator<Molecule>() {
                                public int compare (Molecule m1, Molecule m2) {
                                    double mwt1 = m1.getMass();
                                    double mwt2 = m2.getMass();
                                    if (mwt2 > mwt1) return 1;
                                    if (mwt2 < mwt1) return -1;
                                    return m1.getFormula().compareTo
                                        (m2.getFormula());
                                }
                            });
                    }

                    int net = 0;
                    for (Molecule moiety : moieties) {              
                        for (MolAtom at : moiety.getAtomArray())
                            net += at.getCharge();
                    }
                    
                    StringBuilder pFormula = new StringBuilder ();
                    StringBuilder pSmiles = new StringBuilder ();
                    
                    for (Molecule moiety : moieties) {
                        if (net < 0) {
                            LyChIStandardizer.neutralize(moiety);
                        }
                        
                        if (pFormula.length() > 0) {
                            pFormula.append(".");
                            pSmiles.append(".");
                        }
                        pFormula.append(moiety.getFormula());
                        pSmiles.append(moiety.toFormat("smiles:q"));
                    }

                    System.out.print(","+String.format("%1$.5f", pExact));
                    System.out.print(","+String.format("%1$.5f", fullMass));
                    System.out.print(","+pFormula);
                    System.out.print(","+pSmiles);
                }
                else { // no salt.. parent is the same
                    System.out.print(","+String.format("%1$.5f", exactMass));
                    System.out.print(","+String.format("%1$.5f", fullMass));
                    System.out.print(","+fullFormula);
                    System.out.print(","+fullSmiles);
                }
                System.out.print(","+fullFormula);
                System.out.print(","+fullSmiles);
                System.out.println();
            }
            mi.close();
        }
    }
}
