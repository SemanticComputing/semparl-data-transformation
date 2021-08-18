#!/bin/bash

echo -e "**********************\nSTARTING THE PROCESS\n**********************"

echo -e "\nSTARTING ON PDF-BASED YEARS"
./txt_to_rdf_xml.sh
echo -e "\nALL PDF-BASED YEARS DONE\n"

echo -e "\nSTARTING ON HTML-BASED YEARS"
./html_to_rdf_xml.sh
echo -e "\nALL HTML-BASED YEARS DONE\n"

echo -e "\nSTARTING ON XML-BASED YEARS"
./xml_to_rdf_xml.sh
echo -e "\nALL XML-BASED YEARS DONE\n"

# if [ "$RUNNING_IN_DOCKER_CONTAINER" ]
# then
#     echo "yes"
# else
#     echo "no"
# fi

echo -e "**********************\nPROCESS DONE\n**********************"