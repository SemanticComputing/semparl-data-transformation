#!/bin/sh

for FILE_ANA in $DIR/ParlaMint-FI.ana.xml $DIR/*[0-9].ana.xml; do
  EXTENT=`grep -E '<extent>.+</extent>' $FILE_ANA`
  FILE=`echo $FILE_ANA | sed -E 's/.{8}$//'`.xml
  sed -i '' "s|^.*<extent/>.*$|$EXTENT|" $FILE > $FILE".TEST"
done
