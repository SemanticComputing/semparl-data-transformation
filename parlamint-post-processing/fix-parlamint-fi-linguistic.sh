#/bin/sh

sed -i '' -E 's|(teiCorpus.+xml:id="ParlaMint-FI)"|\1.ana"|' $DIR/ParlaMint-FI.ana.xml
sed -i '' -E 's|(TEI.+xml:id="ParlaMint-FI[^"\.]+)"|\1.ana"|' $DIR/ParlaMint-FI_*.ana.xml

sed -i '' -E 's|(include.+href="ParlaMint-FI[^\.]+)\.xml"|\1.ana.xml"|' $DIR/ParlaMint-FI.ana.xml

if [ "$SAMPLE" = true ]; then
  sed -i '' 's|\[ParlaMint SAMPLE\]|\[ParlaMint.ana SAMPLE\]|' $DIR/ParlaMint-FI.ana.xml
else
  sed -i '' 's|\[ParlaMint\]|\[ParlaMint.ana\]|' $DIR/ParlaMint-FI.ana.xml
fi

sed -i '' -E 's|(title[^>]+>[^<]+\[ParlaMint)|\1.ana|' $DIR/ParlaMint-FI_*.ana.xml

sed -i '' -E 's|target="([^" ]+) ([^" ]+)"|target="#\1 #\2"|g' $DIR/ParlaMint-FI_*.ana.xml

sed -i '' -E 's/"UPosTag=([^"]+)\|"/"UPosTag=\1"/g' $DIR/ParlaMint-FI_*.ana.xml


sed -i '' 's/:ns0//g' $DIR/ParlaMint-FI*.ana.xml
sed -i '' 's/ns0://g' $DIR/ParlaMint-FI*.ana.xml
