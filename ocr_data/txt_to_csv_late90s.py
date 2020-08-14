import re
import csv
import sys
from pprint import pprint


########################
# Script for 1995-1999 #
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
    problem_rows = []
    if 'Äänestys ed.' in row or row in problem_rows:
        return False
    topic = re.compile('^[0-9]+\) [A-ZÅÄÖ].*')
    interpellation = re.compile(
        '^[EF]d. [A-ZÅÄÖ].+ ym. välikysymys')  # välikysymys
    question = re.compile('^N:o [0-9]+ [A-ZÅÄÖ]')
    if topic.match(row) or interpellation.match(row)\
            or question.match(row):
        return True
    return False


def topic_enders(row, row2):
    if 'Valiokuntaan lähettäminen' in row or 'Puhetta johtaa' in row or 'käsittely' in row or 'uhemies:' in row\
        or 'Valjokuntaan lähettäminen' in row or 'Lähetekeskustelu' in row\
            or row.startswith('Vastaus ja keskustelu') or row.startswith('Äänestykset'):
        return True
    if re.compile('lähetetään [a-zåäö]+neuvoston ehdotuksen').match(row):
        return True
    if speech_starters(row, row2):
        return True
    return False


def topic_details(row):
    # Hallituksen esitys 11/1995 vp
    # Työasiainvaliokunnan mietintö 1/1995 vp
    # Lakialoite 11/1995 vp (Pulliainen ym.)
    # Toivomusaloite 182/1995 vp
    # Välikysymys 1/1995 vp
    # Puhemiesneuvoston luettelo 1/1995 vp
    proposal = re.compile('^Hallituksen esitys [0-9]+\/?[0-9]*( vp)?')
    committee = re.compile(
        '^[A-ZÅÄÖ][a-zåäö \-]+valiokunnan mietintö [0-9]+\/?[0-9]*( vp)?')
    iniative = re.compile(
        '^[A-ZÅÄÖ][a-zåäö\-]+aloit(teet|e) [0-9]+\/?[0-9]*( vp)?')
    account = re.compile('Kertomus [0-9]+\/?[0-9]*( vp)?')
    interpellation = re.compile('Välikysymys [0-9]+\/?[0-9]*( vp)?')
    catalogue = re.compile('Puhemiesneuvoston luettelo [0-9]+\/?[0-9]*( vp)?')
    vt = re.compile(
        'Valtioneuvoston (kirjelmä VN|tiedonanto) [0-9]+\/?[0-9]*( vp)?')
    if proposal.match(row) or committee.match(row) or iniative.match(row)\
            or account.match(row) or interpellation.match(row)\
            or catalogue.match(row) or vt.match(row):
        return True
    return False


def speech_starters(row, row2):
    speech_start = re.compile("^[E|F]d. ?[A-ZÅÄÖ].*[^A-ZÅÄÖ][:;]")
    speech_start2 = re.compile("^[A-ZÅÄÖ].*inisteri ?[A-ZÅÄÖ].*[:;]")
    long_title = re.compile('^[A-ZÅÄÖ].*inisteri [A-ZÅÄÖ].*-$')
    long_title2 = re.compile('^[A-ZÅÄÖa-zåäö]+[;:]')
    two_lines1 = re.compile("^[E|F]d. [A-ZÅÄÖ].*\(va")
    two_lines2 = re.compile("[a-z]*ro\) ?:")
    # speech_start = re.compile("^[E|F]d. ?[A-ZÅÄÖ][A-Za-zÀ-ÖØ-öø-ÿ-]+[:;]")
    # speech_start2 = re.compile(
    #    "^[A-ZÅÄÖ][a-zåäö -]*inisteri [A-ZÅÄÖ][A-Za-zÀ-ÖØ-öø-ÿ-]+[:;]")

    # two_lines1 = re.compile(
    #    "^([E|F]d.|[A-ZÅÄÖ][a-zåäö -]+inisteri) ?[A-ZÅÄÖ][A-Za-zÀ-ÖØ-öø-ÿ-]+ ?\(va")
    # two_lines2 = re.compile("[a-z]*ro\) ?:")
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
            or 'Ikäpuhemies:' in row or '(vastauspuheenvuoro)' in row:  # ':' missing
        return True
    return False


def document_start(row):
    # 5. Tiistaina 13 päivänä helmikuuta 1990
    if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ päivänä .*kuuta 199[0-9]').match(row):
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
    if 'Täysistunto lopetetaan' in row and ('kello' in row2 or 'keilo' in row2):
        parts = row2.split()
        end = parts[-1][:-1]
    elif 'Täysistunto lopetetaan ' in row \
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
    # 11. Torstaina 22.4.1999
    new = []
    date_pagehead = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+\..*kuuta [0-9]{4}')
    date_pagehead2 = re.compile(
        '^[0-9]+[\.,] [MTKPLS][a-z]+na [0-9]+\.[0-9]+\.199[0-9]')
    number_lines = re.compile('^[0-9\/\. ]+$')
    pagehead1 = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+\.')
    pagehead2 = re.compile('[a-z]+kuuta [0-9]{4}')
    # print(content)
    for i in range(len(content)):
        if '\f' in content[i]:
            continue
        elif date_pagehead.match(content[i]) or date_pagehead2.match(content[i]):
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
                        or rows[i].endswith('-') or rows[i].endswith(',') or rows[i].endswith('/')\
                        or ('(' in rows[i] and not ')' in rows[i]):
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
            if ('(ko' in all_speeches[i][2] and 'uhemies' in all_speeches[i][2]):
                all_speeches[i][2] = all_speeches[i][2].partition('(')[
                    0].strip()
                all_speeches[i][4] = '(koputtaa)' + all_speeches[i][4]

            if all_speeches[i][2].strip() == 'Puhuja':
                if 'uhemies' in all_speeches[i-1][2]:
                    all_speeches[i][2] = '<Puhuja>' + all_speeches[i-2][2]
                else:
                    all_speeches[i][2] = '<Puhuja>' + all_speeches[i-1][2]

            writer.writerow(
                [all_speeches[i][0], all_speeches[i][1], session_times[all_speeches[i][0]]['start'],
                 end, all_speeches[i][2], all_speeches[i][3], all_speeches[i][4], all_speeches[i][5], all_speeches[i][6]])
    print(len(all_speeches))


if __name__ == "__main__":
    main(sys.argv[1])
