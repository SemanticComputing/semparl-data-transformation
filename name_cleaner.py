import re
import sys
import csv
import time
import collections
import difflib
import os


def find_person(first, last, date, member_info):
    speech_date = time.strptime(date, '%Y-%m-%d')

    if '-' in first:  # M.-L.
        temp = first.partition('-')[0]
        first = temp.strip('.')
    if '.' in first:  # G.G.
        first = first.partition('.')[0]

    # first run considering only the "primary" lastname and primary and alternative firstnames
    for row in member_info[1:]:
        if row[8]:  # started as MP
            first_alters = [] if row[5] is None else row[5].split('; ')
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if (row[2] == last.strip()):
                    if first.strip():
                        if (row[3] and row[3].startswith(first)
                                and row_end >= speech_date >= row_start):
                            return row[3], row[2], row[10], True
                        if first_alters and row[3] and row_end >= speech_date >= row_start:
                            for fa in first_alters:
                                if fa.startswith(first):
                                    return row[3], row[2], row[10], True
                    else:
                        if row_end >= speech_date >= row_start:
                            return row[3], row[2], row[10], True
            else:
                if (row[2] == last.strip()):
                    if first.strip():
                        if (row[3] and row[3].startswith(first) and speech_date >= row_start):
                            return row[3], row[2], row[10], True
                        if first_alters and row[3] and row_end >= speech_date >= row_start:
                            for fa in first_alters:
                                if fa.startswith(first):
                                    # print('orig:', first, last,
                                    #       'found:', row[3], row[2])
                                    return row[3], row[2], row[10], True
                    else:
                        if speech_date >= row_start:
                            return row[3], row[2], row[10], True

    # second run trying alternative lastname
    for row in member_info[1:]:
        if (row[8] and row[4]):  # started as MP + alternative names exist
            first_alters = [] if row[5] is None else row[5].split('; ')
            alters = [] if row[4] is None else row[4].split('; ')
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if (last.strip() in alters):
                    if first.strip():
                        if (row[3] and row[3].startswith(first)
                                and row_end >= speech_date >= row_start):
                            return row[3], row[2], row[10], True
                        if first_alters and row[3] and row_end >= speech_date >= row_start:
                            for fa in first_alters:
                                if fa.startswith(first):
                                    return row[3], row[2], row[10], True
                    else:
                        if row_end >= speech_date >= row_start:
                            return row[3], row[2], row[10], True
            else:
                if (last.strip() in alters):
                    if first.strip():
                        if (row[3] and row[3].startswith(first) and speech_date >= row_start):
                            return row[3], row[2], row[10], True
                        if first_alters and row[3] and row_end >= speech_date >= row_start:
                            for fa in first_alters:
                                if fa.startswith(first):
                                    return row[3], row[2], row[10], True
                    else:
                        if speech_date >= row_start:
                            return row[3], row[2], row[10], True

    return first, last, '', False


# Alters first name


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

    with open('python_csv_parliamentMembers.csv') as f:
        reader = csv.reader(f, delimiter='\t')
        member_info = list(reader)

    # create list of all possible lastnames for last option, "close option matching"
    all_lastnames = []
    for row in member_info[1:]:
        if row[2] not in all_lastnames:
            all_lastnames.append(row[2])
        if row[4]:
            temp = row[4].split('; ')
            for n in temp:
                if n not in all_lastnames:
                    all_lastnames.append(n)

    year_num = int(re.sub('_(XX|II)', '', file_year))
    problems_start = []

    # check the starting state
    for row in rows:
        first, last, party = row[5], row[6], row[7]
        if (not party and not last) or (not 'uhemies' in party and (not first or not last[0].isupper()
                                                                    or (first and not first[0].isupper())
                                                                    or (first and (len(first) < 3 or len(first) > 14)))):
            problems_start.append(', '.join([first, last, party]))

    problem_percentage_start = float(len(problems_start))/len(rows)*100
    num_of_problems_start = 'Before edits {}/{} of speaker names had problems.\nThat is {:.2f} %.\n\n'.format(
        len(problems_start), len(rows), problem_percentage_start)

    freqs_start = list(collections.Counter(problems_start).items())
    freqs_start.sort()

    new_rows = []

    for row in rows:
        first, last, party = row[5], row[6], row[7]
        speech_date = row[2]
        temp_party = ''
        if (party or last) and (not 'uhemies' in party and (not first or not last[0].isupper()
                                                            or (first and not first[0].isupper())
                                                            or (first and (len(first) < 3 or len(first) > 14)))):
            # "easier" mistakes; fix all then try to find person

            if first and re.compile('(\+ )?[FE]d[\.,]?$').match(first):
                first = ''
            if last.startswith('FE'):
                last = last[1:]
            if last.startswith('EF'):
                last = 'E' + last[2:]

            #last = re.sub('F?Ed[\,.]? ', '', last)

            # Party glued to lastname
            if last and last[-3:].isupper() and len(last) > 3:
                party = last[-3:]
                last = last[:-3]

            if party and party[-1] == '-':
                party = party[:-1]
            if last and last[-1] == '-':
                last = last[:-1]

            # , maa, Liikenneministeri Lin n ain
            # , ndersson, MinisteriA
            try:
                if last[0].islower():
                    second_cap_index = [match.start()
                                        for match in re.finditer("[A-ZÅÄÖ]", party)][1]
                    if second_cap_index:
                        temp_last = party[second_cap_index:]+last
                        party = party[:second_cap_index].strip()
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
            #!!!! myös é -> 6

            # JKoskinen, MinisteriHuttu
            for i in range(len(last)-2):
                if (last[i].isupper() or last[i].islower()) and last[i+1].isupper():
                    first = last[:i+1]
                    last = last[i+1:]
                    if 'inisteri' in first:
                        party = first
                        first = ''
                    break

            # "harder" mistakes; try one change at a time
            # Kokeile i -> j tai l
            #         j -> i
            #         l -> 1
            #         r -> t
            #         n -> m
            #         E -> F
            #         V -> W
            #         a <-> ä
            #         o <-> ö
            if party:  # minister
                temp_party = party
            first, last, party, match = find_person(
                first, last, speech_date, member_info)

            #######################
            if match:  # a name's been  found
                if temp_party and 'inisteri' in temp_party:
                    party = temp_party
                else:
                    party = party.strip('.').upper()
                row[5], row[6], row[7] = first, last, party
            ########################
            else:
                # start fresh
                first, last, party = row[5], row[6], row[7]

                #last = last.replace('1', 'i')

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

                first, last, party, match = find_person(
                    first, last, speech_date, member_info)
                ##########################
                if match:  # a name's been  found
                    row[5], row[6], row[7] = first, last, party.strip(
                        '.').upper()
                ##########################
                else:
                    # start fresh, try closest match from all lastnames
                    first, last, party = row[5], row[6], row[7]
                    temp_party = ''
                    match_options = []
                    match_options = difflib.get_close_matches(
                        last, all_lastnames)
                    # if last != 'Ed':
                    #     print(last, match_options)
                    if match_options and abs(len(last)-len(match_options[0])) < 4:
                        last = match_options[0]
                        if party and 'inisteri' in party:
                            temp_party = party
                        first, last, party, match = find_person(
                            first, last, speech_date, member_info)
                        if temp_party:
                            party = temp_party
                        else:
                            party = party.strip('.').upper()
                        ##########################
                        if match:  # a name's been  found
                            row[5], row[6], row[7] = first, last, party
                        ##########################

        new_rows.append(row)

    ################################################################

    # check the results
    problems_end = []
    for row in new_rows:
        first, last, party = row[5], row[6], row[7]
        if (not party and not last) or (not 'uhemies' in party and (not first or not last[0].isupper()
                                                                    or (first and not first[0].isupper())
                                                                    or (first and (len(first) < 3 or len(first) > 14)))):
            if not last.startswith('von ') and not last.startswith('af '):
                problems_end.append(', '.join([first, last, party]))

    problem_percentage_end = float(len(problems_end))/len(new_rows)*100
    num_of_problems_end = 'After edits {}/{} of speaker names had problems.\nThat is {:.2f} %.'.format(
        len(problems_end), len(new_rows), problem_percentage_end)

    freqs_end = list(collections.Counter(problems_end).items())
    freqs_end.sort()

    # name stats
    if not is_in_docker:
        with open('backups/name_log_{}.txt'.format(file_year), 'w',) as log_file:
            log_file.write('Name regognition statistics\n\n')
            log_file.write(num_of_problems_start)
            log_file.write(num_of_problems_end)
            log_file.write('Found issues and frequencies at start:\n')
            for person, freq in freqs_start:
                log_file.write('{}\t{}\n'.format(person, freq))
            log_file.write('\n----------------------------------------\n\n')
            log_file.write('Remaining issues and frequencies after edits:\n')
            for person, freq in freqs_end:
                log_file.write('{}\t{}\n'.format(person, freq))

    # save cleaned version
    with open('speeches_{}.csv'.format(file_year), 'w', newline='') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerows(rows)

    print(num_of_problems_end)


main(sys.argv[1])
