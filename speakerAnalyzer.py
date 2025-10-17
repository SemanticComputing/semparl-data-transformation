'''
Created on 21 Sep 2021, modified 6 March 2023
@author: ptleskin
'''
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
import rdflib as rdflib
from rdflib.namespace import XSD, Namespace
import re
from SPARQLWrapper import SPARQLWrapper, JSON, POST

class SpeakerAnalyzer:
    """Example of usage:

    from speakerAnalyzer import *

    sp = SpeakerAnalyzer()

    res = sp.find('2020-05-05', 'p1323')
    print(res)
    # {'party': 'http://ldf.fi/semparl/groups/Q304191', 'type': 'Oppositiopuolue', 'party_label': 'Kansallinen Kokoomus'}

    Common output cases:

    2020-10-02 p1405
        {'party': 'http://ldf.fi/semparl/groups/Q196695', 'type': 'Hallituspuolue', 'party_label': 'Vihreä liitto'}
    1979-11-27 p215
        {'party': 'http://ldf.fi/semparl/groups/Q304191', 'type': 'Oppositiopuolue', 'party_label': 'Kansallinen Kokoomus'}
    1951-01-17 p910708
        {'party': 'http://ldf.fi/semparl/groups/Q506591', 'type': 'Hallituspuolue', 'party_label': 'Suomen Keskusta (Maalaisliitto -1965)'}
    1922-06-30 p911715
        {'party': 'http://ldf.fi/semparl/groups/Q845537', 'type': 'Virkamieshallitus', 'party_label': 'Suomen ruotsalainen kansanpuolue'}
    1951-01-17 p910708
        {'party': 'http://ldf.fi/semparl/groups/Q506591', 'type': 'Hallituspuolue', 'party_label': 'Suomen Keskusta (Maalaisliitto -1965)'}
    1930-01-01 Q11856432
        {'type': 'ammatti/virkamies'}

    Error cases:
    2021-11-27 p1234xyz
        {'error': 'Tuntematon henkilö'}
    2010-01-01 Q11856432
        {'error': 'Henkilöltä ei löydy jäsenyyttä valittuun aikaan'}
    1908-11-27 p911490
        {'party': 'http://ldf.fi/semparl/groups/Q1713433', 'error': 'Ei hallitusta tänä aikana', 'party_label': 'Nuorsuomalainen Puolue (1894-1918)'}
    """

    def __init__(self):
        """Init the module by querying the sparql endpoint."""
        self.party_data = self.queryPartyInfo(query = self.PREFIXES + self.PARTY_QUERY)
        self.government_data = self.queryGovernmentInfo(query=self.PREFIXES+self.GOVERNMENT_QUERY)

        self.membership_data = {
            **self.queryMemberships(query=self.PREFIXES+self.MEMBERSHIP_QUERY), 
            **self.queryMemberships(query=self.PREFIXES+self.MINISTRY_QUERY),
            **self.queryMemberships(query=self.PREFIXES+self.COUNCELLOR_QUERY)}
    

    def simplify_label(self, st):
        return re.sub(r'^.+[/]([^/]+)$', r'\1', st)
    
    DATATYPECONVERTERS = {
            str(XSD.integer):  int,
            str(XSD.decimal):  float,
            str(XSD.date):     lambda v: datetime.strptime(v, '%Y-%m-%d').date(),
            str(XSD.dateTime): lambda v: datetime.strptime(v, '%Y-%m-%dT%H:%M:%S').date()
        }

    PEOPLE = Namespace('http://ldf.fi/semparl/people/')
    CARETAKER_GOVERNMENT = "Virkamieshallitus"
    GOVERNMENTAL_PARTY = "Hallituspuolue"
    OPPOSITION_PARTY = "Oppositiopuolue"

    def queryPartyInfo(self, query):
        sparql = SPARQLWrapper("https://ldf.fi/semparl-dev/sparql")
        sparql.setQuery(query)
            
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        res = self.convertDatatypes(results)

        party_data = defaultdict(str)
        for ob in res:
            party, label = ob.get('id'), ob.get('label')
            if party and label:
                party_data[party] = label
    
        return party_data

    
    def queryGovernmentInfo(self, query):
        sparql = SPARQLWrapper("https://ldf.fi/semparl-dev/sparql")
        sparql.setQuery(query)
            
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        res = self.convertDatatypes(results)

        government_data = defaultdict(dict)

        for ob in res:
            url = ob.get('id')
            
            v = ob.get('label')
            if v:
                government_data[url]['label'] = v
            
            v = ob.get('start')
            if v:
                government_data[url]['start'] = v

            v = ob.get('end') or datetime.now().date()
            government_data[url]['end'] = v

            party = ob.get('party')
            if party:
                if not 'parties' in government_data[url]:
                    government_data[url]['parties'] = defaultdict(dict)
                government_data[url]['parties'][party] = self.party_data.get(party)
        
        return government_data 

    @lru_cache(maxsize=256, typed=False)
    def find(self, date, member):
        """Find the status of a parliament member at a specified date."""
        if type(date) is str:
            # format e.g., '1974-05-27'
            _date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            _date = date


        st = self.simplify_label(member)
        arr = self.membership_data.get(st)
        if arr:
            for ob in arr:
                if ob.get('start')<=_date and _date<= ob.get('end'):
                    party = ob.get('party')
                    comment = ob.get('comment')

                    if (party is None) and comment:
                        return dict(type=comment)

                    res = dict(party=party)

                    url, ob = self.findGovernment(_date)
                    parties = ob.get('parties', [])
                    
                    if url is None:
                        res['error'] = 'Ei hallitusta tänä aikana'
                    elif len(parties)==0:
                        res['type'] = self.CARETAKER_GOVERNMENT
                    elif party in parties:
                        res['type'] = self.GOVERNMENTAL_PARTY
                    else: 
                        res['type'] = self.OPPOSITION_PARTY
                    
                    if self.party_data.get(party):
                        res['party_label'] = self.party_data.get(party)
                    
                    return res
            
            return dict(error='Henkilöltä ei löydy jäsenyyttä valittuun aikaan')
        else:
            return dict(error='Tuntematon henkilö')
    
    @lru_cache(maxsize=256, typed=False)
    def findGovernment(self, date):
        res = [(url, ob) for url, ob in self.government_data.items() if ob.get('start')<=date and date<=ob.get('end')]
        return res[0] if len(res) else (None, dict(label='no government'))
    
    def queryMemberships(self, query):
        sparql = SPARQLWrapper("https://ldf.fi/semparl-dev/sparql")
        sparql.setQuery(query)
            
        sparql.setReturnFormat(JSON)

        results = sparql.query().convert()
        res = self.convertDatatypes(results)

        membership_data = defaultdict(list)

        for ob in res:
            url = self.simplify_label(ob.get('id'))
            ob['end'] = ob.get('end') or datetime.now().date()
            membership_data[url].append(ob)

        return membership_data
    
    def convertDatatype(self, obj):
        return self.DATATYPECONVERTERS.get(obj.get('datatype'), str)(obj.get('value')) 

    def convertDatatypes(self, results):
        res = results["results"]["bindings"]
        return [dict([(k, self.convertDatatype(v)) for k,v in r.items()]) for r in res]
    
    PREFIXES = """
        PREFIX bioc: <http://ldf.fi/schema/bioc/>
        PREFIX committees: <http://ldf.fi/semparl/groups/committees/>
        PREFIX crm: <http://erlangen-crm.org/current/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX districts: <http://ldf.fi/semparl/groups/districts/>
        PREFIX event: <http://ldf.fi/semparl/events/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX groups: <http://ldf.fi/semparl/groups/>
        PREFIX label: <http://ldf.fi/semparl/label/>
        PREFIX occupations: <http://ldf.fi/semparl/occupations/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX people: <http://ldf.fi/semparl/people/>
        PREFIX places: <http://ldf.fi/semparl/places/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX roles: <http://ldf.fi/semparl/roles/>
        PREFIX schema: <http://schema.org/>
        PREFIX semparl: <http://ldf.fi/schema/semparl/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX times: <http://ldf.fi/semparl/times/>
        PREFIX titles: <http://ldf.fi/semparl/titles/>
        PREFIX xml: <http://www.w3.org/XML/1998/namespace>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> """

    MEMBERSHIP_QUERY = """
        SELECT DISTINCT ?id ?label ?party ?start ?end
        WHERE {
            # VALUES ?id { people:p911397 }
            ?id a bioc:Person ;
            skos:prefLabel ?label ;
            bioc:bearer_of/crm:P11i_participated_in ?evt .
            ?evt a semparl:ParliamentaryGroupMembership ;
            semparl:organization/a/semparl:party ?party ;
            crm:P4_has_time-span ?tspan .
            
            OPTIONAL { ?tspan crm:P82b_end_of_the_end ?end }

            OPTIONAL { ?tspan crm:P81a_begin_of_the_begin ?_start }
            OPTIONAL { ?id semparl:representative_period/crm:P81a_begin_of_the_begin ?_start2 . FILTER (?_start2<?end)}
            BIND(COALESCE(?_start, ?_start2) AS ?start) 
        } """

    PARTY_QUERY = """
        SELECT DISTINCT * WHERE {
        ?id  a semparl:Party ;
            skos:prefLabel ?label .
        FILTER(LANG(?label)='fi')
        } ORDER BY ?label """

    GOVERNMENT_QUERY = """
        SELECT DISTINCT * WHERE {
            ?id  a semparl:Government ;
            skos:prefLabel ?label ;
            crm:P4_has_time-span ?tspan .
            FILTER(LANG(?label)='fi')
            
            ?tspan crm:P81a_begin_of_the_begin ?start .
            OPTIONAL { ?tspan crm:P82b_end_of_the_end ?end }

            OPTIONAL { ?id semparl:party ?party .
            ?party skos:prefLabel ?party_label .
            FILTER(LANG(?party_label)='fi')
            }
        } ORDER BY ?start """

    MINISTRY_QUERY = """
        SELECT DISTINCT ?id ?label ?party ?start ?end ?comment
        WHERE {
            
            ?id a bioc:Person ;
            skos:prefLabel ?label ;
            bioc:bearer_of/crm:P11i_participated_in ?evt .
            ?evt a semparl:GovernmentMembership ; 
                # semparl:ParliamentaryGroupMembership ;
            crm:P4_has_time-span ?tspan .
            
            OPTIONAL { ?evt semparl:party ?party }
            OPTIONAL { ?evt semparl:comment ?comment }
            FILTER (BOUND(?party) || BOUND(?comment))
            
            ?tspan crm:P81a_begin_of_the_begin ?start .
            OPTIONAL {
            ?tspan crm:P82b_end_of_the_end ?end .
            } 
        } """

    COUNCELLOR_QUERY = """
        SELECT DISTINCT ?id ?label ?party ?start ?end ("ammatti/virkamies"@fi AS ?comment)
        WHERE {
            
            ?id a bioc:Person ;
            skos:prefLabel ?label ;
            bioc:bearer_of/crm:P11i_participated_in ?evt .
            ?evt a semparl:Chancellorship ;
            crm:P4_has_time-span ?tspan .
            
            ?tspan crm:P81a_begin_of_the_begin ?start .
            OPTIONAL {
            ?tspan crm:P82b_end_of_the_end ?end .
            }
        } """
