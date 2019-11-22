#!/usr/bin/perl -w

use strict;

# format is as follows:
# <ID> <SCORE> <1|0>
# where 1 is active/positive and 0 is inactive/negative

my @data = ();
my $p = 0; # positive
my $n = 0; # negative
while (<STDIN>) {
    chomp;
    my ($id, $score, $class) = split /\s/;
    my $row = {id=> $id, score => $score, class => $class};
    push @data, $row;
    if ($class == 1) {
	++$p;
    }
    else {
	++$n;
    }
}

my $prev = undef;
my $i = 1;
my $auc = 0;
my ($fp, $fp0, $tp, $tp0) = (0, 0, 0, 0);
foreach my $r (sort {$a->{score} <=> $b->{score}} @data) {
    #print "$r->{id} $r->{score} $r->{class}\n";
    if (!defined ($prev) or $r->{score} != $prev->{score}) {
	$auc += area($fp/$n, $fp0/$n, $tp/$p, $tp0/$p);
	print $fp/$n, "\t", $tp/$p, "\n";
	$prev = $r;
	$fp0 = $fp;
	$tp0 = $tp;
    }
    if ($r->{class} == 1) {
	++$tp;
    }
    else {
	++$fp;
    }
    ++$i;
}

$auc += area(1, $fp0/$n, 1, $tp0/$p);
print $fp/$n,"\t",$tp/$p,"\n";

print STDERR "AUC = $auc\n";

####
sub area {
    my ($x1, $x2, $y1, $y2) = @_;
    return abs($x1-$x2)*($y1+$y2)/2.0;
}