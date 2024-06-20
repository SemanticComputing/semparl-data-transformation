import re
import csv
import sys
import pandas as pd
import pycld2
from pprint import pprint
from speakerAnalyzer import *

member_info = []
not_found = []
sp = SpeakerAnalyzer()


def sort_sessions(row):
    return int(row[1].partition('/')[0])  # session number


def form_speechID(session, index):
    n = session.split('/')
    return '{:s}_{:s}_{:d}'.format(n[1], n[0], index)


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
        'matraskuu': '11', # typo in source data
        'joulukuu': '12',
    }
    parts = date.split('-')
    year = parts[0].strip('"')
    if len(parts[2]) == 1:
        day = '0'+parts[2]
    else:
        day = parts[2]
    return '{:s}-{:s}-{:s}'.format(year, months[parts[1]], day)


def remove_hyphens(content):
    return content.replace('-<REMOVE> ', '',)


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


def clean_actor(actor, date):
    # Ed. Anttila (vastauspuheenvuoro)
    # Ed. FE. Aho
    # Ed. Astala
    # Ed. von Bell
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

    if re.compile('Pääministeri A ?h ?[o0]?').match(actor):
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
    if re.search('\w( \-|\- )[A-ZÅÄÖ]', actor):  # 'Kuuskoski- Vikatmaa'
        actor = re.sub(r'(\w) ?\- ?([A-ZÅÄÖ])', r'\1-\2', actor)

    first_name = ''
    speech_type = ' '
    role = ''
    if int(date[:4]) < 1909:
        #'Ed. Wuolijoki, Wäinö', 'Ed. Aromaa, V.', 'Ed. Rosenqvist, G. G.'
        #'Ed. Sulo Wuolijoki', 'Ed. v. Troll'
        if re.search('(von|af|v\.) [A-ZÅÄÖ]', actor):
            actor = actor.replace('v.', 'von')
            if '.' in actor:
                parts = actor.split('.')
                last_name = parts[1]
            else:
                parts = actor.split()
                last_name = '<KEEPTHIS>'.join(parts[-2:])
                role = ' '.join(parts[:-2])
        elif ', ' in actor:
            first_name = actor.partition(', ')[2]
            rest = actor.partition(', ')[0]
            if '.' in rest:  # MP
                parts = rest.split('.')
                last_name = parts[-1].strip()
            else:  # ministers etc.
                parts = actor.split(' ')
                last_name = parts[-1].strip()
                role = ' '.join(parts[:-1])
        else:
            parts = actor.split(' ')
            first_name = ' '.join(parts[1:-1])
            last_name = parts[-1].strip()
            if not '.' in actor:  # not MP
                role = parts[0]

    else:
        if re.search('(von|af|v\.) [A-ZÅÄÖ]', actor):
            actor = actor.replace('v.', 'von')
            if '.' in actor:
                parts = actor.split('.')
                last_name = parts[1]
            else:
                parts = actor.split()
                last_name = '<KEEPTHIS>'.join(parts[-2:])
                role = ' '.join(parts[:-2])
        elif '.' in actor:  # MP
            parts = actor.split('.')
            if len(parts) > 2:
                # there are initials
                first_name = parts[1].strip()
            last_name = parts[-1].strip()
        else:  # ministers etc.
            parts = actor.split(' ')
            if len(parts)==1:
                # errors like "Pulliainen(vastauspuheenvuoro)"
                # -> ["Pulliainen", "(vastauspuheenvuoro)"]
                parts = re.sub(r'(\w)(\(\w)', r'\1 \2', actor).split(' ')
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
    actor_last = re.sub(r'(von|af)([A-ZÅÄÖ])', r'\1 \2', actor_last)
    actor_last = re.sub('<KEEPTHIS>', ' ', actor_last)

    if (first_name in ['F', 'FE', 'EF'] and actor_last.strip() == 'Aho'):
        first_name = 'E'
    if 'gvist' in actor_last:
        actor_last = actor_last.replace('gvist', 'qvist')
    if actor_last.strip() in ['FEIo', 'E10o', 'E|o', 'F1o', 'E1lo', 'EI1o']:
        actor_last = 'Elo'
    if actor_last == 'S-LAnttila':
        actor_last = 'Anttila'
        first_name = 'S-L'
    if 'Y mpäristöministe' in role:
        role = 'Ympäristöministeri'

    role = re.sub('inisteti', 'inisteri', role)
    role = re.sub('Sos[lti]a[aä]?li', 'Sosiaali', role)
    role = re.sub('astainminis', 'asiainminis', role)
    role = re.sub('etveysminis', 'erveysminis', role)
    role = re.sub('FE?nsimmäinen', 'Ensimmäinen', role)
    role = re.sub("—|\+|\*|'", '', role)
    role = re.sub("^\-?[EF]d[\.,]?$", '', role)
    role = re.sub("  +", ' ', role)

    if role == 'Pääministeri' and actor_last == 'Aho':
        first_name = 'E'  # to avoid Raila Aho

    return first_name, actor_last, role.strip(), speech_type


def check_time(time):
    time = time.replace(',', '.')
    if len(time) == 2:
        return time + '.00'
    if len(time) == 4:
        return '0'+time
    return time


def find_chairman(role, date):
    # find the chairman by role and date
    role = re.sub("-|' ?", "", role)
    role = role.strip()

    chair = member_info[(member_info['role_label'] == role.lower(
    )) & (member_info['parl_period_start'] <= pd.to_datetime(date)) & (member_info['parl_period_end'] >= pd.to_datetime(date))]

    if chair.empty:
        not_found.append(','.join([role, date]))
        return {
            'uri': '',
            'first': '',
            'lastname': '',
            'gender': '',
            'birth': '',
            'role': role,
            'party': '',
            'party_uri': '',
            'speechtype': 'PuhemiesPuheenvuoro',
            'group': ''
        }

    chair_details = {
        'uri': chair['id'].values[0],
        'first': chair['given'].values[0],
        'lastname': chair['family'].values[0],
        'gender': chair['gender'].values[0],
        'birth': chair['birth'].values[0],
        'role': role,
        'speechtype': 'PuhemiesPuheenvuoro'
    }

    # Party details are often on a separete row, find them by id and date
    chair_party = member_info[(member_info['id'] == chair_details['uri']) & (
        member_info['parl_period_start'] <= pd.to_datetime(date)) & (member_info['parl_period_end'] >= pd.to_datetime(date)) & (member_info.party.notnull())]

    if not chair_party.empty:
        chair_details['party'] = chair_party['party'].values[0].strip(
            '.').upper()
        chair_details['party_uri'] = chair_party['party_ids'].values[0]
        chair_details['group'] = chair_party['group_id'].values[0]
    else:
        chair_details['party'] = ''
        chair_details['party_uri'] = ''
        chair_details['group'] = ''

    # pprint(chair_details)
    return chair_details


def extract_details(row, role, last):
    mp = {
        'uri': row['id'],
        'first': row['given'],
        'lastname': last,
        'gender': row['gender'],
        'birth': row['birth'],
        'role': role.strip(),
        'party': row['party'],
        'party_uri': row['party_ids'],
        'group': row['group_id']
    }

    return mp


def find_MP(firstname, last, role, date):
    mp = dict()

    if not last.strip():
        not_found.append(','.join([firstname, last, role]))
        return {
            'uri': '',
            'first': firstname,
            'lastname': '',
            'gender': '',
            'birth': '',
            'role': role.strip(),
            'party': '',
            'party_uri': '',
            'group': ''
        }

    if '-' in firstname:
        temp = firstname.partition('-')[0]
        firstname = temp.strip('.')

    if '.' in firstname:
        firstname = firstname.partition('.')[0]

    speech_date = pd.to_datetime(date)

    # first run considering only the "primary" lastname and primary first name
    for i, row in member_info.iterrows():
        if pd.notnull(row['parl_period_start']):
            if pd.notnull(row['parl_period_end']):
                if (row['family'] == last.strip()):
                    if firstname.strip():
                        if (row['given'].startswith(firstname) and row['parl_period_end'] >= speech_date >= row['parl_period_start']):
                            mp = extract_details(row, role, last)
                            break
                    else:
                        if row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                            mp = extract_details(row, role, last)
                            break
            else:
                if (row['family'] == last.strip()):
                    if firstname.strip():
                        if (row['given'].startswith(firstname) and speech_date >= row['parl_period_start']):
                            mp = extract_details(row, role, last)
                            break
                    else:
                        if speech_date >= row['parl_period_start']:
                            mp = extract_details(row, role, last)
                            break

# if not found, second run trying alternative labels
    if not 'uri' in mp:
        for i, row in member_info.iterrows():
            # started as MP + alternative names exist
            if pd.notnull(row['parl_period_start']) and pd.notnull(row['other_family_names']):
                alters = row['other_family_names'].split('; ')
                if pd.notnull(row['parl_period_end']):
                    if (last.strip() in alters):
                        if firstname.strip():
                            if (row['given'].startswith(firstname)
                                    and row['parl_period_end'] >= speech_date >= row['parl_period_start']):
                                mp = extract_details(row, role, last)
                                break
                        else:
                            if row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                                mp = extract_details(row, role, last)
                                break
                else:
                    if (last.strip() in alters):
                        if firstname.strip():
                            if (row['given'].startswith(firstname) and speech_date >= row['parl_period_start']):
                                mp = extract_details(row, role, last)
                                break
                        else:
                            if speech_date >= row['parl_period_start']:
                                mp = extract_details(row, role, last)
                                break


# If party was missing, try to find it from another row
    if 'uri' in mp and (not mp['party'] or type(mp['party']) == float):
        mp_party = member_info[(member_info['id'] == mp['uri']) & (
            member_info['parl_period_start'] <= pd.to_datetime(date)) & (member_info['parl_period_end'] >= pd.to_datetime(date)) & (member_info.party.notnull())]

        if not mp_party.empty:
            mp['party'] = mp_party['party'].values[0]
            mp['party_uri'] = mp_party['party_ids'].values[0]
            mp['group'] = mp_party['group_id'].values[0]

    if not 'uri' in mp:
        not_found.append(','.join([firstname, last, role]))
        mp = {
            'uri': '',
            'first': firstname,
            'lastname': last,
            'gender': '',
            'birth': '',
            'role': role.strip(),
            'party': '',
            'party_uri': '',
            'group': ''
        }

    if type(mp['party']) == float:  # NaN
        mp['party'] = ''
    else:
        mp['party'] = mp['party'].strip('.').upper()
    # edit here to not cause error on NaN

    # pprint(mp)
    return mp


###########################################################################################
# Clean raw 20th century csv and find speaker details from Actors of Parliament ontology  #
###########################################################################################

filename = sys.argv[1]
cleaned_rows = []
csv.field_size_limit(sys.maxsize)

members = pd.read_csv('parliamentMembers.csv', sep='\t')


with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    index = 0
    current_session = ''
    previous_sessions = {}
    party_roles = {}
    rows = list(reader)

    # filter out some rows based on date for efficiency
    last_date = clean_date(rows[-1][1])

    members['parl_period_start'] = pd.to_datetime(
        members['parl_period_start'], format='%Y-%m-%d')
    members['parl_period_end'] = pd.to_datetime(
        members['parl_period_end'], format='%Y-%m-%d')

    member_info = members[
        members['parl_period_start'] <= pd.to_datetime(last_date)]

    for row in rows:
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

        topic = re.sub('[\|\[!]+', '', topic).strip()
        topic = topic.rstrip(':')

        original_actor = original_actor.partition('(vas')[0].strip()
        speaker = dict()

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

        firstname, actor_last, role, speech_type = clean_actor(
            actor.strip(), date)
        actor_last = actor_last.strip('—')

        if '(vas-<REMOVE>' in actor_last:
            actor_last = actor_last.partition('(')[0]
            speech_type = 'Vastauspuheenvuoro'

        if 'uhemies' in role:
            speaker = find_chairman(role, date)
        else:
            speaker = find_MP(
                firstname, actor_last, role, date)
            if not speaker['role'] and re.compile('[EFB]d[\.,]').search(original_actor):
                speaker['role'] = 'Kansanedustaja'

    # check speech language
        lang = ''
        if content.startswith('(ruotsiksi)'):
            lang = 'sv'
        else:
            lang = detect_language(content)

        if '10) Tuontiviikon järjestäminen Turussa siten kuin Turun metallityöväen ammattiosasto' in topic\
                or '5) Sosiaali- ja terveysviranomaisten on huoleh' in topic:
            topic = ''

        if '8:n' in topic or '$:n' in topic:
            topic = re.sub('[8$]:n', '§:n', topic)

        if (start and start[0].isalpha()):
            start = ''
        if (end and end[0].isalpha()):
            end = ''

        content = re.sub('\n\n+', '\n', content)
        content = re.sub('- [:;]+ ', '', content)
        speech_type = speech_type.replace('-', '').title()

        if not 'speechtype' in speaker:
            if speech_type.strip():
                speaker['speechtype'] = speech_type
            else:
                speaker['speechtype'] = 'Puheenvuoro'

        # find party's position
        res = ''
        if speaker['uri']:
            p = speaker['party']
            if date in party_roles and p in party_roles[date]:
                res = party_roles[date][p]
            else:
                uri = speaker['uri'].rpartition('/')[2]
                try:
                    res = sp.find(date=date, member=uri)['type']
                    if not date in party_roles:
                        party_roles[date] = {}
                    party_roles[date][p] = res
                except:
                    pass

        #print(last, speech_row[date_ix], uri, '\t-->', res)

        cleaned_rows.append([speech_id, session, date, start.strip(), end, speaker['first'],
                             speaker['lastname'], speaker['role'], speaker['party'], topic, content, speaker['speechtype'], speaker['uri'], speaker['gender'], speaker['birth'], speaker['party_uri'], res, speaker['group'], row[8], lang, original_actor, row[7]])
# save to csv.file
output_file = filename[:-8]
csv.field_size_limit(sys.maxsize)

# sort sessions so that split sessions (sessions interrupted by 'Kyselytunti'session)
# are consecutive to avoid issues later on (identical URIs)
cleaned_rows.sort(key=sort_sessions)

with open('{:s}.csv'.format(output_file), 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerow(['speech_id', 'session', 'date', 'start_time', 'end_time', 'given', 'family', 'role', 'party', 'topic',
                     'content', 'speech_type', 'mp_uri', 'gender', 'birth', 'party_uri', 'parliamentary_role', 'group_uri', 'link', 'lang', 'name_in_source', 'page'])
    writer.writerows(cleaned_rows)

# pprint(set(not_found))
