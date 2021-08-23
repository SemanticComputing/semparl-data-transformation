#!/bin/bash

if [ $1 = "all" ]; then
    for (( year=2015; year<=2021; year++ ))
    do
        echo ">> Processing year" $year

        python3 xml_to_CSV.py $year
        echo '> Final CSV ready!'

    # Final transformations
        echo "> Creating XML..."
        python3 csv_to_xml.py $year

        echo "> Creating RDF..."
        python3 create_rdf.py $year

        echo $year "Done! <<<<<"

    done
else
    year=2021
    echo ">> Processing year" $year

    python3 xml_to_CSV.py $year
    echo '> Final CSV ready!'

# Final transformations
    echo "> Creating XML..."
    python3 csv_to_xml.py $year

    echo "> Creating RDF..."
    python3 create_rdf.py $year

    echo $year "Done! <<<<<"
fi

mv *.xml results/
mv *.ttl results