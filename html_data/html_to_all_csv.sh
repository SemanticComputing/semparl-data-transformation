#!/bin/bash

year=2014


python3 html_to_csv.py discussions_$year.html
echo 'Discussions ready!'
python3 main_pages_to_csv.py main_pages_$year.html
echo 'Main pages ready'

python3 combine_speeches.py $year
echo 'Final CSV ready!'

