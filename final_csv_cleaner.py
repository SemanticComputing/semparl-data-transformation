import csv
import re
import sys
import difflib
import os
import pandas as pd

#######################################################
# Script to fix issues that have survived or emerged  #
# from the process, such as splitted speeches         #
#######################################################


def exception_name(last, name_type):
    # check if a name actually ends in -lle and is not allative case, taking possible OCR distortion in consideration
    # or in name actually ends -lta
    match = []
    lle = ['Helle', 'Lille', 'Wuolle']
    lta = ['Koivusilta', 'Markkula-Kivisilta',
           'Mustasilta', 'Pitkäsilta', 'Valta']
    if name_type == 1:
        match = difflib.get_close_matches(last, lle)
    else:
        match = difflib.get_close_matches(last, lta)
    # lastname matches one of the exception names
    if match and abs(len(last)-len(match[0])) < 3:
        return True
    return False


year = sys.argv[1]
csv.field_size_limit(sys.maxsize)
is_in_docker = os.environ.get('RUNNING_IN_DOCKER_CONTAINER', False)

with open('speeches_{}.csv'.format(year), newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    rows = list(reader)
if not is_in_docker:
    with open('backups/speeches_{}_BAK.csv'.format(year), 'w', newline='') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerows(rows)

print(len(rows))
print('>Rows attached to previous ones, fixing cases where one speech was erroneously split:\n***')
new = []
# to follow when year changes in document that didn't mark years in titles
following_year = False

# find right column indexes (this is to ensure that making edits to the pipeline,
# doesn't require rewriting tens on indexes here)

id_ix = rows[0].index('speech_id')
first_ix = rows[0].index('given')
last_ix = rows[0].index('family')
role_ix = rows[0].index('role')
party_ix = rows[0].index('party')
content_ix = rows[0].index('content')
speech_type_ix = rows[0].index('speech_type')
date_ix = rows[0].index('date')
orig_speaker_ix = rows[0].index('name_in_source')
headers = rows[0]


for i in range(1, len(rows)):
    speech_id = rows[i][id_ix]
    first = rows[i][first_ix]
    last = rows[i][last_ix]
    party = rows[i][party_ix]
    role = rows[i][role_ix]

    content = rows[i][content_ix]
    year = speech_id.partition('_')[0]
    date = rows[i][date_ix]
    original_speaker_layout = rows[i][orig_speaker_ix]

    year = int(re.sub('_(II|XX)', '', year))

    rows[i][last_ix] = last.strip('—')

    # Could use endswith('lle), but sometimes it in the middle ('Ahollevielä') and there are names like 'Helle'
    # or could be a weird name split

    if re.search('kysy|totesi|puhu|sano|esille|olisi|myös|vielä|aloite|jatk(oi|aa)|kaikella', last, flags=re.I)\
            or re.search('asiasta|esit|haukkui|totea|lausu|minä|sitaatti|ryhmästä|myös|tä(äll|m)ä|tieduste|luki|ehdot|vasta(ta|si|uk)|,joka', last, flags=re.I)\
            or re.search('sijaan ed|puheet|käsittel|pohti|keskustel|ym,|kuuluva', last, flags=re.I)\
            or re.search('kysy|totesi|puhu|sano|esille|olisi|vielä|relle|jatk(oi|aa)|lälle|osoitti|miel(es)?tä|sitten', role, flags=re.I)\
            or re.search('ilmoitti|viittasi|tiedustel|lausu|totea|sitaatti|pyytäisin|edelleen|epäili|ym,|lopuksi|vastasi', role, flags=re.I)\
            or re.search('\d+ ?\$', last)\
            or (last.endswith('lle') and not exception_name(last, 1))\
            or (last.endswith('lta') and not exception_name(last, 2)) or last.endswith('ltä')\
            or (last.endswith('sta') and not last.endswith('ntausta')) or last.endswith('stä')\
            or ('puheenvuoro' in last and not ')' in last) or 'uskokaa' in role\
            or 'lyhyesti' in last or 'näki' in last\
            or 'Aittoniemitäällänosti88' in last or 'lopuksi' in last\
            or ',että' in last or 'asiaan' in last\
            or 'Koskinenjatkaa' in last or 'hallitusmuodon' in last\
            or 'Kyllä on ihan niin, kuin ministeri Alho' in role\
            or 'aloittee' in last or 'mainits' in last or 'tämä' in role\
            or 'RäsänenottiesiinValtatie10' in last or 'kuunnelkaa' in last\
            or 'Ministeri Niinistö, te olette' in role or 'esiintyi' in role\
            or 'Alarannalleperehtymisestä' in last\
            or 'luomutuotannosta' in last or 'kommente' in last\
            or 'Raskhuomioi' in last or 'tosiasia' in last\
            or ('kanta' in last and not last == 'Hirvikanta')\
            or 'tunnustusta' in last or 'puolesta' in role \
            or ('sitä' in last and not 'Uusitälo' in last) \
            or 'Kun ministeri Pekkala' in role\
            or 'Paloheimonosalta' in last or 'oikeassa' in last\
            or 'hyväksytään' in role or 'Arvoisa' in role or 'arvosteli' in last\
            or 'kiinnitti' in last or 'kritisoi' in role or ' oli' in role or 'ponteen' in last\
            or 'maininnut' in last or 'oikein' in last or 'viittasi' in last or 'kehyskunnis' in last\
            or 'ilmeisesti' in last or 'taisiolla' in last or 'syyt' in role\
            or 'onsiis' in last or 'yritti' in last or 'tekemä' in last\
            or 'kanssa' in last or 'lainasi' in last or 'Suomisenpuhe' in last\
            or 'Katsooko' in role or 'huomaut' in last or 'jamuut' in last \
            or '-asia' in last or 'Leppänen on' in role or 'päätään' in last or 'puuttui' in last\
            or 'ei ole' in role or 'perustel' in last\
            or 'Sorsan ja' in role or 'todennut' in role or 'niinhyvä' in last or 'kannatta' in last\
            or '(Eduskunnasta' in last or 'Törnqvistille' in last\
            or (last == 'Eklund' and content.startswith(' Salailu ei auta!)')):

        print(role, last)
        if not 'Kansanedustaja' in role:  # party.strip().isupper():
            rows[i-1][content_ix] += ' ' + ' '.join([role, last+':', content])
        else:
            rows[i-1][content_ix] += ' ' + ' '.join([last+':', content])

        rows[i-1][content_ix] = rows[i-1][content_ix].replace('-<REMOVE> ', '')
        continue

    if 'Karhunen lähti pois, (Ed' in first or 'Jaakonsaaten välihuuto' in first:
        rows[i-1][content_ix] += ' ' + ' '.join([first, last+':', content])
        continue

    if 'inisteti' in role:
        rows[i][role_ix] == role.replace('inisteti', 'inisteri')
        role = rows[i][role_ix]

    if (first == 'Kettunen (Ed' and last == 'Helminen'):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Pentti', 'Kettunen', 'PS'
        rows[i][content_ix] = ' (Ed. Helminen: ' + content

    if (re.compile('Ministeri [AÅ] ?[1\|lI] ?h?').match(role) and re.compile('h?[o0]$').match(last)):
        rows[i][first_ix], rows[i][last_ix], rows[i][role_ix] = 'Arja', 'Alho', 'Ministeri'

    if (last == 'Ed, K u is m' and year > 1936):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Risto', 'Kuisma', 'SDP'

    if 'Ministeri Siim' in role:
        rows[i][first_ix], rows[i][last_ix], rows[i][role_ix] = 'Suvi-Anne', 'Siimes', 'Ministeri'

    if last.endswith('(jatkaa)') or last.endswith('(jatkuu)'):
        rows[i][last_ix] = last.partition('(jatk')[0]

    if (role == 'Rouva' and last == 'Rehn' and speech_id.startswith('1994')):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Sulo', 'Aittoniemi', 'KESK'
        rows[i][content_ix] = 'Rouva puhemies! Aivan oikein, ministeri Rehn:' + \
            rows[i][content_ix]

    if 'puheenvuoro)' in last or 'puheenvuoto)' in last:
        rows[i][last_ix] = last.partition('(')[0]
        rows[i][speech_type_ix] = 'Vastauspuheenvuoro'

    if role == 'Ed. Björkenheimin ehdotus ”jaa”, ed. Kaup- Puhemies':
        rows[i][role_ix] = 'Puhemies'
        rows[i][content_ix] = 'Ed. Björkenheimin ehdotus ”jaa”, ed. Kauppisen ehdotus ”ei”. Päiväjärjestyksestä poistetaan 2) asia.'

    if 'Isohookana-Asunmaa(vas-<REMOVE>' in last:
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Tytti', 'Isohookana-Asunmaa', 'KESK'
        rows[i][speech_type_ix] = 'Vastauspuheenvuoro'

    if re.compile('Anna-?[lL]ii?saJokinen').match(last):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Anna-Liisa', 'Jokinen', 'SKDL'

    if re.compile("Proc[oa]['im]?p?[e&ä6öé]?6?ö?").match(last):
        rows[i][last_ix] = 'Procopé'

    if re.compile("Hom[e\&6ö]ö?[ö6]?n").match(last):
        rows[i][last_ix] = 'Homén'

    if last in ['Tiutri', 'Tiut!i', 'Tturi', 'Tiurti', 'Tiuti', 'Tiufi', 'Tiufti']:
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Martti', 'Tiuri', 'KOK'

    if re.search('V[\.,] ?A[\.,] ?Virtanen', original_speaker_layout):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = "Viljo", 'Virtanen', 'SDP'

    if re.search('V[\.,] ?R[\.,] ?Virtanen', original_speaker_layout):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = "Väinö", 'Virtanen', 'SKDL'

    if re.search('V[\.,] ?J[\.,] ?Rytkönen', original_speaker_layout):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = "Veikko J.", 'Rytkönen', 'SKDL'

    if re.search('V[\.,] ?I[\.,] ?Rytkönen', original_speaker_layout):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = "Veikko", 'Rytkönen', 'SKDL'

    if (year not in [1970, 1971] and last == 'Laine' and first in ['FE', 'EF', 'F']):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Ensio', 'Laine', 'SKDL'

    if (last == 'Lahtela' and first in ['F', 'EF', 'FE']):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Esa', 'Lahtela', 'SDP'

    if 'Ed. ' in first:
        rows[i][first_ix] = first.replace('Ed. ', '')

    if (year > 1990 and last in ['Ojala', '0jala'] and first in ['O', '0', 'O0']):
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Outi', 'Ojala', 'VAS'

    if last in ['R00s', 'Ro0s', 'R0os', 'R008', 'R005', 'Ro0os']:
        if first == 'T':
            rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Timo', 'Roos', 'SDP'
        elif first == 'J':
            rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Jukka', 'Roos', 'SDP'

    if int(year) < 1920:  # fix incorrect years (due to lack of years in titles)
        if re.search('19[01]\d\-12\-\d\d', date) and not following_year:
            following_year = True
        if not re.search('19[01]\d\-12\-\d\d', date) and following_year:
            rows[i][date_ix] = str(int(date[:4])+1)+date[4:]

    if first == 'SL' and last == 'Anttila':
        rows[i][first_ix] = 'Sirkka-Liisa'

    if first == 'J' and last == 'Partanen':
        rows[i][first_ix] = 'Eemil'

    # Closest match offers the wrong first option for these
    if last == 'Tivari':
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Ulpu', 'Iivari', 'SDP'

    if last == 'Aiho':
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Arja', 'Alho', 'SDP'

    if last == 'Palmen' and year < 1910:
        rows[i][first_ix], rows[i][last_ix], rows[i][party_ix] = 'Ernst', 'Palmén', 'SUOMALAINEN PUOLUE'

    ###

    if ('emilä' in last and 'Maa- ja metsäta' in role)\
            or ('lä' in last and 'Maa- ja metsätalousministeri H' in role):
        rows[i][first_ix], rows[i][last_ix], rows[i][role_ix] = 'Kalevi', 'Hemilä', 'Maa- ja metsätalousministeri'

    if (last == 'Pura' and 'Maa- ja metsätalousministeri' in role) or (last == 'a' and role == 'Maa- ja metsätalousministeri Pur'):
        rows[i][first_ix], rows[i][last_ix], rows[i][role_ix] = 'Martti', 'Pura', 'Maa- ja metsätalousministeri'

    # Actual name in start of the speech
    if last in ['Ed', 'Fd'] and ':' in rows[i][content_ix]:
        x = rows[i][content_ix].split(':', 1)
        if '.' in x[0]:
            y = x[0].rsplit('.', 1)
            rows[i][first_ix] = y[0].strip()
            rows[i][last_ix] = y[1].strip()
        else:
            rows[i][last_ix] = x[0].strip()
        rows[i][content_ix] = x[1].strip()

    if 'puheenvuoro)' in rows[i][last_ix] or 'puheenvuoto)' in rows[i][last_ix]:
        rows[i][last_ix] = rows[i][last_ix].partition('(')[0]
        rows[i][speech_type_ix] = 'Vastauspuheenvuoro'

    new.append(rows[i])

with open('speeches_{}.csv'.format(sys.argv[1]), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerow(headers)
    writer.writerows(new)
print(len(new))
