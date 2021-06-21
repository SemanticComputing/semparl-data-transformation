#!/bin/bash

for (( year=1999; year<=1999; year++ ))
do
    echo $year
    python3 ../../data/2000-2014/discussions_$year.html
    echo '> Discussions ready!'
    python3 main_pages_to_csv.py ../../data/2000-2014/main_pages_$year.html
    echo '> Main pages ready'

    python3 combine_speeches.py $year
    echo '> Final CSV ready!'

# Final transformations
    echo "> Creating XML..."
    python3 ./csv_to_xml.py $year

    echo "> Creating RDF..."
    python3 ./create_rdf.py $year

    echo $year "Done! <<<<<"

done
