import re
import sys
import csv
import time
import collections
import difflib
import os
from pprint import pprint
import pandas as pd

member_info = None


def extract_details(row, role, last):
    mp = {
        'uri': row['id'],
        'first': row['given'],
        'lastname': last,
        'gender': row['gender'],
        'birth': row['birth'],
        'role': role.strip(),
        'party': row['party'],
        'party_uri': row['party_ids']
    }

    return mp


def find_person(first, last, role, date):
    speech_date = pd.to_datetime(date)
    mp = {}
    if '-' in first:  # M.-L.
        temp = first.partition('-')[0]
        first = temp.strip('.')
    if '.' in first:  # G.G.
        first = first.partition('.')[0]

    # first run considering only the "primary" lastname and primary and alternative firstnames
    for i, row in member_info.iterrows():
        if pd.notnull(row['parl_period_start']):
            first_alters = [] if pd.isnull(
                row['other_given_names']) else row['other_given_names'].split('; ')
            if pd.notnull(row['parl_period_end']):  # ended as MP
                if (row['family'] == last.strip()):
                    if first.strip():
                        if (row['given'].startswith(first)
                                and row['parl_period_end'] >= speech_date >= row['parl_period_start']):
                            mp = extract_details(row, role, last)
                            break
                        elif first_alters and row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                            for fa in first_alters:
                                if fa.startswith(first):
                                    mp = extract_details(row, role, last)
                                    break
                    else:
                        if row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                            mp = extract_details(row, role, last)
                            break
            else:
                if (row['family'] == last.strip()):
                    if first.strip():
                        if (row['given'].startswith(first) and speech_date >= row['parl_period_start']):
                            mp = extract_details(row, role, last)
                            break
                        elif first_alters and row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                            for fa in first_alters:
                                if fa.startswith(first):
                                    mp = extract_details(row, role, last)
                                    break
                    else:
                        if speech_date >= row['parl_period_start']:
                            mp = extract_details(row, role, last)
                            break

    # second run trying alternative lastname
    if not mp:
        for i, row in member_info.iterrows():
            # started as MP + alternative names exist
            if (pd.notnull(row['parl_period_start']) and pd.notnull(row['other_family_names'])):
                first_alters = [] if pd.isnull(
                    row['other_given_names']) else row['other_given_names'].split('; ')
                alters = row['other_family_names'].split('; ')
                if pd.notnull(row['parl_period_end']):  # ended as MP
                    if (last.strip() in alters):
                        if first.strip():
                            if (row['given'].startswith(first)
                                    and row['parl_period_end'] >= speech_date >= row['parl_period_start']):
                                mp = extract_details(row, role, last)
                                break
                            elif first_alters and row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                                for fa in first_alters:
                                    if fa.startswith(first):
                                        mp = extract_details(row, role, last)
                                        break
                        else:
                            if row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                                mp = extract_details(row, role, last)
                                break
                else:
                    if (last.strip() in alters):
                        if first.strip():
                            if (row['given'].startswith(first) and speech_date >= row['parl_period_start']):
                                mp = extract_details(row, role, last)
                                break
                            elif first_alters and row['parl_period_end'] >= speech_date >= row['parl_period_start']:
                                for fa in first_alters:
                                    if fa.startswith(first):
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
        else:
            mp['party'] = ''
            mp['party_uri'] = ''

    if not 'uri' in mp:
        mp = {
            'uri': '',
            'first': first,
            'lastname': last,
            'gender': '',
            'birth': '',
            'role': role.strip(),
            'party': '',
            'party_uri': ''
        }

    if type(mp['party']) == float:  # NaN
        mp['party'] = ''
    else:
        mp['party'] = mp['party'].strip('.').upper()
    # edit here to not cause error on NaN

    return mp


##########################################
def main(file_year):
    csv.field_size_limit(sys.maxsize)
    is_in_docker = os.environ.get('RUNNING_IN_DOCKER_CONTAINER', False)

    with open('speeches_{}.csv'.format(file_year), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = list(reader)

    if not is_in_docker:
        with open('backups/speeches_{}_BAK2.csv'.format(file_year), 'w', newline='') as backup:
            writer = csv.writer(backup, delimiter=',')
            writer.writerows(rows)

    members = pd.read_csv('parliamentMembers.csv', sep='\t')


# create list of all possible lastnames for last option, "close option matching"
    all_lastnames = []
    for i, row in members.iterrows():
        if row['family'] not in all_lastnames and type(row['family']) != float:
            all_lastnames.append(row['family'])
        if pd.notnull(row['other_family_names']):
            temp = row['other_family_names'].split('; ')
            for n in temp:
                if n not in all_lastnames and type(n) != float:
                    all_lastnames.append(n)

    year_num = int(re.sub('_(XX|II)', '', file_year))
    problems_start = []
    headers = rows[0]
    first_ix = rows[0].index('given')
    last_ix = rows[0].index('family')
    role_ix = rows[0].index('role')
    party_ix = rows[0].index('party')
    uri_ix = rows[0].index('mp_uri')
    date_ix = rows[0].index('date')
    gender_ix = rows[0].index('gender')
    birth_ix = rows[0].index('birth')
    party_uri_ix = rows[0].index('party_uri')

    # # check the starting state

    # for row in rows[1:]:
    #     first = row[first_ix]
    #     last = row[last_ix]
    #     role = row[role_ix]
    #     mp_uri = row[uri_ix]

    #     # if (not party and not last) or (not 'uhemies' in role and (not first or not last[0].isupper()
    #     #                                                             or (first and not first[0].isupper())
    #     #                                                             or (first and (len(first) < 3 or len(first) > 14)))):
    #     if not mp_uri and not 'uhemies' in role:
    #         problems_start.append(', '.join([first, last, role]))

    # problem_percentage_start = float(len(problems_start))/len(rows)*100
    # num_of_problems_start = 'Before edits {}/{} of speaker names had problems.\nThat is {:.2f} %.\n\n'.format(
    #     len(problems_start), len(rows), problem_percentage_start)

    # freqs_start = list(collections.Counter(problems_start).items())
    # freqs_start.sort()


###############################
    members['parl_period_start'] = pd.to_datetime(
        members['parl_period_start'], format='%Y-%m-%d')
    members['parl_period_end'] = pd.to_datetime(
        members['parl_period_end'], format='%Y-%m-%d')

    # filter out some rows based on date for efficiency
    last_date = rows[-1][date_ix]
    global member_info
    member_info = members[
        members['parl_period_start'] <= pd.to_datetime(last_date)]

##############################
#  start cleaning

    new_rows = []

    for row in rows[1:]:
        speaker = {}
        first = row[first_ix]
        last = row[last_ix]
        party = row[party_ix]
        role = row[role_ix]
        mp_uri = row[uri_ix]
        speech_date = row[date_ix]

        # if (party or last) and (not 'uhemies' in party and (not first or not last[0].isupper()
        #                                                     or (first and not first[0].isupper())
        #                                                     or (first and (len(first) < 3 or len(first) > 14)))):
        if not mp_uri and not 'uhemies' in role:
            # "easier" mistakes; fix all then try to find person

            if first and re.compile('(\+ )?[FE]d[\.,]?$').match(first):
                first = ''
            if last.startswith('FE'):
                last = last[1:]
            if last.startswith('EF'):
                last = 'E' + last[2:]

            if role and role[-1] == '-':
                role = role[:-1]
            if last and last[-1] == '-':
                last = last[:-1]

            # , maa, Liikenneministeri Lin n ain
            # , ndersson, MinisteriA
            try:
                if last[0].islower():
                    second_cap_index = [match.start()
                                        for match in re.finditer("[A-ZÅÄÖ]", party)][1]
                    if second_cap_index:
                        temp_last = role[second_cap_index:]+last
                        role = role[:second_cap_index].strip()
                        last = temp_last.replace(' ', '')
            except:
                pass

            # vonBell
            if re.compile(r'(von|af)(.+)').match(last):
                last = re.sub(r'(von|af)(.+)', r'\1 \2', last)

            # f is an common trail letter
            if last and last[-1] in ['f']:
                last = last[:-1]

            # remove random symbols at end and start, (not zeros and ones)
            if last and not re.compile('[01Ia-zåäö]').match(last[-1]):
                last = last[:-1]

            if last and not re.compile('[01a-zåäöA-ZÅÄÖ]').match(last[0]):
                last = last[1:]

             # zero to o/O
            if '0' in last:
                if last[0] == '0':
                    last = 'O'+last[1:]
            last = last.replace('0', 'o')
            first = first.replace('0', 'O')

            last = last.replace("'", "")

            # 1 could be i as well, tried later
            # MaIm -> Malm, but not IKanerva ->lKanerva
            if last:
                last = last[0]+re.sub('[1I\|\]\[\]]', 'l', last[1:])

            last = last.replace('&', 'é')

            # JKoskinen, MinisteriHuttu
            for i in range(len(last)-2):
                if (last[i].isupper() or last[i].islower()) and last[i+1].isupper():
                    first = last[:i+1]
                    last = last[i+1:]
                    if 'inisteri' in first:
                        role = first
                        first = ''
                    break

        ########################
            speaker = find_person(
                first, last, role, speech_date)

            if speaker['uri']:  # a name's been  found
                row[uri_ix] = speaker['uri']
                row[first_ix] = speaker['first']
                row[last_ix] = speaker['lastname']
                row[gender_ix] = speaker['gender']
                row[birth_ix] = speaker['birth']
                row[role_ix] = speaker['role']
                row[party_ix] = speaker['party']
                row[party_uri_ix] = speaker['party_uri']

 # <-       ########################
            else:
                # start fresh
                first = row[first_ix]
                last = row[last_ix]
                party = row[party_ix]
                role = row[role_ix]
                mp_uri = row[uri_ix]
                speech_date = row[date_ix]
                speaker = {}

                try:  # , SalmelaJärvinen,
                    if not '-' in last and not ',' in last:
                        second_cap_index = []
                        second_cap_index = [match.start()
                                            for match in re.finditer("[A-ZÅÄÖ]", last)][1]
                    if second_cap_index:
                        last = last[:second_cap_index] + \
                            '-'+last[second_cap_index:]
                except:
                    pass

                try:  # [], V,Vennamo, []
                    if ',' in last:
                        temp = last.split(',')
                        first = temp[0].strip()
                        last = temp[1].strip()
                except:
                    pass

                ##########################
                speaker = find_person(
                    first, last, role, speech_date)

                # a name's been  found
                if speaker['uri']:  # a name's been  found
                    row[uri_ix] = speaker['uri']
                    row[first_ix] = speaker['first']
                    row[last_ix] = speaker['lastname']
                    row[gender_ix] = speaker['gender']
                    row[birth_ix] = speaker['birth']
                    row[role_ix] = speaker['role']
                    row[party_ix] = speaker['party']
                    row[party_uri_ix] = speaker['party_uri']
                ##########################
                else:
                    # start fresh, try closest match from all lastnames
                    # start fresh
                    first = row[first_ix]
                    last = row[last_ix]
                    party = row[party_ix]
                    role = row[role_ix]
                    mp_uri = row[uri_ix]
                    speech_date = row[date_ix]
                    speaker = {}

                    match_options = []

                    match_options = difflib.get_close_matches(
                        last, all_lastnames)

                    if match_options and abs(len(last)-len(match_options[0])) < 4:
                        last = match_options[0]

                        ##########################
                        speaker = find_person(
                            first, last, role, speech_date)

                        # a name's been  found
                        if speaker['uri']:  # a name's been  found
                            row[uri_ix] = speaker['uri']
                            row[first_ix] = speaker['first']
                            row[last_ix] = speaker['lastname']
                            row[gender_ix] = speaker['gender']
                            row[birth_ix] = speaker['birth']
                            row[role_ix] = speaker['role']
                            row[party_ix] = speaker['party']
                            row[party_uri_ix] = speaker['party_uri']
                        ##########################

        new_rows.append(row)

    ################################################################
    ################################################################

    # check the results
    # problems_end = []

    # for row in new_rows:
    #     first = row[first_ix]
    #     last = row[last_ix]
    #     role = row[role_ix]
    #     mp_uri = row[uri_ix]

    #     if not mp_uri and not 'uhemies' in role:
    #         problems_end.append(', '.join([first, last, role]))

    # problem_percentage_end = float(len(problems_end))/len(new_rows)*100
    # num_of_problems_end = 'After edits {}/{} of speaker names had problems.\nThat is {:.2f} %.'.format(
    #     len(problems_end), len(new_rows), problem_percentage_end)

    # freqs_end = list(collections.Counter(problems_end).items())
    # freqs_end.sort()

    # # name stats
    # if not is_in_docker:
    #     with open('backups/name_log_{}.txt'.format(file_year), 'w',) as log_file:
    #         log_file.write('Name recognition statistics\n\n')
    #         log_file.write(num_of_problems_start)
    #         log_file.write(num_of_problems_end)
    #         log_file.write('\n\nFound issues and frequencies at start:\n')
    #         for person, freq in freqs_start:
    #             log_file.write('{}\t{}\n'.format(person, freq))
    #         log_file.write('\n----------------------------------------\n\n')
    #         log_file.write('Remaining issues and frequencies after edits:\n')
    #         for person, freq in freqs_end:
    #             log_file.write('{}\t{}\n'.format(person, freq))

    # save cleaned version
    with open('speeches_{}.csv'.format(file_year), 'w', newline='') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerow(headers)
        writer.writerows(new_rows)

    # print(num_of_problems_end)


##################################################
main(sys.argv[1])
