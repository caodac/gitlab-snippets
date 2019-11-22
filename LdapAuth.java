import java.io.*;
import java.util.*;
import javax.naming.*;
import javax.naming.directory.*;
import javax.naming.ldap.*;

public class LdapAuth {

    static public void main (String[] argv) throws Exception {
        if (argv.length < 2) {
            System.out.println("Usage: LdapAuth USER PASS");
            System.exit(1);
        }

        String username = argv[0];
        String password = argv[1];

        SearchControls controls =
            new SearchControls(SearchControls.SUBTREE_SCOPE, 0, 0,
                               new String[]{"mail",
                                            "displayName",
                                            "sn",
                                            "givenName",
                                            "telephoneNumber",
                                            "employeeID",
                                            "department"},
                               true, true);
        controls.setCountLimit(0);

        Hashtable env = new Hashtable();
        env.put(Context.INITIAL_CONTEXT_FACTORY,
                "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, "ldap://directory.nih.gov:389");
        env.put(Context.SECURITY_AUTHENTICATION, "DIGEST-MD5");
        env.put(Context.SECURITY_PRINCIPAL, username);
        env.put(Context.SECURITY_CREDENTIALS, password);

        DirContext ctx = null;
        try {
            ctx = new InitialDirContext(env);
            NamingEnumeration<SearchResult> matches = ctx.search
                ("O=NIH,C=US", 
                 "(&(name="+username+")(objectClass=user)(department=NCATS))",
                 controls);
            int n = 0;
            if (matches.hasMore()) {
                SearchResult res = matches.next();
                Attributes attrs = res.getAttributes();
                Attribute dept = attrs.get("department");
                Attribute name = attrs.get("name");

                System.out.printf("%3d:", ++n);
                System.out.println(attrs);
            }
            System.out.println("Successfully authenticate user "
                               +username+"!!!");
        }
        catch (AuthenticationException ex) {
            System.err.println("Either username or password is bogus for "
                               +username+"!!!");
        }
        catch (NamingException ex) {
            ex.printStackTrace();
        }
        finally {
            if (ctx != null)
                ctx.close();
        }
    }
}
