import re
import csv
import sys
from pprint import pprint

#############################
# Script for 1975_II-1988   #
# (II = Toiset valtiopäivät)#
#############################


def discussion_starters(row):
    if 'Keskustelu:' in row or 'Yleiskeskustelu:' in row or 'Keskustelu;' in row or 'Yleiskeskustelu;' in row:
        return True
    elif 'Keskustelu jatkuu' in row or 'Yleiskeskustelu jatkuu' in row:
        return True
    return False


def discussion_enders(row, row2):
    if 'Keskustelu julistetaan päättyneeksi' in row or 'Yleiskeskustelu julistetaan päättyneeksi' in row:
        return True
    if ('Keskustelu' in row and 'päättyneeksi.' in row2):
        return True
    if 'Asia pannaan pöydälle seuraavaan' in row:
        return True
    return False


def question_starters(row):
    if (re.compile('\d+\) N:o \d+\/?\d*.* [A-ZÅÄÖ].*[:;]')).match(row):
        return True
    return False


def question_enders(row):
    if 'Asia on loppuun käsitelty.' in row or 'Asia on loppun käsitelty.' in row \
            or 'eskustelua ei synny.' in row or 'Puheenvuoroa ei haluta.' in row\
            or 'Kukaan ei pyydä puheenvuoroa.' in row \
            or 'Puheenvuoroa ei pyydetä.' in row\
            or 'Puheenvuoron saatuaan lausuu' in row\
            or row == 'Liitteet':
        return True
    return False


def topic_starter(row):
    problem_rows = [
        '1) Eri maiden hallitusten edustajain kokous',
        '4) Eduskunta kiirehtii niitä liikenneministe-',
        '2) Hyväksyessään läänijakoa koskevan lakiehdo-',
        '1) Pohjoismaisen hyvinvointiyhteiskunnan kan-',
        '2) Kehitysmaiden jättimäinen velkaantuminen',
        '3) Nykyinen teollisuusmaiden välinen kauppa-',
        '1) Laki säädetään perustuslainsäätämisjärjestyk-',
        '2) Tällä hetkellä voimassa olevan lainsäädän-',
        '3) Ennakkotarkastuksessa ovat kuitenkin lain',
        '4) Lisäksi ennakkotarkastuksesta on vapautettu',
        '3) Täystyöllisyyden turvaamiseksi eduskunta',
        '1) Uudistuksen laajuuden ja sen merkityksen',
        '3) Erityisesti ikääntyneillä, pidempään työt-',
        '2) Työttömän kannalta lyhyttä työllistämis-',
        '3) Kun kansanedustajilla on tavallisiin kansa-',
        '5) Kommunisteille on syytä muistuttaa, että',
        '4) Kansanedustajien ja ministereiden palkkauk-',
        '3) SMP vastustaa yksiselitteisesti eduskunnassa',
        '2) SMP:llä on hallituksessa vain kaksi ministeriä',
        '1) SMP joutui muiden hallituspuolueiden ja',
        '1) Äänestys ed, Puolanteen ja ed. P. Ven-',
        '81) N', '44) N .',
    ]
    if 'Äänestys ed.' in row or row in problem_rows\
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
    if topic.match(row) or interpellation.match(row) or iniative.match(row)\
            or budget.match(row) or account.match(row) or budget2.match(row):
        return True
    return False


def topic_enders(row, row2):
    if 'Valiokuntaan lähettäminen' in row or 'Puhetta johtaa' in row or 'käsittely' in row or 'uhemies:' in row\
            or 'Valjokuntaan lähettäminen' in row or 'Lähetekeskustelu' in row:
        return True
    if re.compile('lähetetään [a-zåäö]+neuvoston ehdotuksen').match(row):
        return True
    if row.startswith('Esitellään') or row.startswith('sisältävä')\
            or row.startswith('Yllämainit'):
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
    committee = re.compile('^F?Esitellään [a-zåäö \-]+valiokunnan')
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
    if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ päivänä .*kuuta 19[78][0-9]').match(row):
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
            or 'Eduskunta on käsittelyn pohjaksi hy' in row\
            or 'Eduskunta on tässä äänestyksessä hyväksynyt' in row\
            or 'hyväksytään keskustelutta' in row\
            or 'Puhemiehistön ehdotus hyväksytään' in row\
            or 'Vaaliin ryhdytään ja liput avataan.' in row:
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
    if parliament_year == '1975':
        return session+'_II', parts[-6][:-1], date
    return session, parts[-6][:-1], date


def handle_session_start(rows):
    for row in rows:
        if 'kello' in row:
            parts = row.split()
            if len(parts) > 1:
                if not 'kello' in parts[1]:
                    time = re.sub('\)|:', '', parts[1])
                    return time
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
    if int(parliament_year) >= 1980:
        # Single session
        return 'https://www.eduskunta.fi/FI/vaski/Poytakirja/Documents/ptk_{:s}+{:s}.pdf'.format(session_num, parliament_year)
    elif int(parliament_year) == 1975:
        docs = {'4': '1', '5': '2'}
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/1975/PTK_1975_II_{}.pdf'.format(
            docs[original_document_num]
        )
    else:
        # Collection document
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/{}/PTK_{}_{}.pdf'.format(
            parliament_year, parliament_year, original_document_num
        )


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


def not_content(content, i):
    """Returns true if content[i] is not part of speech
    """
    date_pagehead = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+[\.,].*kuuta [0-9]{4}')
    pagehead1 = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+[\.,]')
    pagehead2 = re.compile('[a-z]+kuuta [0-9]{4}')
    number_lines = re.compile('^[0-9\/\.W ]+$')
    if '\f' in content[i]:
        return True
    elif date_pagehead.match(content[i]):
        return True
    elif (pagehead1.match(content[i]) and i+2 < len(content) and pagehead2.match(content[i+2])):
        return True
    elif number_lines.match(content[i]):
        return True
    elif 'merkitään läsnä ' in content[i] \
            or ('Edustajat' in content[i-1] and 'läsnä olev' in content[i]) \
            or ('Edustajat' in content[i] and i+1 < len(content) and 'läsnä olev' in content[i+1]):
        return True
    elif 'saapuu paikalleen istuntosaliin' in content[i] or 'Puheenvuoron saatuaan lausuu' in content[i]:
        return True
    else:
        return False


def edit_content(content):
    new = []
    # print(content)
    for i in range(len(content)):
        if not_content(content, i):
            continue
        elif (not content[i].strip() and content[i-1] and not not_content(content, i-1)
                and i+1 < len(content) and not not_content(content, i+1)):
            new.append('\n')
        else:
            row = re.sub('=|€|<<|^>> ', '', content[i])
            if row:
                new.append(row)

    mark_removable_hyphens(new)
    return new


def edit_related_documents(topic):
    """ Esitellään valtiovarainvaliokunnan mietintö
    n::o 34 ja otetaan ainoaan käsittelyyn
    siinä valmistelevasti käsitelty yllämainittu pää-
    tös.

    sisältävä hallituksen esitys n:o 66 esitellään va-
    liokuntaan lähettämistä varten.

    sisältävä ed. Jäätteenmäen ym. lakialoite n:o 59

    Yllämainitun lakiehdotuksen sisältävä halli-
    tuksen esitys n:o 57, jota on valmistelevasti kä-
    sitelty ulkoasiainvaliokunnan mietinnössä n:o
    11 ja suuren valiokunnan mietinnössä n:o 79,
    2007
    esitellään osittain kolmanteen, osittain
    ainoaan käsittelyyn.

    Yllämainitut lakiehdotukset sisältävät halli-
    tuksen esitys n:o 193/1987 vp. ja lakialoitteet
    n:ot 139/1987 vp. ja 11, joita on valmistelevasti
    käsitelty sivistysvaliokunnan mietinnössä n:o 1
    ja suureen valiokunnan mietinnössä n:o 33, esi-
    tellään kolmanteen käsittelyyn.

    tarkoittavan hallituksen esityksen n:o 239 johdos-
    ta laadittu valtiovarainvaliokunnan mietintö n:o 93;
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

    bills = re.findall(
        'hallituksen esity(?:ksen|s) n[:;]+o \d+\/?\d*', documents)
    committees = re.findall(
        '(?:suuren |[a-zåäö]+- ja )?[a-zåäöV-]*valiokunnan mietin(?:tö|nössä) n[:;]+o \d+\/?\d*', documents)
    iniatives = re.findall(
        '(?:ed. [A-ZÅÄÖ].+ ym. )?[a-zåäö\-]+aloite n[:;]+o \d+(?:\/\d+)?', documents)

    matches = bills + committees + iniatives
    matches = list(set(matches))

    for match in matches:
        # capitalize() would lowercase names in 'ed. Kettunen ym...'
        match = match[0].upper()+match[1:]
        match = match.replace('esityksen', 'esitys')
        new.append('>>>' + match.replace('mietinnössä',
                                         'mietintö'))

    # plurals
    bills = re.findall(
        'hallituksen esitykset n[:;]+ot \d+[0-9\—\-\/,jasekävp\. ]+\d', documents)
    iniatives = re.findall(
        '(?:ed. [A-ZÅÄÖ].+ ym. )?[a-zåäö\-]+aloitteet n[:;]+ot \d+[0-9\—\-\/,jasekävp\. ]+\d', documents)

    plurals = bills+iniatives

    # multiple document references
    # lakialoitteet n:ot 139/1987 vp. ja 11
    if plurals:
        for doc in list(set(plurals)):
            doc = re.sub('n[:;]+ot', 'n:ot', doc)
            if '—' in doc:
                # raha-asia-aloitteet n:ot 1—3138
                new.append('>>>' + re.sub('n:ot', 'n:o', doc.capitalize()))
            elif '/' in doc:
                # lakialoitteet n:ot 28, 47, 65 ja 134/1987 vp. sekä 13 ja 51
                doc_type = doc.partition('n:ot')[0]
                parts = doc.split()
                year_change = ''
                previous_year = ''
                for i in range(len(parts)):
                    if '/' in parts[i]:
                        year_change = i
                        previous_year = parts[i].partition('/')[-1]
                        break
                for i in range(len(parts)):
                    if parts[i][0].isdigit():
                        if i < year_change:
                            new.append('>>>' + doc_type.capitalize() +
                                       'n:o ' + parts[i].strip(',') + '/' + previous_year)
                        else:
                            new.append('>>>' + doc_type.capitalize() +
                                       'n:o ' + parts[i].strip(','))
            else:
                # lakialoitteet n:ot 64, 86 ja 101
                doc_type = doc.partition('n:ot')[0]
                parts = doc.split()
                for part in parts:
                    if part[0].isdigit():
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
        if speech:
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

            writer.writerow(
                [all_speeches[i][0], all_speeches[i][1], session_times[all_speeches[i][0]]['start'],
                 end, all_speeches[i][2], all_speeches[i][3], all_speeches[i][4], all_speeches[i][5], all_speeches[i][6]])
    print(len(all_speeches))


if __name__ == "__main__":
    main(sys.argv[1])
