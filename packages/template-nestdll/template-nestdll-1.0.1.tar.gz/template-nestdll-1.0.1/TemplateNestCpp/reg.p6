 my $text = " 	text";
 
my Match @spaces_repl = $text ~~ m:g/(<-[\S\r\n]>*) text/;

while @spaces_repl {
 my Match $repl = shift @spaces_repl;  
say "."~$repl;
}

say ">{$0[0]}<";


my %table =     NAME => 'table',
        rows => [{
            NAME => 'table_row',
            name => 'Sam',
            job => 'programm"er'
        }, {
            NAME => 'table_row',
            name => 'Steve',
            job => 'soda jerk'
        }];

say %table.raku;


my $comp = %table;

say $comp.raku;


my $table2 =     %(':', 25, 'Ben', 23, 'Lia', {b=>4}); 

say $table2.raku;

my $table3 =     %(2, 25, 'Ben', 23, 'Lia', {b=>4}); 

say $table3.raku;


my $table4 =     %(2, [1,2,[3]]); 

say $table4.raku;



my $table5 =     %(2, [1,2,${o=>5}]); 

say $table5.raku;

say  $table5{2}[2]<o>;



my $page = {
		NAME => 'page',
		contents => [${
			NAME => 'box',
			title => 'First nested box'
		}]
	};

	push @($page<contents>),{
		NAME => 'box',
		title => 'Second nested box'
	};

say $page.raku;

