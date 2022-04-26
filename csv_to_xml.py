from ast import Sub
import csv
import sys
import time
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
from xml.dom import minidom
from lxml import etree
import re
from pprint import pprint


def chairman_tag(title):
    if 'Ikäpuhemies' in title:
        return 'elderMember'
    elif 'Puhemies' in title:
        return 'chairman'
    elif 'Ensimmäinen varapuhemies' in title or 'Varapuhemies' in title:
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
        '^Liitteet ',
        '^Pöytäkirjan liite',
        'vastalause$',
        'Tulkki esittää puheenvuorosta suomenkielisen yhteenvedon',
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
    num_of_speech_parts = 0
    matches = re.findall('\([^)]+\)|\[[^\]]+\]', content)

    # finds correct interruptions from parts encased in brackets
    if matches:
        for m in matches:
            clean_m = re.sub('\(|\)|\[|\]|\|', '', m).strip()
            if is_interruption(clean_m):
                interruptions.append(m)

    if not interruptions:
        return [content], 0
    else:
        # splits speech to speech and interruption sections
        to_split = content
        for i in interruptions:
            parts += [to_split.partition(i)[0]]  # speech
            num_of_speech_parts += 1  # ceep count of speech parts

            inter = to_split.partition(i)[1].strip()
            # if there are several speakers in one interruption (seperated by -),
            # split interruption
            i_parts = inter.split(' — ')
            for part in i_parts:
                parts += ['INTER'+re.sub('\(|\)|\[|\]|\|', '', part.strip())]

            # parts += ['INTER'+re.sub('\(|\)|\[|\]|\|', '', to_split.partition(i)
            #                         [1]).strip()]  # interruption
            to_split = to_split.partition(i)[2]  # rest of the speech
        if to_split.strip():
            parts += [to_split.strip()]
            num_of_speech_parts += 1
        return parts, num_of_speech_parts


def check_if_interruptor_named(content, year):
    # check if an interrupting agent has been clearly differentiated with ':'
    # 2011->
    # Paavo Arhinmäki
    # Ensimmäinen varapuhemies Mauri Pekkarinen
    # pre 2011:
    # Ed. Oksala | Fd. Aittoniemi | Rdm. Backlund
    # Pääministeri Virolainen | Min. Taina
    # Ed. U-M. Kukkonen | Ed Räisänen | Kanerva

    firstname = ''
    lastname = ''

    if (':'not in content and ';' not in content):
        return '', ''

    agent = re.split(':|;', content, 1)[0]

    parts = agent.split()
    if int(year) >= 2011:
        if(len(parts) > 1 and parts[-2][0].isupper() and (parts[-1][0].isupper() or parts[-1] == 'al-Taee')):
            firstname = parts[-2].strip()
            lastname = parts[-1].strip()
    else:
        if len(parts) > 2:  # there might be initials
            if parts[-2] in ['von', 'af']:
                firstname = ''
                lastname = ' '.join(parts[-2:])
            else:
                firstname = parts[-2].strip()
                lastname = parts[-1].strip()
        else:
            if parts:
                lastname = parts[-1].strip()
        if not lastname or (not lastname[0].isupper() and not re.compile('al\-|von | af ').match(lastname)) or 'uhemies' in lastname:
            return '', ''

    lastname = re.sub('\xa0', '', lastname)
    return firstname, lastname


def find_interrupter_by_lastname(first, last, date, member_info):
    # for years up to 2010 where we don't know interruptors first name, only possible initials
    speech_date = time.strptime(date, '%Y-%m-%d')

    if '-' in first:  # M.-L.
        temp = first.partition('-')[0]
        first = temp.strip('.')
    if '.' in first:  # G.G.
        first = first.partition('.')[0]

    first_mpi = member_info[0].index('given')
    first_alters_mpi = member_info[0].index('other_given_names')
    last_mpi = member_info[0].index('family')
    alters_mpi = member_info[0].index('other_family_names')
    party_mpi = member_info[0].index('party')
    start_mpi = member_info[0].index('parl_period_start')
    end_mpi = member_info[0].index('parl_period_end')
    gender_mpi = member_info[0].index('gender')
    birth_mpi = member_info[0].index('birth')

    # first run considering only the "primary" lastname
    for row in member_info[1:]:
        parl_start = time.strptime(
            row[start_mpi], '%Y-%m-%d') if row[start_mpi] else None
        parl_end = time.strptime(
            row[end_mpi], '%Y-%m-%d') if row[end_mpi] else None

        if parl_start and parl_end:  # started as MP
            if (row[last_mpi] == last) and row[first_mpi].startswith(first) and parl_start <= speech_date <= parl_end:
                return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]
        elif parl_start:
            if (row[last_mpi] == last) and row[first_mpi].startswith(first) and parl_start <= speech_date:
                return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]

    # # second run trying alternative labels
    for row in member_info[1:]:
        parl_start = time.strptime(
            row[start_mpi], '%Y-%m-%d') if row[start_mpi] else None
        parl_end = time.strptime(
            row[end_mpi], '%Y-%m-%d') if row[end_mpi] else None

        alters = row[alters_mpi].split('; ') if row[alters_mpi] else []
        first_alters = row[first_alters_mpi].split(
            '; ') if row[first_alters_mpi] else []

        if parl_start and parl_end:  # started as MP
            if (row[last_mpi] == last or last in alters) and parl_start <= speech_date <= parl_end:
                if first:
                    if row[first_mpi].startswith(first):
                        return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]
                    for f in first_alters:
                        if f.startswith(first):
                            return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]
                else:
                    return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]
        elif parl_start:
            if (row[last_mpi] == last or last in alters) and parl_start <= speech_date:
                if first:
                    if row[first_mpi].startswith(first):
                        return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]
                    for f in first_alters:
                        if f.startswith(first):
                            return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]
                else:
                    return row[first_mpi], row[party_mpi], row[birth_mpi], row[gender_mpi]

    return '', '', '', ''


def find_party(first, last, date):
    speech_date = time.strptime(date, '%Y-%m-%d')
    party = ''
    for row in member_info[1:]:
        if row[8]:  # started as MP
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if (row[2] == last.strip() and row[3] and row[3] == first.strip()
                        and row_end >= speech_date >= row_start):
                    party = row[10]

            else:
                if (row[2] == last.strip() and row[3]
                        and row[3] == first.strip() and speech_date >= row_start):
                    party = row[10]

     # second run trying alternative labels
    for row in member_info[1:]:
        if (row[8] and row[4]):  # started as MP + alternative names exist
            alters = [] if row[4] is None else row[4].split('; ')
            row_start = time.strptime(row[8], '%Y-%m-%d')
            if row[9]:  # ended as MP
                row_end = time.strptime(row[9], '%Y-%m-%d')
                if (last.strip() in alters and row[3] and row[3] == first.strip()
                        and row_end >= speech_date >= row_start):
                    party = row[10]
            else:
                if (last.strip() in alters and row[3] and row[3] == first.strip()
                        and speech_date >= row_start):
                    party = row[10]

    party = party.strip('.').upper()
    return party


def build_tree(speeches, year, member_info):
    root = Element(
        'teiCorpus', {'xml:id': 'Speeches_{:s}'.format(year), 'xml:lang': 'fi'})
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

    speech_id_ix = speeches[0].index('speech_id')
    session_ix = speeches[0].index('session')
    date_ix = speeches[0].index('date')
    start_ix = speeches[0].index('start_time')
    end_ix = speeches[0].index('end_time')

    first_ix = speeches[0].index('given')
    last_ix = speeches[0].index('family')
    role_ix = speeches[0].index('role')
    party_ix = speeches[0].index('party')
    parl_role_ix = speeches[0].index('parliamentary_role')
    gender_ix = speeches[0].index('gender')
    birth_ix = speeches[0].index('birth')

    topic_ix = speeches[0].index('topic')
    content_ix = speeches[0].index('content')
    type_ix = speeches[0].index('speech_type')
    lang_ix = speeches[0].index('lang')
    link_ix = speeches[0].index('link')
    orig_name = speeches[0].index('name_in_source')

    try:  # ->1999
        page_ix = speeches[0].index('page')
    except:
        page_ix = ''

    try:  # 2000->
        status_ix = speeches[0].index('status')
        version_ix = speeches[0].index('version')
    except:
        status_ix, version_ix = '', ''

    try:  # 2015 ->
        speech_status_ix = speeches[0].index('speech_status')  # ei käytössä?
        speech_version_ix = speeches[0].index('speech_version')  # ei käytössä?
        speech_start_ix = speeches[0].index('speech_start')
        speech_end_ix = speeches[0].index('speech_end')
    except:
        speech_status_ix, speech_version_ix, speech_start_ix, speech_end_ix = '', '', '', ''

    #######################
    # Go through speeches #
    #######################
    for row in speeches[1:500]:
        speech_id = row[speech_id_ix]
        document = row[session_ix]
        date = row[date_ix]
        start = row[start_ix]
        end = row[end_ix]

        firstname = row[first_ix].strip()
        lastname = row[last_ix].strip()
        party = row[party_ix].strip()
        role = row[role_ix].strip()
        gender = row[gender_ix]
        birth = row[birth_ix]
        lang = row[lang_ix]

        topic = row[topic_ix]
        content = row[content_ix].replace('\n', '').strip()
        speech_type = row[type_ix]

        link = row[link_ix]
        session_number = document.partition('/')[0]

        status, version = '', ''
        speech_start, speech_end, page = '', '', ''
        speech_status, speech_version = '', ''

        if page_ix and len(row) > page_ix:
            page = row[page_ix]

        if status_ix and len(row) > status_ix:
            status = row[status_ix]

        if version_ix and len(row) > version_ix:
            version = row[version_ix].lstrip('versio')

        if speech_status_ix and len(row) > speech_status_ix:
            speech_status = row[speech_status_ix]

        if speech_version_ix and len(row) > speech_version_ix:
            version = row[speech_version_ix].lstrip('versio')

        if speech_start_ix and len(row) > speech_start_ix:
            speech_start = row[speech_start_ix]

        if speech_end_ix and len(row) > speech_end_ix:
            speech_end = row[speech_end_ix]

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

            if (int(year) > 2008) or (year == '2008' and int(session_number) > 70):
                recordingUrl = 'https://verkkolahetys.eduskunta.fi/fi/taysistunnot/taysistunto-{}-{}'.format(
                    session_number, year)
                recordingStmt = SubElement(tei_fileDesc, 'recordingStmt')
                recording = SubElement(
                    recordingStmt, 'recording', {'type': 'video'})
                media = SubElement(recording, 'media', {
                                   'mimeType': 'mp4', 'url': recordingUrl})
                video_resp = SubElement(recording, 'respStmt')
                resp = SubElement(video_resp, 'resp')
                resp.text = 'Video recording'
                resp_name = SubElement(video_resp, 'name')
                resp_name.text = 'Eduskunta (Parliament of Finland)'

            # Build body = all of the sessions's actual speeches
            text = SubElement(tei, 'text')
            body = SubElement(text, 'body')

        # check if speaker or party already added to corpus metadata, if not, add
        speaker = '{:s}_{:s}'.format(firstname, lastname)
        speaker = speaker.replace(' ', '_')
        speaker = re.sub("[,&\|'!\]\)\(\+\$\d+]", '', speaker)
        speaker_role_party = speaker + role + party  # !!!!!!!!!!!!
        if speaker not in all_speakers:
            all_speakers.append(speaker)
            person = SubElement(listPerson, 'person', {
                                'xml:id': speaker})
            persName = SubElement(person, 'persName')
            surname = SubElement(persName, 'surname')
            surname.text = lastname
            forename = SubElement(persName, 'forename')
            forename.text = firstname
            if gender:
                if gender.lower() == 'male':
                    speaker_sex = SubElement(person, 'sex', {'value': 'M'})
                else:
                    speaker_sex = SubElement(person, 'sex', {'value': 'F'})
                speaker_sex.text = gender
            born_at = SubElement(person, 'birth', {'when': birth})

    # add role and party to personal information
            if role:
                speaker_role = SubElement(persName, 'roleName')
                speaker_role.text = role
                # add chairpeople to taxonomy for referral in utterance 'ana'
                if 'uhemies' in role:
                    tag = chairman_tag(role)
                    if role not in all_roles:
                        all_roles.append(role)
                        tax_cat = SubElement(
                            taxonomy, 'category', {'xml:id': tag})
                        catDesc = SubElement(tax_cat, 'catDesc')
                        term = SubElement(catDesc, 'term')
                        term.text = role

            if party:
                s_party = SubElement(person, 'affliation', {
                    'ref': '#party.' + party.replace(' ', '_')})
                if party not in all_parties:
                    all_parties.append(party)
                    org = SubElement(listOrg, 'org', {
                        'xml:id': party.replace(' ', '_')})
                    if row[parl_role_ix]:
                        org.set('role', row[parl_role_ix])
                    else:
                        org.set('role', 'other')

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
            div, 'note', {'xml:id': speech_id, 'type': 'speaker', 'speechType': speech_type.strip(), 'link': link})
        if page:
            note.set('page', page)
        if speech_start:
            note.set('start', speech_start)
        if speech_end:
            note.set('end', speech_end)
        if not lang:
            note.set('xml:lang', '')
            note.set('multilingual', '')
        else:
            tags = lang.split(':')
            note.set('xml:lang', tags[0])
            if len(tags) > 1:
                note.set('multilingual', 'true')
            else:
                note.set('multilingual', 'false')

        if not 'uhemies' in role:
            content = content.replace(':|', ': ')
            speech_parts, num_of_speech_parts = check_interruptions(
                content)

            # no interruptions
            if num_of_speech_parts == 0:
                u = SubElement(
                    div, 'u', {'who': '#{:s}'.format(speaker), 'xml:id': speech_id})
                u.text = content.strip()
            # interruptions
            else:
                speech_part = 1
                for i, part in enumerate(speech_parts):
                    if part.startswith('INTER'):  # interruption part
                        first, last = check_if_interruptor_named(
                            part.replace('INTER', ''), year)
                        if last:
                            if int(year) < 2011:  # first and lastname unknown
                                last = re.sub('Ed\.', '', last)
                                last = re.sub(
                                    "[,&\|'!\]\)\(\+\$\d+]", '', last)

                            first, i_party, i_birth, i_gender = find_interrupter_by_lastname(
                                first.strip(), last.strip(), date, member_info)

                            i_speaker = '{:s}_{:s}'.format(first, last)
                            i_speaker = i_speaker.replace(' ', '_')

                            if first and i_speaker not in all_speakers:
                                all_speakers.append(i_speaker)
                                person = SubElement(listPerson, 'person', {
                                                    'xml:id': i_speaker})
                                persName = SubElement(person, 'persName')
                                surname = SubElement(persName, 'surname')
                                surname.text = last
                                forename = SubElement(persName, 'forename')
                                forename.text = first
                                if i_birth:
                                    born_at = SubElement(
                                        person, 'birth', {'when': i_birth})
                                if i_gender:
                                    if i_gender.lower() == 'male':
                                        speaker_sex = SubElement(
                                            person, 'sex', {'value': 'M'})
                                    else:
                                        speaker_sex = SubElement(
                                            person, 'sex', {'value': 'F'})
                                    speaker_sex.text = i_gender
                                if i_party:
                                    s_party = SubElement(person, 'affliation', {
                                        'ref': '#party.' + i_party.upper().strip('.').replace(' ', '_')})

                        vocal = SubElement(div, 'vocal')
                        if first:
                            vocal.set('who', i_speaker)
                        desc_v = SubElement(
                            vocal, 'desc')
                        desc_v.text = part.replace('INTER', '')
                    else:  # speech part
                        if num_of_speech_parts == 1:
                            # only one speech section and one interruption, no need for extra id digit
                            u = SubElement(
                                div, 'u', {'who': '#{:s}'.format(speaker), 'xml:id': speech_id})
                        else:
                            u = SubElement(
                                div, 'u', {'who': '#{:s}'.format(speaker), 'xml:id': speech_id + '.' + str(speech_part)})
                            if i > 1:  # there's a previous section
                                u.set('prev', speech_id +
                                      '.' + str(speech_part-1))
                            if i < num_of_speech_parts:  # there's a follow-up section
                                u.set('next', speech_id +
                                      '.' + str(speech_part+1))
                            speech_part += 1
                        u.text = part
        else:
            u = SubElement(
                div, 'u', {'who': '#{:s}'.format(speaker), 'xml:id': speech_id, 'ana': '#' + chairman_tag(role)})
            u.text = content

    return root


def main(year):
    speeches = []
    csv.field_size_limit(sys.maxsize)
    with open('speeches_{:s}.csv'.format(year), newline='') as f:
        reader = csv.reader(f)
        speeches = list(reader)

    # read member_info
    with open('parliamentMembers.csv') as f:
        reader = csv.reader(f, delimiter='\t')
        member_info = list(reader)

    root = build_tree(speeches, year, member_info)

    # write to file
    # ORIGINAL:
    pretty_root = minidom.parseString(
        tostring(root).decode('utf-8')).toprettyxml(indent="   ")
    save_to_file = 'Speeches_{:s}.xml'.format(year)
    with open(save_to_file, "w") as file:
        file.write(pretty_root)

    # test_1: PURE ELEMENTTREE:
    #tree = ElementTree(root)
    # with open('test_1.xml', 'w') as file:
    #    tree.write(file, encoding='unicode', xml_declaration=True)

    # test_2: READABLE COMBINATION lxml:
    # temp = tostring(root, encoding="utf-8", method="xml",
    #                 short_empty_elements=True)
    # new_root = etree.fromstring(temp)
    # save_to = 'Speeches_{:s}.xml'.format(year)
    # with open(save_to, 'w') as file:
    #     file.write(etree.tostring(
    #         new_root, encoding='unicode', pretty_print=True))


if __name__ == "__main__":
    main(sys.argv[1])


#from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
#from xml.dom import minidom
