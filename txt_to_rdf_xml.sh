#!/bin/bash

#######################################################
# Transform plenary debates 1907-1999 to XML and RDF  #
#######################################################


# Chooce correct time range
for (( year=1907; year<=1999; year++ )) 
do
    if [[ $year -eq 1915 || $year -eq 1916 ]]; then
        echo ">> No data for year $year <<"
        continue
    fi

    decade="${year:2:1}"
    path=./fixed_title_txt-files/$year
    files=$path/*.txt

# Choosing correct script for correct year
    if [ $year -le 1909 ] #less or equal
    then 
        script='txt_to_csv_00s.py'
    elif [ $year -le 1919 ]
    then
        script='txt_to_csv_10s.py'
    elif [ $year -le 1939 ]
    then
        script='txt_to_csv_20-30s.py'
    elif [ $year -le 1975 ]
    then
        script='txt_to_csv_40s-early70s.py'
    elif [ $year -le 1988 ]
    then
        script='txt_to_csv_80s.py'
    elif [ $year -le 1994 ]
    then
        script='txt_to_csv_early90s.py'
    else
        script='txt_to_csv_late90s.py'
    fi


# Extract data
    echo ""
    echo ">> Processing year" $year
    echo "[Using script: $script]"
    echo "> Converting OCR'ed text files into raw csv format..."
    for file in $files
        do
            python3 ./$script  $(realpath $file)
        done


# Combine RAW files
    echo "> Combining individual csvs into 'speeches_${year}_RAW.csv'"
    cat $path/*.csv > $path/speeches_${year}_RAW.csv


# Cleaning the combined raw speeches
    echo "> Creating cleaned up cvs from raw version..."
    python3 ./clean_raw_csv.py $path/speeches_*_RAW.csv


# Moving files   
    # echo "> Moving raw csv into directory 'RAW'..."
    # mv $path/speeches_*_RAW.csv ../data/1908-1999/19${decade}0s/RAW

    echo "> Removing redundant raw csvs"
    rm $path/*_RAW.csv

    echo "> Moving cleaned csv into current directory"
    mv $path/*.csv ./


# Post-corrections
    echo "> Cleaning final cvs"
    echo "* Clean-up logs:"
    python3 ./final_csv_cleaner.py $year
    python3 ./name_cleaner.py $year
    echo "End of cleanup logs *"

# Final transformations (except for year 1999 which is half html-based and finalized in html script)
    if [[ ! $year -eq 1999 ]]; then
        echo "> Creating XML..."
        python3 ./csv_to_xml.py $year

        echo "> Creating RDF..."
        python3 ./create_rdf.py $year
    fi
    


###################################################
# Transform second Valtiopäivät if there are such #
###################################################
    if test -d "$path/toiset";  
    then
        
        path=./fixed_title_txt-files/$year/toiset
        files=$path/*.txt
        
        #Choose correct script
        if [ $year -le 1908 ] #less or equal
        then 
            script='txt_to_csv_00s.py'
        elif [ $year -le 1919 ]
        then
            script='txt_to_csv_10s.py'
        elif [ $year -le 1939 ]
        then
            script='txt_to_csv_20-30s.py'
        elif [ $year -le 1974 ]
        then
            script='txt_to_csv_40s-early70s.py'
        elif [ $year -le 1988 ]
        then
            script='txt_to_csv_80s.py'
        elif [ $year -le 1994 ]
        then
            script='txt_to_csv_early90s.py'
        else
            script='txt_to_csv_late90s.py'
        fi
        
        echo ""
        echo ">> Processing II year" $year
        echo "[Using script: $script]"
        echo "> Second VP: Converting OCR'ed text files into raw csv format..."
        for file in $files
        do
            python3 ./$script  $(realpath $file)
        done

        echo "> Combining individual csvs into 'speeches_${year}_II_RAW.csv'"
        cat $path/*.csv > $path/speeches_${year}_II_RAW.csv

    # Cleaning the combined raw speeches
        echo "> Creating cleaned up cvs from raw version..."
        python3 ./clean_raw_csv.py $path/speeches_*_RAW.csv

    # Moving files
        # echo "> Moving raw csv into directory 'RAW'..."
        # mv $path/speeches_*_RAW.csv ../data/1908-1999/19${decade}0s/RAW

        echo "> Removing redundant raw csvs"
        rm $path/*_RAW.csv

        echo "> Moving cleaned csv into current directory"
        mv $path/*.csv ./

    # Post-corrections
        echo "> Cleaning final cvs"
        echo "* Clean-up logs:"
        python3 ./final_csv_cleaner.py ${year}_II
        python3 ./name_cleaner.py ${year}_II
        echo "End of cleanup logs *"

    # Final transformations
        echo "> Creating XML for second VP..."
        python3 ./csv_to_xml.py ${year}_II

        echo "> Creating RDF for second VP..."
        python3 ./create_rdf.py ${year}_II
    fi



#############################################################
# Transform the exception file between Valtiopäivät in 1917 #
#############################################################
    if test -d "../data/1908-1999/19${decade}0s/fixed_ocr-text/$year/valiliite";  
    then 
        path=./fixed_title_txt-files/$year/valiliite
        files=$path/*.txt
        script='txt_to_csv_10s.py'
        
        echo ""
        echo ">>> Processing XX year" $year
        echo "[Using script: $script]"
        echo "> XX: Converting OCR'ed text files into raw csv format..."
        for file in $files
        do
            python3 ./$script  $(realpath $file)
        done

        echo "> Combining individual csvs into 'speeches_${year}_XX_RAW.csv'"
        cat $path/*.csv > $path/speeches_${year}_XX_RAW.csv

    # Cleaning the combined raw speeches
        echo "> Creating cleaned up cvs from raw version..."
        python3 ./clean_raw_csv.py $path/speeches_*_RAW.csv

    # Moving files
        # echo "> Moving raw csv into directory 'RAW'..."
        # mv $path/speeches_*_RAW.csv ../data/1908-1999/19${decade}0s/RAW

        echo "> Removing redundant raw csvs"
        rm $path/*_RAW.csv

        echo "> Moving cleaned csv into current directory"
        mv $path/*.csv ./

    # Post-corrections
        echo "> Cleaning final cvs"
        echo "* Clean-up logs:"
        python3 ./final_csv_cleaner.py ${year}_XX
        python3 ./name_cleaner.py ${year}_XX
        echo "End of cleanup logs *"

    # Final transformations
        echo "> Creating XML for XX VP..."
        python3 ./csv_to_xml.py ${year}_XX
        echo "> Creating RDF for XX VP..."
        python3 ./create_rdf.py ${year}_XX
    fi

    echo $year "Done! <<<<<"
done

mv *.xml results/
mv *.ttl results/

