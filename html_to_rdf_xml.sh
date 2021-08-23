#!/bin/bash

# First take care of year 1999 that is half text, half html based, text half has been created previously
mv speeches_1999.csv speeches_1999_a.csv

for (( year=1999; year<=2014; year++ ))
do
    echo ">> Processing year" $year
    python3 html_to_csv.py ./original_html/discussions_$year.html
    echo '> Discussions ready!'
    python3 main_pages_to_csv.py ./original_html/main_pages_$year.html
    echo '> Main pages ready'

    python3 combine_speeches.py $year
    echo '> Final CSV ready!'

    if [[ $year -eq 1999 ]]; then
        mv speeches_1999.csv speeches_1999_b.csv
        cat speeches_1999_a.csv speeches_1999_b.csv > speeches_1999.csv
    fi

# Final transformations
    echo "> Creating XML..."
    python3 ./csv_to_xml.py $year

    echo "> Creating RDF..."
    python3 ./create_rdf.py $year

    echo $year "Done! <<<<<"

done

mv *.xml results/
mv *.ttl results/