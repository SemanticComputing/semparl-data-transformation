import re
import csv
import sys
from pprint import pprint

########################
# Script for 1989-1994 #
########################


def discussion_starters(row):
    if 'Keskustelu:' in row or 'Yleiskeskustelu:' in row or 'Keskustelu;' in row or 'Yleiskeskustelu;' in row:
        return True
    elif 'Keskustelu jatkuu' in row or 'Yleiskeskustelu jatkuu' in row:
        return True
    return False


def discussion_enders(row, row2):
    if 'Keskustelu julistetaan päättyneeksi.' in row or 'Yleiskeskustelu julistetaan päättyneeksi.' in row:
        return True
    if ('Keskustelu' in row and 'päättyneeksi.' in row2):
        return True
    return False


def question_starters(row):
    if (re.compile("\d+\) N:o \d+\/?\d*.* [A-ZÅÄÖ].*[:;]")).match(row):
        return True
    return False


def question_enders(row):
    if 'Asia on loppuun käsitelty.' in row or 'Asia on loppun käsitelty.' in row \
            or 'eskustelua ei synny.' in row:
        return True
    return False


def topic_starter(row):
    problem_rows = [
        '1) Työttömyysturvan peruspäivärahan ta-',
        '2) Eri sosiaalivakuutusjärjestelmien yh-',
        '3) Lasten kotihoidon tuen tasoa korote-',
        '4) Opintotukimenot —kaksinkertaistuvat',
        '5) Kunnallisessa toimeentulotuessa siirryt-',
        '1) Nivän pä grunddagpenningen inom',
        '2) Kompatibiliteten hos de olika socialför-',
        '3) Hemvärdsstödet för barn höjs väsentligt',
        '4) Utgifterna för studiestödet fördubblas',
        '5) Inom det kommunala utkomstskyddet',
        '4) Pääomien ja työvoiman vapaa liikkuvuus.',
        '3) Valtioiden välinen kauppa kontra itsekäs',
        '2) Tasapainoitettu kauppa. Suhteellisen edun',
        '6) Tahdommeko varsin vahvoja yhteisiä EU-',
        '1) Olemmeko kauppapolitiikassa vapaakau-',
        '2) Pitääkö maatalouden mielestämme olla',
        '3) Tuemmeko Keski- ja Itä-Euroopan maiden',
        '4) Haluammeko korkean ympäristönormita-',
        '5) Euroopan unioni antoi Maastrichtin sopi-',
        '1) Yksittäisten valtioiden tuotteiden ympäristö-',
        '2) Kuljetukset ja niihin liittyvä energian käyttö',
        '3) Tuotevirrat kasvavat voimakkaasti markki-',
        '4) Pääoma voi liikkua vapaasti koko EU:n'


    ]
    if 'Äänestys ed.' in row or row in problem_rows:
        return False
    # 7) N:o 61 Ed. Pulliainen: Asioiden käsittely
    topic = re.compile('^[0-9]+\) [A-ZÅÄÖ].*')
    interpellation = re.compile(
        '^[EF]d. [A-ZÅÄÖ].+ ym. välikysymys')  # välikysymys
    if topic.match(row) or interpellation.match(row):
        return True
    return False


def topic_enders(row, row2):
    if 'Valiokuntaan lähettäminen' in row or 'Puhetta johtaa' in row or 'käsittely' in row or 'uhemies:' in row\
            or 'Valjokuntaan lähettäminen' in row or 'Lähetekeskustelu' in row:
        return True
    if re.compile('lähetetään [a-zåäö]+neuvoston ehdotuksen').match(row):
        return True
    if speech_starters(row, row2):
        return True
    return False


def topic_details(row):
    proposal = re.compile('^Hallituksen esity(s|kset) n[;:]o')
    committee = re.compile(
        '^[A-ZÅÄÖ][a-zåäö \-]+valiokunnan mietin(nöt|tö) n[:;]o')
    iniative = re.compile('^[A-ZÅÄÖ][a-zåäö\-]+aloit(teet|e) n[;:]o')
    if proposal.match(row) or committee.match(row) or iniative.match(row) or 'Mainittu kertomus (K' in row:
        return True
    return False


def speech_starters(row, row2):
    speech_start = re.compile("^[E|F]d. [A-ZÅÄÖ].*[:;]")
    speech_start2 = re.compile("^[A-ZÅÄÖ].*iniste[tr]i [A-ZÅÄÖ].*[:;]")
    long_title = re.compile('^[A-ZÅÄÖ].*iniste[tr]i [A-ZÅÄÖ].*-$')
    long_title2 = re.compile('^[A-ZÅÄÖa-zåäö]+[;:]')
    two_lines1 = re.compile("^[E|F]d. [A-ZÅÄÖ].*\(va")
    two_lines2 = re.compile("[a-z]*ro\) ?:")
    chairman = re.compile(
        '(Ensimmäinen |Toinen )?(Puhemies|varapuhemies) ?(\(koputtaa\))? ?[;:]')
    chairman_knock = re.compile(
        '(Ensimmäinen |Toinen )?(Puhemies|varapuhemies) ?')
    chairman_knock2 = re.compile('taa\) ?[;:]')
    continuation = re.compile('^Puhuja ?[;:]')
    if speech_start.match(row) or speech_start2.match(row) \
            or chairman.match(row) or continuation.match(row)\
            or (chairman_knock.match(row) and chairman_knock2.match(row2))\
            or (two_lines1.match(row) and two_lines2.match(row2))\
            or (long_title.match(row) and long_title2.match(row2))\
            or 'Ikäpuhemies:' in row or '(vastauspuheenvuoro)' in row:
        return True
    return False


def document_start(row):
    # 5. Tiistaina 13 päivänä helmikuuta 1990
    if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p(\.|\-|äivänä) .*kuuta 19[89][0-9]').match(row):
        return True
    return False


def document_end(row, row2):
    if ('Täysistunto lopetetaan ' in row
            or 'Täysistunto keskeytetään ' in row):
        return True
    return False


def index_end(row):
    if re.compile('Puhetta johtaa( ensimmäinen| toinen)? (puhemies|varapuhemies)').match(row):
        return True
    if 'Päiväjärjestyksessä olevat asiat:' in row:
        return True
    return False


def closing_statement(row):
    if 'Eduskunnan seuraava ' in row:
        return True
    if re.compile('seuraava (varsinainen )?täysistunto').match(row):
        return True
    return False


def page_header(row):
    header = re.compile('\f')
    if header.match(row):
        return True
    return False


def acceptance(row):
    if 'Selonteko myönnetään oikeaksi.' in row or 'Menettelytapa hyväksytään.' in row \
            or 'Eduskunta on hyväksynyt mietinnön.' in row \
            or 'Eduskunta on käsittelyn pohjaksi hy' in row:
        return True
    return False


def get_speaker(all_):
    if ('(vastauspuheenvuoro)' in all_ and not 'vuoro):' in all_ and not 'vuoro);' in all_
            and not 'vuoro) :' in all_ and not 'vuoro) ;' in all_):
        all_ = all_.replace('vuoro)', 'vuoro):', 1)
    parts = re.split(':|;', all_, maxsplit=1)
    if len(parts) > 1:
        return parts[0], parts[1]
    return ' ', parts[0]


def session_details(row, parliament_year):
    # 145. Maanantaina 10 päivänä joulukuuta 1990
    # to year-month-day
    row = row.replace(')', '.')
    row = row.replace('(', '')
    parts = row.split()
    session = '{:s}/{:s}'.format(parts[-6][:-1], parliament_year)
    date = '{:s}-{:s}-{:s}'.format(parts[-1].strip('s'),
                                   parts[-2][:-2], parts[-4])
    return session, parts[-6][:-1], date


def handle_session_start(rows):
    for row in rows:
        if 'kello' in row:
            parts = row.split()
            if len(parts) > 1:
                return(parts[1].strip(')'))
    return ''


def handle_session_end(row, row2):
    end = ''
    if 'Täysistunto lopetetaan' in row and (not 'kello' in row and ('kello' in row2 or 'keilo' in row2)):
        parts = row2.split()
        end = parts[-1][:-1]
    elif 'Täysistunto lopetetaan ' in row\
            or 'Täysistunto keskeytetään ' in row:
        parts = row.split()
        end = parts[-1][:-1]
    return end or ''


def document_link(parliament_year, session_num):
    return 'https://www.eduskunta.fi/FI/vaski/Poytakirja/Documents/ptk_{:s}+{:s}.pdf'.format(session_num, parliament_year)


def handle_page_num(row, parliament_year):
    if not any(char.isdigit() for char in row):
        return -1
    else:
        parts = row.split()
        for part in parts:
            if (part.isdigit() and part != parliament_year):
                return int(part)
            return -1


def chairman_name(speaker, session):
    # because things are hard:
    chairs = {
        '1990': {
            'Puhemies': 'Sorsa',
            'Ensimmäinen varapuhemies': 'Hetemäki-Olander',
            'Toinen varapuhemies': 'Pesälä',
            'Ikäpuhemies': 'Junnila'
        },
        '1991': {
            'Ikäpuhemies': 'Kohijoki'
        }
    }
    if (session[-4:] in chairs.keys() and speaker in chairs[session[-4:]].keys()):
        return chairs[session[-4:]][speaker]
    return ''


def mark_removable_hyphens(new):
    for i in range(len(new)-1):
        if new[i][-1] == '-':
            # print(new[i])
            # print(new[i+1])
            # cases where '-' shouldn't be removed
            if ('(vastaus' in new[i] and 'ro)' in new[i+1]):  # dealt elsewhere
                continue
            if new[i+1][0].isupper():  # Hetemäki-\nOllander
                continue
            if (len(new[i]) > 1 and new[i][-2].isdigit()):  # 1-3-\nluokkalaisten
                continue
            if new[i+1].startswith('ja ') \
                    or new[i+1].startswith('tai ') \
                    or new[i+1].startswith('sekä ') \
                    or new[i+1].startswith(','):  # kesä-\n, talvi- tai kevätkausi
                continue
            if(new[i+1][0] in ('a', 'e', 'y', 'u', 'i', 'o', 'ä', 'ö') and len(new[i]) > 1 and new[i+1][0] == new[i][-2]):
                # raha-\nasia
                continue
            new[i] += '<REMOVE>'


def edit_content(content):
    new = []
    date_pagehead = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+\..*kuuta [0-9]{4}')
    pagehead1 = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+\.')
    pagehead2 = re.compile('[a-z]+kuuta [0-9]{4}')
    number_lines = re.compile('^[0-9\/\.C ]+$')
    # print(content)
    for i in range(len(content)):
        if '\f' in content[i]:
            continue
        elif date_pagehead.match(content[i]):
            continue
        elif (pagehead1.match(content[i]) and i+2 < len(content) and pagehead2.match(content[i+2])):
            continue
        elif not content[i].strip() or number_lines.match(content[i]):
            continue
        elif 'merkitään läsnä ' in content[i] \
                or ('Edustajat' in content[i-1] and 'läsnä olev' in content[i]) \
                or ('Edustajat' in content[i] and i+1 < len(content) and 'läsnä olev' in content[i+1]):
            continue
        else:
            row = re.sub('=|€', '', content[i])
            if row:
                new.append(row)

    mark_removable_hyphens(new)
    return new


def edit_related_documents(topic):
    # Lakialoitteet n:ot 1 ja 2/1987 vp. sekä 3 ja 23/1989 vp.
    # Toivomusaloitteet n:ot 8 ja 11/1987 vp. sekä 13 ja 14/1988 vp.
    # Hallitukse esitykset n:ot 6 ja 127
    topic = topic.replace('n;o', 'n:o')
    if 'n:ot' in topic:
        new = []
        docs = topic.split('>>>')
        if not topic.startswith('>>>'):
            new.append(docs.pop(0))
        for doc in docs:
            if 'n:ot' in doc:
                doc_type = doc.partition('n:ot')[0]
                parts = doc.split()
                year_change = ''
                given_year = ''
                if not '/' in doc:  # Everything is of current year
                    for part in parts:
                        if part[0].isdigit():
                            if '—' in part:  # 131—133
                                start = int(part.partition('—')[0])
                                try:
                                    end = int(part.strip(
                                        ',').partition('—')[-1])
                                except:
                                    continue
                                for l in range(start, end+1):
                                    new.append('>>>' + doc_type +
                                               'n:o ' + str(l))
                            else:
                                new.append('>>>'+doc_type +
                                           'n:o ' + part.strip(','))
                else:
                    for i in range(len(parts)):
                        if '/' in parts[i]:
                            year_change = i
                            given_year = parts[i].partition('/')[-1]
                            for j in range(year_change):
                                if (parts[j][0].isdigit() and not '/' in parts[j]):
                                    if '—' in parts[j]:  # 131—133
                                        start = int(parts[j].partition('—')[0])
                                        end = int(parts[j].strip(
                                            ',').partition('—')[-1])
                                        for l in range(start, end+1):
                                            new.append('>>>' + doc_type +
                                                       'n:o ' + str(l) + '/' + given_year)
                                    else:
                                        new.append('>>>' + doc_type +
                                                   'n:o ' + parts[j].strip(',') + '/' + given_year)
                            new.append('>>>' + doc_type + 'n:o ' +
                                       parts[i].strip(','))

                    if int(year_change) < len(parts)-1:  # last document (no given year)
                        for k in range(year_change+1, len(parts)):
                            if parts[k][0].isdigit():
                                if '—' in parts[k]:  # 131—133
                                    start = int(parts[k].partition('—')[0])
                                    end = int(parts[k].partition('—')[-1])
                                    for l in range(start, end+1):
                                        new.append('>>>' + doc_type +
                                                   'n:o ' + str(l))
                                else:
                                    new.append('>>>' + doc_type + 'n:o ' +
                                               parts[k].strip(','))

            else:
                new.append('>>>' + doc)

        return ' '.join(new)

    else:
        return topic


def main(filename):
    file = open(filename, "r")
    contents = file.read()
    rows = contents.split('\n')
    file.close()

    parliament_year = filename[-10:-6]
    # While going trough document gather session times
    # in a nested dict to be used after file has been run through
    session_times = {}

    current_topic = []
    index = False
    topic = False
    discussion = False
    question = False
    speech = False
    current_speech = []
    all_speeches = []
    page = -1
    start_page = ''
    session_num = ''
    session = ''
    date = ''
    # session_chairman = ''
    # ********************************
    #
    # session = xx/xxxx
    # ********************************

    for i in range(len(rows)-1):
        if page_header(rows[i]):
            if not document_start(rows[i]):
                if page == -1:
                    page = handle_page_num(rows[i], parliament_year)
                    if page != -1:
                        page -= 1
            if page != -1:
                page += rows[i].count('\f')
        if document_start(rows[i]):
            if current_speech:
                clean_content = edit_content(current_speech)
                speaker, content = get_speaker(' '.join(clean_content))
                link = document_link(parliament_year, session_num)
                if 'uhemies' in speaker:
                    speaker += ' ' + chairman_name(speaker, session)
                mark_removable_hyphens(current_topic)
                all_speeches.append(
                    [session, date, speaker, ' '.join(current_topic), content, start_page, link])
                current_speech = []
            speech = False
            index = True
            current_topic = []
            # session_chairman = ''
            topic = False
            session, session_num, date = session_details(
                rows[i], parliament_year)
            session_times[session] = {}
            session_times[session]['start'] = handle_session_start(
                rows[i+1:i+100])
        if document_end(rows[i], rows[i+1]):
            discussion = False
            speech = False
            session_times[session]['end'] = handle_session_end(
                rows[i], rows[1+i])
        if index_end(rows[i]):
            index = False
            speech = False
        if discussion_starters(rows[i]):
            discussion = True
            speech = False
            topic = False
        if discussion_enders(rows[i], rows[i+1]):
            discussion = False
            speech = False
        if question_starters(rows[i]):
            question = True
            speech = False
        if question_enders(rows[i]):
            question = False
            speech = False
        if closing_statement(rows[i]):
            current_topic = []
        if acceptance(rows[i]):
            speech = False
        # if 'Puhetta johtaa' in rows[i]:
        #    session_chairman = chairman_name(rows[i], rows[i+1])
        if speech_starters(rows[i], rows[i+1]):
            speech = True
            topic = False
            if current_speech:
                clean_content = edit_content(current_speech)
                speaker, content = get_speaker(' '.join(clean_content))
                link = document_link(parliament_year, session_num)
                if 'uhemies' in speaker:
                    speaker += ' ' + chairman_name(speaker, session)
                mark_removable_hyphens(current_topic)
                all_speeches.append(
                    [session, date, speaker, ' '.join(current_topic), content, start_page, link])
                current_speech = []
            start_page = page
        if (speech and 'Pöytäkirjan vakuudeksi:' in rows[i]):
            speech = False
        if (not index and not discussion):
            if topic_starter(rows[i]):
                speech = False
                topic = True
            if (topic_enders(rows[i], rows[i+1])):
                topic = False
        if (not index and topic_details(rows[i])):
            speech = False
            if rows[i] not in current_topic:
                current_topic.append('>>>'+rows[i])
                if rows[i].endswith('ja') or rows[i].endswith('sekä') \
                        or rows[i].endswith('-') or rows[i].endswith(',') or rows[i].endswith('/'):
                    if rows[i+1]:
                        current_topic.append(rows[i+1])
                elif (rows[i+1] and (rows[i+1].startswith('ja ') or rows[i+1].startswith('sekä '))):
                    current_topic.append(rows[i+1])
        if speech:
            current_speech.append(rows[i])
        else:
            if current_speech:
                clean_content = edit_content(current_speech)
                speaker, content = get_speaker(' '.join(clean_content))
                link = document_link(parliament_year, session_num)
                if 'uhemies' in speaker:
                    speaker += ' ' + chairman_name(speaker, session)
                mark_removable_hyphens(current_topic)
                all_speeches.append(
                    [session, date, speaker, ' '.join(current_topic), content, start_page, link])
                current_speech = []
        if (not index and not discussion):
            if topic_starter(rows[i]):
                current_topic = []
        if (topic and '\f' not in rows[i] and rows[i]):
            current_topic.append(rows[i])

    # pprint(session_times)
    output_file = filename[:-4]
    with open('{:s}_RAW.csv'.format(output_file), 'w', newline='') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        for i in range(len(all_speeches)):
            if 'end' in session_times[all_speeches[i][0]]:
                end = session_times[all_speeches[i][0]]['end']
            else:
                end = ''
            if ', >>>' in all_speeches[i][3]:
                all_speeches[i][3] = all_speeches[i][3].replace(
                    ', >>>', ' >>>')

            if 'Kauppa- ja teollisuusministeri Suomi-<REMOVE> nen' in all_speeches[i][2]:
                all_speeches[i][2] = 'Kauppa- ja teollisuusministeri Suominen'

            if ('(ko' in all_speeches[i][2] and 'uhemies' in all_speeches[i][2]):
                all_speeches[i][2] = all_speeches[i][2].partition('(')[
                    0].strip()
                all_speeches[i][4] = '(koputtaa)' + all_speeches[i][4]

            if all_speeches[i][2].strip() == 'Puhuja':
                if 'uhemies' in all_speeches[i-1][2]:
                    all_speeches[i][2] = '<Puhuja>' + all_speeches[i-2][2]
                else:
                    all_speeches[i][2] = '<Puhuja>' + all_speeches[i-1][2]

            all_speeches[i][3] = edit_related_documents(all_speeches[i][3])

            writer.writerow(
                [all_speeches[i][0], all_speeches[i][1], session_times[all_speeches[i][0]]['start'],
                 end, all_speeches[i][2], all_speeches[i][3], all_speeches[i][4], all_speeches[i][5], all_speeches[i][6]])
    print(len(all_speeches))


if __name__ == "__main__":
    main(sys.argv[1])
