from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, FOAF, XSD, SKOS, DCTERMS
import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib import request
import lxml
import json
import datetime
import time
from pprint import pprint


def find_proposal_ids():
    bills = []
    bill_ids = []
    page = 0
    has_more = True

    while has_more:
        parameters = {'perPage': 100, 'page': page,
                      'languageCode': 'fi', 'filter': 'Hallituksen esitys'}

        response = requests.get(
            'https://avoindata.eduskunta.fi/api/v1/vaski/asiakirjatyyppinimi', params=parameters)
        json_data = json.loads(response.content)

        try:
            rows = json_data['rowData']
        except:
            print(json_data)

        for row in rows:
            bill_ids.append(row[0])

        has_more = json_data['hasMore']
        page += 1
        print('len:', len(bill_ids))

    return list(set(bill_ids))


def main():
    # A) use premaid list of ids (quicker, but might not be up-to-date)
    with open('gov_prop_ids.txt', newline='') as f:
        reader = f.readlines()
        ids = list(reader)

    # B) Research ids first:
    #ids = find_proposal_ids()

    g = Graph()
    semparls = Namespace('http://ldf.fi/schema/semparl/')
    g.bind('semparls', semparls)
    g.bind('skos', SKOS)
    g.bind("dct", DCTERMS)

    # with open('output.xml', 'w', newline='') as file:
    for i in ids:
        # retrieve government proposal
        parameters = {'perPage': 100, 'page': 0,
                      'columnName': 'Id', 'columnValue': i.strip('\n')}
        response = requests.get(
            'https://avoindata.eduskunta.fi/api/v1/tables/VaskiData/rows', params=parameters)
        json_data = json.loads(response.content)
        proposal = BeautifulSoup(json_data['rowData'][0][1], "xml")

        # file.write(str(proposal.prettify()))
        # file.write('\nEND**********************************************\n')
        # continue
        try:
            prop_id = proposal.find_all(
                ['met1:EduskuntaTunnus', 'ns:EduskuntaTunnus', 'ns:ViiteTeksti', 'sis1:ViiteTeksti'])
            if not prop_id:
                prop_id = proposal.find_all(['ns:JulkaisuMetatieto', 'vpa:KasittelytiedotValtiopaivaasia', 'he:HallituksenEsitys'])[0][
                    'met1:eduskuntaTunnus']
            else:
                prop_id = prop_id[0].string.strip()

            name = proposal.find_all(['met1:NimekeTeksti', 'ns:NimekeTeksti'])
            title = name[0].string.replace('\n', ' ')
            title = title.strip()

            if 'POISTETTU' in title:
                continue

            uri = URIRef(
                'http://ldf.fi/semparl/documents/{}'.format(re.sub(' |/', '_', prop_id)))
            g.add((uri, RDF.type, semparls.GovernmentProposal))
            g.add((uri, DCTERMS.title, Literal(
                title, lang='fi')))

            if proposal.find('vsk1:LakiehdotusPaatosNimi'):
                decision = proposal.find('vsk1:LakiehdotusPaatosNimi').string
                g.add((uri, semparls.decision, Literal(decision, lang='fi')))
            if proposal.find('vsk1:VahvistusPvmTeksti'):
                decided = proposal.find('vsk1:VahvistusPvmTeksti').string
                decided_on = datetime.datetime.strptime(
                    decided, '%d.%m.%Y').strftime('%Y-%m-%d')
                g.add((uri, semparls.dateDecided, Literal(
                    decided_on, datatype=XSD.date)))

            if proposal.find_all(['ns:AiheTeksti', 'met1:AiheTeksti']):
                keywords = proposal.find_all(
                    ['ns:AiheTeksti', 'met1:AiheTeksti'])
                for word in keywords:
                    g.add((uri, DCTERMS.subject, Literal(word.string, lang='fi')))
        except:
            print(i, prop_id)

    g.serialize(destination='government_proposals.ttl', format='turtle')


if __name__ == "__main__":
    main()
