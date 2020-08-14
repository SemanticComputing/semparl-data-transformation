import re
import csv
import sys
import requests
import json
import time
from pprint import pprint


def sort_sessions(row):
    return int(row[1].partition('/')[0])  # session number


def form_speechID(session, index):
    n = session.split('/')
    return '{:s}.{:s}.{:d}'.format(n[1], n[0], index)


def clean_date(date):
    months = {
        'tammikuu': '01',
        'helmikuu': '02',
        'maaliskuu': '03',
        'huhtikuu': '04',
        'toukokuu': '05',
        'kesäkuu': '06',
        'heinäkuu': '07',
        'elokuu': '08',
        'syyskuu': '09',
        'lokakuu': '10',
        'marraskuu': '11',
        'joulukuu': '12',
    }
    parts = date.split('-')
    if len(parts[2]) == 1:
        day = '0'+parts[2]
    else:
        day = parts[2]
    return '{:s}-{:s}-{:s}'.format(parts[0], months[parts[1]], day)


def remove_hyphens(content):
    return content.replace('-<REMOVE> ', '',)


def clean_actor(actor):
    # Ed. Anttila (vastauspuheenvuoro)
    # Ed. FE. Aho
    # Ed. Astala
    # Ed. P. Lahtinen (vastauspuheenvuoro)
    # Ed. Wasz-Höckert (vastauspuheen-
    # Ed. Kuuskoski-Vikatmaa (vastaus-
    # Ministeri Halonen
    # Maa- ja metsätalousministeri Pohjala

    if actor.strip().endswith('uhemies'):
        return '', '', actor.strip(), ' '
    if actor == '(vastauspuheenvuoro)':
        return '', '', '', 'Vastauspuheenvuoro'

    pattern = re.compile('^[EF]d-[A-ZÅÄÖ]')
    if pattern.match(actor):
        actor = actor.replace('d-', 'd. ', 1)
    actor = actor.replace('d,', 'd.')
    actor = actor.replace('-<REMOVE> ', '')

    if 'Pääministeri A h o' in actor:
        actor = "Pääministeri Aho"
    if 'Oikeusministeri P o' in actor:
        actor = 'Oikeusministeri Pokka'
    if 'Maa- ja metsätalousministeri P u' in actor:
        actor = 'Maa- ja metsätalousministeri Pura'
    if 'Liikenneministeri N o' in actor:
        actor = 'Liikenneministeri Norrback'
    if 'inisteriRehn' in re.sub(' ', '', actor):
        tmp = actor.partition(' ')[0] + ' Rehn'
        actor = tmp
    if 'Ministeri A 1 h o ' in actor or 'Ministeri A 1h o' in actor:
        actor = 'Ministeri Alho'
    if 'Kuuskoski- Vikatmaa' in actor or 'Kuuskoski- Vikarmaa' in actor:
        actor = actor.replace('Kuuskoski- Vikatmaa', 'Kuuskoski-Vikatmaa')

    first_name = ''
    speech_type = ' '
    role = ''

    if '.' in actor:  # MP
        parts = actor.split('.')
        if len(parts) > 2:
            # there are initials
            first_name = parts[1].strip()
        last_name = parts[-1].strip()
    else:  # ministers etc.
        parts = actor.split(' ')
        if '(vastaus' in parts[-1]:
            last_name = parts[-2].strip()
            role = ' '.join(parts[:-2])
        else:
            last_name = parts[-1].strip()
            role = ' '.join(parts[:-1])

    if '(vastaus' in last_name or '(vastaus' in parts[-1]:
        speech_type = 'Vastauspuheenvuoro'
        p = last_name.split('(')
        last_name = p[0]

    actor_last = re.sub(' ', '', last_name.rstrip('—'))
    if (first_name in ['F', 'FE', 'EF'] and actor_last.strip() == 'Aho'):
        first_name = 'E'
    if 'gvist' in actor_last:
        actor_last = actor_last.replace('gvist', 'qvist')
    if actor_last.strip() in ['Flo', 'E10', 'E1o', 'F10']:
        actor_last = 'Elo'
    if actor_last == 'S-LAnttila':
        actor_last = 'Anttila'
        first_name = 'S-L'
    if 'Y mpäristöministeri' in role:
        role = 'Ympäristöministeri'

    return first_name, actor_last, role, speech_type


def check_time(time):
    time = time.replace(',', '.')
    if len(time) == 2:
        return time + '.00'
    if len(time) == 4:
        return '0'+time
    return time


def find_speaker(member_info, actor_first, last, party, date):
    if 'uhemies' in party:
        return actor_first, party
    problem_cases = {
        'Holkeri': 'Harri',
        'Norrback': 'Ole',
        'Pohjala': 'Toivo T.',
        'Tuomisto': 'Konstantin',
        'Lindblom': 'Seppo',
        'Björkstrand': 'Gustav',
    }

    if not last.strip():
        return actor_first, party
    if actor_last in problem_cases.keys():
        return problem_cases[actor_last], party

    if '-' in actor_first:
        temp = actor_first.partition('-')[0]
        actor_first = temp.strip('.')

    speech_date = time.strptime(date, '%Y-%m-%d')

    for row in member_info[1:]:
        if row[7]:  # started as MP
            row_start = time.strptime(row[7], '%Y-%m-%d')
            if row[8]:  # ended as MP
                row_end = time.strptime(row[8], '%Y-%m-%d')
                # and row[2] in actor_last or actor_last in row[2]
                if (row[2] == actor_last.strip()):
                    if actor_first.strip():
                        if (row[3] and row[3].startswith(actor_first)  # actor_first in row[3]
                                and row_end >= speech_date >= row_start):
                            if not party.strip():
                                return row[3], row[9].strip('.').upper()
                            else:
                                return row[3], party
                    else:
                        if row_end >= speech_date >= row_start:
                            if not party.strip():
                                return row[3], row[9].strip('.').upper()
                            else:
                                return row[3], party
            else:
                # and row[2] in actor_last or actor_last in row[2]
                if (row[2] == actor_last.strip()):
                    if actor_first.strip():
                        # actor_first in row[3]
                        if (row[3] and row[3].startswith(actor_first) and speech_date >= row_start):
                            if not party.strip():
                                return row[3], row[9].strip('.').upper()
                            else:
                                return row[3], party
                    else:
                        if speech_date >= row_start:
                            if not party.strip():
                                return row[3], row[9].strip('.').upper()
                            else:
                                return row[3], party
    return actor_first, party


def correct_party(party, lastname, date):
    current_date = time.strptime(date, '%Y-%m-%d')
    if 'KESK.;SMP' == party:
        if lastname.strip() == 'Vennamo':
            return 'SMP'
        if current_date >= time.strptime('1994-02-07', '%Y-%m-%d'):
            return 'KESK'
        return 'SMP'

    if 'RKP;SDP;SKDL' == party:
        return 'RKP'

    if 'SKP;SKDL;VAS.' == party or 'SKDL;DEVA;VAS' == party or 'SKDL;VAS' == party:
        if lastname.strip() == 'Tennilä':
            if time.strptime('1990-09-10', '%Y-%m-%d') >= current_date >= time.strptime('1986-06-05', '%Y-%m-%d'):
                return'DEVA'
            elif time.strptime('1986-06-04', '%Y-%m-%d') >= current_date:
                return 'SKDL'
        return 'VAS'

    if 'KP;KESK' == party:
        if current_date >= time.strptime('2016-03-08', '%Y-%m-%d'):
            return 'KP'
        return 'KESK'

    if 'SKP;SKDL' == party:
        return 'SKDL'

    if 'SDP;SKDL' == party:
        if current_date.tm_year >= 1945:
            return 'SKDL'
        return 'SDP'

    if 'SKP;SDP;SKDL' == party:
        # rydberg kaisu-mirjami
        if current_date >= time.strptime('1945-04-06', '%Y-%m-%d'):
            return 'SKDL'
        elif current_date <= time.strptime('1941-01-31', '%Y-%m-%d'):
            return 'SPD'
        else:
            return party  # not really in SKP but "Kuusikko"?

    if 'SKP;SDP' == party:
        return 'SPD'

    if 'KESK.;KOK.' == party:
        if current_date.year >= 1924:
            return 'KESK'
        return 'KOK'

    if 'KP;LKP' == party:
        if current_date.tm_year >= 1962:
            return 'LKP'
        return 'KP'

    return party


# read raw(minimal formatting) csv.file
filename = sys.argv[1]
cleaned_rows = []
member_info = []
csv.field_size_limit(sys.maxsize)
with open('python_csv_parliamentMembers.csv') as f:
    reader = csv.reader(f, delimiter='\t')
    member_info = list(reader)
with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    index = 0
    current_session = ''
    previous_sessions = {}
    for row in reader:
        if not row[6].strip():
            continue
        index += 1
        session = row[0]
        date = clean_date(row[1])
        start = check_time(row[2].strip())
        end = check_time(row[3].strip())
        actor = row[4].replace('<Puhuja>', '',)
        original_actor = row[4].replace('<REMOVE> ', '',)
        topic = remove_hyphens(row[5])
        content = remove_hyphens(row[6])

        original_actor = original_actor.partition('(vas')[0].strip()

        if session != current_session:
            previous_sessions[current_session] = index
            current_session = session
            # to ensure that speech order index for a continuation session picks of from where
            # the first part was left so there won't be identical ids
            if current_session in previous_sessions:
                index = previous_sessions[current_session]
            else:
                index = 1

        speech_id = form_speechID(session, index)

        actor_first, actor_last, party, speech_type = clean_actor(
            actor.strip())
        actor_first, party = find_speaker(
            member_info, actor_first, actor_last, party, date)
        party = correct_party(party, actor_last, date)
        langs = ' '  # This a remnant of earlier structure but left here to keep compability

        """ try:
            parameters = {'text': content}
            results = requests.get(
                'http://demo.seco.tkk.fi/las/identify', params=parameters).json()
            tags = []
            tags = [k for d in results['details']
                    ['languageDetectorResults'] for k in d.keys()]
            langs = ':'.join(tags)
        except:
            langs = ''
        print(speech_id) """

        if '(vas-<REMOVE>' in actor_last:
            actor_last = actor_last.partition('(')[0]
            speech_type = 'Vastauspuheenvuoro'

        if '10) Tuontiviikon järjestäminen Turussa siten kuin Turun metallityöväen ammattiosasto' in topic\
                or '5) Sosiaali- ja terveysviranomaisten on huoleh' in topic:
            topic = ''

        if '8:n' in topic or '$:n' in topic:
            topic = re.sub('[8$]:n', '§:n', topic)

        if (start and start[0].isalpha()):
            start = ''
        if (end and end[0].isalpha()):
            end = ''

        cleaned_rows.append([speech_id, session, date, start.strip(), end, actor_first,
                             actor_last, party, topic, content, speech_type, ' ', ' ', row[8], langs, original_actor, row[7]])


# save to csv.file
output_file = filename[:-8]
csv.field_size_limit(sys.maxsize)

# sort sessions so that split sessions (sessions interrupted by 'Kyselytunti'session)
# are consecutive to avoid issues later on (identical URIs)
cleaned_rows.sort(key=sort_sessions)

with open('{:s}.csv'.format(output_file), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerows(cleaned_rows)
