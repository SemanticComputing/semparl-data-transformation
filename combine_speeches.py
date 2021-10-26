import sys
import re
import csv
import json
import requests


def session_number(string):
    parts = string.split('/')
    return int(parts[0])


def fix_date(row):
    parts = row[1].split('-')
    if len(parts[2]) == 1:
        date = row[1][:8]+'0'+row[1][8:]
        row[1] = date


def fix_times(time):
    if ((len(time)) > 0 and '.' not in time):
        return time + '.00'


def main(year):
    main_page_csv = 'main_page_speeches_{:s}.csv'.format(
        year)
    discussions_csv = 'discussions_{:s}.csv'.format(
        year)
    skt_times_csv = 'skt_times_{:s}.csv'.format(
        year)
    main_page_rows = []
    discussion_rows = []
    skt_times = []
    with open(main_page_csv, newline='') as mpf:
        main_page_reader = csv.reader(mpf)
        main_page_rows = list(main_page_reader)
    with open(discussions_csv, newline='') as df:
        discussion_reader = csv.reader(df)
        discussion_rows = list(discussion_reader)
    with open(skt_times_csv, newline='') as sktf:
        skt_reader = csv.reader(sktf)
        skt_times = list(skt_reader)

#'session', 'date', 'session_start', 'session_end', 'actorFirstname',
# 'actorLastname', 'party', 'topic', 'content', 'speechType', 'status', 'version', 'link', 'discussionLink'])

    # There were no speeches in the main page for 'Suullinen kyselytunti'
    # so no ending time info for those sessions exists in _speeches-document but had to be gathered separately
    times = {}
    for row in skt_times:
        times[row[0]] = {}
        times[row[0]]['end'] = row[1]

    all_speeches = []
    current_session = session_number(main_page_rows[1][0])
    for row in main_page_rows[1:]:
        session = session_number(row[0])
        # add time
        if not row[0] in times.keys():
            times[row[0]] = {}
            times[row[0]]['end'] = row[3]
        # a session skipped in main_page_csv (=kyselytunti)
        if session > current_session+1:
            for drow in discussion_rows[1:]:
                if session_number(drow[0]) == current_session+1:
                    all_speeches.append(drow)
                    times[drow[0]]['start'] = drow[2]
            current_session += 1
        if session == current_session + 1:
            # discussion pages that had no leading chairman comment to anchor them
            for drow in discussion_rows[1:]:
                if (session_number(drow[0]) == current_session and drow not in all_speeches):
                    all_speeches.append(drow)
                    times[drow[0]]['start'] = drow[2]
            current_session = session
        all_speeches.append(row)
        if row[13]:
            if '+skt+puh+' in row[13]:
                for drow in discussion_rows[1:]:
                    if '+skt+puh+' in drow[12] and session_number(drow[0]) == current_session and drow not in all_speeches:
                        #drow[7] = row[7]
                        all_speeches.append(drow)
                        times[drow[0]]['start'] = drow[2]

            else:
                for drow in discussion_rows[1:]:
                    if drow[12] == row[13]:
                        #drow[7] = row[7]
                        all_speeches.append(drow)
                        times[drow[0]]['start'] = drow[2]
    for drow in discussion_rows[1:]:
        if drow not in all_speeches:
            all_speeches.append(drow)
            times[drow[0]]['start'] = drow[2]

    chairman, vice, second_vice = '', '', ''
    current_session = all_speeches[0][0]
    i = 1
    for row in all_speeches:
        clean_name = re.sub(' +', ' ', row[6])
        row[6] = clean_name
        # fill in chairpeople names
        if (row[6] == 'Puhemies' and row[5] and row[4] and not chairman):
            chairman = [row[4], row[5]]
        if (row[6] == 'Ensimmäinen varapuhemies' and row[5] and row[4] and not vice):
            vice = [row[4], row[5]]
        if (row[6] == 'Toinen varapuhemies' and row[5] and row[4] and not second_vice):
            second_vice = [row[4], row[5]]
        if ('Puhemies' in row[6] and not row[5] and not row[4] and chairman):
            row[4], row[5] = chairman[0], chairman[1]
            row[6] = 'Puhemies'  # fixes Puhemies Riitta Uosukainen
        if ('Ensimmäinen varapuhemies' in row[6] and not row[5] and not row[4] and vice):
            row[4], row[5] = vice[0], vice[1]
            row[6] = 'Ensimmäinen varapuhemies'
        if ('Toinen varapuhemies' in row[6] and not row[5] and not row[4] and second_vice):
            row[4], row[5] = second_vice[0], second_vice[1]
            row[6] = 'Toinen varapuhemies'
        if ('Ikäpuhemies' in row[6] and len(row[6]) > 12):
            parts = row[6].split()
            row[4] = parts[1]
            row[5] = parts[2]
            row[6] = 'Ikäpuhemies'
        if (not row[2] and row[0] in times.keys() and 'start' in times[row[0]].keys()):
            row[2] = times[row[0]]['start']
        if (not row[3] and row[0] in times.keys() and 'end' in times[row[0]].keys()):
            row[3] = times[row[0]]['end']
        if current_session != row[0]:
            current_session = row[0]
            i = 1
        # ensure times and times are in proper format
        fix_date(row)
        if len(row[2]) < 5:
            row[2] = fix_times(row[2])
        if len(row[3]) < 5:
            row[3] = fix_times(row[3])
        # create speech ids
        speech_order_num = '{:s}_{:d}_{:d}'.format(
            year, session_number(row[0]), i)
        row.insert(0, speech_order_num)
        i += 1
        # check language
        try:
            parameters = {'text': str(row[9])}
            results = requests.get(
                'http://demo.seco.tkk.fi/las/identify', params=parameters).json()
            tags = []
            tags = [k for d in results['details']
                    ['languageDetectorResults'] for k in d.keys()]
            l = len(row)
            row.insert(14, ':'.join(tags))
        except:
            row.insert(14, '')

        if 'uhemies' in row[7]:
            row.insert(15, row[7] + ' ' + row[5] + ' ' + row[6])
        else:
            row.insert(15, row[5] + ' ' + row[6])
        if row[1] == '89/2009':
            row[2] = '2009-10-08'

        if row[7].isupper():
            # party known, add role
            row.insert(7, 'Kansanedustaja')
        else:
            # role known, add placeholder for party
            row.insert(7, row[7])
            row[8] = ''

    with open('speeches_{:s}.csv'.format(year), 'w') as save_to:
        writer = csv.writer(save_to, delimiter=',')
        writer.writerow(['speech_id', 'session', 'date', 'start_time', 'end_time', 'given', 'family', 'role', 'party', 'topic',
                         'content', 'speech_type', 'status', 'version', 'link', 'lang', 'name_in_source', 'discussion_page_link'])
        writer.writerows(all_speeches)
    # with open('speeches_{:s}.tsv'.format(year), 'w') as save_to:
    #    writer = csv.writer(save_to, delimiter='\t')
    #    writer.writerows(all_speeches)


if __name__ == "__main__":
    main(sys.argv[1])
