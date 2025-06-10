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

    echo '> Enriching speaker info...'
    python3 enrich_member_info.py $year

    if [[ $year -eq 1999 ]]; then
        mv speeches_1999.csv speeches_1999_b.csv
        python3 combine_1999.py
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
mv speeches_*.csv results/
rm results/speeches_1999_a.csv
rm results/speeches_1999_b.csv