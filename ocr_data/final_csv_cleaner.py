import csv
import re
import sys
import difflib

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

with open('speeches_{}.csv'.format(year), newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    rows = list(reader)
with open('backups/speeches_{}_BAK.csv'.format(year), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerows(rows)
print(len(rows))
print('>Rows attached to previous ones, fixing cases where one speech was erroneously split:\n***')
new = []
# to follow when year changes in document that didn't mark years in titles
following_year = False

for i in range(len(rows)):
    speech_id = rows[i][0]
    first = rows[i][5]
    last = rows[i][6]
    party = rows[i][7]
    topic = rows[i][8]
    content = rows[i][9]
    reply = rows[i][10]
    year = speech_id.partition('_')[0]
    date = rows[i][2]
    original_speaker_layout = rows[i][15]

    year = int(re.sub('_(II|XX)', '', year))

    rows[i][6] = last.strip('—')

    # Could use endswith('lle), but sometimes it in the middle ('Ahollevielä') and there are names like 'Helle'
    # or could be a weird name split

    if re.search('kysy|totesi|puhu|sano|esille|olisi|myös|vielä|aloite|jatk(oi|aa)|kaikella', last, flags=re.I)\
            or re.search('asiasta|esit|haukkui|totea|lausu|minä|sitaatti|ryhmästä|myös|tä(äll|m)ä|tieduste|luki|ehdot|vasta(ta|si|uk)|,joka', last, flags=re.I)\
            or re.search('sijaan ed|puheet|käsittel|pohti|keskustel|ym,|kuuluva', last, flags=re.I)\
            or re.search('kysy|totesi|puhu|sano|esille|olisi|vielä|relle|jatk(oi|aa)|lälle|osoitti|miel(es)?tä|sitten', party, flags=re.I)\
            or re.search('ilmoitti|viittasi|tiedustel|lausu|totea|sitaatti|pyytäisin|edelleen|epäili|ym,|lopuksi|vastasi', party, flags=re.I)\
            or re.search('\d+ ?\$', last)\
            or (last.endswith('lle') and not exception_name(last, 1))\
            or (last.endswith('lta') and not exception_name(last, 2)) or last.endswith('ltä')\
            or (last.endswith('sta') and not last.endswith('ntausta')) or last.endswith('stä')\
            or ('puheenvuoro' in last and not ')' in last) or 'uskokaa' in party\
            or 'lyhyesti' in last or 'näki' in last\
            or 'Aittoniemitäällänosti88' in last or 'lopuksi' in last\
            or ',että' in last or 'asiaan' in last\
            or 'Koskinenjatkaa' in last or 'hallitusmuodon' in last\
            or 'Kyllä on ihan niin, kuin ministeri Alho' in party\
            or 'aloittee' in last or 'mainits' in last or 'tämä' in party\
            or 'RäsänenottiesiinValtatie10' in last or 'kuunnelkaa' in last\
            or 'Ministeri Niinistö, te olette' in party or 'esiintyi' in party\
            or 'Alarannalleperehtymisestä' in last\
            or 'luomutuotannosta' in last or 'kommente' in last\
            or 'Raskhuomioi' in last or 'tosiasia' in last\
            or ('kanta' in last and not last == 'Hirvikanta')\
            or 'tunnustusta' in last or 'puolesta' in party \
            or ('sitä' in last and not 'Uusitälo' in last) \
            or 'Kun ministeri Pekkala' in party\
            or 'Paloheimonosalta' in last or 'oikeassa' in last\
            or 'hyväksytään' in party or 'Arvoisa' in party or 'arvosteli' in last\
            or 'kiinnitti' in last or 'kritisoi' in party or ' oli' in party or 'ponteen' in last\
            or 'maininnut' in last or 'oikein' in last or 'viittasi' in last or 'kehyskunnis' in last\
            or 'ilmeisesti' in last or 'taisiolla' in last or 'syyt' in party\
            or 'onsiis' in last or 'yritti' in last or 'tekemä' in last\
            or 'kanssa' in last or 'lainasi' in last or 'Suomisenpuhe' in last\
            or 'Katsooko' in party or 'huomaut' in last or 'jamuut' in last \
            or '-asia' in last or 'Leppänen on' in party or 'päätään' in last or 'puuttui' in last\
            or 'ei ole' in party or 'perustel' in last\
            or 'Sorsan ja' in party or 'todennut' in party or 'niinhyvä' in last or 'kannatta' in last\
            or '(Eduskunnasta' in last or 'Törnqvistille' in last\
            or (last == 'Eklund' and content.startswith(' Salailu ei auta!)')):

        print(party, last)
        if not party.strip().isupper():
            rows[i-1][9] += ' ' + ' '.join([party, last+':', content])
        else:
            rows[i-1][9] += ' ' + ' '.join([last+':', content])

        rows[i-1][9] = rows[i-1][9].replace('-<REMOVE> ', '')
        continue

    if 'Karhunen lähti pois, (Ed' in first or 'Jaakonsaaten välihuuto' in first:
        rows[i-1][9] += ' ' + ' '.join([first, last+':', content])
        continue

    if 'ministeti' or 'Ministeti' in party:
        rows[i][7] == party.replace('inisteti', 'inisteri')
        party = rows[i][7]

    if (first == 'Kettunen (Ed' and last == 'Helminen'):
        rows[i][5], rows[i][6], rows[i][7] = 'Pentti', 'Kettunen', 'PS'
        rows[i][9] = ' (Ed. Helminen: ' + content

    if (re.compile('Ministeri [AÅ] ?[1\|lI] ?h?').match(party) and re.compile('h?[o0]$').match(last)):
        rows[i][5], rows[i][6], rows[i][7] = 'Arja', 'Alho', 'Ministeri'

    if last in ['FEIo', 'E10o', 'E|o', 'F1o', 'E1lo', 'EI1o']:
        rows[i][5], rows[i][6], rows[i][7] = 'Mikko', 'Elo', 'SDP'

    if (last == 'Ed, K u is m' and year > 1936):
        rows[i][5], rows[i][6], rows[i][7] = 'Risto', 'Kuisma', 'SDP'

    if ('Ministeri N' in party and 'back' in last):
        rows[i][5], rows[i][6], rows[i][7] = 'Ole', 'Norrback', 'Ministeri'

    if 'Ministeri Siim' in party:
        rows[i][5], rows[i][6], rows[i][7] = 'Suvi-Anne', 'Siimes', 'Ministeri'

    if 'Pääministeri A h' in party or 'Pääministeri Ah' in party:
        rows[i][5], rows[i][6], rows[i][7] = 'Esko', 'Aho', 'Pääministeri'

    if last.endswith('(jatkaa)') or last.endswith('(jatkuu)'):
        rows[i][6] = last.partition('(jatk')[0]

    if last in ['Linden', 'Lindön', 'Lind6n']:
        if 'Kulttuuriministeri' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Suvi', 'Lindén', 'Kulttuuriministeri'
        else:
            rows[i][5], rows[i][6], rows[i][7] = 'Suvi', 'Lindén', 'KOK'

    if (('teollisuusministeri T' in party or 'teollisuusministeriT' in party) and last.endswith('ja')):
        rows[i][5], rows[i][6], rows[i][7] = 'Erkki', 'Tuomioja', 'Kauppa- ja teollisuusministeri'

    if (party == 'Rouva' and last == 'Rehn' and speech_id.startswith('1994')):
        rows[i][5], rows[i][6], rows[i][7] = 'Sulo', 'Aittoniemi', 'KESK'
        rows[i][9] = 'Rouva puhemies! Aivan oikein, ministeri Rehn:' + rows[i][9]

    if 'puheenvuoro)' in last or 'puheenvuoto)' in last:
        rows[i][6] = last.partition('(')[0]
        rows[i][10] = 'Vastauspuheenvuoro'

    if party == 'Ed. Björkenheimin ehdotus ”jaa”, ed. Kaup- Puhemies':
        rows[i][7] = 'Puhemies'
        rows[i][9] = 'Ed. Björkenheimin ehdotus ”jaa”, ed. Kauppisen ehdotus ”ei”. Päiväjärjestyksestä poistetaan 2) asia.'

    if 'Isohookana-Asunmaa(vas-<REMOVE>' in last:
        rows[i][5], rows[i][6], rows[i][7] = 'Tytti', 'Isohookana-Asunmaa', 'KESK'
        rows[i][10] = 'Vastauspuheenvuoro'

    if (('Yläjätvi' in last or 'Yläjärtvi' in last) and 'metsätalousministeri' in party):
        rows[i][5], rows[i][6], rows[i][7] = 'Toivo', 'Yläjärvi', 'Maa- ja metsätalousministeri'

    if re.compile('Anna-?[lL]ii?saJokinen').match(last):
        rows[i][5], rows[i][6], rows[i][7] = 'Anna-Liisa', 'Jokinen', 'SKDL'

    if re.compile("Proc[oa]['im]?p?[e&ä6öé]?6?ö?").match(last):
        rows[i][6] = 'Procopé'

    if re.compile("Hom[e\&6ö]ö?[ö6]?n").match(last):
        rows[i][6] = 'Homén'

    # if last == 'AilaJokinen':
    #    rows[i][5], rows[i][6], rows[i][7] = 'Aila', 'Jokinen', 'KOK'

    if last in ['Tiutri', 'Tiut!i', 'Tturi', 'Tiurti', 'Tiuti', 'Tiufi', 'Tiufti']:
        rows[i][5], rows[i][6], rows[i][7] = 'Martti', 'Tiuri', 'KOK'

    if re.search('V[\.,] ?A[\.,] ?Virtanen', original_speaker_layout):
        rows[i][5], rows[i][6], rows[i][7] = "Viljo", 'Virtanen', 'SDP'

    if re.search('V[\.,] ?R[\.,] ?Virtanen', original_speaker_layout):
        rows[i][5], rows[i][6], rows[i][7] = "Väinö", 'Virtanen', 'SKDL'

    if re.search('V[\.,] ?J[\.,] ?Rytkönen', original_speaker_layout):
        rows[i][5], rows[i][6], rows[i][7] = "Veikko J.", 'Rytkönen', 'SKDL'

    if re.search('V[\.,] ?I[\.,] ?Rytkönen', original_speaker_layout):
        rows[i][5], rows[i][6], rows[i][7] = "Veikko", 'Rytkönen', 'SKDL'

    if (year not in [1970, 1971] and last == 'Laine' and first in ['FE', 'EF', 'F']):
        rows[i][5], rows[i][6], rows[i][7] = 'Ensio', 'Laine', 'SKDL'

    if (last == 'Lahtela' and first in ['F', 'EF', 'FE']):
        rows[i][5], rows[i][6], rows[i][7] = 'Esa', 'Lahtela', 'SDP'

    if 'Ed. ' in first:
        rows[i][5] = first.replace('Ed. ', '')

    if (year > 1990 and last in ['Ojala', '0jala'] and first in ['O', '0', 'O0']):
        rows[i][5], rows[i][6], rows[i][7] = 'Outi', 'Ojala', 'VAS'

    if last in ['R00s', 'Ro0s', 'R0os', 'R008', 'R005', 'Ro0os']:
        if first == 'T':
            rows[i][5], rows[i][6], rows[i][7] = 'Timo', 'Roos', 'SDP'
        elif first == 'J':
            rows[i][5], rows[i][6], rows[i][7] = 'Jukka', 'Roos', 'SDP'

    if (last in ['Ollila', 'Oilila', 'Oliila', 'Olliia'] and ('Valtiovarainmi' in party or 'teollisuusministe' in party)):
        if 'Valtiovarainmi' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Esko', 'Ollila', 'Valtiovarainministeri'
        elif 'teollisuusministe' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Esko', 'Ollila', 'Kauppa- ja teollisuusministeri'

    if (last in ['Jämsén', 'Jamsen', 'Jämsen', 'Jämsän', 'Jämsö&n', 'Jäms&n', 'Jämsän'] and 'iniste' in party):
        rows[i][5], rows[i][6] = 'Artturi', 'Jämsén'

    # if last in ['Nederström-Lundön', 'Nederström-Lunden', 'Nederström-Lundän', 'Nederström-Lundäön',
    #            'Nederström-Lund6&n', 'Nederström-Lundäön', 'Nederström-Lund&ö&n', 'Nederström-Lund6n']:
    #    rows[i][5], rows[i][6], rows[i][7] = 'Judit', 'Nederström-Lundén', 'SKDL'

    if int(year) < 1920:  # fix incorrect years (due to lack of years in titles)
        if re.search('19[01]\d\-12\-\d\d', date) and not following_year:
            following_year = True
        if not re.search('19[01]\d\-12\-\d\d', date) and following_year:
            rows[i][2] = str(int(date[:4])+1)+date[4:]

    if party == '-Ikäpuhemies':
        rows[i][7] = 'Ikäpuhemies'

    if first == 'SL' and last == 'Anttila':
        rows[i][5] = 'Sirkka-Liisa'

    if first == 'J' and last == 'Partanen':
        rows[i][5] = 'Eemil'

    # Closest match offers the wrong first option for these
    if last == 'Tivari':
        rows[i][5], rows[i][6], rows[i][7] = 'Ulpu', 'Iivari', 'SDP'

    if last == 'Aiho':
        rows[i][5], rows[i][6], rows[i][7] = 'Arja', 'Alho', 'SDP'

    if last == 'Palmen' and year < 1910:
        rows[i][5], rows[i][6], rows[i][7] = 'Ernst', 'Palmén', 'SUOMALAINEN PUOLUE'

    #########
    # Non-MP Ministers
    ########

    if ('Pohjala' in last and 'metsätalousministeri' in party and not first):
        rows[i][5], rows[i][6], rows[i][7] = 'Toivo T.', 'Pohjala', 'Maa- ja metsätalousministeri'

    if ('emilä' in last and 'Maa- ja metsäta' in party)\
            or ('lä' in last and 'Maa- ja metsätalousministeri H' in party):
        rows[i][5], rows[i][6], rows[i][7] = 'Kalevi', 'Hemilä', 'Maa- ja metsätalousministeri'

    if('Oikeusminis' in party and last == 'Simonen'):
        rows[i][5], rows[i][7] = 'Aarre', 'Oikeusministeri'

    if(last == 'Jansson' and 'Kauppa- ja teollisuusministe' in party):
        rows[i][5], rows[i][7] = 'Jan-Magnus', 'Kauppa- ja teollisuusministeri'

    if(last == 'Linnamo' and 'iniste' in party):
        rows[i][5] = 'Jussi'

    if re.compile('L[åä]ng').match(last) and 'Oikeusminis' in party:
        rows[i][5], rows[i][6], rows[i][7] = 'K.', 'Lång', 'Oikeusministeri'

    if (last == 'Berner' and 'teollisuusminis' in party and year < 1980):
        rows[i][5], rows[i][6], rows[i][7] = 'Arne', 'Berner', 'Kauppa- ja teollisuusministeri'

        rows[i][5], rows[i][6], rows[i][7] = 'Johannes', 'Koikkalainen', 'Ministeri'

    if (last == 'Pura' and 'Maa- ja metsätalousministeri' in party) or (last == 'a' and party == 'Maa- ja metsätalousministeri Pur'):
        rows[i][5], rows[i][6], rows[i][7] = 'Martti', 'Pura', 'Maa- ja metsätalousministeri'

    # Actual name in start of the speech
    if last in ['Ed', 'Fd'] and ':' in rows[i][9]:
        # print('{}|{}|{}|{}'.format(
        #    rows[i][5], rows[i][6], rows[i][7], rows[i][9][:30]))
        x = rows[i][9].split(':', 1)
        if '.' in x[0]:
            y = x[0].rsplit('.', 1)
            rows[i][5] = y[0].strip()
            rows[i][6] = y[1].strip()
        else:
            rows[i][6] = x[0].strip()
        rows[i][9] = x[1].strip()
        # print('**')

    new.append(rows[i])

with open('speeches_{}.csv'.format(sys.argv[1]), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerows(new)
print(len(new))
