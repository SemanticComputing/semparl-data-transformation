import csv
import sys
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
from xml.dom import minidom
import re
from pprint import pprint


def chairman_tag(title):
    if 'Ikäpuhemies' in title:
        return 'elderMember'
    elif 'Puhemies' in title:
        return 'chairman'
    elif 'Ensimmäinen varapuhemies' in title:
        return 'viceChair'
    elif 'Toinen varapuhemies' in title:
        return 'secondViceChair'
    else:
        return 'chair'


def is_interruption(m):
    bad_patterns = [
        '^[A-ZÅÄÖ]+ \d?',   # Documents, all-cap abbreviations
        '\d+/\d+',          # More documents
        '^[ÄA]än[\.,]? ?\d+',     # Votes
        '^Kon[ec]e?ään[\.,]? ?\d+',     # Votes
        'Lähde:', 'Källa:',
        '^Liite ',
        '^Pöytäkirjan liite',
        'vastalause$'
    ]

    for bad in bad_patterns:
        if re.compile(bad).search(m):
            return False
    if not m[0].isupper() or m.isupper():  # or m[0].isdigit()
        return False
    if len(m) > 300:
        return False
    return True


def check_interruptions(content):
    parts = []
    interruptions = []
    matches = re.findall('\([^)]+\)|\[[^\]]+\]', content)

    # finds correct interruptions from parts encased in brackets
    if matches:
        for m in matches:
            clean_m = re.sub('\(|\)|\[|\]|\|', '', m).strip()
            if is_interruption(clean_m):
                interruptions.append(m)

    if not interruptions:
        return [content]
    else:
        # splits speech to speech and interruption sections
        to_split = content
        for i in interruptions:
            parts += [to_split.partition(i)[0]]  # speech
            parts += ['INTER'+re.sub('\(|\)|\[|\]|\|', '', to_split.partition(i)
                                     [1]).strip()]  # interruption
            to_split = to_split.partition(i)[2]  # rest of the speech
        if to_split.strip():
            parts += [to_split.strip()]
        return parts


def build_tree(speeches, year):
    root = Element(
        'teiCorpus', {'xml:id': 'Speeches_{:s}'.format(year), 'xml:lang': 'eng'})
    # xml:id should be equal to file name module extension(.xml)

    # Build teiHeader for the whole odcument
    teiHeader = SubElement(root, 'teiheader')

    fileDesc = SubElement(teiHeader, 'fileDesc')
    titleStmt = SubElement(fileDesc, 'titleStmt')
    title = SubElement(titleStmt, 'title')
    title.text = 'Finnish Parliament plenary session speeches during Diet {:s}'.format(
        year)
    title2 = SubElement(titleStmt, 'title')
    title2.text = 'Suomen eduskunnan täysistuntojen puheet Valtiopäivillä {:s}'.format(
        year)
    extent = SubElement(fileDesc, 'extent')
    measure = SubElement(extent, 'measure', {
                         'unit': 'speeches', 'quantity': str(len(speeches))})
    measure.text = '{:d} speeches'.format(len(speeches))

    encodingDesc = SubElement(teiHeader, 'encodingDesc')
    classDecl = SubElement(encodingDesc, 'classDecl')
    taxonomy = SubElement(classDecl, 'taxonomy')
    tax_desc = SubElement(taxonomy, 'desc')
    tax_desc.text = 'Types of chairmen'

    profileDesc = SubElement(teiHeader, 'profileDesc')
    settingDesc = SubElement(profileDesc, 'settingDesc')
    setting = SubElement(settingDesc, 'setting')
    setting_name = SubElement(
        setting, 'name', {'type': 'country', 'key': 'FIN'})
    setting_name.text = 'Finland'
    particDesc = SubElement(profileDesc, 'particDesc')
    listPerson = SubElement(particDesc, 'listPerson')
    listOrg = SubElement(particDesc, 'listOrg')

    all_speakers = []
    all_parties = []
    all_roles = []
    current_document = ''
    current_topic = '-'
    year = year.partition('_')[0]  # 1975_II
    for row in speeches:
        speech_id, document, date, start, end = row[0], row[1], row[2], row[3], row[4]
        firstname, lastname, party = row[5].strip(
        ), row[6].strip(), row[7].strip(),
        topic, content, reply = row[8], row[9], row[10]
        status, version, link = row[11], row[12].lstrip('versio'), row[13]
        speech_start, speech_end, page = '', '', ''
        content = content.replace('\n', '')
        if int(year) > 2014:
            if len(row) > 17:
                speech_start = row[17]
            if len(row) > 18:
                speech_end = row[18]
        if int(year) < 1999 or (int(year) == 1999 and int(document.partition('/')[0]) < 86):
            page = row[16]

        if document != current_document:
            current_document = document
            current_topic = '-'
           # new session -> new TEI child for teiCorpus

            # Build TEI = session's speeches
            tei = SubElement(
                root, 'TEI', {'xml:id': 'ptk_' + document.replace('/', '_')})
            tei_teiHeader = SubElement(tei, 'teiHeader')

            tei_fileDesc = SubElement(tei_teiHeader, 'fileDesc')
            tei_titleStmt = SubElement(tei_fileDesc, 'titleStmt')
            tei_title = SubElement(tei_titleStmt, 'title')
            tei_title.text = 'PTK {:s}'.format(
                document)
            tei_sourceDesc = SubElement(tei_fileDesc, 'sourceDesc')
            bibl = SubElement(tei_sourceDesc, 'bibl')
            tei_edition = SubElement(bibl, 'edition')
            if status.strip():
                tei_edition.text = status
            if version.strip():
                tei_edition.set('n', version.lstrip('.'))
            tei_profileDesc = SubElement(tei_teiHeader, 'profileDesc')
            settingDesc = SubElement(tei_profileDesc, 'settingDesc')
            setting = SubElement(settingDesc, 'setting')
            date_tag = SubElement(setting, 'date', {
                'when': date})
            date_tag.text = date
            time = SubElement(setting, 'time', {'from': start, 'to': end})

            # Build body = all of the sessions's actual speeches
            text = SubElement(tei, 'text')
            body = SubElement(text, 'body')

        # check if speaker or party already added to corpus metadata, if not, add
        speaker = '{:s}_{:s}'.format(firstname.replace(' ', '_'), lastname)
        if speaker not in all_speakers:
            all_speakers.append(speaker)
            person = SubElement(listPerson, 'person', {'xml:id': speaker})
            persName = SubElement(person, 'persName')
            surname = SubElement(persName, 'surname')
            surname.text = lastname
            forename = SubElement(persName, 'forename')
            forename.text = firstname

            if (not party.isupper() and 'uhemies' not in party):
                # add role to personal information
                role = SubElement(persName, 'roleName')
                role.text = party

            elif 'uhemies' in party:
                role = SubElement(persName, 'roleName')
                role.text = party
                # add chairpeople to taxonomy for referral in utterance 'ana'
                tag = chairman_tag(party)
                if party not in all_roles:
                    all_roles.append(party)
                    tax_cat = SubElement(taxonomy, 'category', {'xml:id': tag})
                    catDesc = SubElement(tax_cat, 'catDesc')
                    term = SubElement(catDesc, 'term')
                    term.text = party

            else:
                affliation = SubElement(person, 'affliation', {
                    'ref': '#party.' + party})
                if party not in all_parties:
                    all_parties.append(party)
                    org = SubElement(listOrg, 'org', {'xml:id': party})

        # for the years there are no names for chairs, add the roles to taxonomy
        if (party.endswith('uhemies') and party not in all_roles):
            tag = chairman_tag(party)
            all_roles.append(party)
            tax_cat = SubElement(taxonomy, 'category', {'xml:id': tag})
            catDesc = SubElement(tax_cat, 'catDesc')
            term = SubElement(catDesc, 'term')
            term.text = party

        # one topic in one div, subsequent topicless speeches are in one div
        if topic != current_topic:
            current_topic = topic
            topic_div = SubElement(body, 'div')
            head = SubElement(topic_div, 'head')
            if topic:
                parts = topic.split('>>>')
                head.text = re.sub('[0-9]+\)\W', '', parts[0])
                if len(parts) > 1:
                    listBibl = SubElement(head, 'listBibl')
                    b_head = SubElement(listBibl, 'head')
                    b_head.text = 'Related documents:'
                    for part in parts[1:]:
                        bibl = SubElement(listBibl, 'bibl')
                        bibl.text = part

        # one speech (with possible interruptions) in one sub-div
        div = SubElement(topic_div, 'div')
        note = SubElement(
            div, 'note', {'type': 'speaker', 'speechType': reply.strip(), 'link': link})
        if page:
            note.set('page', page)

        if not 'uhemies' in party:
            content = content.replace(':|', ': ')
            speech_parts = check_interruptions(content.strip())
            # no interruptions
            if len(speech_parts) == 1:
                u = SubElement(
                    div, 'u', {'who': '#{:s}'.format(speaker), 'xml.id': speech_id})
                if speech_start:
                    u.set('start', speech_start)
                if speech_end:
                    u.set('end', speech_end)
                u.text = content.strip()

            # interruptions
            else:
                speech_part = 1
                for i, part in enumerate(speech_parts):
                    if part.startswith('INTER'):  # interruption part
                        vocal = SubElement(div, 'vocal')
                        desc_v = SubElement(
                            vocal, 'desc')
                        desc_v.text = part.replace('INTER', '')
                    else:  # speech part
                        if len(speech_parts) == 2:
                            # only one speech section and one interruption, no need for extra id digit
                            u = SubElement(
                                div, 'u', {'who': '#{:s}'.format(speaker), 'xml.id': speech_id})
                        else:
                            u = SubElement(
                                div, 'u', {'who': '#{:s}'.format(speaker), 'xml.id': speech_id + '.' + str(speech_part)})
                            if i > 1:  # there's a previous section
                                u.set('prev', speech_id +
                                      '.' + str(speech_part-1))
                            if i < len(speech_parts)-2:  # there's a follow-up section
                                u.set('next', speech_id +
                                      '.' + str(speech_part+1))
                            speech_part += 1
                        u.text = part
        else:
            u = SubElement(
                div, 'u', {'who': '#{:s}'.format(speaker), 'xml.id': speech_id, 'ana': '#' + chairman_tag(party)})
            u.text = content

    return root


def main(year):
    speeches = []
    csv.field_size_limit(sys.maxsize)
    with open('speeches_{:s}.csv'.format(year), newline='') as f:
        reader = csv.reader(f)
        speeches = list(reader)
    root = build_tree(speeches, year)

    pretty_root = minidom.parseString(
        tostring(root).decode('utf-8')).toprettyxml(indent="   ")
    save_to_file = 'Speeches_{:s}.xml'.format(year)
    with open(save_to_file, "w") as file:
        file.write(pretty_root)


if __name__ == "__main__":
    main(sys.argv[1])
