#!/bin/bash
set -eo pipefail 

echo -e "**********************\nSTARTING THE PROCESS\n**********************"


if [ $1 = "all" ]; then
    echo -e "\nSTARTING ON PDF-BASED YEARS"
    ./txt_to_rdf_xml.sh
    echo -e "\nALL PDF-BASED YEARS DONE\n"

    echo -e "\nSTARTING ON HTML-BASED YEARS"
    ./html_to_rdf_xml.sh
    echo -e "\nALL HTML-BASED YEARS DONE\n"

    echo -e "\nSTARTING ON XML-BASED YEARS"
    ./xml_to_rdf_xml.sh all
    echo -e "\nALL XML-BASED YEARS DONE\n"
else
    echo -e "\nSTARTING ON SPEECHES FROM 2021"
    ./xml_to_rdf_xml.sh update
    echo -e "\nSPEECHES FROM 2021 DONE\n"
fi



# if [ "$RUNNING_IN_DOCKER_CONTAINER" ]
# then
#     echo "yes"
# else
#     echo "no"
# fi

echo -e "**********************\nPROCESS DONE\n**********************"