import re
import csv
import sys
import time
import string
from datetime import datetime
from pprint import pprint

##################################
# Script for 1907-1909_I         #
# Second Valtiopäivät:           #
# 1908_2-4                       #
##################################


def discussion_starters(row):
    if 'Keskustelu:' in row or 'Keskustelu.' in row or 'Keskustelu;' in row:
        return True
    elif 'Keskustelu jatkuu' in row:
        return True
    return False


def discussion_enders(row, row2):
    if 'Keskustelu julistetaan päättyneeksi' in row or 'Yleiskeskustelu julistetaan päättyneeksi' in row:
        return True
    if ('Keskustelu' in row and 'päättyneeksi' in row2):
        return True
    if 'Asia pannaan pöydälle seuraavaan' in row or 'Päätös:' in row:
        return True
    return False


def question_starters(row):
    if (re.compile('\d+\) N:o \d+\/?\d*.* [A-ZÅÄÖ].*[:;]')).match(row):
        return True
    return False


def question_enders(row):
    if 'Asia on loppuun käsitelty' in row or 'Asia on loppun käsitelty' in row \
            or 'eskustelua ei synny.' in row or 'Puheenvuoroa ei haluta' in row\
            or 'Kukaan ei pyydä puheenvuoroa' in row or 'Keskustelua ei haluta' in row\
            or 'Kukaan ei pyydä yleiskeskustelussa pu' in row\
            or 'Puheenvuoroa ei pyydetä' in row or 'Puheenvuotoa ei haluta' in row\
            or 'Puheenvuoroja ei pyydetä' in row\
            or 'Puheenvuoron saatuaan lausu' in row \
            or 'Yleiskeskustelussa kukaan ei pyydä' in row\
            or 'Yleiskeskustelussa ei kukaan halua pu' in row\
            or 'Kun tämä on tapahtunut, toteaa' in row\
            or 'Eduskunta on siis hyväksynyt' in row or 'Päätös:' in row\
            or 'Puhujalavalta lausuvat tämän jälkeen:' in row:
        return True
    return False


def topic_starter(row, prev_row):
    problem_rows = []

    if ('Äänestys ' in row and 'ed.' in row)\
            or 'Äänestys suuren valiokunnan ehdo-' in row\
            or 'Hyväksyessään lakiehdotuksen eduskunta' in row \
            or 'Eduskunta kehottaa' in row or 'Eduskunta ei hyväksy' in row\
            or re.search("\d\) (Ken|Joka) ?—?(ehdollisesti )?('?hyväksyy?|vasta(ehdotukseksi|esitykseksi)|tässä äänestyk|tahtoo)", row)\
            or re.compile('\d+\) Senaatin talousosaston ').match(row)\
            or re.compile('\d+\) Äänestys (mietinnön ja  |valtiovarainvaliokunnan)').match(row):
        # or row in problem_rows:
        return False
    # 7) N:o 61 Ed. Pulliainen: Asioiden käsittely
    topic = re.compile('^[0-9]+\) [A-ZÅÄÖ].*')
    interpellation = re.compile(
        '^[EBF]d. (af|von|v\.)? ?[A-ZÅÄÖ].+n (y\.? ?m\. )?välikysymys')  # välikysymys
    iniative = re.compile('^Ehdotu(kset|s) laiksi ')
    budget = re.compile('^Ehdotus valtion tulo- ja menoarvioksi vuodelle')
    budget2 = re.compile('^Lisäyksiä ja muutoksia vuoden 19\d{2} tulo- ja')
    account = re.compile('^Valtioneuvoston talouspoliittinen selonteko')
    chair_questions = re.compile(
        '^Kysymy(s|ksiä) ja [sn]iih[ie]n annettu(ja)? vastau(s|ksia)[\.,]')
    members = re.compile('Valiokunta?ie?n jäsenet.')
    suggestion = re.compile(
        '[FE]d[\.,] (af|von|v\.)? ?[A-ZÅÄÖ].+n (y\.? ?m\. )?edusk(unta|[\.,]) ?esit(ys|[\.,]) \(?n:o \d+\)')

    if prev_row.startswith('Päiväjärjestyksessä oleva asia'):
        return True
    if topic.match(row) or interpellation.match(row) or iniative.match(row)\
            or budget.match(row) or account.match(row) or budget2.match(row)\
            or members.match(row)\
            or chair_questions.match(row) or 'Ikäpuhemiehen alkajaissanat' in row\
            or 'Puhemiehen puhe.' == row or 'Puhemiehen tervehdyspuhe.' == row\
            or 'Vaitiepäivien avaaminen.' == row\
            or suggestion.match(row)\
            or 'Muutos päiväjärjestykseen.' in row\
            or row == 'Puhemiehen ja varapuhemiesten vaali.':
        return True
    return False


def topic_enders(row, row2):
    if 'Valiokuntaan lähettäminen' in row or 'Puhetta johtaa' in row or 'käsittely' in row or 'uhemies:' in row\
            or 'Valjokuntaan lähettäminen' in row or 'Lähetekeskustelu' in row\
            or 'esitellään valiokuntaan lähettämistä' in row:
        return True
    if re.compile('lähetetään [a-zåäö]+neuvoston ehdotuksen').match(row):
        return True
    if re.compile('[FE]i?site(ll|t)ään').match(row) or row.startswith('sisältävä')\
            or row.startswith('Yllämainit')\
            or row.startswith('Mainittu lakiehdotus')\
            or re.compile('Ne jotka hyväksyvät').match(row):
        return True
    if 'Puhemiehen paikalle asetuttuaan' in row or 'Paikalleen noustuaan' in row\
            or 'Kenraalikuvernööri palasi sitten' in row or 'jäseniksi ehdottaa' in row\
            or 'sihteeri lukee' in row or row.startswith('Hyväksytään')\
            or ' Kun täysi-istuntoa jälleen jatketaan' in row\
            or 'Jatketaan viime täysi-istunnossa ' in row\
            or 'Puhemiehen poistuttua ja ' in row\
            or row == 'Ikäpuhemiehen jälkeen asettui paikalleen Puhemies ja'\
            or row == 'Ikäpuhemies kehoitti Eduskuntaa V. J:n 23 8:n mukai-':
        return True
    if speech_starters(row, row2):
        return True
    return False


def topic_details(row, topic):

    related = re.compile(
        '^Yllämainitu[nt] (laki)?ehdotukse[nt] sisä[il]tävät?')
    proposal = re.compile(
        'Esitetään arm[\.,] esitys [nN] ?[;:]o')
    # '^(sisä[il]tävä|koskevan?) (hallituksen esityk?s(en)? n ?[;:]o |ed\. )')
    proposal2 = re.compile(
        '^tarkoittavai?n? (hallituksen esity(s|ksen)|ed\. |[a-z]* ?anomusehdotuksen johdo|Laki- ja talousvaliokunnan)')
    proposal3 = re.compile(
        '[eEF]d[\.,] (af|von)? ?[A-ZÅÄÖ].+ y[\.,] ?m[\.,] anomusehdotuk?s(en)? n ?[:;]o \d+')
    committee = re.compile(
        '^\*? ?F?E?i?site(ll|t)ään [a-zåäöA-Z \-]+valiokunnan')
    committee2 = re.compile(
        '[a-zåäöA-Z \-]+valiokunnan mietinnön n ?[:;]o \d+ johdo(lla|sta) esitetään')
    iniative = re.compile(
        'sisä[il]tävä ed[\.,] (af|von)? ?[A-ZÅÄÖ].+ (?:y\.? ?m\. )?[a-zåäö\-]+[\.,] ?a[l!][\.,]')  # n[;:]o')
    iniative2 = re.compile(
        '^([EF]d[\.,] (af|von)? ?[A-ZÅÄÖ][^,\(\)\d]+ (?:y\.? ?m\. )?)?[a-zåäö\-]+[\.,] ?a[l!][\.,] n ?[:;]+o')
    iniative3 = re.compile(
        '(sisäi?ltävä )?[eEF]d[\.,] (af|von)? ?[A-ZÅÄÖ].+ (y[\.,] ?m[\.,] )?(edusk|anom)[\.,] e(sit|hd)[\.,]( n ?[:;]o \d+)?')
    budgeting = re.compile('^Valtiovarainvaliokunnan mietinnössä n ?:o')
    mention = re.compile('^Mainitun (lakiehdotuksen|kertomuksen) johdosta')
    mention2 = re.compile('^Mainittu lakiehdotus')
    due_to = re.compile(
        '(^koskevan? (hallituksen esityksen|välikysymyksen) )?johdosta( laadittu )?')

    if proposal.match(row) or committee.match(row) or iniative.match(row)\
            or iniative2.match(row) or related.match(row) or budgeting.match(row)\
            or proposal2.match(row) or proposal3.match(row) or mention.match(row)\
            or mention2.match(row) or iniative3.match(row) or due_to.match(row)\
            or committee2.match(row) or (topic and row.startswith('Asiakirjat:'))\
            or (topic and row.startswith('koskeva')) or row == 'Ehdotuksen oppivelvollisuuslaiksi ja laiksi kansakoululaitoksen':
        return True
    return False


def speech_starters(row, row2):
    speech_start = re.compile("^[EF]d[\.,] ?(af|von|v\.)? ?[A-ZÅÄÖ].*?[:;] ")
    speech_start2 = re.compile(
        "^[A-ZÅÄÖ][^(:]*iniste[rt]i (af|von|v\.)? ?[A-ZÅÄÖ].*?[:;] ")
    speech_start3 = re.compile('Senaattori (af|von)? ?[A-ZÅÄÖ].*?[;:] ')
    long_title = re.compile(
        '^[A-ZÅÄÖ][^(:]*iniste[rt]i (af|von|v\.)? ?[A-ZÅÄÖ].*-$')
    long_title2 = re.compile('^[A-ZÅÄÖa-zåäö]+[;:] ')

    chairman = re.compile(
        '(F?[EF]nsimmäinen |Toinen )?(Puhemies|[vV]arapuhemies) ?(\(koputtaa\))? ?[;:]')
    chairman_knock = re.compile(
        '(F?[EF]nsimmäinen |Toinen )?(Puhemies|varapuhemies) ?')
    chairman_knock2 = re.compile('taa\) ?[;:]')
    continuation = re.compile('^Puhuja ?[;:]')
    eldest = re.compile('-?Ikäpuhemie ?s( \(ruotsiksi\))?[;:]')

    # the two first speeches if all time (don't get couaght otherwise)
    elder = re.compile(
        'Ikäpuhemies Hoikka lausui kokoontuneille edustaiille :')
    vuolijoki = re.compile(
        'Edustaja Vuolijoki, Väinö: Valtiopäiväjärjestyksen 67')

    if re.search(re.compile('y[\.,] ?m[\.,] '), row) or 'ilmoitetaan sairaaksi' in row:
        return False

    if speech_start.match(row) or speech_start2.match(row) or speech_start3.match(row) \
            or chairman.match(row) or continuation.match(row)\
            or (chairman_knock.match(row) and chairman_knock2.match(row2))\
            or (long_title.match(row) and long_title2.match(row2))\
            or eldest.match(row) or elder.match(row) or vuolijoki.match(row):
        return True
    return False


def document_start(row, year):
    # 5. Tiistaina 13 päivänä helmikuuta 1990
    if year > 1920:
        if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p[\-\.] .*kuuta 19[0123][0-9]').match(row):
            return True
    else:  # mostly no year in the title
        if re.compile('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p[\-\.] .*kuuta( 190[789])?').match(row):
            return True
    return False


def document_end(row):
    if 'Täysistunto lopetetaan ' in row \
            or re.compile('(Täys(i-)?)?[Ii]stunto päätty[yi] ').match(row)\
            or re.compile('.*?Puhemies julisti (tämän )?täysi-istunnon päät').match(row):  # or 'Täysistunto keskeytetään ' in row
        return True
    return False


def handle_session_start(rows, year):
    time = ''
    for row in rows:
        row = re.sub('klo|k[;:] ?lo|keilo', 'kello', row)
        if 'kello' in row:
            parts = row.split()
            if year > 1928:
                if len(parts) > 1:
                    if not 'kello' in parts[1]:
                        time = re.sub('\)|:', '', parts[1])
                        time = time.replace(',', '.')
                        return time.rstrip('.')
            else:  # 12 h clock
                for i in range(len(parts)):
                    if ('kello' in parts[i] and len(parts) > i+1):
                        time = re.sub(',|;|:|/', '.', parts[i+1])
                        break
                if time:  # am or pm?
                    am = re.search(re.compile('a\. ?P?p\.|yöllä'), row)
                    pm = re.search(re.compile(
                        '[il1]?\.? ?p\.|illalla|päivällä'), row)
                    if am:
                        return time
                    elif pm:
                        if re.compile('\d+\.\d$').match(time):
                            time += '0'
                        elif len(time) < 4:
                            time += '.00'
                        try:
                            temp = datetime.strptime(time + ' PM', '%I.%M %p')
                            return datetime.strftime(temp, '%H.%M')
                        except:
                            # print(row)
                            return ''
    return ''


def handle_session_end(row, row2, year):
    end = ''
    #row = re.sub('klo|k[;:] ?lo|keilo', 'kello', row)
    #row2 = re.sub('klo|k[;:] ?lo|keilo', 'kello', row2)
    temp = row + ' ' + row2
    temp = re.sub('klo|k[;:] ?lo|keilo', 'kello', temp)

    parts = temp.split()  # row.split() + row2.split()
    for i in range(len(parts)):
        if ('kello' in parts[i] and len(parts) > i+1):
            end = re.sub(',|;|:|/', '.', parts[i+1])
            break
    if end:  # am or pm?
        am = re.search(re.compile('a\. ?P?p\.|yöllä'), temp)  # row)
        pm = re.search(re.compile(
            '[il1]?\.? ?p\.|illalla|päivällä'), temp)  # row)
        if am:
            return end
        elif pm:
            if re.compile('\d+\.\d$').match(end):
                end += '0'
            elif len(end) < 4:
                end += '.00'
            try:
                temp = datetime.strptime(end + ' PM', '%I.%M %p')
                return datetime.strftime(temp, '%H.%M')
            except:
                # print(row)
                return ''
    return end or ''


def index_end(row):
    agenda = re.compile('Päiväjärjestyksessä olevat? asiat?:')
    notice = re.compile('(Il|Ti|H)moitusasiat:')
    roll_call = re.compile(
        '(Poissa oleviksi merkitään )?[Nn]imen ?huudo(ssa( merkitään)?|n asem[ea]sta)|Läsnä oleviksi tnerkitään')
    roll_call_pass = re.compile('Ajan voittamiseksi|Nimenhuutoa ei toimitettu')
    if agenda.match(row) or notice.match(row) or re.search(roll_call, row)\
            or re.search(roll_call_pass, row)\
            or 'Ikäpuhemiehen alkajaissanat' in row\
            or 'Ikäpuhemies.' == row or "Valitsijamiehet." == row\
            or 'kokoontui Suomen Eduskunta ensimäiseen' in row:
        return True
    return False


def end_compendium(row):
    if re.compile('\f+Liite\.').match(row)\
            or re.compile('\f+LIITTEITÄ\.').match(row)\
            or re.compile('\f+Jäsen- ja Asialuettelot').match(row):
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
    if 'Selonteko myönnetään oikeaksi.' in row\
            or re.compile('^Eduskunta on hyväksynyt ').match(row) \
            or 'Eduskunta on käsittelyn pohjaksi hy' in row\
            or 'Eduskunta on tässä äänestyksessä hyväksynyt' in row\
            or 'hyväksytään keskustelutta' in row\
            or 'Puhemiesneuvoston ehdotus hyväksytään' in row\
            or 'Puhemiehistön ehdotus hyväksytään' in row\
            or 'Vaaliin ryhdytään ja liput avataan.' in row\
            or row == 'Vaali toimitetaan.' or 'Vaalitoimitukseen ryhdytään.' in row\
            or 'Anomukseen suostutaan.' in row\
            or 'Anomuksiin suostutaan.' in row or 'Pyyntöön suostutaan.' in row\
            or re.compile('(Anomus|Menettelytapa|Toimenpide|Käsittelytapa|Ehdotus) hyväksytään\.').match(row)\
            or re.compile('(Täysi-)?[iI]stunto keskeytetään k(el)?lo ').match(row)\
            or re.compile('Täysi-istuntoa jatketaan').match(row)\
            or 'Puhemiehen mainitsema asiakirja luetaan' in row\
            or 'Puhemies ilmoitti vielä olevan kahdeksan puheenvuoroa' in row\
            or 'Sihteeri lukee' in row or 'Äänestysesitys ja päätös:' in row\
            or row == 'Sen jälkeen toimitetussa vaalissa Kansaneduskunnan'\
            or row == 'Ed.':
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


def session_details(row, parliament_year, document_num):
    # 145. Maanantaina 10 päivänä joulukuuta 1990
    # 15. Maanantaina 10 p. joulukuuta <- mostly no year before 1920 halfway
    # to year-month-day

    row = row.replace(')', '.')
    row = row.replace('(', '')
    parts = row.split()
    session = '{:s}/{:s}'.format(parts[0][:-1], parliament_year)

    if re.search('\f*\(?[0-9]+[\.,\)] [A-Z][a-zåäö]+ [0-9]+ p[\-\.] .*kuuta$', row):  # no year
        date = '{:s}-{:s}-{:s}'.format(parliament_year,
                                       parts[4][:-2], parts[2])
    else:
        date = '{:s}-{:s}-{:s}'.format(parts[-1].strip('s'),
                                       parts[-2][:-2], parts[-4])

    if (parliament_year == '1908' and int(document_num) >= 2):
        return session+'_II', parts[0][:-1], date
    return session, parts[0][:-1], date


def document_link(parliament_year, session_num, original_document_num):
    romans = {'1': 'I', '2': 'II', '3': 'III',
              '4': 'IV', '5': 'V', '6': 'VI'}

    if parliament_year == '1907':
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/1907/PTK_1907_{}.pdf'.format(romans[original_document_num])
    elif parliament_year in ['1908', '1909'] and original_document_num == '1':
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/{0}/PTK_{0}.pdf'.format(parliament_year)
    else:
        return 'https://s3-eu-west-1.amazonaws.com/eduskunta-asiakirja-original-documents-prod/suomi/1908/PTK_1908_{}_II_vp.pdf'.format(romans[str(int(original_document_num)-1)])


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
        '(\d+ )?Istunto \d+ p[\.,] [A-Z]?[a-z]kuuta [0-9]{4}')
    # '[0-9]* ?[A-Z][a-z]+na [0-9]+ p\. .*kuuta( [0-9]{4}|\.)')
    pagehead1 = re.compile(
        '[0-9]* ?[A-Z][a-z]+na [0-9]+ p\.$')
    pagehead2 = re.compile('[a-z]+kuuta( [0-9]{4}|\.)$')
    number_lines = re.compile('^[0-9\/\. ]+$')
    chair_questions = re.compile(
        '^Kysymy(s|ksiä) ja [sn]iih[ie]n annettu(ja)? vastau(s|ksia)[\.,]')

    if '\f' in content[i]:  # or number_lines.match(content[i]):
        return True
    elif date_pagehead.match(content[i]):
        return True
    elif pagehead1.match(content[i]) or pagehead2.match(content[i]):
        return True
    elif content[i].isdigit():
        return True
    elif 'Puheenvuoroa käyttäen lausuu:' in content[i] or 'Puheenvuoron saatuaan lausu' in content[i]\
            or 'Puheenvuoroa käyttää:' in content[i] or 'Puhevuoroa käyttäen lausuu:' in content[i]:
        return True
    elif chair_questions.match(content[i]):
        return True
    else:
        return False


def start_of_swedish_translation(row, row2):
    p = re.compile('on [rtv]uotsinkielisenä näin kuuluva[;:]')
    p2 = re.compile(
        'Ruotsinkielinen (vastaus|puhe|saarna) o(li|n) näin kuuluva[;:]')
    p3 = re.compile('Ruotsinkielisenä ')
    p1_1 = re.compile('o(n|li) [rvt]uotsin[a-zä]*\-')
    p1_2 = re.compile('näin kuuluva[:;]')
    p2_1 = re.compile('o(n|li) [rvt]uot[a-zä]*\-')
    p2_2 = re.compile('kielisenä näin kuuluva[:;]')
    p3_1 = re.compile('on(n|li) ([rtv]uotsinkielisenä|ruotsiksi)')
    p3_2 = re.compile('kuuluva[:;]')

    if re.search(p, row) or re.search(p2, row):
        return True
    if re.search(p1_1, row) and re.search(p1_2, row2):
        return True
    if re.search(p2_1, row) and re.search(p2_2, row2):
        return True
    if re.search(p3_1, row) and re.search(p3_2, row2):
        return True
    if re.search(p3, row) and re.search(p3_2, row2):
        return True
    return False


def edit_content(content):
    new = []

    # print(content)
    for i in range(len(content)):
        if not_content(content, i):
            continue
        elif (not content[i].strip() and content[i-1].strip() and not not_content(content, i-1)
                and i+1 < len(content) and not not_content(content, i+1) and content[i+1][0].isupper()):
            # empty row (and) is not the first (and) row-1 is real content (and) row is not last row
            # (and) row+1 has real content (and) starts with capital
            new.append('\n')
        else:
            row = re.sub('=|€|\*|<<|^>> | ?\|', '', content[i])
            row = re.sub('  +', ' ', row)
            if row.strip():
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

    bills = re.findall(
        '[Aa]rm[\.,] esitys [nN] ?[:;]o \d+', documents)
    committees = re.findall(
        '(?:suuren |[a-zåäöA-ZÅÄÖ]+- ja )?[a-zåäöA-ZÅÄÖ\-]*valiokunnan mietin(?:tö|nössä) n ?[:;]+o \d+(?: \(\d+ vp)?', documents)
    iniatives = re.findall(
        '(?:[EFe]d[\.,] (?:af|von)? ?[A-ZÅÄÖ][^,\(\)\d]+ (?:y\.? ?m\. )?)?[a-zåäö\-]+[\.,] ?a[l!][\.,] n ?[:;]+o \d+(?: \(\d+ vp)?', documents)
    iniatives2 = re.findall(
        '[eEF]d[\.,] (?:af|von)? ?[A-ZÅÄÖ].+ y[\.,] ?m[\.,] (?:edusk|anom)[\.,] e(?:sit|hd)[\.,] n ?[:;]o \d+', documents)
    iniatives3 = re.findall(
        '[eEF]d[\.,] (?:af|von)? ?[A-ZÅÄÖ].*? (?:y[\.,] ?m[\.,] )?(?:eduskuntaesitys|anomusehdotu(?:s|kse[nt])) n ?[:;]o \d+', documents)
    grace = re.findall('armollinen esitys n ?[:;]o \d+', documents)

    matches = bills + committees + iniatives + iniatives2 + iniatives3 + grace
    matches = list(set(matches))

    for match in matches:
        match = re.sub('N ?[:;]o', 'n:o', match)
        match = re.sub('lak[\.,] ?a[l!][\.,]', 'lakialoite', match)
        match = re.sub('toiv[\.,] ?a[l!][\.,]', 'toivomusaloite', match)
        match = re.sub('rah[\.,] ?a[l!][\.,]', 'raha-asia-aloite', match)
        match = re.sub('edusk[\.,] esit[\.,]', 'eduskuntaesitys', match)
        match = re.sub('[Aa]rm[\.,] esitys', 'armoitettu esitys', match)
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
        'hallituksen esitykset n ?[:;]+ot \d+[0-9\—\-\/,jasekävpP\.\,\(\) ]+[\)\d]', documents)
    iniatives = re.findall(
        '(?:[EFd]d[\.,] (?:af|von)? ?[A-ZÅÄÖ].+ y\.? ?m\. )?[a-zåäö\-]+[\.,] ?a[l!][\.,] n ?[:;]+ot \d+[0-9\—\-\/,jasekävpP\.\,\(\) ]+[\)\d]', documents)

    plurals = bills+iniatives

    # multiple document references
    # hallituksen esitykset n:ot 90 ja 235 (1974 vp.)
    if plurals:
        for doc in list(set(plurals)):
            doc = re.sub('n ?[:;]+ot', 'n:ot', doc)
            doc = re.sub('lak[\.,] ?a[l!][\.,]', 'lakialoite', doc)
            doc = re.sub('toiv[\.,] ?a[l!][\.,]', 'toivomusaloite', doc)
            doc = re.sub('rah[\.,] ?a[l!][\.,]', 'raha-asia-aloite', doc)
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
            if not document_start(rows[i], int(parliament_year)):
                if page == -1:
                    page = handle_page_num(rows[i], parliament_year)
                    if page != -1:
                        page -= 1
            if page != -1:
                page += rows[i].count('\f')
        if document_start(rows[i], int(parliament_year)):
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
            details = False
            session, session_num, date = session_details(
                rows[i], parliament_year, original_document_num)
            session_times[session] = {}
            session_times[session]['start'] = handle_session_start(
                rows[i+1:i+100], int(parliament_year))
        if document_end(rows[i]):
            discussion = False
            speech = False
            session_times[session]['end'] = handle_session_end(
                rows[i], rows[1+i], int(parliament_year))
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
        if start_of_swedish_translation(rows[i], rows[i+1]):
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
            if topic_starter(rows[i], rows[i-1] or ''):
                speech = False
                details = False
                topic = True
            if topic_enders(rows[i], rows[i+1]):
                topic = False
        if (not index and topic_details(rows[i], topic)):
            #speech = False
            details = True
            topic = False
            current_topic.append('>>>')
        if speech:  # (speech and rows[i].strip()):  # latter added
            # if rows[i].strip():
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
            if topic_starter(rows[i], rows[i-1] or ''):
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

            # taking care of the first two ever speeches that were problematic
            if i == 0 and all_speeches[i][2].startswith('Ikäpuhemies Hoikka lausui kokoontuneille edustaiille'):
                all_speeches[i][2] = 'Ikäpuhemies Hoikka'
            if i == 1 and all_speeches[i][2].startswith('Edustaja Vuolijoki, Väinö'):
                all_speeches[i][2] = 'Ed. Vuolijoki, Väinö'

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

            if ('(ruotsiksi)' in all_speeches[i][2] and 'Ikäpuhemies' in all_speeches[i][2]):
                all_speeches[i][2] = all_speeches[i][2].partition('(')[
                    0].strip()
                all_speeches[i][4] = '(ruotsiksi)' + all_speeches[i][4]

            if all_speeches[i][2].strip() == 'Puhuja':
                if 'uhemies' in all_speeches[i-1][2]:
                    all_speeches[i][2] = '<Puhuja>' + all_speeches[i-2][2]
                else:
                    all_speeches[i][2] = '<Puhuja>' + all_speeches[i-1][2]

            all_speeches[i][4] = re.sub(
                '  +\n', '', all_speeches[i][4]).strip('\n')

            all_speeches[i][2] = re.sub(
                ',? ?(joka )?lausu(en|akseen|u)', '', all_speeches[i][2])

            writer.writerow(
                [all_speeches[i][0], all_speeches[i][1], session_times[all_speeches[i][0]]['start'].strip('.'),
                 end.strip('.'), all_speeches[i][2], all_speeches[i][3], all_speeches[i][4], all_speeches[i][5], all_speeches[i][6]])
    # print(len(all_speeches))


if __name__ == "__main__":
    main(sys.argv[1])
