sed -i '' -E 's|(teiCorpus.+xml:id="ParlaMint-FI)"|\1.ana"|' Data/ParlaMint-FI/ParlaMint-FI.ana.xml
sed -i '' -E 's|(TEI.+xml:id="ParlaMint-FI[^"\.]+)"|\1.ana"|' Data/ParlaMint-FI/ParlaMint-FI_*.ana.xml
