#!/bin/bash

#original ocr-files 
files=../data/1908-1989/1950s/fixed_ocr-text/1952/*

for file in $files
do
  echo $file
  python3 ./print_session_titles.py $(realpath $file)
done