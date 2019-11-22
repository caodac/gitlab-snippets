
import java.util.*;

/**
Hi, do you know of an algorithm (more elegant than brute force) that given a set of pairwise ranks, 

A > B
A > C
B > C
D > A

can construct the fully ranked (ordered?) sequence

D > A > B > C

More generally, given a set of partial ranks of arbitrary length

A > B > C
D > A
...

generate the fully ranked sequence of all elements

*/

public class PartialRank {
    static class Node {
        String label;
        List<Node> next = new ArrayList<Node>();

        Node (String label) {
            this.label = label;
        }
    }

    static class RankedList {
        Node head;

        public RankedList () {
        }

        public void add (String... s) {
            if (s.length == 0)
                return;

            Node node = get (s[0]);
            if (node == null) {
                node = new Node (s[0]);
                if (head != null)
                    node.next.add(head);
                head = node;
            }

            for (int i = 1; i < s.length; ++i) {
                Node n = get (s[i]);
                if (n == null)
                    n = new Node (s[i]);

                if (node.next.indexOf(n) < 0)
                    node.next.add(n);
                node = n;
            }
        }

        Node get (String label) {
            List<Node> found = new ArrayList<Node>();
            find (label, head, found);
            if (!found.isEmpty())
                return found.iterator().next();
            return null;
        }
        
        void find (String label, Node node, List<Node> found) {
            if (node == null)
                ;
            else if (node.label.equals(label))
                found.add(node);
            else {
                for (Node n : node.next) {
                    find (label, n, found);
                }
            }
        }

        void dump () {
            if (head == null) {
                System.out.println("{}");
                return;
            }

            dump (head, 0);
        }

        void dump (Node node, int depth) {
            if (node == null)
                return;

            for (int i = 0; i <= depth; ++i)
                System.out.print(" ");
            System.out.println("{"+node.label+":"+ node+"}");
            for (Node n : node.next)
                dump (n, depth+1);
        }

        /**
         * Find the longest path from the head
         */
        public List<String> rankedList () {
            List<Node> best = new ArrayList<Node>();
            ranked (head, new ArrayList<Node>(), best);
            List<String> ranked = new ArrayList<String>();
            for (Node n : best)
                ranked.add(n.label);
            return ranked;
        }

        void ranked (Node node, List<Node> current, List<Node> best) {
            current.add(node);
            if (node.next.isEmpty()) {
                if (current.size() > best.size()) {
                    best.clear();
                    best.addAll(current);
                }
                current.clear();
            }
            else {
                for (Node n : node.next)
                    ranked (n, current, best);
            }
        }
    }

    public static void main (String[] argv) throws Exception {
        RankedList rl = new RankedList ();
        /*
        rl.add("A", "B");
        rl.add("A", "C");
        rl.add("B", "C");
        rl.add("D", "A");
        */

        rl.add("A", "B", "C");
        rl.add("D", "A");

        List<String> ranked = rl.rankedList();
        for (Iterator<String> it = ranked.iterator(); it.hasNext(); ) {
            String s = it.next();
            System.out.print(s);
            if (it.hasNext()) System.out.print(" > ");
        }
        System.out.println();
    }
}
