import requests
import json
import pandas as pd


class WikidataHandler:
    """ Class that constructs Wikidata queries, executes them and reads responses """

    def __init__(self, language, country):
        self.url = 'https://query.wikidata.org/sparql'
        if language == 'dutch':
            self.language_tag = 'nl'
            self.parliament_indicator = 'Q18887908 ; pq:P580 ?start .'
        elif language == 'english':
            self.language_tag = 'en'
            if country == 'united states':
                self.parliament_indicator = 'Q13218630; pq:P580 ?start .'
            elif country == 'united kingdom':
                self.parliament_indicator = 'Q16707842 ; pq:P580 ?start .'
        elif language == 'german':
            self.language_tag = 'de'
            # this one is not functioning yet
            self.parliament_indicator = 'Q154797'
        elif language == 'french':
            self.language_tag = 'fr'
            if country == 'canada':
                self.parliament_indicator = 'Q15964890 ; pq:P2937 wd:Q108651352.'
            elif country == 'france':
                self.parliament_indicator = 'Q3044918 ; pq:P2937 wd:Q24939798 .'
        elif language == 'danish':
            self.language_tag = 'dk'
            self.parliament_indicator = 'Q12311817 ; pq:P2937 wd:Q114902058 .'
        elif language == 'portuguese':
            self.language_tag == 'pt'
            if country == 'brazil':
                self.parliament_indicator = 'Q20058725 ; pq:P2937 wd:Q18479094 .'
            elif country == 'portugal':
                self.parliament_indicator = 'Q19953703 ; pq:P580 ?start .'

    def execute_query(self, query):
        """
        Sends a SPARQL query to Wikidata.
        TO DO: Write tests
        """
        try:
            r = requests.get(self.url, params={'format': 'json', 'query': query})
            return r
        except (ConnectionAbortedError, ConnectionError):
            return ConnectionError

    @staticmethod
    def read_response(data, label):
        """
        Returns all unique values for a particular label.
        Lowercases occupation data, which is relevant when returning results in English
        """
        output = []
        for x in data['results']['bindings']:
            if label in x:
                if label == 'occupations':
                    output.append(x[label]['value'].lower())
                else:
                    output.append(x[label]['value'])
        return list(set(output))

    def read_person_response_list(self, response):
        """
        Attempt to retrieve values for each of the value types relevant for people data.
        Leaves value empty in case Wikidata has no information about it.
        """
        try:
            data = response.json()

            givenname = self.read_response(data, 'givenname')
            familyname = self.read_response(data, 'familyname')
            occupations = self.read_response(data, 'occupations')
            party = self.read_response(data, 'party')
            positions = self.read_response(data, 'position')
            gender = self.read_response(data, 'gender')
            citizen = self.read_response(data, 'citizen')
            ethnicity = self.read_response(data, 'ethnicity')
            place_of_birth = self.read_response(data, 'place_of_birth')
            sexuality = self.read_response(data, 'sexuality')

            return {'givenname': givenname, 'familyname': familyname, 'gender': gender, 'occupations': occupations,
                    'party': party, 'positions': positions, 'citizen': citizen, 'ethnicity': ethnicity,
                    'sexuality': sexuality, 'place_of_birth': place_of_birth}
        except json.decoder.JSONDecodeError:
            return []
        except IndexError:
            return []

    def read_company_response_list(self, response):
        try:
            data = response.json()
            industry = self.read_response(data, 'industryLabel')
            instance = self.read_response(data, 'instanceLabel')
            country = self.read_response(data, 'countryLabel')
            return {'industry': industry, 'instance': instance, 'country': country}
        except json.decoder.JSONDecodeError:
            return []

    def get_person_data(self, label, alternatives):
        response = self.person_data_query(label)
        if response and (response['givenname'] or response['gender'] or response['citizen']):
            return label, response
        else:
            for alternative in alternatives:
                response = self.person_data_query(alternative)
                if response and (response['givenname'] or response['gender'] or response['citizen']):
                    return alternative, response
        return label, {}

    def person_data_query(self, label):
        try:
            query = """
                SELECT DISTINCT ?s ?givenname ?familyname ?occupations ?party ?position ?gender ?citizen ?ethnicity ?place_of_birth ?sexuality WHERE { 
                ?s ?label '""" + label + """'@"""+self.language_tag+""" .
              OPTIONAL {
                ?s wdt:P735 ?a . 
                ?a rdfs:label ?givenname .
                FILTER(LANG(?givenname) = "" || LANGMATCHES(LANG(?givenname), \""""+self.language_tag+"""\"))
              }
              OPTIONAL {
                ?s wdt:P734 ?b . 
                ?b rdfs:label ?familyname .
                FILTER(LANG(?familyname) = "" || LANGMATCHES(LANG(?familyname), \""""+self.language_tag+"""\"))
              }
              OPTIONAL {
                ?s wdt:P106 ?c .
                ?c rdfs:label ?occupations .
                FILTER(LANG(?occupations) = "" || LANGMATCHES(LANG(?occupations), "en"))
              }
              OPTIONAL {
                ?s wdt:P102 ?d .
                ?d rdfs:label ?party .
                FILTER(LANG(?party) = "" || LANGMATCHES(LANG(?party), \""""+self.language_tag+"""\"))
              }
              OPTIONAL {
                ?s wdt:P39 ?e .
                ?e rdfs:label ?position .
                FILTER(LANG(?position) = "" || LANGMATCHES(LANG(?position), "en"))
              }
              OPTIONAL {
                ?s wdt:P21 ?f .
                ?f rdfs:label ?gender .
                FILTER(LANG(?gender) = "" || LANGMATCHES(LANG(?gender), "en"))
              }
              OPTIONAL {
                   ?s wdt:P172 ?g . 
                   ?g rdfs:label ?ethnicity .
                   FILTER(LANG(?ethnicity) = "" || LANGMATCHES(LANG(?ethnicity), "en"))
                }
               OPTIONAL {
                   ?s wdt:P19 ?pb . 
                   ?pb wdt:P17 ?country .
                   ?country rdfs:label ?place_of_birth .
                   FILTER(LANG(?place_of_birth) = "" || LANGMATCHES(LANG(?place_of_birth), "en"))
                }
              OPTIONAL {
                ?s wdt:P27 ?h .
                ?h rdfs:label ?citizen
                FILTER(LANG(?citizen) = "" || LANGMATCHES(LANG(?citizen), "en"))
                }
               OPTIONAL {
                ?s wdt:P91 ?i .
                ?i rdfs:label ?sexuality
                FILTER(LANG(?sexuality) = "" || LANGMATCHES(LANG(?sexuality), "en"))
                }
            }"""
            r = self.execute_query(query)
            return self.read_person_response_list(r)
        except (ConnectionAbortedError, requests.exceptions.ChunkedEncodingError):  # in case the connection fails
            return []

    def get_company_data(self, label):
        try:
            query = """
            SELECT DISTINCT ?instanceLabel ?industryLabel ?countryLabel WHERE { 
                ?s rdfs:label '""" + label + """'@"""+self.language_tag+""" .
                ?s wdt:P571 ?inception .
                OPTIONAL {?s wdt:P31 ?instance . }
                OPTIONAL {?s wdt:P452 ?industry . }
                OPTIONAL {?s wdt:P17 ?country }
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }            
            """
            r = self.execute_query(query)
            return self.read_company_response_list(r)
        except ConnectionAbortedError:
            return []

    def get_politicians(self):
        try:
            query = """
                SELECT ?itemLabel ?groupLabel
                  WHERE { 
                    ?item p:P39 ?ps . 
                    ?ps ps:P39/wdt:P279* wd:"""+self.parliament_indicator+"""
                    OPTIONAL { ?ps pq:P580 ?start }
                    OPTIONAL { ?ps pq:P582 ?end }
                    OPTIONAL { ?ps pq:P4100 ?group }
                    FILTER(!BOUND(?end))
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                    }
            """
            r = self.execute_query(query)
            data = r.json()

            output = []
            for x in data['results']['bindings']:
                row = {}
                for label in x:
                    row[label] = x[label]['value']
                output.append(row)

            df = pd.DataFrame(output)
            df = df.rename(columns={'itemLabel': 'name', 'groupLabel': 'group', 'districtLabel': 'district'})
            return df
        except ConnectionAbortedError:
            return pd.DataFrame()
