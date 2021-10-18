import csv
import sys


csv.field_size_limit(sys.maxsize)


with open('speeches_1999_a.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    a = list(reader)

with open('speeches_1999_b.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    b = list(reader)


with open('speeches_1999.csv', 'w', newline='') as save_to:
    writer = csv.writer(save_to, delimiter=',')
    writer.writerow(['speech_id', 'session', 'date', 'start_time', 'end_time', 'given', 'family', 'role', 'party',
                     'topic', 'content', 'speech_type', 'mp_uri', 'gender', 'birth', 'party_uri', 'parliamentary_role', 'group_uri',
                     'status', 'version', 'link', 'lang', 'name_in_source', 'page', 'discussion_page_link'])

    for row in a[1:]:
        row[18:18] = ['', '']
        writer.writerow(row)

    for row in b[1:]:
        row.insert(23, '')
        writer.writerow(row)
