#!/bin/bash

#check that correct script-version is used in the first step
for (( year=1965; year<=1968; year++ ))
do
    path=../data/1908-1989/1960s/fixed_ocr-text/$year

    files=$path/*.txt

    echo ">> Processing year " $year
    echo "Converting OCR'ed text files into raw csv format..."
    for file in $files
        do
            python3 ./txt_to_csv_early70s.py $(realpath $file)
        done

    #if [ ! -d "../data/1990-1999/$year/RAW" ] 
    #then
    #    mkdir ../data/1990-1999/$year/RAW
    #    echo "Created directory '$year/RAW' for result files."
    #fi

    echo "Creating cleaned up cvs-files from raw versions..."
    files=$path/*_RAW.csv
    for file in $files
    do
        python3 ./clean_raw_csv.py $(realpath $file)
    done

    #echo "Moving raw files into directory 'RAW'..."
    #mv $path/*_RAW.csv ../data/1990-1999/RAW/

    #cat $path/*.csv > ./speeches_$year.csv

    #echo "Moving individual csvs into directory 'individual_csvs'..."
    #mv $path/*.csv ../data/1990-1999/individual_csvs/

    #echo "Cleaning final cvs"
    #python3 ./final_csv_cleaner.py $year

    #echo "Creating XML..."
    #python3 ./csv_to_xml.py $year


    #echo $year " Creating RDF..."
    #python3 ./create_rdf.py $year

    echo "Done!"
#mv ../data/PTK_1990s-all/PTK_1990s_txt/*.csv ../data/PTK_1990s-all/PTK_1990s_csv/
done