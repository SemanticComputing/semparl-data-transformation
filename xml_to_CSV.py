from bs4 import BeautifulSoup
from urllib import request
import json
import re
import csv
import requests
import sys
import pycld2
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
    # if 'met1:toinenKieliKoodi' in tag_content.keys():
    #     details['language'] = details['language'] + ':' + \
    #         tag_content['met1:toinenKieliKoodi'].strip()
    # Issue: kieliKoodi is always 'fi', if speech uses swedish there is toinenKieliKoodi with value 'sv', but there is still
    # always 'fi' also whether finnish was used or not

    return details


def extract_content(speech_section):
    content = ''
    for child in speech_section.children:
        if 'PuheenjohtajaRepliikki' in child.name:
            content += '<<' + child.find('vsk1:PuheenjohtajaTeksti').string + ':| ' \
                + child.find('sis:KappaleKooste').string + '>>'
        elif ('KappaleKooste' in child.name and child.string):
            content += child.string + '\n'

    return content.rstrip('\n')


def extract_cp_content(speech):
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
    if 'PuheenvuoroToimenpide' in tag.name or 'PuhujaRepliikki' in tag.name:
        return True
    elif ('PuheenjohtajaRepliikki' in tag.name
            and not tag.find_parent('vsk:PuheenvuoroToimenpide')):
        return True
    return False


def sub_section_to_previous(previous_num, new_num):
    # check whether the new section is a subsection of previous top level topic

    if '.' in new_num and previous_num == new_num.partition('.')[0]:
        return True
    return False


def detect_language(text):
    tags = []
    try:
        result = pycld2.detect(text)
        for lang_tuple in result[2]:
            if 'fi' in lang_tuple:
                tags.append('fi')
            elif 'sv' in lang_tuple:
                tags.append('sv')
    except:
        pass

    # typical short comments that do not get recognized
    words = ['samoin', 'kannatan', 'kyllä', 'puhujalistaan', 'edustaja',
             'ministeri', 'luovun', 'enemmistö', 'poistetaan', 'merkitään']
    if not tags:
        for word in words:
            if word in text.lower():
                tags.append('fi')
                break

    return ':'.join(tags)


def main(year):
    session_count = {
        '2015': 85,
        '2016': 139,
        '2017': 147,
        '2018': 181,
        '2019': 87,
        '2020': 170,
        '2021': 167,
        '2022': 180
    }
    all_speeches = []
    #print('vajaa lista')
    end_limit = 500
    if year in session_count:
        end_limit = session_count[year] + 1

    empty_responses = 0

    for i in range(1, end_limit):
        # download minutes for one session
        id_doc = 'PTK {:d}/{} vp'.format(i, year)
        parameters = {'perPage': 10, 'page': 0,
                      'columnName': 'Eduskuntatunnus', 'columnValue': id_doc}
        response = requests.get(
            'https://avoindata.eduskunta.fi/api/v1/tables/VaskiData/rows', params=parameters)
        json_data = json.loads(response.content)
        rows = json_data['rowData']

        if len(rows) == 0:
            empty_responses += 1
        if empty_responses > 9:
            break

        for row in rows:
            soup = BeautifulSoup(row[1], "xml")
            topic, item_num, topsection_topic = '', '', ''
            session = '{:d}/{}'.format(i, year)
            date, session_start, session_end = date_times(
                soup.find('asi:IdentifiointiOsa'))

            if soup.find('ptk:Poytakirja'):
                doc_status = soup.find(
                    'ptk:Poytakirja').attrs['met1:tilaKoodi']
                doc_version = soup.find(
                    'ptk:Poytakirja').attrs['met1:versioTeksti']
            counter = 1
            # find all items
            items = soup.find_all(['vsk:Asiakohta', 'vsk:MuuAsiakohta'])

            for item in items:

                # carry topic info into sub sections that are in their own element
                if item['vsk1:kohtatyyppiKoodi'] == 'Alikohta':
                    if not topsection_topic:
                        topsection_topic = topic
                        topsection_item_num = item_num
                        # check number hierarchy
                    if sub_section_to_previous(topsection_item_num, item.find('vsk1:KohtaNumero').string.strip()):
                        topic = item.find(
                            ['met1:NimekeTeksti', 'sis1:OtsikkoTeksti']).string

                        # Squeeze the sub topic in between top topic and related documents
                        top_topic_parts = topsection_topic.split('>>>', 1)
                        topic = top_topic_parts[0] + ' - ' + topic
                        if len(top_topic_parts) > 1:
                            topic += '>>>' + top_topic_parts[1]
                        # Pointless redundancy
                        topic = topic.replace('Suullinen kyselytunti - ', '')

                # not a subsection
                else:
                    topsection_item_num, topsection_topic = '', ''
                    topic = item.find(
                        ['met1:NimekeTeksti', 'sis1:OtsikkoTeksti']).string

                # item number, related document, link
                item_num = item.find('vsk1:KohtaNumero').string.strip()
                related_documents = item.find_all(
                    ['vsk:KohtaAsia', 'vsk:KohtaAsiakirja'])
                if related_documents:
                    for doc in related_documents:
                        topic += '>>>' + \
                            doc.find('met1:AsiakirjatyyppiNimi').string
                        if doc.find(['met1:EduskuntaTunnus', 'sis1:MultiViiteTunnus']):
                            topic += '  ' + \
                                doc.find(['met1:EduskuntaTunnus',
                                          'sis1:MultiViiteTunnus']).string
                link = 'https://www.eduskunta.fi/FI/vaski/PoytakirjaAsiakohta/Sivut/PTK_{}+{}+{}.aspx'.format(
                    i, year, item_num
                )

                # find speech parts
                speech_sections = item.find_all(speech_part)
                for speech in speech_sections:
                    speech_id = '{}_{}_{}'.format(year, i, counter)

        # Chairman speech
                    if 'PuheenjohtajaRepliikki' in speech.name:
                        speaker = speech.find(
                            'vsk1:PuheenjohtajaTeksti').string.split()

                        content = extract_cp_content(speech).strip()

                        # check language
                        langs = detect_language(content)

                        try:
                            all_speeches.append([speech_id, session, date, session_start, session_end,
                                                 speaker[-2], speaker[-1], ' '.join(
                                                     speaker[:-2]), '', topic, content,
                                                 ' ', doc_status, doc_version, link, langs, ' '.join(
                                                     speaker)])
                        except:
                            all_speeches.append([speech_id, session, date, session_start, session_end,
                                                 '', '', ' '.join(
                                                     speaker), '', topic, content,
                                                 ' ', doc_status, doc_version, link, langs, ' '.join(
                                                     speaker)])
        # MP speech
                    else:
                        #speech_type = speech.attrs['vsk1:puheenvuoroLuokitusKoodi']
                        speech_type = ' '
                        if speech.find('vsk1:TarkenneTeksti'):
                            speech_type = re.sub('\(|\)', '', speech.find(
                                'vsk1:TarkenneTeksti').string)
                            speech_type = speech_type.replace(
                                '-', '').capitalize()
                        try:
                            speaker_id = speech.find(
                                'Henkilo').attrs['met1:muuTunnus'].strip()
                        except:
                            speaker_id = ''
                        first = speech.find('org1:EtuNimi').string.strip()
                        last = speech.find(
                            'org1:SukuNimi').string.strip()
                        party = ''
                        role = 'Kansanedustaja'
                        if (speech.find(
                                'org1:LisatietoTeksti')):
                            party = speech.find(
                                'org1:LisatietoTeksti').string
                            if party:
                                party = party.upper()
                        if (speech.find('org1:AsemaTeksti')):
                            role = speech.find(
                                'org1:AsemaTeksti').string.strip()

                        if 'uhemies' in first:  # Fixing mistakes in source data
                            role = re.search('.*uhemies', first).group(0)
                            first = re.sub('.*uhemies ', '', first)

                        if speech.find('vsk:PuheenvuoroOsa'):
                            details = extract_speech_details(
                                speech.find('vsk:PuheenvuoroOsa').attrs)
                            content = extract_content(
                                speech.find('vsk:KohtaSisalto'))

                        else:  # Small comments about wrong vote or such
                            details = ''
                            content = speech.find('sis:KappaleKooste').string

                        langs = detect_language(content)

        # A chairman comment trailing the speech. Add it as a separate speech (as it is shown as such in rendered view)
                        if content.endswith('>>'):
                            parts = content.rsplit('<<', 1)
                            chairman_parts = parts[-1].partition(
                                '|')[0].strip(':').split(' ')
                            cm_firstname = chairman_parts[-2]
                            cm_lastname = chairman_parts[-1]
                            cm_title = ' '.join(chairman_parts[:-2])
                            cm_content = parts[-1].partition('|')[
                                2].strip('>>').strip()

                            cm_lang = detect_language(cm_content)

                            # Remove chairman trailing comment and other unneeded helper markings
                            content = parts[0].strip()
                            content = re.sub(
                                r'<<(.+?)\|(.+?)>>', r'[\1 \2] ', content)

                            # append speech
                            # append chairman comment
                            all_speeches.append([speech_id, session, date, session_start, session_end,
                                                 first, last, role, party, topic, content, speech_type,
                                                 doc_status, doc_version, link, langs, first + ' ' + last, speaker_id,
                                                 details['startTime'], details['endTime'], details['status'], details['textVersion']])
                            counter += 1
                            speech_id = '{}_{}_{}'.format(year, i, counter)
                            all_speeches.append([speech_id, session, date, session_start, session_end,
                                                 cm_firstname, cm_lastname, cm_title, '', topic, cm_content, ' ',
                                                 doc_status, doc_version, link, cm_lang, ' '.join([
                                                     cm_title, cm_firstname, cm_lastname]), ' ',
                                                 '', '', details['status'], details['textVersion']])
                        else:
                            content = re.sub(
                                r'<<(.+?)\|(.+?)>>', r'[\1 \2] ', content)

                            if details:
                                all_speeches.append([speech_id, session, date, session_start, session_end,
                                                     first, last, role, party, topic, content, speech_type,
                                                     doc_status, doc_version, link, langs, first + ' ' + last, speaker_id,
                                                     details['startTime'], details['endTime'], details['status'], details['textVersion']])
                            else:
                                all_speeches.append([speech_id, session, date, session_start, session_end,
                                                     first, last, role, party, topic, content, speech_type,
                                                     doc_status, doc_version, link, langs, first + ' ' + last, speaker_id,
                                                     '', '', '', ''])
                    counter += 1
                    # print(counter)

    with open('speeches_{}.csv'.format(year), 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['speech_id', 'session', 'date', 'start_time', 'end_time', 'given', 'family', 'role', 'party', 'topic',
                         'content', 'speech_type', 'status', 'version', 'link', 'lang', 'name_in_source', 'speaker_id', 'speech_start', 'speech_end', 'speech_status', 'speech_version'])

        writer.writerows(all_speeches)

    #print('KIELI PUUTTUU x3')


if __name__ == "__main__":
    main(sys.argv[1])


#
# ##
