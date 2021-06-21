#!/bin/bash

for (( year=2015; year<=2021; year++ ))
do
    echo $year

    python3 xml_to_csv.py $year
    echo '> Final CSV ready!'

# Final transformations
    echo "> Creating XML..."
    python3 csv_to_xml.py $year

    echo "> Creating RDF..."
    python3 create_rdf.py $year

    echo $year "Done! <<<<<"

done
