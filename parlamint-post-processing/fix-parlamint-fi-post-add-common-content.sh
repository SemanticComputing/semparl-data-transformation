#!/bin/sh

for FILE_ANA in Data/ParlaMint-FI/ParlaMint-FI.ana.xml Data/ParlaMint-FI/*[0-9].ana.xml; do
  MEASURE=`grep -E '<ns0:measure[^<]+</ns0:measure>' $FILE_ANA`
  OLD_IFS="$IFS"
  IFS=$'\n'
  MEASURE_TMP=""
  for LINE in $MEASURE; do
    LINE_TMP=`echo $LINE | sed -E 's/^[[:space:]]*.{12}(.+$)/\1/'`
    LINE_TMP=`echo $LINE_TMP | sed -E 's/(^.+).{14}[[:space:]]*$/\1/'`
    LINE_TMP="<measure"$LINE_TMP"</measure>"
    MEASURE_TMP=$MEASURE_TMP$LINE_TMP
  done
  IFS="$OLD_IFS"
  FILE=`echo $FILE_ANA | sed -E 's/.{8}$//'`.xml
  sed -i '' "s|^.*<extent/>.*$|<extent>$MEASURE_TMP</extent>|" $FILE
done
