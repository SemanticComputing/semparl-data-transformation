sed -i '' -E 's|(teiCorpus.+xml:id="ParlaMint-FI)"|\1.ana"|' Data/ParlaMint-FI/ParlaMint-FI.ana.xml
sed -i '' -E 's|(TEI.+xml:id="ParlaMint-FI[^"\.]+)"|\1.ana"|' Data/ParlaMint-FI/ParlaMint-FI_*.ana.xml

sed -i '' -E 's|(include.+href="ParlaMint-FI[^\.]+)\.xml"|\1.ana.xml"|' Data/ParlaMint-FI/ParlaMint-FI.ana.xml

sed -i '' 's|\[ParlaMint SAMPLE\]|\[ParlaMint.ana SAMPLE\]|' Data/ParlaMint-FI/ParlaMint-FI.ana.xml

sed -i '' -E 's|(title[^>]+>[^<]+\[ParlaMint)|\1.ana|' Data/ParlaMint-FI/ParlaMint-FI_*.ana.xml

sed -i '' -E 's|target="([^" ]+) ([^" ]+)"|target="#\1 #\2"|g' Data/ParlaMint-FI/ParlaMint-FI_*.ana.xml
