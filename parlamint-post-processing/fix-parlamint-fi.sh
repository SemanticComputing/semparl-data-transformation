sed -i '' -f <(printf 's|%s|%s|g\n' $(<patterns.txt)) Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' 's|\[ParlaMint\]|\[ParlaMint\ SAMPLE\]|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -E -i '' 's|(.+)role="minister"([^<]+)$|\1role="minister"\2\1role="member"\2|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' 's|<term/>|<term>Pysyvä komitea</term>|' Data/ParlaMint-FI/ParlaMint-FI.xml


sed -i '' '/<person xml:id="SDP">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' '/<person xml:id="RKP">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml


sed -i '' 's| </head>|</head>|' Data/ParlaMint-FI/ParlaMint-FI_2015-05-28-ps-8.xml

sed -i '' 's|<idno subtype="handle" type="URI"/>|<idno subtype="handle" type="URI">http://hdl.handle.net/11356/XXXX</idno>|' Data/ParlaMint-FI/ParlaMint-FI.xml Data/ParlaMint-FI/*[0-9].xml

