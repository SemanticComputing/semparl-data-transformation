import re
import csv
import sys
from pprint import pprint

#############################################
# Script for 1960-1975_I                    #
# (I = 1. valtiopäivät, PTK_1975_1-3)   #
#############################################


def discussion_starters(row):
    if 'Keskustelu:' in row or 'Yleiskeskustelu:' in row or 'Keskustelu;' in row or 'Yleiskeskustelu;' in row:
        return True
    elif 'Keskustelu jatkuu' in row or 'Yleiskeskustelu jatkuu' in row:
        return True
    return False


def discussion_enders(row, row2):
    if 'Keskustelu julistetaan päättyneeksi' in row or 'Yleiskeskustelu julistetaan päättyneeksi' in row:
        return True
    if ('Keskustelu' in row and 'päättyneeksi' in row2):
        return True
    if 'Asia pannaan pöydälle seuraavaan' in row:
        return True
    return False


def question_starters(row):
    if (re.compile('\d+\) N:o \d+\/?\d*.* [A-ZÅÄÖ].*[:;]')).match(row):
        return True
    return False


def question_enders(row):
    if 'Asia on loppuun käsitelty' in row or 'Asia on loppun käsitelty' in row \
            or 'eskustelua ei synny.' in row or 'Puheenvuoroa ei haluta' in row\
            or 'Kukaan ei pyydä puheenvuoroa' in row \
            or 'Puheenvuoroa ei pyydetä' in row or 'Puheenvuotoa ei haluta' in row\
            or 'Puheenvuoron saatuaan lausuu' in row:
        return True
    return False


def topic_starter(row):
    problem_rows = [

    ]
    if ('Äänestys ' in row and 'ed.' in row) or row in problem_rows\
            or 'Eduskunta toteaa' in row or 'duskunta edellyttää' in row\
            or 'Eduskunnassa on' in row or 'Eduskunta katsoo' in row or 'Eduskunta edellyttää' in row\
            or 'Eduskunta painottaa' in row or 'Hyväksyessään lakiehdotuksen eduskunta' in row \
            or 'Eduskunta kehottaa' in row or 'Eduskunta ei hyväksy' in row:
        return False
    # 7) N:o 61 Ed. Pulliainen: Asioiden käsittely
    topic = re.compile('^[0-9]+\) [A-ZÅÄÖ].*')
    interpellation = re.compile(
        '^[EF]d. [A-ZÅÄÖ].+ ym. välikysymys')  # välikysymys
    iniative = re.compile('^Ehdotu(kset|s) laiksi ')
    budget = re.compile('^Ehdotus valtion tulo- ja menoarvioksi vuodelle')
    budget2 = re.compile('^Lisäyksiä ja muutoksia vuoden 19\d{2} tulo- ja')
    account = re.compile('^Valtioneuvoston talouspoliittinen selonteko')
    chair_questions = re.compile(
        '^Kysymy(s|ksiä) ja [sn]iih[ie]n annettu(ja)? vastau(s|ksia)[\.,]')
    if topic.match(row) or interpellation.match(row) or iniative.match(row)\
            or budget.match(row) or account.match(row) or budget2.match(row)\
            or chair_questions.match(row) or 'Ikäpuhemiehen alkajaissanat' in row:
        return True
    return False


def topic_enders(row, row2):
    if 'Valiokuntaan lähettäminen' in row or 'Puhetta johtaa' in row or 'käsittely' in row or 'uhemies:' in row\
            or 'Valjokuntaan lähettäminen' in row or 'Lähetekeskustelu' in row:
        return True
    if re.compile('lähetetään [a-zåäö]+neuvoston ehdotuksen').match(row):
        return True
    if row.startswith('Esitellään') or row.startswith('sisältävä')\
            or row.startswith('Yllämainit') or row.startswith('Eisitellään'):
        return True
    if 'Puhemiehen paikalle asetuttuaan' in row:
        return True
    if speech_starters(row, row2):
        return True
    return False


def topic_details(row):
    # sisältävä ed. Wahlströmin ym. lakialoite n:o 38

    # Esitellään valtiovarainvaliokunnan mietintö
    # n:o 11 ja otetaan ensimmäiseen käsit-
    # telyyn siinä valmistelevasti käsitelty hallituk-
    # sen esitys n:o 15, joka sisältää yllämainitun
    # lakiehdotuksen.

    # tarkoittavan hallituksen esityksen n:o 129 johdos-
    # ta laadittu ulkoasiainvaliokunnan mietintö n:o 19;

    related = re.compile(
        '^Yllämainitu[nt] (laki)?ehdotukse[nt] sisä[il]tävät?')
    proposal = re.compile('^(sisä[il]tävä|koskeva) hallituksen esitys n[;:]o ')
    proposal2 = re.compile('^tarkoittavan? hallituksen esity(s|ksen)')
    committee = re.compile('^F?Ei?sitellään [a-zåäö \-]+valiokunnan')
    iniative = re.compile(
        'sisä[il]tävä ed. [A-ZÅÄÖ].+ ym. [a-zåäö\-]+aloit(teet|e)')  # n[;:]o')
    budgeting = re.compile('^Valtiovarainvaliokunnan mietinnössä n:o')
    #  or 'Mainittu kertomus (K' in row:
    if proposal.match(row) or committee.match(row) or iniative.match(row)\
            or related.match(row) or budgeting.match(row)\
            or proposal2.match(row):
        return True
    return False


def speech_starters(row, row2):
    speech_start = re.compile("^[E|F]d. [A-ZÅÄÖ].*[:;]")
    speech_start2 = re.compile("^[A-ZÅÄÖ].*iniste[rt]i [A-ZÅÄÖ].*[:;]")
    long_title = re.compile('^[A-ZÅÄÖ].*iniste[rt]i [A-ZÅÄÖ].*-$')
    long_title2 = re.compile('^[A-ZÅÄÖa-zåäö]+[;:]')
    two_lines1 = re.compile("^[E|F]d. [A-ZÅÄÖ].*\(va")
    two_lines2 = re.compile("[a-z]*ro\) ?:")
    chairman = re.compile(
        '(F?[EF]nsimmäinen |Toinen )?(Puhemies|varapuhemies) ?(\(koputtaa\))? ?[;:]')
    chairman_knock = re.compile(
        '(F?[EF]nsimmäinen |Toinen )?(Puhemies|varapuhemies) ?')
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
    if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p[\-\.] .*kuuta 19[67][0-9]').match(row):
        return True
    return False


def document_end(row, row2):
    if 'Täysistunto lopetetaan ' in row\
            or 'Täysistunto keskeytetään ' in row:
        return True
    return False


def index_end(row):
    if re.compile('Puhetta johtaa( ensimmäinen| toinen)? (puhemies|varapuhemies)').match(row):
        return True
    if 'Päiväjärjestyksessä olevat asiat:' in row or 'Päiväjärjestyksessä oleva asia:' in row\
            or 'Ilmoitusasiat:' in row or 'Ikäpuhemiehen alkajaissanat' in row:
        return True
    return False


def end_compendium(row):
    if re.compile('\f+HAKEMISTO').match(row)\
            or re.compile('\f+SISÄLLYSLUETTELO').match(row):
        return True


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
            or re.compile('^Eduskunta on hyväksynyt ').match(row) \
            or 'Eduskunta on käsittelyn pohjaksi hy' in row\
            or 'Eduskunta on tässä äänestyksessä hyväksynyt' in row\
            or 'hyväksytään keskustelutta' in row\
            or 'Puhemiehistön ehdotus hyväksytään' in row\
            or 'Vaaliin ryhdytään ja liput avataan.' in row\
            or 'Hyväksytään.' in row or 'Anomukseen suostutaan.' in row:
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
    # (145) Maanantaina 10 päivänä joulukuuta 1990 <- continued session
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
                if not 'kello' in parts[1]:
                    time = re.sub('\)|:', '', parts[1])
                    time = time.replace(',', '.')
                    return time.rstrip('.')
    return ''


def handle_session_end(row, row2):
    end = ''
    if 'Täysistunto lopetetaan' in row and (not 'kello' in row and ('kello' in row2 or 'keilo' in row2)):
        parts = row2.split()
        end = parts[-1][:-1]
    elif 'Täysistunto lopetetaan ' in row \
            or 'Täysistunto keskeytetään ' in row:
        parts = row.split()
        end = parts[-1][:-1]
    if 'kello' in end:
        return ''
    return end or ''


def document_link(parliament_year, session_num, original_document_num):
    if int(parliament_year) == 1975:
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/1975/PTK_1975_I_{}.pdf'.format(
            original_document_num
        )
    elif int(parliament_year) > 1972:
        # Collection document
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/{}/PTK_{}_{}.pdf'.format(
            parliament_year, parliament_year, original_document_num
        )
    else:
        romans = {'1': 'I', '2': 'II', '3': 'III',
                  '4': 'IV', '5': 'V', '6': 'VI'}
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/{}/PTK_{}_{}.pdf'.format(
            parliament_year, parliament_year, romans[original_document_num]
        )  # https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/1972/PTK_1972_IV.pdf


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
        '[0-9]* ?[A-Z][a-z]+na [0-9]+ p\. .*kuuta [0-9]{4}')
    pagehead1 = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+ p\.')
    pagehead2 = re.compile('[a-z]+kuuta [0-9]{4}')
    number_lines = re.compile('^[0-9\/\. ]+$')
    chair_questions = re.compile(
        '^Kysymy(s|ksiä) ja [sn]iih[ie]n annettu(ja)? vastau(s|ksia)[\.,]')
    # print(content)
    for i in range(len(content)):
        if '\f' in content[i]:  # or number_lines.match(content[i]):
            continue
        elif date_pagehead.match(content[i]):
            continue
        elif (pagehead1.match(content[i]) and i+2 < len(content) and pagehead2.match(content[i+2])):
            continue
        elif not content[i].strip():
            continue
        elif 'merkitään läsnä ' in content[i] or 'todetaan läsnäolevaksi' in content[i]:
            continue
        elif 'saapuu paikalleen istuntosaliin' in content[i] or 'Puheenvuoron saatuaan lausuu' in content[i]:
            continue
        elif chair_questions.match(content[i]):
            continue
        else:
            row = re.sub('=|€|<<|^>> ', '', content[i])
            if row:
                new.append(row)

    mark_removable_hyphens(new)
    return new


def edit_related_documents(topic):
    """Esitellään — valtiovarainvaliokunnan = mietintö
    n:o 23 ja otetaan ensimmäiseen käsit-
    telyyn siinä valmistelevasti käsitellyt hallituk-
    sen esitys n:o 28 ja Mäen ym. lak.al. n:o 280,
    jotka sisältävät yllämainitut lakiehdotukset.

    Yllämainitut lakiehdotukset sisältävät hallituk-
    sen esitys n:o 178 (1974 vp.) sekä lak.al. n:ot
    18, 205 ja 206 (1973 vp.) sekä 15—17, 404 ja
    405 (1974 vp.), joita on valmistelevasti käsitelty
    perustuslakivaliokunnan mietinnössä n:o 10 ja
    suuren valiokunnan mietinnössä n:o 26, esitel-
    lään kolmanteen käsittelyyn sekä
    ainoaan käsittelyyn samassa yhteydessä
    käsitellyt toiv.al. n:ot 16 (1972 vp.) ja 4 (1973
    vp.)

    Esitellään suuren valiokunnan mietintö n:o 28
    ja otetaan toiseen käsittelyyn siinä sekä
    maa- ja metsätalousvaliokunnan mietinnössä n:o
    2 valmistelevasti käsitellyt hallituksen esitys n:o
    11 ja lak.al. n:ot 209 ja 291 (1972 vp.), 128
    (1973 vp.) sekä 179 ja 180 (1974 vp.), jotka sisäl-lakialoitteet n:ot 139/1987 vp. ja 11
    tävät yllämainitut lakiehdotukset.
    """

    mark_removable_hyphens(topic)
    new = []
    documents = ''
    related = False
    for i in range(len(topic)):
        if'>>>' in topic[i]:
            related = True
        if not related:
            new.append(topic[i])
        else:
            documents = ' '.join(topic[i+1:])
            break

    # cleans the documents section, main topic cleaned later
    documents = documents.replace('-<REMOVE> ', '')
    documents = documents.replace('/ ', '/')

    # OTA HUOMIOON

    bills = re.findall(
        'hallituksen esity(?:ksen|s) n[:;]+o \d+(?: ?\(\d+ v[pP][\.,]\))?', documents)
    committees = re.findall(
        '(?:suuren |[a-zåäö]+- ja )?[a-zåäöV-]*valiokunnan mietin(?:tö|nössä) n[:;]+o \d+\/?\d*', documents)
    iniatives = re.findall(
        '(?:ed. [A-ZÅÄÖ].+ ym. )?[a-zåäö\-]+[\.,]a[l!][\.,] n[:;]+o \d+(?: \(\d+ vp)?', documents)

    matches = bills + committees + iniatives
    matches = list(set(matches))

    for match in matches:
        # capitalize() would lowercase names in 'ed. Kettunen ym...'
        match = match[0].upper()+match[1:]
        # hallituksen esitys n:o 128 (1974 vp.)
        match = re.sub(' \(', '/', match)
        match = re.sub(' v[pP][\.,]\)', '', match)
        match = match.replace('esityksen', 'esitys')
        new.append('>>>' + match.replace('mietinnössä',
                                         'mietintö'))

    # plurals
    bills = re.findall(
        'hallituksen esitykset n[:;]+ot \d+[0-9\—\-\/,jasekävpP\.\,\(\) ]+[\)\d]', documents)
    iniatives = re.findall(
        '(?:ed. [A-ZÅÄÖ].+ ym. )?[a-zåäö\-]+[\.,]a[l!][\.,] n[:;]+ot \d+[0-9\—\-\/,jasekävpP\.\,\(\) ]+[\)\d]', documents)

    plurals = bills+iniatives

    # multiple document references
    # hallituksen esitykset n:ot 90 ja 235 (1974 vp.)
    if plurals:
        for doc in list(set(plurals)):
            doc = re.sub('n[:;]+ot', 'n:ot', doc)
            doc = re.sub('lak[\.,]a[l!][\.,]', 'lakialoite', doc)
            doc = re.sub('toiv[\.,]a[l!][\.,]', 'toivomusaloite', doc)
            if '(' in doc:
                # lak.al. n:ot 18, 205 ja 206 (1973 vp.) sekä 15, 16, 17, 404 ja 405 (1974 vp.)
                doc_type = doc.partition('n:ot')[0]
                # ['lak.al. n:ot 18, 205 ja 206 (1973 vp.', 'sekä 15, 16, 17, 404 ja 405 (1974 vp.']
                year_sections = doc.split(')')
                for part in year_sections:
                    year = '/' + part.partition('(')[-1]  # 1973 vp.)
                    year = re.sub('[vpP\., \)]', '', year)
                    year = re.sub(' ?\— ?', '—', year)
                    if year.endswith('/'):
                        year = ''  # no mentioned year
                    # ['lak.al.', 'n:ot 18,', '205', 'ja', '206', '(1973', 'vp.']
                    docs = part.split()
                    for doc in docs:
                        if doc[0].isdigit():
                            if '—' in doc:
                                # raha-asia-aloitteet n:ot 1—3138
                                if re.search('\d+\—\d+', doc):
                                    doc_range = re.search(
                                        '\d+\—\d+', doc).group()
                                else:
                                    continue
                                start = int(doc_range.partition('—')[0])
                                end = int(doc_range.partition('—')[-1])
                                for i in range(start, end+1):
                                    new.append('>>>' + doc_type.capitalize() +
                                               'n:o ' + str(i) + year)
                            else:
                                new.append('>>>' + doc_type.capitalize() +
                                           'n:o ' + doc.strip(',') + year)
            else:
                # lakialoitteet n:ot 64, 86 ja 101
                doc_type = doc.partition('n:ot')[0]
                parts = doc.split()
                for part in parts:
                    if part[0].isdigit():
                        if '—' in doc:
                            # raha-asia-aloitteet n:ot 1—3138
                            if re.search('\d+\—\d+', doc):
                                doc_range = re.search('\d+\—\d+', doc).group()
                            else:
                                continue
                            start = int(doc_range.partition('—')[0])
                            end = int(doc_range.partition('—')[-1])
                            for i in range(start, end+1):
                                new.append('>>>' + doc_type.capitalize() +
                                           'n:o ' + str(i))
                        else:
                            new.append('>>>' + doc_type.capitalize() +
                                       'n:o ' + part.strip(','))

    return new


def main(filename):
    file = open(filename, "r")
    contents = file.read()
    rows = contents.split('\n')
    file.close()

    parliament_year = filename[-10:-6]
    original_document_num = filename[-5]
    # While going trough document gather session times
    # in a nested dict to be used after file has been run through
    session_times = {}

    current_topic = []
    index = False
    topic = False
    discussion = False
    question = False
    speech = False
    details = False
    current_speech = []
    all_speeches = []
    page = -1
    start_page = ''
    session_num = ''
    session = ''
    date = ''

    # session = xx/xxxx
    # ********************************

    for i in range(len(rows)-1):
        if end_compendium(rows[i]):
            break
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
                link = document_link(
                    parliament_year, session_num, original_document_num)
                cleaned_topic = edit_related_documents(current_topic)
                all_speeches.append(
                    [session, date, speaker, ' '.join(cleaned_topic), content, start_page, link])
                current_speech = []
            speech = False
            index = True
            current_topic = []
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
        if (speech_starters(rows[i], rows[i+1]) and not index):  # Risk?
            speech = True
            topic = False
            details = False
            if current_speech:
                clean_content = edit_content(current_speech)
                speaker, content = get_speaker(' '.join(clean_content))
                link = document_link(
                    parliament_year, session_num, original_document_num)
                cleaned_topic = edit_related_documents(current_topic)
                all_speeches.append(
                    [session, date, speaker, ' '.join(cleaned_topic), content, start_page, link])
                current_speech = []
            start_page = page
        if (speech and 'Pöytäkirjan vakuudeksi:' in rows[i]):
            speech = False
        if (not index and not discussion):
            if topic_starter(rows[i]):
                speech = False
                details = False
                topic = True
            if topic_enders(rows[i], rows[i+1]):
                topic = False
        if (not index and topic_details(rows[i])):
            #speech = False
            details = True
            topic = False
            current_topic.append('>>>')
        if speech:  # (speech and rows[i].strip()):  # latter added
            if rows[i].strip():
                current_speech.append(rows[i])
        else:
            if current_speech:
                clean_content = edit_content(current_speech)
                speaker, content = get_speaker(' '.join(clean_content))
                link = document_link(
                    parliament_year, session_num, original_document_num)
                cleaned_topic = edit_related_documents(current_topic)
                all_speeches.append(
                    [session, date, speaker, ' '.join(cleaned_topic), content, start_page, link])
                current_speech = []
        if (not index and not discussion):
            if topic_starter(rows[i]):
                current_topic = []
        if (topic and '\f' not in rows[i] and rows[i]):
            current_topic.append(rows[i])
        if (details and rows[i].strip() and '\f' not in rows[i]):
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
