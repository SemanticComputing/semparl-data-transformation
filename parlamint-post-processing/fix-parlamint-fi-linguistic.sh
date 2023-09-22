#/bin/sh

sed -i '' -E 's|(teiCorpus.+xml:id="ParlaMint-FI)"|\1.ana"|' $DIR/ParlaMint-FI.ana.xml
sed -i '' -E 's|(TEI.+xml:id="ParlaMint-FI[^"\.]+)"|\1.ana"|' $DIR/ParlaMint-FI_*.ana.xml

sed -i '' -E 's|(include href="ParlaMint-FI[^\.]+)\.xml"|\1.ana.xml"|g' $DIR/ParlaMint-FI.ana.xml

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

sed -i '' 's/<w xml:id="ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.761" lemma="Ukko\.fin" msd="UPosTag=SYM|Abbr=Yes|Case=Gen|Number=Sing">Ukko\.fi:n<\/w>/<w xml:id="ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.761" lemma="Ukko\.fi" msd="UPosTag=PROPN|Abbr=Yes|Case=Gen|Number=Sing">Ukko\.fi:<\/w>/' $DIR/ParlaMint-FI_2017-12-08-ps-134.ana.xml
sed -i '' 's/<w xml:id="ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.762" lemma="" msd="UPosTag=NOUN|Abbr=Yes|Case=Gen|Number=Sing" join="right" \/>/<w xml:id="ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.762" lemma="n" msd="UPosTag=NOUN|Abbr=Yes|Case=Gen|Number=Sing" join="right">n<\/w>/' $DIR/ParlaMint-FI_2017-12-08-ps-134.ana.xml
sed -i '' 's/<link ana="ud-syn:goeswith" target="#ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.761 #ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.761" \/>/<link ana="ud-syn:flat_name" target="#ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.761 #ParlaMint-FI_2017-12-08-ps-134\.seg232\.28\.762" \/>/' $DIR/ParlaMint-FI_2017-12-08-ps-134.ana.xml