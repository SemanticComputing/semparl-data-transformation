from speakerAnalyzer import *
import re
import sys
import csv
import time
import collections
import os
from pprint import pprint


########################################################
# Fetch more member info for HTML and XML -based years #
########################################################

sp = SpeakerAnalyzer()


def main(year):

    def find_by_name(first, last):
        if '-' in first:  # M.-L.
            temp = first.partition('-')[0]
            first = temp.strip('.')

        # first run considering only the "primary" lastname
        for row in member_info[1:]:
            parl_start = time.strptime(
                row[start_mpi], '%Y-%m-%d') if row[start_mpi] else None
            parl_end = time.strptime(
                row[end_mpi], '%Y-%m-%d') if row[end_mpi] else None
            if parl_start and parl_end:  # started as MP
                if (row[last_mpi] == last):
                    if (row[first_mpi].startswith(first)
                            and parl_start <= speech_date <= parl_end):
                        return row
            elif parl_start:
                if (row[last_mpi] == last):
                    if (row[first_mpi].startswith(first)
                            and parl_start <= speech_date):
                        return row

        # second run trying alternative names
        for row in member_info[1:]:
            parl_start = time.strptime(
                row[start_mpi], '%Y-%m-%d') if row[start_mpi] else None
            parl_end = time.strptime(
                row[end_mpi], '%Y-%m-%d') if row[end_mpi] else None
            alters = [] if row[alters_mpi] is None else row[alters_mpi].split(
                '; ')
            first_alters = [
            ] if row[first_alters_mpi] is None else row[first_alters_mpi].split('; ')

            if (parl_start and parl_end and alters):
                if ((last in alters or last == row[last_mpi]) and (row[first_mpi].startswith(first) or first in first_alters)
                        and parl_start <= speech_date <= parl_end):
                    return row
            elif parl_start and alters:
                if (last in alters):
                    if ((last.strip() in alters or last == row[last_mpi]) and (row[first_mpi].startswith(first) or first in first_alters)
                            and parl_start <= speech_date):
                        return row
        return ''

    with open('speeches_{}.csv'.format(year), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        speech_rows = list(reader)

    with open('parliamentMembers.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        member_info = list(reader)

    headers = speech_rows[0]
    first_ix = headers.index('given')
    last_ix = headers.index('family')
    party_ix = headers.index('party')
    role_ix = headers.index('role')
    date_ix = headers.index('date')
    type_ix = headers.index('speech_type')

    first_mpi = member_info[0].index('given')
    first_alters_mpi = member_info[0].index('other_given_names')
    last_mpi = member_info[0].index('family')
    alters_mpi = member_info[0].index('other_family_names')
    party_mpi = member_info[0].index('party')
    party_uri_mpi = member_info[0].index('party_ids')
    start_mpi = member_info[0].index('parl_period_start')
    end_mpi = member_info[0].index('parl_period_end')
    uri_mpi = member_info[0].index('id')
    short_uri_mpi = member_info[0].index('id__short')
    gender_mpi = member_info[0].index('gender')
    birth_mpi = member_info[0].index('birth')
    role_mpi = member_info[0].index('role_label')
    group_mpi = member_info[0].index('group_id')

    party_roles = {}

    if int(year) >= 2015:
        speaker_id_ix = speech_rows[0].index('speaker_id')
    else:
        speaker_id_ix = ''

    for speech_row in speech_rows[1:]:
        first = speech_row[first_ix].strip()
        last = speech_row[last_ix].strip()
        party = speech_row[party_ix]
        speech_date = time.strptime(speech_row[date_ix], '%Y-%m-%d')
        role = speech_row[role_ix].lower()
        speech_type = speech_row[type_ix].strip()
        correct_row = ''

        if speaker_id_ix and len(speech_row) > speaker_id_ix and speech_row[speaker_id_ix].strip():
            # speaker id is already known
            speaker_id = speech_row[speaker_id_ix]

            for r in member_info[1:]:
                parl_start = time.strptime(
                    r[start_mpi], '%Y-%m-%d') if r[start_mpi] else None
                parl_end = time.strptime(
                    r[end_mpi], '%Y-%m-%d') if r[end_mpi] else None

                if speaker_id == r[short_uri_mpi].replace('Q', '') and parl_start:
                    if parl_end and parl_start <= speech_date <= parl_end:
                        correct_row = r
                        break
                    elif not parl_end and parl_start <= speech_date:
                        correct_row = r
                        break

        elif 'uhemies' in speech_row[role_ix] and not last:
            # unnamed chairperson
            for row in member_info[1:]:
                parl_start = time.strptime(
                    row[start_mpi], '%Y-%m-%d') if row[start_mpi] else None
                parl_end = time.strptime(
                    row[end_mpi], '%Y-%m-%d') if row[end_mpi] else None
                if row[role_mpi] == role:
                    if parl_start and parl_end and parl_start <= speech_date <= parl_end:
                        correct_row = row
                        break

        else:  # find mp by name
            correct_row = find_by_name(first, last)

        # used ID might not have matched the one in member_info (e.g. oikeusasiamies), try by name
        if speaker_id_ix and len(speech_row) > speaker_id_ix and speech_row[speaker_id_ix].strip() and not correct_row:
            correct_row = find_by_name(first, last)

        if correct_row:
            if not first:
                speech_row[first_ix] = correct_row[first_mpi]
            if not last:
                speech_row[last_ix] = correct_row[last_mpi]
            if not party:
                speech_row[party_ix] = correct_row[party_mpi].upper().strip(
                    '.')

            speech_row[12:12] = [correct_row[uri_mpi], correct_row[gender_mpi],
                                 correct_row[birth_mpi], correct_row[party_uri_mpi], correct_row[group_mpi]]

            # Find party's oppositon/government status
            if correct_row[uri_mpi]:
                p = speech_row[party_ix]
                date_string = speech_row[date_ix]
                if date_string in party_roles and p in party_roles[date_string]:
                    res = party_roles[date_string][p]
                else:
                    uri = correct_row[uri_mpi].rpartition('/')[2]
                    try:
                        res = sp.find(date=date_string, member=uri)[
                            'type'].replace('ammatti/', '')
                        if not date_string in party_roles:
                            party_roles[date_string] = {}
                        party_roles[date_string][p] = res
                    except:
                        res = ''
                speech_row.insert(16, res)
                #print(last, speech_row[date_ix], uri, '\t-->', res)

        else:
            speech_row[12:12] = ['', '', '', '', '', '']

        if not speech_type:
            if 'uhemies' in role:
                speech_row[type_ix] = 'PuhemiesPuheenvuoro'
            else:
                speech_row[type_ix] = 'Puheenvuoro'

    headers[12:12] = ['mp_uri', 'gender',
                      'birth', 'party_uri', 'parliamentary_role', 'group_uri']
    # pprint(party_roles)

    with open('speeches_{}.csv'.format(year), 'w', newline='') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerow(headers)
        writer.writerows(speech_rows[1:])


if __name__ == "__main__":
    csv.field_size_limit(sys.maxsize)
    #print(sp.find(date='1932-02-01', member='Q11858669'))
    # sys.exit()
    main(sys.argv[1])
