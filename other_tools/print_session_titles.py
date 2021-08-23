import re
import sys
from pprint import pprint

filename = sys.argv[1]
file = open(filename, "r")
contents = file.read()
rows = contents.split('\n')
file.close()

# 5. Tiistaina 13 päivänä helmikuuta 1990
for i in range(len(rows)):
    # if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p(\.|\-|äivänä) .*kuuta 19[0123][0-9]$').match(rows[i]):
    if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p(\.|\-|äivänä) .*kuuta( 19[0123][0-9])?$').match(rows[i]):
        print(rows[i])
    if 'Täysistunto keskeytetään kello' in rows[i]:
        print(rows[i:i+5])
