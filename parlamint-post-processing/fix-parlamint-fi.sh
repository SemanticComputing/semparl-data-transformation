#/bin/sh

sed -i '' -f <(printf 's|%s|%s|g\n' $(<patterns.txt)) $DIR/ParlaMint-FI.xml

if [ "$SAMPLE" = true ]; then
  sed -i '' -f <(printf 's|%s|%s|g\n' $(<patterns-sample.txt)) $DIR/ParlaMint-FI.xml
  sed -i '' 's|\[ParlaMint\]|\[ParlaMint\ SAMPLE\]|' $DIR/ParlaMint-FI.xml
fi

sed -E -i '' 's|(.+)role="minister"([^<]+)$|\1role="minister"\2\1role="member"\2|' $DIR/ParlaMint-FI.xml

sed -i '' 's|<term/>|<term>Pysyvä komitea</term>|' $DIR/ParlaMint-FI.xml

sed -i '' '/<person xml:id="SDP">/{N;N;N;N;N;d;}' $DIR/ParlaMint-FI.xml

sed -i '' '/<person xml:id="RKP">/{N;N;N;N;N;d;}' $DIR/ParlaMint-FI.xml

sed -i '' "s|<listOrg>|<listOrg><org role=\"politicalParty\" xml:id=\"party.SMP\"><orgName full=\"yes\" xml:lang=\"fi\">Suomen Maaseudun Puolue</orgName><orgName full=\"yes\" xml:lang=\"en\">Finnish Rural Party</orgName><orgName full=\"abb\">SMP</orgName><event from=\"1959-02-09\" to=\"2003-08-12\"><label xml:lang=\"en\">existence</label></event><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"fi\">https://fi.wikipedia.org/wiki/Suomen_Maaseudun_Puolue</idno><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"en\">https://en.wikipedia.org/wiki/Finnish_Rural_Party</idno></org><org role=\"politicalParty\" xml:id=\"party.KP\"><orgName full=\"yes\" xml:lang=\"fi\">Kansalaispuolue</orgName><orgName full=\"yes\" xml:lang=\"en\">Citizens' Party</orgName><orgName full=\"abb\">KP</orgName><event from=\"2016-03-08\" to=\"2022-08-25\"><label xml:lang=\"en\">existence</label></event><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"fi\">https://fi.wikipedia.org/wiki/Kansalaispuolue</idno><idno subtype=\"wikimedia\" type=\"URI\" xml:lang=\"en\">https://en.wikipedia.org/wiki/Citizens%27_Party_(Finland)</idno></org>|" $DIR/ParlaMint-FI.xml

sed -i '' -E '/<surname>Mäenpää<\/surname>/,+1 s|<forename/>|<forename>Jani</forename>|' $DIR/ParlaMint-FI.xml

sed -i '' '/<person xml:id="Eerola">/{N;N;N;N;N;d;}' $DIR/ParlaMint-FI.xml
sed -i '' 's|#Eerola|#JuhoEerola|' $DIR/*[0-9].xml

sed -i '' '/<person xml:id="Korhonen">/{N;N;N;N;N;d;}' $DIR/ParlaMint-FI.xml
sed -i '' 's|#Korhonen|#TimoV.Korhonen|' $DIR/*[0-9].xml

sed -i '' -E '/<person xml:id="Hoskinen">/,+3 s|<forename/>|<forename>Hannu</forename>|' $DIR/ParlaMint-FI.xml

sed -i '' '/<person xml:id="Sarkomaan">/{N;N;N;N;N;d;}' $DIR/ParlaMint-FI.xml
sed -i '' 's|#Sarkomaan|#SariSarkomaa|' $DIR/*[0-9].xml

sed -i '' 's| </head>|</head>|' $DIR/*[0-9].xml

sed -i '' 's|<idno subtype="handle" type="URI"/>|<idno subtype="handle" type="URI">http://hdl.handle.net/11356/XXXX</idno>|' $DIR/ParlaMint-FI.xml $DIR/*[0-9].xml

for FILE_XML in $DIR/*[0-9].xml; do
  ID_TMP=`grep -E '<TEI .+>' $FILE_XML`
  ID=`echo $ID_TMP | sed -E 's/.+xml:id="([^"]+)".+/\1/'`
  mv $FILE_XML $DIR/$ID.xml
  BASENAME_FILE_XML=`basename $FILE_XML`
  sed -i '' "s|$BASENAME_FILE_XML|$ID.xml|" $DIR/ParlaMint-FI.xml

  DATE=`echo $ID | sed -E 's/^[^0-9]+([0-9-]+)-.+$/\1/'`
  MEETING=`echo $ID | sed -E 's/^.+-([0-9]+)$/\1/'`
  if [[ $DATE < "2016-02-02" ]]; then
    SESSION="2015"
  elif [[ $DATE < "2017-02-01" ]]; then
    SESSION="2016"
  elif [[ $DATE < "2018-02-05" ]]; then
    SESSION="2017"
  elif [[ $DATE < "2019-04-17" ]]; then
    SESSION="2018"
  elif [[ $DATE < "2020-04-02" ]]; then
    SESSION="2019"
  elif [[ $DATE < "2021-02-02" ]]; then
    SESSION="2020"
  else
    SESSION="2021"
  fi
  if [[ $SESSION = "2019" || $SESSION = "2020" || $SESSION = "2021" ]]; then
    TERM=2019
  else
    TERM=2015
  fi
  sed -i '' -E "s|<meeting.+|<meeting ana='#parla.uni #parla.term #parl_term.$TERM' corresp='#fi_parliament' n='$TERM'>Vaalikausi $TERM</meeting><meeting ana='#parla.uni #parla.session' corresp='#fi_parliament' n='$SESSION'>Valtiopäivät $SESSION</meeting><meeting ana='#parla.uni #parla.meeting' corresp='#fi_parliament' n='$MEETING'>Täysistunto $MEETING</meeting><meeting ana='#parla.uni #parla.sitting' corresp='#fi_parliament' n='$DATE'>$DATE</meeting>|" $DIR/$ID.xml
done

sed -i '' "s/$(echo -ne '\u00A0')/ /g" $DIR/*[0-9].xml

sed -i '' -E 's/(relation active="[^"]+) "/\1"/' $DIR/ParlaMint-FI.xml

sed -i '' -E 's/next="([^#"][^"]+)"/next="#\1"/' $DIR/*[0-9].xml
sed -i '' -E 's/prev="([^#"][^"]+)"/prev="#\1"/' $DIR/*[0-9].xml

sed -E -i '' 's/who="#(RKP|SDP)"//' $DIR/*[0-9].xml

sed -i '' -E 's|<seg[^/>]+/>||' $DIR/*[0-9].xml
