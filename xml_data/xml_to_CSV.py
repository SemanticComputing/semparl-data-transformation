from bs4 import BeautifulSoup
from urllib import request
import json
import re
import csv
import requests
import sys
from pprint import pprint


def extract_speech_details(tag_content):
    details = {
        "speechOrder": tag_content['vsk1:puheenvuoroJNro'].strip(),
        "startTime": tag_content['vsk1:puheenvuoroAloitusHetki'].strip(),
        "endTime": '',
        "language": tag_content['met1:kieliKoodi'].strip(),
        "status": tag_content['met1:tilaKoodi'].strip(),
        "textVersion": tag_content['met1:versioTeksti'].strip(),
        "speechID": tag_content['met1:muuTunnus'].strip(),
    }
    if 'vsk1:puheenvuoroLopetusHetki' in tag_content.keys():
        details['endTime'] = tag_content['vsk1:puheenvuoroLopetusHetki'].strip()
    else:
        details['endTime'] = ''
    return details


def extract_content(speech_section):
    content = ''
    for child in speech_section.children:
        if 'PuheenjohtajaRepliikki' in child.name:
            content += '(' + child.find('vsk1:PuheenjohtajaTeksti').string + ': ' \
                + child.find('sis:KappaleKooste').string + ')'
        elif ('KappaleKooste' in child.name and child.string):
            content += child.string + '\n'

    """ content_parts = []
    content = ''
    for child in speech_section.descendants:
        if child.name == 'KappaleKooste':
            content_parts.append(child.string)

    for part in content_parts:
        if isinstance(part, str):  # covering erroneus tagging in original xml
            content += '{:s} '.format(part) """
    return content.rstrip('\n')


def extract_cp_content(speech):
    """  print('**********************')
    contents = speech.find_all('sis:KappaleKooste')
    print(contents) """
    content = ''
    speech.find('vsk1:PuheenjohtajaTeksti').extract()
    content = speech.strings
    return re.sub('  ', ' ', ' '.join(content))


def date_times(section):
    if section:
        # print(section.find('met1:NimekeTeksti'))
        parts = section.find('met1:NimekeTeksti').string.split()
        date = parts[1].split('.')
        try:
            if len(date[0]) == 1:
                new = '0'+date[0]
                date[0] = new
            if len(date[1]) == 1:
                new = '0'+date[1]
                date[1] = new
            start = parts[-1].partition('—')[0].strip()
            end = parts[-1].partition('—')[2].strip()
            return '{}-{}-{}'.format(date[2], date[1], date[0]), start, end
        except:
            return '', '', ''
    return '', '', ''


def speech_part(tag):
    if 'PuheenvuoroToimenpide' in tag.name:
        return True
    elif ('PuheenjohtajaRepliikki' in tag.name
            and not tag.find_parent('vsk:PuheenvuoroToimenpide')):
        return True
    return False


def main(year):
    session_count = {
        '2015': 85,
        '2016': 139,
        '2017': 147,
        '2018': 181,
        '2019': 87,
        '2020': 115  # !!!!!! checked 20.9.2020
    }
    all_speeches = []
    for i in range(1, session_count[year]+1):
        id_doc = 'PTK {:d}/{} vp'.format(i, year)
        parameters = {'perPage': 10, 'page': 0,
                      'columnName': 'Eduskuntatunnus', 'columnValue': id_doc}
        response = requests.get(
            'https://avoindata.eduskunta.fi/api/v1/tables/VaskiData/rows', params=parameters)
        json_data = json.loads(response.content)
        rows = json_data['rowData']
        for row in rows:
            soup = BeautifulSoup(row[1], "xml")
            # **************************
            """ file = open('vaski.xml', "a")
            file.write(soup.prettify())
            file.write('****************************************')
            file.close() """
            # ***********************************
            session = '{:d}/{}'.format(i, year)
            date, session_start, session_end = date_times(
                soup.find('asi:IdentifiointiOsa'))
            if soup.find('ptk:Poytakirja'):
                doc_status = soup.find(
                    'ptk:Poytakirja').attrs['met1:tilaKoodi']
                doc_version = soup.find(
                    'ptk:Poytakirja').attrs['met1:versioTeksti']
            counter = 1
            items = soup.find_all('vsk:Asiakohta')
            for item in items:
                item_num = item.find('vsk1:KohtaNumero').string.strip()
                topic = item.find('met1:NimekeTeksti').string
                related_documents = item.find_all('vsk:KohtaAsia')
                if related_documents:
                    for doc in related_documents:
                        topic += '>>>' + \
                            doc.find('met1:AsiakirjatyyppiNimi').string
                        if doc.find('met1:EduskuntaTunnus'):
                            topic += '  ' + \
                                doc.find('met1:EduskuntaTunnus').string
                link = 'https://www.eduskunta.fi/FI/vaski/PoytakirjaAsiakohta/Sivut/PTK_{}+{}+{}.aspx'.format(
                    i, year, item_num
                )

                speech_sections = item.find_all(speech_part)

                for speech in speech_sections:
                    speech_id = '{}.{}.{}'.format(year, i, counter)
                    if 'PuheenjohtajaRepliikki' in speech.name:
                        speaker = speech.find(
                            'vsk1:PuheenjohtajaTeksti').string.split()

                        content = extract_cp_content(speech)

                        # check language
                        try:
                            parameters = {'text': content}
                            results = requests.get(
                                'http://demo.seco.tkk.fi/las/identify', params=parameters).json()
                            tags = []
                            tags = [k for d in results['details']
                                    ['languageDetectorResults'] for k in d.keys()]
                            langs = ':'.join(tags)
                        except:
                            langs = ''
                        try:
                            all_speeches.append([speech_id, session, date, session_start, session_end,
                                                 speaker[-2], speaker[-1], ' '.join(
                                                     speaker[:-2]), topic, content,
                                                 ' ', doc_status, doc_version, link, langs, ' '.join(
                                                     speaker)])
                        except:
                            all_speeches.append([speech_id, session, date, session_start, session_end,
                                                 '', '', ' '.join(
                                                     speaker), topic, content,
                                                 ' ', doc_status, doc_version, link, langs, ' '.join(
                                                     speaker)])
                    else:
                        response = ' '
                        if (speech.find('vsk1:TarkenneTeksti')
                                and 'astauspuheenvuoro' in speech.find('vsk1:TarkenneTeksti').string):
                            response = 'Vastauspuheenvuoro'
                        speaker_id = speech.find(
                            'Henkilo').attrs['met1:muuTunnus'].strip()
                        first = speech.find('org1:EtuNimi').string.strip()
                        last = speech.find(
                            'org1:SukuNimi').string.strip()
                        party = ''
                        if (speech.find(
                                'org1:LisatietoTeksti')):
                            party = speech.find(
                                'org1:LisatietoTeksti').string
                            if party:
                                party = party.upper()
                        if (speech.find('org1:AsemaTeksti') and not party):
                            party = speech.find(
                                'org1:AsemaTeksti').string.strip()

                        details = extract_speech_details(
                            speech.find('vsk:PuheenvuoroOsa').attrs)
                        content = extract_content(
                            speech.find('vsk:KohtaSisalto'))

                        try:
                            parameters = {'text': content}
                            results = requests.get(
                                'http://demo.seco.tkk.fi/las/identify', params=parameters).json()
                            tags = []
                            tags = [k for d in results['details']
                                    ['languageDetectorResults'] for k in d.keys()]
                            langs = ':'.join(tags)
                        except:
                            langs = ''

                        all_speeches.append([speech_id, session, date, session_start, session_end,
                                             first, last, party, topic, content, response,
                                             doc_status, doc_version, link, langs, first + ' ' + last, speaker_id,
                                             details['startTime'], details['endTime'], details['status'], details['textVersion']])
                    counter += 1
                    # print(counter)

    with open('speeches_{}.csv'.format(year), 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(all_speeches)


if __name__ == "__main__":
    main(sys.argv[1])
