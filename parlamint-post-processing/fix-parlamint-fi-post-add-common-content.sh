#!/bin/sh

for FILE_ANA in $DIR/ParlaMint-FI.ana.xml $DIR/*[0-9].ana.xml; do
  MEASURE=`grep -E '<measure[^<]+</measure>' $FILE_ANA`
  OLD_IFS="$IFS"
  IFS=$'\n'
  MEASURE_TMP=""
  for LINE in $MEASURE; do
    LINE_TMP=`echo $LINE | sed -E 's/^[[:space:]]*.{8}(.+$)/\1/'`
    LINE_TMP=`echo $LINE_TMP | sed -E 's/(^.+).{10}[[:space:]]*$/\1/'`
    LINE_TMP="<measure"$LINE_TMP"</measure>"
    MEASURE_TMP=$MEASURE_TMP$LINE_TMP
  done
  IFS="$OLD_IFS"
  FILE=`echo $FILE_ANA | sed -E 's/.{8}$//'`.xml
  sed -i '' "s|^.*<extent/>.*$|<extent>$MEASURE_TMP</extent>|" $FILE
done
