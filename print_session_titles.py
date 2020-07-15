import re
import sys

filename = sys.argv[1]
file = open(filename, "r")
contents = file.read()
rows = contents.split('\n')
file.close()

# 5. Tiistaina 13 päivänä helmikuuta 1990
for row in rows:
    if re.compile('\f*[0-9]+[\.,] [A-Z][a-zåäö]+ [0-9]+ päivänä .*kuuta 199[0-9]').match(row):
        print(row)
