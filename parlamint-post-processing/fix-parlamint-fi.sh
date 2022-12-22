sed -i '' -f <(printf 's|%s|%s|g\n' $(<patterns.txt)) Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' 's|\[ParlaMint\]|\[ParlaMint\ SAMPLE\]|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -E -i '' 's|(.+)role="minister"([^<]+)$|\1role="minister"\2\1role="member"\2|' Data/ParlaMint-FI/ParlaMint-FI.xml

sed -i '' 's| </head>|</head>|' Data/ParlaMint-FI/ParlaMint-FI_2015-05-28-ps-8.xml
