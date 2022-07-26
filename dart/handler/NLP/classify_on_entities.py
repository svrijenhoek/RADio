from collections import defaultdict
import dart.Util


class Classifier:

    def __init__(self, language):
        self.language = language
        if language == 'dutch':
            self.local_code = 'NL'
            self.financial_terms = ['beurs', 'beurzen', 'Wall Street', 'Nikkei', 'Dow Jones', 'Nasdaq', 'aandelen',
                                    'aandelenbeurs', 'aandelenbeurzen', 'kwartaalcijfers', 'omzet', 'fusie', 'AEX',
                                    'AMX']
        elif language == 'english':
            self.local_code = 'EN'
            # to do
            self.financial_terms = ['beurs', 'beurzen', 'Wall Street', 'Nikkei', 'Dow Jones', 'Nasdaq', 'aandelen',
                                    'aandelenbeurs', 'aandelenbeurzen', 'kwartaalcijfers', 'omzet', 'fusie', 'AEX',
                                    'AMX']
        elif language == 'german':
            self.local_code = 'DE'
            # to do
            self.financial_terms = ['beurs', 'beurzen', 'Wall Street', 'Nikkei', 'Dow Jones', 'Nasdaq', 'aandelen',
                                    'aandelenbeurs', 'aandelenbeurzen', 'kwartaalcijfers', 'omzet', 'fusie', 'AEX',
                                    'AMX']
        try:
            self.occupation_mapping = dart.Util.read_csv('data/occupations_mapping.csv')
            self.instance_mapping = dart.Util.read_csv('data/instance_mapping.csv')
        except FileNotFoundError:  # when no mapping files are found
            self.occupation_mapping = {}
            self.instance_mapping = {}

    def map(self, cue, key):
        if key == 'PER' or key == 'PERSON':
            df = self.occupation_mapping
        elif key == 'ORG':
            df = self.instance_mapping
        df1 = df[df.cue == cue]
        try:
            return df1.iloc[0].classification
        except IndexError:
            return 'unknown'

    def find_type(self, entity, key):
        types = defaultdict(int)
        if (key == 'PER' or key == 'PERSON') and 'occupations' in entity:
            for occupation in entity['occupations']:
                occupation_type = self.map(occupation, 'PER')
                types[occupation_type] += 1
        if key == 'ORG' and 'instance' in entity:
            for instance in entity['instance']:
                instance_type = self.map(instance, 'ORG')
                types[instance_type] += 1
        if len(types) > 0:
            if 'politician' in types:
                return 'politics'
            else:
                max_key = max(types.items(), key=lambda a: a[1])[0]
                return max_key
        else:
            return 'unknown'

    def classify_type(self, entities, text):
        types = defaultdict(int)
        persons = [entity for entity in entities if (entity['label'] == 'PER' or entity['label'] == 'PERSON')]
        organisations = [entity for entity in entities if entity['label'] == 'ORG']

        for person in persons:
            person_type = self.find_type(person, 'PER')
            if not person_type == 'unknown':
                types[person_type] += 1
        for organisation in organisations:
            organization_type = self.find_type(organisation, 'ORG')
            if not organization_type == 'unknown':
                types[organization_type] += 1
        for term in self.financial_terms:
            if term in text:
                types['business'] += 1

        if len(types) > 0:
            return max(types.items(), key=lambda a: a[1])[0]
        else:
            return 'unknown'

    def classify_scope(self, entities):
        loc = 0
        glob = 0
        for entity in (entity for entity in entities if (entity['label'] == 'LOC' or entity['label'] == 'GPE')):
            if 'country_code' in entity:
                if entity['country_code'] == self.local_code:
                    loc += 1
                else:
                    glob += 1
        if loc == 0 and glob == 0:
            return 'unknown'
        elif loc >= glob:
            return 'local'
        else:
            return 'global'

    def classify(self, entities, text):
        classification = self.classify_type(entities, text)
        scope = self.classify_scope(entities)
        return classification, scope

