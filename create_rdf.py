from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, FOAF, XSD, SKOS, DCTERMS
import csv
import re
import sys
import time
import datetime
import requests
from pprint import pprint


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
            print(document)
            print(link)
            print(response.status_code)
            print('---')
            return ''
        except:
            print('exception', document)
            return ''
    return link


def find_speaker(member_info, firstname, lastname, party,  date, not_found):
    if not firstname or not lastname:
        return '', ''
    lastname = re.sub('\xa0', '', lastname)

    if (firstname == 'Leena-Kaisa' and lastname == 'Harkimo'):
        firstname = 'Leena'
    if (firstname == 'Timo' and lastname == 'Korhonen'):
        firstname = 'Timo V.'
    if (firstname == 'Eeva Maria' and lastname == 'Maijala'):
        firstname = 'Eeva-Maria'

    speech_date = time.strptime(date, '%Y-%m-%d')

    for row in member_info[1:]:
        alters = [] if row[4] is None else row[4].split('; ')
        if row[8]:  # started as MP
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if ((row[2] == lastname or (alters and lastname in alters))
                    and (row[3] == firstname)
                        and row_end >= speech_date >= row_start):
                    return row[1], row[11]
            else:
                if ((row[2] == lastname or (alters and lastname in alters))
                    and (row[3] == firstname)  # or firstname in row[3])
                        and speech_date >= row_start):
                    return row[1], row[11]

    # Occasionally there is a speech from a person who is not a MP anymore, so there is no proper
    # time slice for them. Another run, taking only the person URI
    for row in member_info[1:]:
        if ((row[2] == lastname or (alters and lastname in alters))
                and (row[3] == firstname)):  # or firstname in row[3])):
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
    }
    if party in uris:
        return uris[party]
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
    document = document.replace(' >', '')
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
            id_ += word[0:2].upper()
        if (len(parts) > 1 and parts[1].strip()):  # [Lakialoite, 21/1989 vp.]
            # there's a document number
            num_part = parts[1].split()            # [21/1989, vp.]
            if '/' in num_part[0].strip():
                id_ += re.sub('/', '_', num_part[0].strip())
                return id_
            # id_ += re.sub('/', '_', num_part[0].strip())
            return id_ + num_part[0].strip() + '_' + year
        else:
            return id_ + '_' + re.sub('/', '_', session)


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

    g = Graph()  # speeches
    sg = Graph()  # sessions + transripts
    ig = Graph()  # items + related documents

    s = Namespace('http://ldf.fi/semparl/')                 # :
    semparls = Namespace('http://ldf.fi/schema/semparl/')   # semparls

    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("dct", DCTERMS)
    g.bind('semparls', semparls)
    g.bind('', s)

    sg.bind("xsd", XSD)
    sg.bind("rdfs", RDFS)
    sg.bind("dct", DCTERMS)
    sg.bind('semparls', semparls)
    sg.bind('', s)

    ig.bind("xsd", XSD)
    ig.bind("rdfs", RDFS)
    ig.bind("dct", DCTERMS)
    ig.bind('semparls', semparls)
    ig.bind('', s)

    finnish = URIRef('http://id.loc.gov/vocabulary/iso639-2/fin')
    swedish = URIRef('http://id.loc.gov/vocabulary/iso639-2/swe')

    current_session = ''
    current_topic = ''
    not_found = []
    item_index = 0
    # **************************************************************************
    # **************************************************************************
    for row in speeches:
        csv_speech_id = row[0]
        csv_session = row[1]
        date = row[2]
        session_start = row[3]
        session_end = row[4]
        firstname = row[5].strip()
        lastname = row[6].strip()
        csv_party = row[7].strip()
        csv_topic = row[8]
        content = row[9].strip()
        response = row[10]
        status = row[11]
        version = row[12].lstrip('versio')
        link = row[13]
        lang = row[14]
        original_speaker = row[15]
        speech_start, speech_end = '', ''
        csv_speaker_ID = ''
        speech_version, speech_status = '', ''
        page = ''
        subject_parts = ''
        interpreted_party = ''

        if (int(year) < 2000 and not(int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86)):
            page = row[16]
            interpreted_party = csv_party.strip()
            try:
                parameters = {'text': content}
                results = requests.get(
                    'http://demo.seco.tkk.fi/las/identify', params=parameters).json()
                tags = []
                tags = [k for d in results['details']
                        ['languageDetectorResults'] for k in d.keys()]
                lang = ':'.join(tags)
            except:
                lang = ''
            print(csv_speech_id)

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

        speech = URIRef('http://ldf.fi/semparl/s{}'.format(csv_speech_id))
        speaker_URI, party_URI = find_speaker(
            member_info, firstname, lastname, csv_party, date, not_found)

        # Speaker was given multiple parties, hence multiple URIs
        if ';' in party_URI:
            party_URI = correct_party_URI(csv_party, party_URI)

        order = csv_speech_id.rpartition('.')[2]
        session = URIRef(
            'http://ldf.fi/semparl/ps_{}'.format(re.sub('/', '_', csv_session)))
        transcript = URIRef(
            'http://ldf.fi/semparl/ptk_{}'.format(re.sub('/', '_', csv_session)))

        g.add((speech, RDF.type, semparls.Speech))
        g.add((speech, semparls.speaker, URIRef(speaker_URI)))
        g.add((speech, semparls.party, URIRef(party_URI)))

        if '<Puhuja>' in original_speaker:
            original_speaker = original_speaker.replace('<Puhuja>', '',)
            g.add((speech, semparls.speaker_literal,
                   Literal('Puhuja')))
            g.add((speech, semparls.speaker_literal_interpreted,
                   Literal(original_speaker)))
        else:
            g.add((speech, semparls.speaker_literal, Literal(
                original_speaker)))

        g.add((speech, semparls.speechOrder, Literal(order, datatype=XSD.integer)))
        g.add((speech, semparls.content, Literal(content)))
        g.add((speech, DCTERMS.date, Literal(date, datatype=XSD.date)))
        g.add((speech, semparls.end_date, Literal(date, datatype=XSD.date)))
        g.add((speech, semparls.session, session))
        g.add((speech, semparls.diary, URIRef(link)))

        if (page and '-1' not in page):
            g.add((speech, semparls.page, Literal(page, datatype=XSD.integer)))
        if speech_start:
            g.add((speech, semparls.end_time, Literal(
                speech_start, datatype=XSD.datetime)))
        if speech_end:
            g.add((speech, semparls.start_time, Literal(
                speech_end, datatype=XSD.datetime)))
        if speech_status:
            if 'yväksytty' in speech_status:
                g.add((speech, semparls.status, s.Accepted))
            elif 'arkistettu' in speech_status:
                g.add((speech, semparls.status, s.Validated))
            elif 'äsitelty' in speech_status:
                g.add((speech, semparls.status, s.Processed))
            elif 'almis' in speech_status:
                g.add((speech, semparls.status, s.Ready))
            else:
                g.add((speech, semparls.status, s.Other))
        if speech_version:
            g.add((speech, semparls.version, Literal(
                float(speech_version.lstrip('.')), datatype=XSD.decimal)))

        if not csv_party.isupper():
            csv_party = re.sub('>|<|\|', '', csv_party)
            role = URIRef(
                'http://ldf.fi/semparl/{}'.format(re.sub(' ', '_', csv_party)))
            g.add((speech, semparls.role, role))

        if (interpreted_party and interpreted_party.isupper()):
            g.add((speech, semparls.party_literal_interpreted,
                   Literal(interpreted_party)))
        elif csv_party.isupper():
            g.add((speech, semparls.party_literal,
                   Literal(csv_party)))

        if 'astauspuheenvuoro' in response:
            g.add((speech, semparls.isResponse, Literal(True)))

        if lang:
            if 'fi' in lang:
                g.add((speech, DCTERMS.language, finnish))
            if 'sv' in lang:
                g.add((speech, DCTERMS.language, swedish))
            if content == 'Kannatan.':
                g.add((speech, DCTERMS.language, finnish))

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
                'http://ldf.fi/semparl/i{}'.format(source_year+csv_session.partition('/')[0]+str(item_index)))
            g.add((speech, semparls.item, item))
            ig.add((item, RDF.type, semparls.Item))
            ig.add((item, semparls.session, session))
            ig.add((item, DCTERMS.title, Literal(subject.strip(), lang='fi')))

            # link to item/topic
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
                    document_id = make_doc_id(document, session, year)
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
                    'http://ldf.fi/semparl/{}'.format(document_id))

                if 'HE' in document or 'Hallituksen esity' in document:
                    ig.add((item, semparls.government_proposal, doc))
                    ig.add((doc, RDF.type, semparls.GovernmentProposal))
                elif 'LA' in document or 'akialoit' in document:
                    ig.add((item, semparls.legislative_motion, doc))
                    ig.add((doc, RDF.type, semparls.LegislativeMotion))
                elif 'mietintö' in document:
                    ig.add((item, semparls.committee_report, doc))
                    ig.add((doc, RDF.type, semparls.CommitteeReport))
                elif 'VK' in document:
                    ig.add((item, semparls.interpellation, doc))
                    ig.add((doc, RDF.type, semparls.Interpellation))
                elif 'ertomus' in document:
                    ig.add((item, semparls.account, doc))
                    ig.add((doc, RDF.type, semparls.Account))
                elif 'Keskustelualoite' in document:
                    ig.add((item, semparls.debate_motion, doc))
                    ig.add((doc, RDF.type, semparls.DebateMotion))
                else:
                    ig.add((item, semparls.related_document, doc))
                    ig.add((doc, RDF.type, semparls.RelatedDocument))

                if int(year) > 1999 or (int(year) == 1999 and int(csv_session.partition('/')[0]) >= 86):
                    if int(year) < 2015:
                        doc_link = find_doc_link(
                            related_documents, document)
                        ig.add((doc, DCTERMS.title, Literal(
                            re.sub('\xa0', '', document), lang="fi")))
                    else:  # elif 1998 < int(year) < 2015: virhe?
                        temp_l = re.sub(' ', '_', l2[0].strip())
                        doc_link = 'https://www.eduskunta.fi/FI/vaski/KasittelytiedotValtiopaivaasia/Sivut/{}.aspx'.format(
                            re.sub('\/', '+', temp_l.strip('_vp'))
                        )
                        ig.add((doc, DCTERMS.title, Literal(
                            re.sub('  ', ' ', document), lang="fi")))
                    ig.add((doc, semparls.id, Literal(
                        l2[0].strip(), datatype=XSD.string)))
                    ig.add((doc, semparls.url, URIRef(doc_link)))
                elif int(year) < 1980:
                    # no document URL
                    ig.add((doc, DCTERMS.title, Literal(
                        document.strip(), lang="fi")))
                else:
                    if document in document_links:
                        doc_link = document_links[document]
                    else:
                        doc_link = make_doc_link(document, year)
                        document_links[document] = doc_link
                    if doc_link:
                        ig.add((doc, semparls.url, URIRef(doc_link)))
                    ig.add((doc, DCTERMS.title, Literal(
                        document.strip(), lang="fi")))

        if current_session != csv_session:
            current_session = csv_session
            sg.add((session, RDF.type, semparls.Session))
            sg.add((session, semparls.id, Literal(csv_session)))
            sg.add((session, DCTERMS.date, Literal(date, datatype=XSD.date)))
            if session_start:
                sg.add((session, semparls.start_time, Literal(
                    re.sub('\.', ':', session_start) + ':00', datatype=XSD.time)))
            end_date = end_day(session_end, date)
            sg.add((session, semparls.end_date,
                    Literal(end_date, datatype=XSD.date)))
            if session_end:
                sg.add((session, semparls.end_time, Literal(
                    re.sub('\.', ':', session_end) + ':00', datatype=XSD.time)))
            sg.add((session, semparls.transcript, transcript))

            sg.add((transcript, RDF.type, semparls.Transcript))
            if version.strip():
                sg.add((transcript, semparls.version, Literal(
                    float(version.lstrip('.')), datatype=XSD.decimal)))
            if status.strip():
                if 'yväksytty' in status:
                    sg.add((transcript, semparls.status, s.Accepted))
                elif 'arkistettu' in status:
                    sg.add((transcript, semparls.status, s.Validated))
                elif 'äsitelty' in status:
                    sg.add((transcript, semparls.status, s.Processed))
                elif 'almis' in status:
                    sg.add((transcript, semparls.status, s.Ready))
                else:
                    sg.add((transcript, semparls.status, s.Other))
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


if __name__ == "__main__":
    main(sys.argv[1])
