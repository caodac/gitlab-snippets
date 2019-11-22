// $Id$

import java.io.*;
import java.util.*;
import javax.naming.*;
import javax.naming.directory.*;
import javax.naming.ldap.*;
import java.text.*;

public class LdapConnector {

    /* 
     * change these values accordingly
     */
    static final String LDAP_URL = "ldap://ldapad.nih.gov:389";
    static final String LDAP_PROTOCOL = "ssl";
    static final String LDAP_AUTHENTICATION = "DIGEST-MD5";
    static final String LDAP_BASEDN = 
        "OU=Users,OU=NCATS,OU=NIH,OU=AD,DC=nih,DC=gov";
    static final String LDAP_BASEDN2 = 
        "OU=Users,OU=NCATS OD Transition,OU=NCATS,OU=NIH,OU=AD,DC=nih,DC=gov";

    private SearchControls userSearchControls = 
        new SearchControls (SearchControls.SUBTREE_SCOPE, 0, 0, 
                            new String[]{"mail", 
                                         "displayName", 
                                         "givenName",
                                         "telephoneNumber",
                                         "employeeID",
                                         "department"}, 
                            true, true);

    public LdapConnector () {
    }

    void basedn (DirContext ctx, String basedn) throws Exception {
        System.out.println("BASEDN: "+basedn);
        SimpleDateFormat df = new SimpleDateFormat ("yyyyMMddHHmmss");        
        NamingEnumeration<Binding> names = 
            ctx.listBindings(new LdapName (basedn));
        //System.out.println("{");
        //System.out.println(" \"events\": [");
        while (names.hasMore()) {
            Binding b = names.next();
            LdapContext ldap = (LdapContext)b.getObject();
            Attributes attrs = ldap.getAttributes("");
            
            /*
              NamingEnumeration<String> en = attrs.getIDs();
              while (en.hasMore()) {
              String a = en.next();
              System.out.println(" "+a+"="+attrs.get(a).get());
              }
            */
            Date date = df.parse(getAttr(attrs, "whenCreated"));
            /*
              System.out.println(getAttr (attrs, "givenName")
              +","+getAttr (attrs, "cn")
              +","+getAttr (attrs, "mail")
              +","+getAttr (attrs, "employeeID")
              +","+getAttr (attrs, "description")
              +","+date);
            */
            /*
              String div = getAttr (attrs, "description");
              if (div.indexOf("DPCI") > 0) {
              System.out.println("  {");
              System.out.println
              ("     \"start\": \""+df2.format(date)+"\",");
              System.out.println("     \"title\": \""
              +getAttr (attrs, "givenName")
              +" "+getAttr (attrs, "sn")+"\",");
              System.out.println("     \"durationEvent\": false");
              System.out.println("  }");
                    
              if (names.hasMore())
              System.out.print(",");
              }
            */
            System.out.println("{");
            System.out.println
                ("\"userName\":\""+getAttr(attrs, "cn")+"\",");
            System.out.println
                ("\"firstName\":\""+getAttr(attrs, "givenName")+"\",");
            System.out.println
                ("\"lastName\":\""+getAttr(attrs, "sn")+"\",");
            System.out.println
                ("\"email\":\""+getAttr(attrs, "mail")+"\",");
            System.out.println("\"created\":\""+date+"\",");
            System.out.println("\"employeeID\":\""
                               +getAttr(attrs,"employeeID")+"\"");
            System.out.println("}");
        }
        //System.out.println("]}");
                
    }
    
    /*
     * this method returns a unique session handler that is used to
     * communicate between the client and the servlet
     */
    public boolean authenticate (String username, String password) {
        Hashtable env = new Hashtable ();
        env.put(Context.INITIAL_CONTEXT_FACTORY, 
                "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, LDAP_URL);
        //env.put(Context.SECURITY_PROTOCOL, LDAP_PROTOCOL);
        // don't need to define trustStore here... we're not validating
        //  the certificate
        //env.put( "java.naming.ldap.factory.socket",
        //       DummySSLSocketFactory.class.getName());
        //env.put(Context.SECURITY_AUTHENTICATION, LDAP_AUTHENTICATION);
        env.put(Context.SECURITY_AUTHENTICATION, "simple");

        env.put(Context.SECURITY_PRINCIPAL, 
                "cn="+username+",OU=Users,OU=NCATS,OU=NIH,OU=AD,DC=nih,DC=gov");
        env.put(Context.SECURITY_CREDENTIALS, password);
        //env.put("javax.security.sasl.qop", "auth");
        //env.put("javax.security.sasl.strength", "high");


        SimpleDateFormat df2 = new SimpleDateFormat ("MMM dd yyyy hh:mm:ss");
        try {
            DirContext ctx = new InitialDirContext (env);
            // now get the directory entry for the user

            /*
            NamingEnumeration<SearchResult> matches =
                ctx.search(LDAP_BASEDN, "OU=Users", userSearchControls);

            while (matches.hasMore()) {
                SearchResult res = matches.next();
                //account = createUserAccount (res.getAttributes());
                System.out.println(res.getAttributes());
            }
            */
            basedn (ctx, LDAP_BASEDN);
            //basedn (ctx, LDAP_BASEDN2);
            
            Object obj = ctx.lookup("CN="+username+","+LDAP_BASEDN);
            System.err.println("## "+username+": "+obj);

            ctx.close();

            return true;
        }
        catch (Exception ex) {
            ex.printStackTrace();
        }

        return false;
    }

    static String getAttr (Attributes attrs, String name) 
        throws NamingException {
        Attribute a = attrs.get(name);
        return a != null ? a.get().toString() : "";
    }

    public UserAccount[] getAuthorizedUsers () {
        UserAccount[] users = null;

        Hashtable env = new Hashtable ();
        env.put(Context.INITIAL_CONTEXT_FACTORY, 
                "com.sun.jndi.ldap.LdapCtxFactory");
        /*
        env.put("java.naming.ldap.factory.socket",
                DummySSLSocketFactory.class.getName());
        */
        // this server allows anonymous connection
        env.put(Context.PROVIDER_URL, "ldap://directory.nih.gov");
        try {
            DirContext ctx = new InitialDirContext (env);

            Attributes attrs = ctx.getAttributes("O=NIH,C=US");
            //("CN=USER-NAME,OU=Users,OU=NCATS,OU=NIH,OU=AD,DC=nih,DC=gov");
            users = new UserAccount[attrs.size()];
            System.out.println("** size="+attrs.size());
            for (int i = 0; i < attrs.size(); ++i) {

                //users[i] = createUserAccount (ctx, attr.get(i).toString());
            }
            ctx.close();

            // sort the user
            Arrays.sort(users);
        }
        catch (NamingException ex) {
            ex.printStackTrace();
        }
        return users;
    }

    protected UserAccount createUserAccount 
        (DirContext ctx, String name) throws NamingException {
        // escape special characters and keep only the leaf node...
        //   can't figure out why I can just go directly to the node
        //   with the distinguishedName
        //    CN=Nguyen\, Dac-Trung (NIH/NHGRI) [C],OU=NIH,OU=DHHS,OU=ADAM,DC=NIH,DC=GOV
        StringBuffer properName = new StringBuffer ();
        for (int i = 0; i < name.length(); ++i) {
            char ch = name.charAt(i);
            switch (ch) {
            case ',':
                if (name.charAt(i-1) == '\\') {
                    // leave this alone
                    properName.append(ch);
                }
                else {
                    i = name.length(); // we're done
                }
                break;

            case '(':
                properName.append("\\28");
                break;

            case ')':
                properName.append("\\29");
                break;

            case '*':
                properName.append("\\2a");
                break;

            default:
                properName.append(ch);
            }
        }

        //System.out.println(properName);       
        NamingEnumeration<SearchResult> matches
            = ctx.search("OU=NIH,OU=DHHS,ou=adam,dc=nih,dc=gov", 
                         "(&(objectClass=user)(" + properName + "))", 
                         //"(" + properName + ")",
                         userSearchControls);

        UserAccount account = null;
        while (matches.hasMore()) {
            SearchResult res = matches.next();
            account = createUserAccount (res.getAttributes());
        }

        return account;
    }

    protected static UserAccount createUserAccount (Attributes attrs) 
        throws NamingException {
        String email = null;
        String username = null;
        String given = null;
        String display = null;
        String phone = null;
        String insti = null;
        String id = null;

        Attribute attr;
        
        attr = attrs.get("mail");       
        if (attr.size() > 0) {
            email = attr.get(0).toString();
            // since the anonymous directory isn't setup properly
            //   we extract the username from the email
            username = email.substring(0, email.indexOf('@'));
        }
        attr = attrs.get("displayName");
        if (attr.size() > 0) {
            display = attr.get(0).toString();
        }
        attr = attrs.get("givenName");
        if (attr.size() > 0) {
            given = attr.get(0).toString();
        }
        attr = attrs.get("telephoneNumber");
        if (attr.size() > 0) {
            phone = attr.get(0).toString();
        }
        attr = attrs.get("employeeID");
        if (attr.size() > 0) {
            id = attr.get(0).toString();
        }
        attr = attrs.get("department");
        if (attr.size() > 0) {
            insti = attr.get(0).toString();
        }

        /*
        System.out.println("attributes...");
        for (NamingEnumeration<String> e = attrs.getIDs(); e.hasMore();) {
            String name = e.next();
            System.out.println(name);
            attr = attrs.get(name);
            for (int i = 0; i < attr.size(); ++i) {
                System.out.println("  " + i + " " + attr.get(i));
            }
        }
        */

        UserAccount account =  new UserAccount 
            (username, display, given, email, phone);
        account.setEmployeeId(id);
        account.setInstitution(insti);

        return account;
    }

    public static void main (String[] argv) throws Exception {
        LdapConnector service = new LdapConnector ();
        /*
        UserAccount[] users = service.getAuthorizedUsers();
        if (users != null) {
            for (UserAccount u : users) {
                System.out.println(u);
            }
            System.out.println(users.length + " users found!");
        }
        */
        String username = null, password = null;
        System.err.print("Enter username: ");
        username = new BufferedReader
            (new InputStreamReader (System.in)).readLine();
        System.err.print("Enter password: ");
        password = new BufferedReader
            (new InputStreamReader (System.in)).readLine();

        if (service.authenticate (username, password)) {
            System.err.println("Successfully authenticated "+username);
        }
        else {
            System.err.println("Can't authenticate "+username);
        }
    }
}
