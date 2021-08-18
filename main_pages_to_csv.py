from bs4 import BeautifulSoup
import lxml
import sys
import re
import csv
import pprint


def save_document_info(document_info, document):
    names = document.text.split('\n')
    link = 'https://www.eduskunta.fi' + document.a.get('href')
    document_info.append([names[0].strip(), names[1].strip(), link])


def form_date(date_time):
    # 3. TIISTAINA 6. HELMIKUUTA 2001
    months = {
        'tammikuuta': '01',
        'helmikuuta': '02',
        'maaliskuuta': '03',
        'huhtikuuta': '04',
        'toukokuuta': '05',
        'kesäkuuta': '06',
        'heinäkuuta': '07',
        'elokuuta': '08',
        'syyskuuta': '09',
        'lokakuuta': '10',
        'marraskuuta': '11',
        'joulukuuta': '12',
    }

    d = re.sub('\n *', ' ', date_time)
    dt = re.sub('\t|PÄIVÄNÄ ', '', d)
    if re.search(r'\bKUUTA ', dt):
        index = dt.index('KUUTA')
        cleaned = dt[:index-1]+dt[index:]
        parts = cleaned.split()
    else:
        parts = dt.split()
    date = '{:s}-{:s}-{:s}'.format(parts[4],
                                   months[parts[3].lower()], parts[2][:-1])
    return date


def session_number(document):
    # PTK 161/2001 vp
    parts = document.split()
    return parts[1]


def status_info(text):
    # Tarkistettu versio 2.0
    parts = text.split()
    if len(parts) > 2:
        return parts[-1].rstrip('.'), parts[0]
    else:
        return parts[-1].rstrip('.'), ''


def get_ending(text):
    parts = text.split()
    return parts[-1][:-1]


def get_chairman(text):
    parts = text.split()
    info = {}
    info[parts[-2]] = parts[-1]
    return info


def parse_speech(s):
    # print(s)
    s2 = re.sub('\n *', ' ', s.text)
    section = re.sub('\t', '', s2)
    if '20, 24, 28, 41, 69, 83, 84, 90 ja 100' in section:
        return '', '', 'Toinen varapuhemies', section
    parts = section.split(':', 1)
    if 'EDPVUORO' in s['class'] or 'EHDOTUS' in s['class'] or 'EDPUHE' in s['class']:
        speaker = parts[0].split()
        return ' '.join(speaker[:-2]), speaker[-2], speaker[-1][1:].upper(), parts[1].strip()
    elif 'PMPUHE' in s['class'] or 'PRESPUHE' in s['class']:
        if 'lausu' in section:
            ps = s.find_all('p')
            speaker = []
            speech = ''
            for p in ps:
                if not p.attrs:
                    relevant = p.text[p.text.index('lausu')+7:]
                    speaker = relevant.split()
                else:
                    text = re.sub('\n *', ' ', p.text)
                    text = re.sub('\t|\* \* \*|__+', '', text)
                    speech += '{:s}\n'.format(text)  # p.text)
            #no_linebreaks = re.sub('\n *', ' ', speech)
            #speech = re.sub('\t', '', no_linebreaks)
            speech = speech.rstrip('\n')
            if speaker:
                return speaker[-2], speaker[-1], ' '.join(speaker[:-2]).capitalize(), speech.strip()
            else:
                return '', '', '', speech.strip()
        else:
            return '', '', parts[0].strip(), parts[1].strip()
    elif 'VAKUUTUS' in s['class']:
        speaker = parts[0].split()
        return speaker[-2], speaker[-1], ' '.join(speaker[:-2]), parts[1].strip()
    else:
        return '', '', parts[0].strip(), parts[1].strip()


def main(file):
    parliament_year = file[-9:-5]
    with open(file, 'r', encoding="utf-8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        divs = soup.find_all(id='content')

    with open('main_page_speeches_{:s}.csv'.format(parliament_year), 'w') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerow(['session', 'date', 'session_start', 'session_end', 'actorFirstname',
                         'actorLastname', 'party', 'topic', 'content', 'speechType', 'status', 'version', 'link', 'discussionLink'])

        all_speeches = []
        skt_times = []
        document_info = []
        for div in divs[:50]:
            version, status = ' ', ' '
            date = form_date(div.h2.string)
            session = session_number(re.sub('\n *', ' ', div.h5.string))
            if div.find('p', 'akversio right italics'):
                version, status = status_info(
                    div.find('p', 'akversio right italics').string)

            link = 'https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+{:s}'.format(
                session)
            session_end = get_ending(div.find(id='LOPETUS').string)
            if (div.has_attr('class') and 'SKT' in div['class']):
                skt_times.append([session, session_end])
            for child in div.children:
                if not isinstance(child, str):
                    if child.find('div', [re.compile('PVUORO'), 'VAKUUTUS', re.compile('PUHE')]):
                        for grandchild in child.children:
                            if not isinstance(grandchild, str):
                                if (grandchild.has_attr('class') and 'PMPUHE' in grandchild['class']):
                                    firstname, lastname, party, speech = parse_speech(
                                        grandchild)
                                    all_speeches.append([
                                        session, date, session_end, firstname, lastname,
                                        party, ' ', speech, status, version, link, ''
                                    ])
                                elif grandchild.find('div', [re.compile('PVUORO'), 'VAKUUTUS', re.compile('PUHE')]):
                                    topic = ' '
                                    discussion_divs = []
                                    if grandchild.find('div', ['KYSKESK', 'KESKUST']):
                                        discussion_divs = grandchild.find_all(
                                            'div', ['KYSKESK', 'KESKUST'])

                                    if grandchild.find('h4'):
                                        topic = grandchild.h4.text
                                    if grandchild.find('p', re.compile('AK')):
                                        documents = grandchild.find_all(
                                            'p', re.compile('AK'))
                                        for document in documents:
                                            topic += '>>>' + document.text
                                            save_document_info(
                                                document_info, document)
                                    cleaner = re.sub(
                                        '\n *', ' ', topic)
                                    topic = re.sub('\t', '', cleaner)
                                    comments = grandchild.find_all(
                                        'div', [re.compile('PVUORO'), 'VAKUUTUS', re.compile('PUHE')])
                                    for comment in comments:
                                        firstname, lastname, party, speech = parse_speech(
                                            comment)
                                        discussion = ''
                                        if len(discussion_divs) > 0:
                                            discussion = 'https://www.eduskunta.fi' + discussion_divs.pop(0).a.get(
                                                'href')
                                        all_speeches.append([
                                            session, date, session_end, firstname, lastname,
                                            party, topic, speech, status, version, link, discussion
                                        ])

        print(len(all_speeches))
        for row in all_speeches:
            writer.writerow([row[0], row[1], '', row[2], row[3], row[4],
                             row[5], row[6], row[7], ' ', row[8], row[9], row[10], row[11]])

        with open('skt_times_{:s}.csv'.format(parliament_year), 'w') as save_to:
            writer = csv.writer(save_to, delimiter=',')
            writer.writerows(skt_times)
        with open('related_documents_details_{:s}.csv'.format(parliament_year), 'w') as save_to:
            writer = csv.writer(save_to, delimiter=',')
            writer.writerows(document_info)


if __name__ == "__main__":
    main(sys.argv[1])
