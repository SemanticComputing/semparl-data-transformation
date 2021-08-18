from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, FOAF, XSD, SKOS, DCTERMS
import csv
import re
import sys
import time
import datetime
import requests
from pprint import pprint


def find_interruptor_by_lastname(member_info, first, last, date):
    # for years up to 2010 where we don't know interruptors first name, only possible initials
    speech_date = time.strptime(date, '%Y-%m-%d')

    if '-' in first:  # M.-L.
        temp = first.partition('-')[0]
        first = temp.strip('.')
    if '.' in first:  # G.G.
        first = first.partition('.')[0]

    # first run considering only the "primary" lastname
    for row in member_info[1:]:
        if row[8]:  # started as MP
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if (row[2] == last.strip()):
                    if first.strip():
                        if (row[3] and row[3].startswith(first)
                                and row_end >= speech_date >= row_start):
                            return row[1]
                    else:
                        if row_end >= speech_date >= row_start:
                            return row[1]
            else:
                if (row[2] == last.strip()):
                    if first.strip():
                        if (row[3] and row[3].startswith(first) and speech_date >= row_start):
                            return row[1]
                    else:
                        if speech_date >= row_start:
                            return row[1]

    # second run trying alternative labels
    for row in member_info[1:]:
        if (row[8] and row[4]):  # started as MP + alternative names exist
            alters = [] if row[4] is None else row[4].split('; ')
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if (last.strip() in alters):
                    if first.strip():
                        if (row[3] and row[3].startswith(first)
                                and row_end >= speech_date >= row_start):
                            return row[1]
                    else:
                        if row_end >= speech_date >= row_start:
                            return row[1]
            else:
                if (last.strip() in alters):
                    if first.strip():
                        if (row[3] and row[3].startswith(first) and speech_date >= row_start):
                            return row[1]
                    else:
                        if speech_date >= row_start:
                            return row[1]

    return ''


def check_int_content(m):
    # sort interruptions from other info in paranthesis
    bad_patterns = [
        '^[A-ZÅÄÖ]+ \d?',   # Documents, all-cap abbreviations
        '\d+/\d+',          # More documents
        '^[ÄA]än[\.,]? ?\d+',     # Votes
        '^Kon[ec]e?ään[\.,]? ?\d+',     # Votes
        'Lähde:', 'Källa:',
        '^Liite ',
        '^Pöytäkirjan liite',
        'vastalause$',
        'Tulkki esittää puheenvuorosta suomenkielisen yhteenvedon',
    ]

    for bad in bad_patterns:
        if re.compile(bad).search(m):
            return False
    if not m[0].isupper() or m.isupper():  # or m[0].isdigit()
        return False
    if len(m) > 300:
        return False
    return True


def handle_interruptions(content):
    # find interruptions among speech
    interruptions = []
    matches = re.findall('\([^)]+\)|\[[^\]]+\]', content)

    if matches:
        for m in matches:
            m = re.sub('\(|\)|\[|\]', '', m).strip()
            if check_int_content(m):
                # Ed. M. Pohjola: Totta kai! — Ed. M. Korhonen: Voitte äänestää vastaan!
                if ' — ' in m and re.search(';|:', m[m.index(' — '):]):
                    separate_interruptions = m.split(' — ', 1)
                    # this will be a problem: "Eduskunnasta: Hurraa  — Naurua — Antti Rantakangas: Nyt päästään vauhtiin vasta!"
                    # second name will end up being: Naurua — Antti Rantakangas
                    # But does this happen?
                    for s in separate_interruptions:
                        interruptions.append(s.strip())
                else:
                    interruptions.append(m)
    return interruptions


def check_interrupter(content):
    # check if an interrupting agent has been clearly differentiated with ':'
    if (':'not in content and ';' not in content):
        return ''

    # Ed. M. Pohjola: Totta kai!
    return re.split(':|;', content, 1)[0]

    # sections = content.split(' — ')
    # agents = []
    # for s in sections:
    #     if ':' in s or ';' in s:
    #         agents.append(re.split(':|;', s, 1)[0])
    # return agents


def indentify_interrupter(agent, date, year, member_info, not_found):
    # 2011->
    # Paavo Arhinmäki
    # Ensimmäinen varapuhemies Mauri Pekkarinen
    # pre 2011:
    # Ed. Oksala | Fd. Aittoniemi | Rdm. Backlund
    # Pääministeri Virolainen | Min. Taina
    # Ed. U-M. Kukkonen | Ed Räisänen | Kanerva

    speaker_URI = ''
    # uris = []
    # for agent in agents:
    parts = agent.split()
    if int(year) >= 2011:
        if(len(parts) > 1 and parts[-2][0].isupper() and (parts[-1][0].isupper()
                                                          or parts[-1] == 'al-Taee')):
            speaker_URI, party_URI = find_speaker(
                member_info, parts[-2], parts[-1], date, not_found)
    else:
        if len(parts) > 2:  # there might be initials
            if parts[-2] in ['af', 'von']:
                speaker_URI = find_interruptor_by_lastname(
                    member_info, '', ' '.join(parts[-2:]), date)
            else:
                speaker_URI = find_interruptor_by_lastname(
                    member_info, parts[-2].strip('.'), parts[-1], date)
        else:
            try:
                speaker_URI = find_interruptor_by_lastname(
                    member_info, '', parts[-1], date)
            except:
                speaker_URI = ''

    # if speaker_URI:
    #     uris.append(speaker_URI)

    return speaker_URI  # uris


def make_doc_link(document, year):
    # Hallituksen esitys n:o 298/1993 vp
    # Lakialoite n:o 2
    # Valtiovarainvaliokunnan mietintö n:o 1
    # Mainittu kertomus (K n:o 4/1989 vp.)
    # Maa- ja metsätalousvaliokunnan mietintö 1/ 1996 vp

    link = ''
    id_num = ''
    document = document.replace('/ ', '/')
    parts = document.split()
    if int(year) < 1995:
        for i in range(len(parts)):
            if ('n:o' in parts[i] and i+1 < len(parts) and parts[i+1].strip()):
                id_num = parts[i+1].strip()
                break
    else:
        for part in parts:
            if part[0].isdigit():
                id_num = part
                break
    # id_num = document.partition('n:o ')[-1]  # .replace(' vp', '')
    if '/' in id_num:
        id_num = id_num.replace('/', '+').strip()
    else:
        id_num = id_num.strip() + '+' + year
    id_num = re.sub('[a-zåöäA-ZÅÄÖ\-\.\) ,>]', '', id_num)
    if 'Hallituksen esity' in document:
        link = 'https://www.eduskunta.fi/FI/vaski/HallituksenEsitys/Documents/he_{}.pdf'.format(
            id_num)
    elif 'Lakialoit' in document or 'lakialoit' in document:
        link = 'https://www.eduskunta.fi/FI/vaski/Lakialoite/Documents/la_{}.pdf'.format(
            id_num)
    elif 'ertomus' in document:
        if not 'n:o' in document:
            id_num = re.sub('[a-zåöäA-ZÅÄÖ\-\.\)\( ]',
                            '', document)
            if '/' in id_num:
                id_num = id_num.replace('/', '+')
            else:
                id_num = id_num.strip() + '+' + year

        link = 'https://www.eduskunta.fi/FI/vaski/Kertomus/Documents/k_{}.pdf'.format(
            id_num)
    elif 'Toivomus' in document:
        link = 'https://www.eduskunta.fi/FI/vaski/EduskuntaAloite/Documents/ta_{}.pdf'.format(
            id_num)
    elif 'Keskustelualoit' in document:
        link = 'https://www.eduskunta.fi/FI/vaski/eduskuntaaloite/Documents/ka_{}.pdf'.format(
            id_num
        )
    elif 'Valtioneuvoston kirjelmä' in document:
        link = 'https://www.eduskunta.fi/FI/vaski/Kirjelma/Documents/u_{}.pdf'.format(
            id_num
        )
    elif 'Valtioneuvoston tiedonanto' in document:
        link = 'https://www.eduskunta.fi/FI/vaski/Selonteko/Documents/vnt_{}.pdf'.format(
            id_num
        )
    elif 'valiokunnan mietintö' in document:
        abrev = ''
        if 'Suuren' in document:
            abrev = 'suvm'
        elif 'Perustus' in document:
            abrev = 'pevm'
        elif 'Ulkoasiain' in document:
            abrev = 'uavm'
        elif 'Valtiovarain' in document:
            abrev = 'vavm'
        elif 'Tarkastus' in document:
            abrev = 'trvm'
        elif 'Hallinto' in document:
            abrev = 'havm'
        elif 'Laki' in document:
            abrev = 'lavm'
        elif 'Toisen laki' in document:
            abrev = 'ii_lavm'
        elif 'Liikenne' in document:
            abrev = 'livm'
        elif 'metsätalous' in document:
            abrev = 'mmvm'
        elif 'Puolustus' in document:
            abrev = 'puvm'
        elif 'Sivistys' in document:
            abrev = 'sivm'
        elif 'Sosiaali' in document or 'terveys' in document:
            abrev = 'stvm'
        elif 'Talous' in document:
            abrev = 'tavm'
        elif 'Tiedustelu' in document:
            abrev = 'tivm'
        elif 'Tulevaisuus' in document:
            abrev = 'tuvm'
        elif 'Työ' in document:
            abrev = 'tyvm'
        elif 'Ympäristö' in document or 'Y mpäristö' in document:
            abrev = 'ymvm'
        link = 'https://www.eduskunta.fi/FI/vaski/Mietinto/Documents/{}_{}.pdf'.format(
            abrev, id_num)
    if link:
        try:
            response = requests.get(link)
            if str(response.status_code).startswith('2'):
                return link
            # print(document)
            # print(link)
            # print(response.status_code)
            # print('---')
            return ''
        except:
            #print('exception', document)
            return ''
    return link


def find_speaker(member_info, firstname, lastname,  date, not_found):  # , party
    if not firstname or not lastname:
        return '', ''
    lastname = re.sub('\xa0', '', lastname)

    # if (firstname == 'Leena-Kaisa' and lastname == 'Harkimo'):
    #    firstname = 'Leena'
    if (firstname == 'Timo' and lastname == 'Korhonen'):
        firstname = 'Timo V.'
    # if (firstname == 'Eeva Maria' and lastname == 'Maijala'):
    #    firstname = 'Eeva-Maria'

    speech_date = time.strptime(date, '%Y-%m-%d')

    for row in member_info[1:]:
        alters = [] if row[4] is None else row[4].split('; ')
        first_alters = [] if row[5] is None else row[5].split('; ')
        if row[8]:  # started as MP
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if ((row[2] == lastname or (alters and lastname in alters))
                    and (row[3] == firstname or firstname in first_alters)
                        and row_end >= speech_date >= row_start):
                    return row[1], row[11]
            else:
                if ((row[2] == lastname or (alters and lastname in alters))
                    and (row[3] == firstname or firstname in first_alters)
                        and speech_date >= row_start):
                    return row[1], row[11]

    # Occasionally there is a speech from a person who is not a MP, so there is no proper
    # time slice for them. Another run, taking only the person URI
    for row in member_info[1:]:
        alters = [] if row[4] is None else row[4].split('; ')
        first_alters = [] if row[5] is None else row[5].split('; ')
        if ((row[2] == lastname or (alters and lastname in alters))
                and (row[3] == firstname or firstname in first_alters)):
            return row[1], ''
    not_found.append([firstname, lastname])
    return '', ''


def correct_party_URI(party, double_URI):
    uris = {
        'SMP': 'http://ldf.fi/semparl/groups/Q1854411',
        'KESK': 'http://ldf.fi/semparl/groups/Q506591',
        'RKP': 'http://ldf.fi/semparl/groups/Q845537',
        'DEVA': 'http://ldf.fi/semparl/groups/Q540982',
        'SKDL': 'http://ldf.fi/semparl/groups/Q585735',
        'VAS': 'http://ldf.fi/semparl/groups/Q385927',
        'KP': 'http://ldf.fi/semparl/groups/Q1628434',
        'SDP': 'http://ldf.fi/semparl/groups/Q499029',
        'KOK': 'http://ldf.fi/semparl/groups/Q304191',
        'LKP': 'http://ldf.fi/semparl/groups/Q613849',
        'LIIK': 'http://ldf.fi/semparl/groups/Q52157683',
    }
    if party in uris:
        return uris[party]
    #print('Multiparty not in def correct_party_uri:',party)
    return double_URI


def find_doc_link(related_documents, document):
    for row in related_documents:
        if (row[0] in document and row[1] in document):
            return row[2]
    return ''


def end_day(end_time, date):
    p = re.compile('^0[0-6]?\.')
    if (end_time and p.match(end_time)):
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        d2 = d + datetime.timedelta(days=1)
        return str(d2).partition(' ')[0]
    return date


def make_doc_id(document, session, year):
    # Lakialoite n:o 21/1989 vp.
    id_ = ''
    document = re.sub(' >|,|"|:|<|—|=', '', document)
    if 1994 < int(year) < 2000:
        parts = document.split()
        if not '/' in document:
            document += year
        for part in parts:
            if part[0].isalpha():
                id_ += part[0:2].upper()
            elif part[0].isdigit():
                id_ += part.replace('/', '_')
        return id_
    else:
        parts = document.split('n:o')
        name = parts[0].split()
        # initials
        for word in name:
            if word.isdigit():
                id_ += word
            elif not word in ['ym.', 'n:o']:
                id_ += word[0:2].upper()
        if (len(parts) > 1 and parts[1].strip()):  # [Lakialoite, 21/1989 vp.]
            # there's a document number
            num_part = parts[1].split()            # [21/1989, vp.]
            if '/' in num_part[0].strip():
                id_ += re.sub('/', '_', num_part[0].strip())
                return id_
            return id_ + num_part[0].strip() + '_' + year
        else:
            return id_ + '_' + re.sub('/', '_', session)


###############################################################


def main(year):
    speeches = []
    related_documents = []
    member_info = []
    document_links = {}
    csv.field_size_limit(sys.maxsize)
    with open('speeches_{:s}.csv'.format(year), newline='') as f:
        reader = csv.reader(f)
        speeches = list(reader)

    source_year = year
    year = year.partition('_')[0]  # 1975_II

    if 1998 < int(year) < 2015:
        with open('related_documents_details_{:s}.csv'.format(year), newline='') as f:
            reader = csv.reader(f)
            related_documents = list(reader)
    with open('python_csv_parliamentMembers.csv') as f:
        reader = csv.reader(f, delimiter='\t')
        member_info = list(reader)
###############################################################
    g = Graph()  # speeches + interruptions
    sg = Graph()  # sessions + transripts
    ig = Graph()  # items + related documents

    s = Namespace('http://ldf.fi/semparl/')                 # :
    sp = Namespace('http://ldf.fi/semparl/speeches/')  # speech
    semparls = Namespace('http://ldf.fi/schema/semparl/')   # semparls
    s_status = Namespace('http://ldf.fi/semparl/status/')

    #speeches, interruptions
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("dct", DCTERMS)
    g.bind('semparls', semparls)
    g.bind('', s)
    g.bind("foaf", FOAF)
    g.bind('speeches', sp)
    g.bind('skos', SKOS)
    g.bind('s_status', s_status)

    #Sessions, transcripts
    sg.bind("xsd", XSD)
    sg.bind("rdfs", RDFS)
    sg.bind("dct", DCTERMS)
    sg.bind('semparls', semparls)
    sg.bind('', s)
    sg.bind('skos', SKOS)
    sg.bind('s_status', s_status)

    # Items, documents
    ig.bind("xsd", XSD)
    ig.bind("rdfs", RDFS)
    ig.bind("dct", DCTERMS)
    ig.bind('semparls', semparls)
    ig.bind('', s)
    ig.bind('skos', SKOS)

    finnish = URIRef('http://id.loc.gov/vocabulary/iso639-2/fin')
    swedish = URIRef('http://id.loc.gov/vocabulary/iso639-2/swe')

    current_session = ''
    current_topic = ''
    not_found = []
    item_index = 0

# 3
    # **************************************************************************
    # For cathering details about LAS assigning languages
    language_oddities = []
    # **************************************************************************
 # create parliamentary session instance and link it to electoral term
    parliamentary_session_URI = ''
    plenary_session_date = time.strptime(speeches[0][2], '%Y-%m-%d')

    with open('parliamentary_sessions.csv', newline='') as pf:
        reader = csv.reader(pf)
        parliamentary_sessions = list(reader)

    for row in parliamentary_sessions[1:]:
        start = time.strptime(row[1], '%d.%m.%Y')
        end = time.strptime(time.strftime("%d.%m.%Y", time.localtime()
                                          ), '%d.%m.%Y') if not row[2] else time.strptime(row[2], '%d.%m.%Y')
        if start <= plenary_session_date <= end:
            parliamentary_session_URI = URIRef('http://ldf.fi/semparl/times/parliamentary-sessions/parl_ses_{}'.format(
                row[0].replace(' ', '_'))
            )
            sg.add((parliamentary_session_URI, RDF.type,
                    semparls.ParliamentarySession))
            sg.add((parliamentary_session_URI, SKOS.prefLabel,
                    Literal('Valtiopäivät ' + row[0], lang="fi")))
            sg.add((parliamentary_session_URI,
                    semparls.electoralTerm, URIRef(row[3])))
            sg.add((parliamentary_session_URI, semparls.startDate,
                    Literal(time.strftime("%Y-%m-%d", start), datatype=XSD.date)))
            if row[2]:
                sg.add((parliamentary_session_URI, semparls.endDate,
                        Literal(time.strftime("%Y-%m-%d", end), datatype=XSD.date)))
            break

    # *****************************************************************************
    # helper methods that need to see the bindings
    def add_status(graph, subject, given_status):
        if 'yväksytty' in given_status:
            graph.add((subject, semparls.status, s_status.Accepted))
        elif re.search('ark[ia]stett?u', given_status):
            graph.add((subject, semparls.status, s_status.Validated))
        elif 'äsitelty' in given_status:
            graph.add((subject, semparls.status, s_status.Processed))
        elif 'almis' in given_status:
            graph.add((subject, semparls.status, s_status.Ready))
        elif re.search('ark[ia]stamaton', given_status):
            graph.add((subject, semparls.status, s_status.Unvalidated))
        elif 'unnistettu' in given_status:
            graph.add((subject, semparls.status, s_status.Recognized))
        else:
            graph.add((subject, semparls.status, s_status.Other))

    def add_document(document, item, doc):
        if re.search('mietin(tö|nöt)', document):
            ig.add((item, semparls.committeeReport, doc))
            ig.add((doc, RDF.type, semparls.CommitteeReport))
        elif 'HE' in document or 'Hallituksen esity' in document:
            ig.add((item, semparls.governmentProposal, doc))
            ig.add((doc, RDF.type, semparls.GovernmentProposal))
        elif 'LA' in document or 'akialoit' in document:
            ig.add((item, semparls.legislativeMotion, doc))
            ig.add((doc, RDF.type, semparls.LegislativeMotion))
        elif 'VK' in document or 'älikysymys' in document:
            ig.add((item, semparls.interpellation, doc))
            ig.add((doc, RDF.type, semparls.Interpellation))
        elif 'SKT' in document or 'uullinen kysymy' in document:
            ig.add((item, semparls.spokenQuestion, doc))
            ig.add((doc, RDF.type, semparls.SpokenQuestion))
        elif 'ertomus' in document:
            ig.add((item, semparls.account, doc))
            ig.add((doc, RDF.type, semparls.Account))
        elif 'eskustelualoit' in document:
            ig.add((item, semparls.debateMotion, doc))
            ig.add((doc, RDF.type, semparls.DebateMotion))
        elif 'aha-asia-aloit' in document:
            ig.add((item, semparls.financialMotion, doc))
            ig.add((doc, RDF.type, semparls.FinancialMotion))
        elif re.search('((Toi)?[vV]omusaloit|[Aa]nom(\. |us)(ehd(\.|otus)| ?n:o))', document):
            ig.add((item, semparls.petitionaryMotion, doc))
            ig.add((doc, RDF.type, semparls.PetitionaryMotion))
        elif re.search('aloitt?e', document):
            ig.add((item, semparls.motion, doc))
            ig.add((doc, RDF.type, semparls.Motion))
        else:
            ig.add((item, semparls.relatedDocument, doc))
            ig.add((doc, RDF.type, semparls.Document))

    # ********************************************************************************
    #print("VAJAA LISTA")
    for row in speeches:

        csv_speech_id = row[0].replace('.', '_')
        csv_session = row[1]
        date = row[2]
        session_start = row[3]
        session_end = row[4]
        firstname = row[5].strip()
        lastname = row[6].strip()
        csv_party = row[7].strip()
        csv_topic = row[8]
        content = row[9].strip()
        response = row[10].strip()
        status = row[11]
        version = row[12].lstrip('versio')
        link = row[13].strip()
        lang = row[14]
        original_speaker = row[15]
        speech_start, speech_end = '', ''
        csv_speaker_ID = ''
        speech_version, speech_status = '', ''
        page = ''
        subject_parts = ''
        #interpreted_party = ''
        plenary_session = csv_session.partition('/')[0]

        if re.compile('\d\.\d\d').match(session_end):
            session_end = '0' + session_end

    # check language for years before last half of 1999 + set other metadata fot that period
        if (int(year) < 2000 and not(int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86)):
            page = row[16]

    # gathering language recognition issues
       # if lang=='' or lang not in ['sv:fi', 'fi:sv', 'fi', 'sv']:
        #    language_oddities.append([csv_speech_id, lang, content])

    # metadata from XML-source
        if int(year) > 2014:
            if len(row) > 16:
                csv_speaker_ID = row[16]
            if len(row) > 17:
                speech_start = row[17]
            if len(row) > 18:
                speech_end = row[18]
            if len(row) > 19:
                speech_status = row[19]
            if len(row) > 20:
                speech_version = row[20].lstrip('versio')

        speech = URIRef(
            'http://ldf.fi/semparl/speeches/s{}'.format(csv_speech_id))
        speaker_URI, party_URI = find_speaker(
            member_info, firstname, lastname, date, not_found)

    # Speaker was given multiple parties, hence multiple URIs
        if ';' in party_URI:
            party_URI = correct_party_URI(csv_party, party_URI)
            #####################
            # PLACEHOLDER
            if ';' in party_URI:
                party_URI = party_URI.partition(';')[0]
            # FIX ISSUE
            ###############################

    # speech order number, session, transcript info
        order = csv_speech_id.rpartition('_')[2]
        session = URIRef(
            'http://ldf.fi/semparl/times/plenary-sessions/ps_{}'.format(re.sub('/', '_', csv_session)))
        transcript = URIRef(
            'http://ldf.fi/semparl/documents/ptk_{}'.format(re.sub('/', '_', csv_session)))

    # add speech and speaker info to graph
        g.add((speech, RDF.type, semparls.Speech))
        if speaker_URI:
            g.add((speech, semparls.speaker, URIRef(speaker_URI)))
        if party_URI:
            g.add((speech, semparls.party, URIRef(party_URI)))

    # prefLabel Vp 2021 - istunto 2 - puhe 3 (Veikko Vennamo)@fi
        speech_pref_label = 'Vp {} - istunto {} - puhe {} '.format(
            source_year, plenary_session, order)
        if 'uhemies' in csv_party:
            speech_pref_label += '({})'.format(csv_party)
        else:
            speech_pref_label += '({} {})'.format(firstname, lastname)
        g.add((speech, SKOS.prefLabel, Literal(speech_pref_label, lang="fi")))

      # SPEAKER LITERAL & LITERAL INTERPRETED

        # if '<Puhuja>' in original_speaker:
        #     original_speaker = original_speaker.replace('<Puhuja>', '',)
        #     g.add((speech, semparls.speakerLiteral,
        #            Literal('Puhuja')))
        #     g.add((speech, semparls.speakerLiteralInterpreted,
        #            Literal(original_speaker)))
        # else:
        #     if original_speaker:
        #         g.add((speech, semparls.speakerLiteral, Literal(
        #             original_speaker)))

        if '<Puhuja>' in original_speaker:
            original_speaker = original_speaker[1:].partition('>')[0]
        g.add((speech, semparls.speakerAsInSource, Literal(original_speaker)))

        #######################################

    # add speech metadata
        g.add((speech, semparls.speechOrder, Literal(order, datatype=XSD.integer)))
        g.add((speech, semparls.content, Literal(content)))
        g.add((speech, DCTERMS.date, Literal(date, datatype=XSD.date)))
        g.add((speech, semparls.plenarySession, session))
        g.add((speech, semparls.diary, URIRef(link)))
        # check if session end time is after midnight, adjust endDate
        end_date = end_day(session_end, date)
        g.add((speech, semparls.endDate, Literal(end_date, datatype=XSD.date)))

    # interruptions
        interruptions = handle_interruptions(content)
        if interruptions:
            for i in range(len(interruptions)):
                interruptions[i] = interruptions[i].replace('\n', '')
                inter_id = csv_speech_id+'_'+str(i+1)
                interruption = URIRef(
                    'http://ldf.fi/semparl/speeches/in{}'.format(inter_id))
                g.add((speech, semparls.isInterruptedBy, interruption))
                g.add((interruption, RDF.type, semparls.Interruption))
                g.add((interruption, semparls.content,
                       Literal(interruptions[i])))
                g.add((interruption, SKOS.prefLabel, Literal('Vp {} - istunto {} - puhe {} - Keskeytys - {}'.format(
                    source_year, plenary_session, order, str(i+1)), lang="fi")))
        # check if interrupter has been named:
                interrupter = check_interrupter(interruptions[i])
                if interrupter:
                    g.add((interruption, semparls.interrupter, Literal(interrupter)))
                    interrupter_URI = indentify_interrupter(
                        interrupter, date, year, member_info, not_found)
                    if interrupter_URI:
                        g.add((interruption, semparls.speaker,
                               URIRef(interrupter_URI)))

                    # [g.add((interruption, semparls.interrupter, Literal(agent)))
                    #  for agent in interrupter]
                    # interrupter_URIs = indentify_interrupter(
                    #     interrupter, date, year, member_info, not_found)
                    # if interrupter_URIs:
                    #     [g.add((interruption, semparls.speaker, URIRef(uri)))
                    #      for uri in interrupter_URIs]

    # Varying metadata if exists: page, speech-specific times, status, version
        if (page and '-1' not in page):
            g.add((speech, semparls.page, Literal(page, datatype=XSD.integer)))
        if speech_start:
            g.add((speech, semparls.startTime, Literal(
                speech_start.partition('T')[2], datatype=XSD.time)))
        if speech_end:
            g.add((speech, semparls.endTime, Literal(
                speech_end.partition('T')[2], datatype=XSD.time)))
        if speech_status:
            add_status(g, speech, speech_status)
        if speech_version:
            g.add((speech, semparls.version, Literal(
                float(speech_version.lstrip('.')), datatype=XSD.decimal)))

    # speakers role
        if csv_party.strip() and not csv_party.isupper():  # Special role mentioned
            csv_party = re.sub('>|<|\|', '', csv_party)
            role = URIRef(
                'http://ldf.fi/semparl/{}'.format(re.sub(' ', '_', csv_party)))
        else:  # default
            role = URIRef(
                'http://ldf.fi/semparl/Kansanedustaja')
        g.add((speech, semparls.role, role))

        # party as interpreted from external mp-info as literal
        # if (interpreted_party and interpreted_party.isupper()):
        #     g.add((speech, semparls.partyLiteralInterpreted,
        #            Literal(interpreted_party)))
        # elif csv_party.isupper():
        #     g.add((speech, semparls.partyLiteral,
        #            Literal(csv_party)))

    # Add party as in source for easier validation
        # if csv_party.isupper():
        #      g.add((speech, semparls.partyInSource,
        #             Literal(csv_party, datatype=XSD.string)))

    # speech type, language
        if response and not response == 'Varsinainen puheenvuoro':
            speech_type = URIRef(
                'http://ldf.fi/semparl/speechtypes/{}'.format(re.sub(' ', '', response.title())))
        elif 'uhemies' in original_speaker:
            speech_type = URIRef(
                'http://ldf.fi/semparl/speechtypes/PuhemiesPuheenvuoro')
        else:
            speech_type = URIRef(
                'http://ldf.fi/semparl/speechtypes/Puheenvuoro')
        g.add((speech, semparls.speechType, speech_type))

        if lang:
            if 'fi' in lang:
                g.add((speech, DCTERMS.language, finnish))
            if 'sv' in lang:
                g.add((speech, DCTERMS.language, swedish))
            if content == 'Kannatan.':
                g.add((speech, DCTERMS.language, finnish))

        # create item instance from speech topic
        if csv_topic.strip():  # There's a topic
            subject_parts = csv_topic.split('>>>')
            if (len(subject_parts) > 1 and not subject_parts[0].strip()):
                # only documents, no separate topic, splitting creates empty first member
                subject = subject_parts[1]
            else:
                subject = re.sub('[0-9]+\)\W', '', subject_parts[0])

            if current_topic != csv_topic:
                current_topic = csv_topic
                item_index += 1
            item = URIRef(
                'http://ldf.fi/semparl/items/i{}'.format(source_year+csv_session.partition('/')[0]+str(item_index)))

            # link item to speech and add to item graph
            g.add((speech, semparls.item, item))
            ig.add((item, RDF.type, semparls.Item))
            ig.add((item, semparls.plenarySession, session))
            ig.add((item, SKOS.prefLabel, Literal(subject.strip(), lang='fi')))

            # URL to item/topic
            pattern = re.compile('\d+\)')
            if int(year) > 2014\
                    or (int(year) < 2000 and not(int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86)):
                item_link = link
            elif 1998 < int(year) < 2015:
                if pattern.match(csv_topic):
                    section = csv_topic.partition(')')[0]
                    item_link = 'https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+{}#KOHTA{}'.format(
                        csv_session, section)
                else:
                    item_link = link
            ig.add((item, semparls.diary, URIRef(item_link)))

        # if related documents
        if len(subject_parts) > 1:
            for document in subject_parts[1:]:
                document = document.replace('n;o', 'n:o')
                # make document_id
                if (int(year) < 2000 and not(int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86)):
                    document_id = make_doc_id(document, csv_session, year)
                    document_id = re.sub('\.|\||\]|\[', '', document_id)
                else:
                    if int(year) < 2015:
                        l = document.split('\xa0')
                    else:
                        l = document.split('  ')
                    if len(l) < 2:
                        continue
                    l2 = l[1].split(' (')
                    document_id = re.sub(' |/', '_', l2[0].strip())

                doc = URIRef(
                    'http://ldf.fi/semparl/documents/{}'.format(document_id))
                add_document(document, item, doc)

                if int(year) > 1999 or (int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86):
                    if int(year) < 2015:
                        doc_link = find_doc_link(
                            related_documents, document)
                        ig.add((doc, SKOS.prefLabel, Literal(
                            re.sub('\xa0', '', document), lang="fi")))
                    else:  # elif 1998 < int(year) < 2015: virhe?
                        temp_l = re.sub(' ', '_', l2[0].strip())
                        doc_link = 'https://www.eduskunta.fi/FI/vaski/KasittelytiedotValtiopaivaasia/Sivut/{}.aspx'.format(
                            re.sub('\/', '+', temp_l.strip('_vp'))
                        )
                        ig.add((doc, SKOS.prefLabel, Literal(
                            re.sub('  +', ' ', document), lang="fi")))
                    ig.add((doc, semparls.id, Literal(
                        l2[0].strip(), datatype=XSD.string)))
                    ig.add((doc, semparls.url, URIRef(doc_link)))
                elif int(year) < 1980:
                    # no document URL
                    ig.add((doc, SKOS.prefLabel, Literal(
                        document.strip(), lang="fi")))
                else:
                    if document in document_links:
                        doc_link = document_links[document]
                    else:
                        doc_link = make_doc_link(document, year)
                        document_links[document] = doc_link
                    if doc_link:
                        ig.add((doc, semparls.url, URIRef(doc_link)))
                    ig.add((doc, SKOS.prefLabel, Literal(
                        document.strip(), lang="fi")))

    # create session instance
        if current_session != csv_session:
            current_session = csv_session
            sg.add((session, RDF.type, semparls.PlenarySession))
            sg.add((session, SKOS.prefLabel, Literal(
                csv_session.replace('_', ' ') + ' vp', lang='fi')))
            sg.add((session, DCTERMS.date, Literal(date, datatype=XSD.date)))
            if session_start:
                sg.add((session, semparls.startTime, Literal(
                    re.sub('\.', ':', session_start) + ':00', datatype=XSD.time)))
            end_date = end_day(session_end, date)
            sg.add((session, semparls.endDate,
                    Literal(end_date, datatype=XSD.date)))
            if session_end:
                sg.add((session, semparls.endTime, Literal(
                    re.sub('\.|\-', ':', session_end) + ':00', datatype=XSD.time)))
            sg.add((session, semparls.transcript, transcript))
            sg.add((session, semparls.parliamentarySession,
                    URIRef(parliamentary_session_URI)))

    # Trancript info
            sg.add((transcript, RDF.type, semparls.Transcript))
            sg.add((transcript, SKOS.prefLabel, Literal(
                'PTK ' + csv_session.replace('_', ' ') + ' vp', lang='fi')))
            if version.strip():
                sg.add((transcript, semparls.version, Literal(
                    float(version.lstrip('.')), datatype=XSD.decimal)))
            if status.strip():
                add_status(sg, transcript, status)
            if int(year) > 2014:
                transcript_url = 'https://www.eduskunta.fi/FI/vaski/Poytakirja/Sivut/PTK_{}.aspx'.format(
                    re.sub('\/', '+', csv_session)
                )
            elif int(year) > 1999 or (int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86):
                transcript_url = 'https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+{}'.format(
                    csv_session)
            else:
                transcript_url = link
            sg.add((transcript, semparls.url, URIRef(
                transcript_url)))

    # print(g.serialize(format='turtle').decode('utf-8'))
    g.serialize(destination='speeches_{}.ttl'.format(
        source_year), format='turtle')
    sg.serialize(destination='sessions_and_transcripts_{}.ttl'.format(
        source_year), format='turtle')
    ig.serialize(destination='items_and_documents_{}.ttl'.format(
        source_year), format='turtle')
    print('personal ID number not found for following persons:')
    pprint(not_found)
    #print('HTTP-haut POIS PÄÄLTÄ')

    # with open('language_logs/language_issues_{:s}.csv'.format(source_year), 'w', newline='') as lang_save_to:
    #     writer = csv.writer(lang_save_to, delimiter=',')
    #     writer.writerow(['speechID', 'langTagsByLAS', 'content'])
    #     writer.writerows(language_oddities)


if __name__ == "__main__":
    main(sys.argv[1])
