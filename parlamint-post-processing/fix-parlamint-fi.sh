sed -i '' -f <(printf 's|%s|%s|g\n' $(<patterns.txt)) Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' 's|\[ParlaMint\]|\[ParlaMint\ SAMPLE\]|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -E -i '' 's|(.+)role="minister"([^<]+)$|\1role="minister"\2\1role="member"\2|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' 's|<term/>|<term>Pysyvä komitea</term>|' Data/ParlaMint-FI/ParlaMint-FI.xml


sed -i '' '/<person xml:id="SDP">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' '/<person xml:id="RKP">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' "s|<listOrg>|<listOrg><org role=\"politicalParty\" xml:id=\"party.SMP\"><orgName full=\"yes\" xml:lang=\"fi\">Suomen Maaseudun Puolue</orgName><orgName full=\"yes\" xml:lang=\"en\">Finnish Rural Party</orgName><orgName full=\"abb\">SMP</orgName><event from=\"1959-02-09\" to=\"2003-08-12\"><label xml:lang=\"en\">existence</label></event><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"fi\">https://fi.wikipedia.org/wiki/Suomen_Maaseudun_Puolue</idno><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"en\">https://en.wikipedia.org/wiki/Finnish_Rural_Party</idno></org><org role=\"politicalParty\" xml:id=\"party.KP\"><orgName full=\"yes\" xml:lang=\"fi\">Suomen Kansanpuolue</orgName><orgName full=\"yes\" xml:lang=\"en\">People's Party of Finland</orgName><orgName full=\"abb\">KP</orgName><event from=\"1951-02-03\" to=\"1965\"><label xml:lang=\"en\">existence</label></event><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"fi\">https://fi.wikipedia.org/wiki/Suomen_Kansanpuolue</idno><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"en\">https://en.wikipedia.org/wiki/People%27s_Party_of_Finland_(1951)</idno></org>|" Data/ParlaMint-FI/ParlaMint-FI.xml


sed -i '' -E '/<surname>Mäenpää<\/surname>/,+1 s|<forename/>|<forename>Jani</forename>|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' '/<person xml:id="Eerola">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml
sed -i '' 's|#Eerola|#JuhoEerola|' Data/ParlaMint-FI/*[0-9].xml

sed -i '' '/<person xml:id="Korhonen">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml
sed -i '' 's|#Korhonen|#TimoV.Korhonen|' Data/ParlaMint-FI/*[0-9].xml

sed -i '' -E '/<person xml:id="Hoskinen">/,+3 s|<forename/>|<forename>Hannu</forename>|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' '/<person xml:id="Sarkomaan">/{N;N;N;N;N;d;}' Data/ParlaMint-FI/ParlaMint-FI.xml
sed -i '' 's|#Sarkomaan|#SariSarkomaa|' Data/ParlaMint-FI/*[0-9].xml


sed -i '' 's| </head>|</head>|' Data/ParlaMint-FI/ParlaMint-FI_2015-05-28-ps-8.xml

sed -i '' 's|<idno subtype="handle" type="URI"/>|<idno subtype="handle" type="URI">http://hdl.handle.net/11356/XXXX</idno>|' Data/ParlaMint-FI/ParlaMint-FI.xml Data/ParlaMint-FI/*[0-9].xml


for FILE_XML in Data/ParlaMint-FI/*[0-9].xml; do
  ID_TMP=`grep -E '<TEI ana="#parla.sitting #reference" xml:id="[^"]+" xml:lang="fi" xmlns="http://www.tei-c.org/ns/1.0">' $FILE_XML`
  ID_TMP=`echo $ID_TMP | sed -E 's/^[[:space:]]*.{45}(.+$)/\1/'`
  ID=`echo $ID_TMP | sed -E 's/(^.+).{52}[[:space:]]*$/\1/'`
  mv $FILE_XML Data/ParlaMint-FI/$ID.xml
  BASENAME_FILE_XML=`basename $FILE_XML`
  sed -i '' "s|$BASENAME_FILE_XML|$ID.xml|" Data/ParlaMint-FI/ParlaMint-FI.xml
done

