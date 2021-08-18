from bs4 import BeautifulSoup
import lxml
import sys
import re
import csv
import os
from pprint import pprint

# Gather content-html elements from discussion links.
# Links in a file given as parameter
# Results saved to file


def form_date(date_time):
    # 3. TIISTAINA 6. HELMIKUUTA 2001 kello 14
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
    return date, re.sub('\)|\(', '', parts[-1])


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


def speaker_info(s):
    # Olavi Ala-Nissilä /kesk
    # Alue- ja kuntaministeri Martti Korhonen
    sp = re.sub('/ +', '/', s)
    speak = re.sub(' :', ':', sp)
    sp = re.sub(' +\(', '\(', speak)
    speaker = re.sub(' vastaus', '(vastaus', sp)
    parts = speaker.split()
    if 'inisteri' in speaker or 'n oikeus' in speaker:
        return parts[-2], parts[-1], ' '.join(parts[:-2])
    else:

        if (' vastaus') in speaker:
            print(speaker)
        return ' '.join(parts[:-2]), parts[-2], re.sub(':', '', parts[-1][1:].upper())


def check_type(party):
    if 'VASTAUSPUHEENVUORO' in party:
        parts = party.split('(')
        return parts[0].strip(), 'Vastauspuheenvuoro'
    elif 'RYHMÄPUHEENVUORO' in party:
        parts = party.split('(')
        return parts[0].strip(), 'Ryhmäpuheenvuoro'
    elif 'ESITTELYPUHEENVUORO' in party:
        parts = party.split('(')
        return parts[0].strip(), 'Esittelypuheenvuoro'
    else:
        return party, ' '


def parse_speech(speech_parts):
    speech = []
    for part in speech_parts:
        text = part.text.replace('\t', '')
        speech.append(re.sub('\n *', ' ', text))

    return '\n'.join(speech)  # re.sub('\n *', ' ', ' '.join(speech))


def parse_pm_speech(speech_section):
    speech = []
    for child in speech_section.children:
        if not isinstance(child, str):
            if (child.name == 'div' and 'PMVALI' in child['class']):
                chairman = child.find('p', 'PUHEMIES inline strong').text
                chairman_comments = child.find_all(
                    'p', attrs={'xmlns:edk': 'http://eduskunta'})
                chairman_comment = []
                for comment in chairman_comments:
                    chairman_comment.append(comment.string)
                speech.append('<<{:s}|{:s}>>'.format(
                    chairman, ' '.join(chairman_comment)))
            if child.has_attr('xmlns:edk'):
                speech.append(child.string)
    # pprint(speech)
    no_nones = list(filter(None, speech))
    return re.sub('\n *', ' ', ' '.join(no_nones))


def main(file):
    is_in_docker = os.environ.get('RUNNING_IN_DOCKER_CONTAINER', False)
    parliament_year = file[-9:-5]

    if is_in_docker:
        link_file = 'original_html/links/links_{:s}.txt'.format(
            parliament_year)
    else:
        link_file = '../../data/2000-2014/links/links_{:s}.txt'.format(
            parliament_year)
    with open(link_file, 'r') as links_f:
        contents = links_f.read()
        links = contents.split('\n')

    with open(file, 'r', encoding="utf-8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        divs = soup.find_all(id='content')

    with open('discussions_{:s}.csv'.format(parliament_year), 'w') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerow(['session', 'date', 'session_start', 'session_end', 'actorFirstname',
                         'actorLastname', 'party', 'topic', 'content', 'speechType', 'status', 'version', 'link'])
        i = 1
        for div in divs[:50]:
            topic = ' '
            date, session_start = form_date(div.h2.string)
            session = session_number(re.sub('\n *', ' ', div.h5.string))
            version, status = status_info(
                div.find('p', 'akversio right italics').string)
            if (div.find('h3')):
                topic = re.sub('\n *', ' ', div.h3.string)
            link = links[i]
            i += 1
            speeches = div.find_all('div', ['PVUORO', 'SKTPVUOR'])
            for speech in speeches:
                speaker = speech.find(
                    ['p', 'span'], ['EDUSTAJA strong inline', 'MINISTER strong inline']).string
                firstname, lastname, tmp_party = speaker_info(speaker)
                party, speech_type = check_type(tmp_party)
                if speech.find('div', 'PMVALI'):
                    content = parse_pm_speech(speech)
                else:
                    content = parse_speech(
                        speech.find_all('p', attrs={'xmlns:edk': 'http://eduskunta'}))

                writer.writerow([session, date, session_start, '', firstname,
                                 lastname, party.strip('\\'), topic, content, speech_type, status, version, link])


if __name__ == "__main__":
    main(sys.argv[1])
