import csv
import re
import sys

#######################################################
# Script to fix issues that have survived or emerged  #
# from the process, such as splitted speeches         #
#######################################################


year = sys.argv[1]
csv.field_size_limit(sys.maxsize)

with open('speeches_{}.csv'.format(year), newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    rows = list(reader)
with open('speeches_{}_BAK.csv'.format(year), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerows(rows)
print(len(rows))
print('>Rows attached to previous ones, fixing cases where one speech was erroneously split:\n***')
new = []


for i in range(len(rows)):
    speech_id = rows[i][0]
    first = rows[i][5]
    last = rows[i][6]
    party = rows[i][7]
    topic = rows[i][8]
    content = rows[i][9]
    reply = rows[i][10]
    year = int(speech_id.partition('.')[0])
    original_speaker_layout = rows[i][15]

    if year < 2000:
        rows[i][6] = last.strip('—')
        # Could use endswith('lle), but sometimes it in the middle ('Ahollevielä') and there are names like 'Helle'
        # or could be a weird name split
        if 'Kysy' in party or 'kysy' in party or 'totesi' in party\
                or 'totesi' in last or 'puhui' in party or 'vielä' in last\
                or 'ilmoitti' in party or 'vielä' in party or 'Vielä' in party\
                or 'kysy' in last or 'aloite' in last or 'puhui' in last\
                or 'asiasta' in last or 'esit' in last or 'viittasi' in party\
                or ('puheenvuoro' in last and not ')' in last) or 'iedustel' in party\
                or 'sano' in party or 'Kun' in party or 'haukkui' in last\
                or 'sano' in last or 'totea' in last or 'lausu' in last\
                or 'Totean' in party or 'totea' in party or 'uskokaa' in party\
                or 'lyhyesti' in last or 'käsitteli' in last or 'näki' in last\
                or ',kaikellaystävyydellä' in last or 'Rehnille' in last\
                or 'Aittoniemitäällänosti88' in last or 'ehdotu' in last\
                or 'Saapungille' in last or 'Backmanille' in last or 'minä' in last\
                or 'jatkoi' in party or 'Koskelle' in last or 'jatkoi' in last\
                or 'Vihriälälle' in last or 'keskustelu' in last\
                or 'Laaksolle' in last or 'Mölsälle' in last or 'maalle' in last\
                or 'relle' in party or 'kuuluva' in last\
                or 'mieltä' in last or 'mieltä' in party or ',että' in last or 'asiaan' in last\
                or 'Koskinenjatkaa' in last or 'hallitusmuodon' in last\
                or 'Alholle' in last or 'teelle' in last or 'tolle' in last\
                or 'Kyllä on ihan niin, kuin ministeri Alho' in party\
                or 'aloittee' in last or 'mainits' in last or 'tämä' in party\
                or 'RäsänenottiesiinValtatie10' in last or 'Tiurille' in last\
                or 'Ala-Harjalle' in last or 'talolle' in last\
                or 'Nurmelle' in last or 'niemelle' in last\
                or 'Enestamille' in last or 'kuunnelkaa' in last\
                or 'epäili' in party or 'olisi' in last or 'olisi' in first\
                or 'Ministeri Niinistö, te olette' in party\
                or 'Kuismalle' in last or 'esit' in party or 'koskelle' in last\
                or 'sitaatti' in party or 'Sitaatti' in last\
                or 'Tuomiojajatkaa' in last or 'Hassille' in last\
                or 'esille' in party or 'ryhmästä' in last\
                or 'esille' in last or 'Alarannalleperehtymisestä' in last\
                or 'Soininvaaralle' in last or 'Saariselle' in last\
                or 'luomutuotannosta' in last or 'kommente' in last\
                or 'Raskhuomioi' in last or 'tosiasia' in last\
                or 'Asunaalle' in last or 'lälle' in party or 'pohti' in last\
                or 'Joenpalolle' in last or 'Niinistölle' in last\
                or 'Nissilälle' in last or 'vastasi' in party or 'Harjalle' in last\
                or 'ojalle' in last or 'Hemilälle' in last or 'kanta' in last or 'mäelle' in last\
                or 'myös' in last or 'Perholle' in last or 'dahlille' in last\
                or 'tieduste' in last or ('sitä' in last and not 'Uusitälo' in last) or 'vastasi' in last\
                or 'täällä' in last or 'Antvuorelle' in last or 'mille' in last\
                or 'Laxille' in last or 'sälälle' in last or 'lalle' in last\
                or 'Paloheimonosalta' in last or 'backalle' in last\
                or 'osoitti' in party or 'esitell' in last or 'selle' in last\
                or 'Myllerille' in last or 'Rengolle' in last or 'oikeassa' in last\
                or 'hyväksytään' in party or 'Arvoisa' in party or 'arvosteli' in last\
                or 'kiinnitti' in last or 'kritisoi' in party or ' oli' in party\
                or 'luki' in last or 'ponteen' in last or 'rille' in last\
                or 'maininnut' in last or 'oikein' in last or 'viittasi' in last\
                or 'puheet' in last or 'Tainalle' in last or 'molle' in last\
                or 'kehyskunnis' in last or 'Aholle' in last or 'Pyytäisin' in party\
                or 'ilmeisesti' in last or 'taisiolla' in last or 'syyt' in party\
                or 'onsiis' in last or 'yritti' in last or 'tekemä' in last\
                or 'kanssa' in last or 'lainasi' in last or 'Suomisenpuhe' in last\
                or 'Katsooko' in party or 'huomaut' in last or 'jamuut' in last \
                or '-asia' in last or 'tämä' in last or 'Leppänen on' in party\
                or 'päätään' in last or 'Vainiolle' in last or 'puuttui' in last\
                or 'vastauks' in party or 'ei ole' in party or 'kaikella' in last\
                or 'edelleen' in party or 'mielestä' in party or 'perustel' in last\
                or 'Sorsan ja' in party or 'vastata' in last or 'todennut' in party \
                or 'niinhyvä' in last or 'kannatta' in last or 'ehdotus' in last\
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

        if (first == 'Kettunen (Ed' and last == 'Helminen'):
            rows[i][5], rows[i][6], rows[i][7] = 'Pentti', 'Kettunen', 'PS'
            rows[i][9] = ' (Ed. Helminen: ' + content

        if ('emilä' in last and 'Maa- ja metsätalousministeri' in party)\
                or ('lä' in last and 'Maa- ja metsätalousministeri H' in party):
            rows[i][5], rows[i][6], rows[i][7] = 'Kalevi', 'Hemilä', 'Maa- ja metsätalousministeri'

        if 'Ministeri A 1 h' in party or 'Ministeri A | h' in party\
                or 'Ministeri A1h' in party \
                or (('Ministeri Alh' in party or 'Ministeri A I h' in party) and (last == 'o'
                                                                                  or last == '0')):
            rows[i][5], rows[i][6], rows[i][7] = 'Arja', 'Alho', 'Ministeri'

        if last == 'E10o' or last == 'E|o' or last == 'F1o' or last == 'E1lo':
            rows[i][5], rows[i][6], rows[i][7] = 'Mikko', 'Elo', 'SDP'

        if ('terveysministeri M' in party and 'önkäre' in last)\
                or ('terveysministeri M ö n k ä' in party and last.strip() == 'e'):
            rows[i][5], rows[i][6], rows[i][7] = 'Sinikka', 'Mönkäre', 'Sosiaali- ja terveysministeri'

        if 'Työministeri M' in party and 'önkäre' in last:
            rows[i][5], rows[i][6], rows[i][7] = 'Sinikka', 'Mönkäre', 'Työministeri'

        if 'TyöministeriJaakonsaari' in last:
            rows[i][6], rows[i][7] = 'Jaakonsaari', 'Työministeri'

        if 'JAndersson' in last:
            rows[i][5], rows[i][6], rows[i][7] = 'Janina', 'Andersson', 'VIHR'

        if (last.strip() == 'Mö1sä' and year < 2004):
            rows[i][5], rows[i][6], rows[i][7] = 'Tero', 'Mölsä', 'KESK'

        if last.strip() == 'PääministeriLipponen':
            rows[i][5], rows[i][6], rows[i][7] = 'Paavo', 'Lipponen', 'Pääministeri'

        if (last == 'Ed, K u is m' and year > 1936):
            rows[i][5], rows[i][6], rows[i][7] = 'Risto', 'Kuisma', 'SDP'

        if ('Ministeri N' in party and 'back' in last):
            rows[i][5], rows[i][6], rows[i][7] = 'Ole', 'Norrback', 'Ministeri'

        if last == 'Pohjoia' and first == 'T':
            rows[i][5], rows[i][6], rows[i][7] = 'Tuija', 'Pohjola', 'SDP'

        if last == 'LiikenneministeriLinnainmaa':
            rows[i][6], rows[i][7] = 'Linnainmaa', 'Liikenneministeri'

        if last == 'JohannesKoskinen':
            rows[i][5], rows[i][6], rows[i][7] = 'Johannes', 'Koskinen', 'SDP'

        if last == 'JariKoskinen':
            rows[i][5], rows[i][6], rows[i][7] = 'Jari', 'Koskinen', 'KOK'

        if last == 'RKorhonen':
            rows[i][5], rows[i][6], rows[i][7] = 'Riitta', 'Korhonen', 'KOK'

        if (party == 'Liikenneministeri A' and last == 'ura')\
                or party == 'Liikenneministeri A ur':
            rows[i][5], rows[i][6], rows[i][7] = 'Matti', 'Aura', 'Liikenneministeri'

        if last == 'JKukkonen':
            rows[i][6] = 'Kukkonen'

        if ('Sisäasiainministeri E' in party and last.strip().endswith('m')):
            rows[i][5], rows[i][6], rows[i][7] = 'Jan-Erik', 'Enestam', 'Sisäasiainministeri'

        if ('Puolustusministeri E' in party and last.strip().endswith('m')):
            rows[i][5], rows[i][6], rows[i][7] = 'Jan-Erik', 'Enestam', 'Puolustusministeri'

        if 'Ministeri Siim' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Suvi-Anne', 'Siimes', 'Ministeri'

        if last.endswith('(jatkaa)') or last.endswith('(jatkuu)'):
            rows[i][6] = last.partition('(jatk')[0]

        if 'terveysministeri P e r h' in party or 'Sosiaali- ja terveysministeri P er h' in party\
                or 'terveysministeri Per ' in party or 'terveysministeri P  r h' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Maija', 'Perho', 'Sosiaali- ja terveysministeri'

        if 'Opetusministeri R a s' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Maija', 'Rask', 'Opetusministeri'

        if 'Ulkomaankauppaministeri S a' in party and last == 'si':
            rows[i][5], rows[i][6], rows[i][7] = 'Kimmo', 'Sasi', 'Ulkomaankauppaministeri'

        if ('Kulttuuriministeri Lin' in party and last.endswith('n'))\
                or last == 'Linden':
            rows[i][5], rows[i][6], rows[i][7] = 'Suvi', 'Lindén', 'Kulttuuriministeri'

        if (('teollisuusministeri T' in party or 'teollisuusministeriT' in party) and last.endswith('ja')):
            rows[i][5], rows[i][6], rows[i][7] = 'Erkki', 'Tuomioja', 'Kauppa- ja teollisuusministeri'

        if last == 'Vilen' and not first:
            rows[i][5], rows[i][6], rows[i][7] = 'Jari', 'Vilén', 'KOK'

        if last == 'Markkula-Kivisilta':
            rows[i][5], rows[i][6], rows[i][7] = 'Hanna', 'Markkula-Kivisilta', 'KOK'

        if (party == 'Rouva' and last == 'Rehn' and speech_id.startswith('1994')):
            rows[i][5], rows[i][6], rows[i][7] = 'Sulo', 'Aittoniemi', 'KESK'
            rows[i][9] = 'Rouva puhemies! Aivan oikein, ministeri Rehn:' + rows[i][9]

        if 'puheenvuoro)' in last or 'puheenvuoto)' in last:
            rows[i][6] = last.partition('(')[0]
            rows[i][10] = 'Vastauspuheenvuoro'

        if party == 'Ed. Björkenheimin ehdotus ”jaa”, ed. Kaup- Puhemies':
            rows[i][7] = 'Puhemies'
            rows[i][9] = 'Ed. Björkenheimin ehdotus ”jaa”, ed. Kauppisen ehdotus ”ei”. Päiväjärjestyksestä poistetaan 2) asia.'

        if 'Pääministeri A h' in party or 'Pääministeri Ah' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Esko', 'Aho', 'Pääministeri'

        if 'Sisäasiainministeri P e k k a rin' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Mauri', 'Pekkarinen', 'Sisäasiainministeri'

        if 'Opetusministeri U' in party and last.endswith('nen'):
            rows[i][5], rows[i][6], rows[i][7] = 'Riitta', 'Uosukainen', 'Opetusministeri'

        if 'Wahiström' in last:
            rows[i][5], rows[i][6], rows[i][7] = 'Jarmo', 'Wahlström', 'SKDL'

        if 'Tsohookana-Asunmaa' in last:
            rows[i][5], rows[i][6], rows[i][7] = 'Tytti', 'Isohookana-Asunmaa', 'KESK'

        if 'Isohookana-Asunmaa(vas-<REMOVE>' in last:
            rows[i][5], rows[i][6], rows[i][7] = 'Tytti', 'Isohookana-Asunmaa', 'KESK'
            rows[i][10] = 'Vastauspuheenvuoro'

        if 'Yläjätvi' in last or 'Yläjärtvi' in last:
            rows[i][5], rows[i][6], rows[i][7] = 'Toivo', 'Yläjärvi', 'Maa- ja metsätalousministeri'

        if last == 'Anna-LiisaJokinen' or last == 'Anna-LisaJokinen':
            rows[i][5], rows[i][6], rows[i][7] = 'Anna-Liisa', 'Jokinen', 'SKDL'

        if last == 'AilaJokinen':
            rows[i][5], rows[i][6], rows[i][7] = 'Aila', 'Jokinen', 'KOK'

        if (last == 'Ollila' and party == 'Valtiovarainministeri'):
            rows[i][5], rows[i][6], rows[i][7] = 'Esko', 'Ollila', 'Valtiovarainministeri'

        if last in ['Tiutri', 'Tiut!i', 'Tturi', 'Tiurti', 'Tiuti', 'Tiufi', 'Tiufti']:
            rows[i][5], rows[i][6], rows[i][7] = 'Martti', 'Tiuri', 'KOK'

        if ('Kauppa- ja teollisuusministeri Lind' in party and last.endswith('blom')):
            rows[i][5], rows[i][6], rows[i][7] = 'Seppo', 'Lindblom', 'Kauppa- ja teollisuusministeri'

        if 'Sosiaali- ja terveysministeri Kuusko ski' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Eeva', 'Kuuskoski', 'Sosiaali- ja terveysministeri'

        if 'Oikeusministeri T a x' in party or 'Oikeusministeri T ax' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Christoffer', 'Taxell', 'Oikeusministeri'

        if 'Ympäristöministeri A h d' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Matti', 'Ahde', 'Ympäristöministeri'

        if 'Maa- ja metsätalousministeri T äh k' in party:
            rows[i][5], rows[i][6], rows[i][7] = 'Taisto', 'Tähkämaa', 'Maa- ja metsätalousministeri'

        if ('Maatalousministeri' in party and 'Westerma' in last):
            rows[i][5], rows[i][6], rows[i][7] = 'Nils', 'Westermarck', 'Maatalousministeri'

        if ('Opetusministeri' in party and 'Numminen' in last):
            rows[i][5], rows[i][6], rows[i][7] = 'Jaakko', 'Numminen', 'Opetusministeri'

        if last == 'Jämsen' or last == 'Jämsön':
            rows[i][5], rows[i][6], rows[i][7] = 'Artturi', 'Jämsén', 'KESK'

        if re.search('V[\.,] ?A[\.,] ?Virtanen', original_speaker_layout):
            rows[i][5], rows[i][6], rows[i][7] = "Viljo", 'Virtanen', 'SDP'

        if re.search('V[\.,] ?R[\.,] ?Virtanen', original_speaker_layout):
            rows[i][5], rows[i][6], rows[i][7] = "Väinö", 'Virtanen', 'SKDL'

        if re.search('V[\.,] ?J[\.,] ?Rytkönen', original_speaker_layout):
            rows[i][5], rows[i][6], rows[i][7] = "Veikko J.", 'Rytkönen', 'SKDL'

        if re.search('V[\.,] ?I[\.,] ?Rytkönen', original_speaker_layout):
            rows[i][5], rows[i][6], rows[i][7] = "Veikko", 'Rytkönen', 'SKDL'

        if last == 'Äsvik':
            rows[i][5], rows[i][6], rows[i][7] = "Toivo", 'Åsvik', 'SKDL'

    new.append(rows[i])

with open('speeches_{}.csv'.format(year), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerows(new)
print(len(new))
