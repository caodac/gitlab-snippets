
import java.util.*;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.io.*;
import java.net.*;
import java.security.*;

import javax.swing.text.*;
import javax.swing.text.html.*;
import javax.swing.text.html.parser.DocumentParser;
import javax.swing.text.html.parser.DTD;

/**
 * A simple web crawler that does depth first traversal of a given seed
 * url. This is useful for testing web app.
 */
public class WebCrawler {
    static final Logger logger = Logger.getLogger(WebCrawler.class.getName());

    static final String[] AGENTS = {
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322)",
        "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.1 SUSE/6.0.428.0 (KHTML, like Gecko) Chrome/6.0.428.0 Safari/534.1",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.428.0 Safari/534.1",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-US) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/6.0.428.0 Safari/534.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.3) Gecko/20100401"
    };

    static class HtmlParser extends HTMLEditorKit.ParserCallback {
        HTML.Tag tag;
        MutableAttributeSet attr;
        URL url;
        List<URL> hrefs = new ArrayList<URL>();

        HtmlParser (URL url) throws Exception {
            this.url = url;
            
            URLConnection http = url.openConnection();
            http.setRequestProperty
                ("User-Agent", AGENTS[RAND.nextInt(AGENTS.length)]);
            
            DocumentParser doc = new DocumentParser (DTD.getDTD("html"));
            doc.parse(new InputStreamReader
                      (http.getInputStream()), this, true);
        }

        @Override
        public void handleStartTag (HTML.Tag t,
                                    MutableAttributeSet attr, int pos) {
        }
        
        @Override
        public void handleEndTag (HTML.Tag t, int pos) {
        }
        
        @Override
        public void handleSimpleTag 
            (HTML.Tag t, MutableAttributeSet a, int pos) {
            tag = t;
            attr = new SimpleAttributeSet (a);
            //logger.info("simpletag: "+t);
            if (t == HTML.Tag.A) {
                String url = (String)attr.getAttribute(HTML.Attribute.HREF);
                if (url != null) {
                    try {
                        URL u = url.startsWith("?")
                            ? new URL (this.url.toString()+url)
                            : new URL (this.url, url);
                        // no linkout.. keep with within the same site
                        if (u.getHost().equals(this.url.getHost()))
                            hrefs.add(u);
                    }
                    catch (Exception ex) {
                        logger.log(Level.SEVERE, "Bogus url: "+url, ex);
                    }
                }
            }                   
        }

        public List<URL> getLinks () { return hrefs; }
    }
    
    static int MAXDEPTH = Integer.getInteger("maxdepth", 10);
    static final Random RAND = new Random ();
    
    private int maxdepth;
    private int pause = 1000; // in millis
    private List<URL> visited = new ArrayList<URL>();

    public WebCrawler () {
        this (MAXDEPTH);
    }

    public WebCrawler (int depth) {
        this.maxdepth = depth;
    }

    public void start (URL url) throws Exception {
        depthFirstCrawl (0, url);
    }

    void depthFirstCrawl (int depth, URL url)
        throws Exception {
        if (depth >= maxdepth) {
            /*
            logger.warning("Max depth ("+maxdepth
                           +") reached; backtracking "+url+"!");
            */
        }
        else {
            for (int i = 0; i <= depth; ++i)
                System.out.print(" ");
            System.out.println(">> "+url);

            try {
                HtmlParser parser = new HtmlParser (url);
                for (URL u : parser.getLinks()) {
                    depthFirstCrawl (depth+1, u);
                }
            }
            catch (Exception ex) {
                logger.warning(url+": "+ex.getMessage());
            }
        }
    }

    public static void main (String[] argv) throws Exception {
        if (argv.length == 0) {
            System.err.println("Usage: WebCrawler URL...");
            System.exit(1);
        }

        WebCrawler crawler = new WebCrawler ();
        for (String u : argv) {
            crawler.start(new URL (u));
        }
    }
}
