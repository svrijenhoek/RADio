import dart.Util
import dart.handler.other.wikidata
import dart.handler.other.openstreetmap
import string
import pandas as pd
from collections import defaultdict


class EntityEnricher:

    def __init__(self, metrics, language, politics, handlers):
        self.handlers = handlers
        self.metrics = metrics
        self.language = language
        self.openstreetmap = dart.handler.other.openstreetmap.OpenStreetMap()
        self.wikidata = dart.handler.other.wikidata.WikidataHandler(self.language)
        self.printable = set(string.printable)
        self.political_data = pd.DataFrame(politics)
        self.unknown_persons = defaultdict(int)

    def known(self, name, alternative, entity_type):
        entity = {}
        # situation 1: name is directly known
        if self.handlers.entities.find_entity(entity_type, name):
            entity = self.handlers.entities.find_entity(entity_type, name)
        elif self.handlers.entities.find_alternative_name(entity_type, name):
            entity = self.handlers.entities.find_alternative_name(entity_type, name)
        else:
            for alt in alternative:
                if not (entity_type == 'persons' and (name.startswith(alt) and " " not in alt)):
                    if self.handlers.entities.find_entity(entity_type, alt):
                        entity = self.handlers.entities.find_entity(entity_type, alt)
        if entity:
            known_alternatives = entity['alternative']
            new_set = list(set(alternative + known_alternatives))
            if new_set != known_alternatives:
                entity['alternative'] = new_set
                self.handlers.entities.update_entity(entity_type, entity)
            return entity
        return

    def enrich(self, entity):
        if entity['label'] == 'PER' or entity['label'] == 'PERSON':
            if 'occupation' not in entity:
                entity = self.retrieve_person_data(entity)
            # if 'ethnicity' in self.metrics and 'ethnicity' not in entity:
            #     entity = self.retrieve_ethnicity(entity)
        if entity['label'] == 'LOC' or entity['label'] == 'GPE':
            if 'country_code' not in entity:
                entity = self.retrieve_geolocation(entity)
        if entity['label'] == 'ORG':
            if 'type' not in entity:
                entity = self.retrieve_company_data(entity)
        entity['annotated'] = 'Y'
        if '_id' in entity:
            entity['_id'] = str(entity['_id'])
        return entity

    def retrieve_person_data(self, entity):
        """
        Function that first aims to see if the entity is already known. If not, it retrieves data from Wikipedia.
        """
        name = entity['text']
        # see if the entity is already known
        known_entry = self.known(name, entity['alternative'], 'persons')
        # if it is unknown, or we don't gave any additional data about it, try to find it again
        # reasoning here is that we may have encountered another way of spelling the entity's name that would be found
        if not known_entry or 'givenname' not in known_entry or known_entry['givenname'] == []:
            # if the entity is already known, but we just don't have additional data about it, try if we can find
            # information with a different way of spelling
            if known_entry:
                found, data = self.wikidata.get_person_data(name, known_entry['alternative'])
                alternative = list(set(known_entry['alternative'] + entity['alternative']))
                # if a new way of spelling is found, delete the old entry
                if found != name and self.known(name, [], 'persons'):
                    self.handlers.entities.delete_with_label('persons', name)
            # if this is an entirely new entry
            else:
                found, data = self.wikidata.get_person_data(name, entity['alternative'])
                alternative = entity['alternative']
                if 'occupations' in data and 'politician' in data['occupations']:
                    data = self.resolve_politicians(found, data)
            # update the list with the information that was found
            try:
                if data:
                    data['key'] = name
                    data['alternative'] = alternative
                    entity['alternative'] = alternative
                    entity['key'] = found
                    for k, v in data.items():
                        entity[k] = v
                    self.handlers.entities.insert_one('persons', data)
                else:
                    self.unknown_persons[name] += 1
            except AttributeError as e:
                print(e)
                print(data)
            except KeyError:
                print(name)
                print(known_entry)
                print(found)
        else:
            for k, v in known_entry.items():
                entity[k] = v
        return entity

    def resolve_politicians(self, name, data):
        df = self.political_data
        try:
            row = df.loc[df['name'] == name]
            if not row.empty:
                data['current_party'] = row.iloc[0].group
        except KeyError:
            pass
        return data

    def retrieve_geolocation(self, entity):
        name = entity['text']
        place = ''.join(filter(lambda x: x in self.printable, name))
        place = place.replace('\n', '').replace('\r', '')
        if len(place) > 2 and '|' not in place and place.lower() != 'None'.lower():
            known_entry = self.known(name, entity['alternative'], 'locations')
            if known_entry:
                location = known_entry
                entity['location'] = {
                    'lat': location['lat'],
                    'lon': location['lon']
                }
                entity['country_code'] = location['country_code']
            else:
                try:
                    # retrieve the coordinates from OpenStreetMap
                    try:
                        lat, lon, country_code = self.openstreetmap.get_coordinates(place)
                        if not lat == 0 or not lon == 0 or not country_code == 0:
                            # self.known_locations[place] = {'country_code': country_code, 'lat': lat, 'lon': lon,
                            #                               'alternative': entity['alternative']}
                            entity['location'] = {
                                'lat': lat,
                                'lon': lon
                            }
                            entity['country_code'] = country_code
                            self.handlers.entities.insert_one('locations', {
                                'key': name,
                                'country_code': country_code,
                                'lat': lat, 'lon': lon,
                                'alternative': entity['alternative']
                            })
                        else:
                            entity['calculated'] = 'Y'
                    except TypeError:
                        pass
                except IndexError:
                    entity['calculated'] = 'Y'
        return entity

    def retrieve_company_data(self, entity):
        name = entity['text']
        known_entry = self.known(name, entity['alternative'], 'organizations')
        if known_entry:
            entity['industry'] = known_entry['industry']
            entity['instance'] = known_entry['instance']
            entity['country'] = known_entry['country']
            return entity
        else:
            # for now we see if we can work with only the first result
            # problem with this approach: if one field is not filled, they all fail!!
            response = self.wikidata.get_company_data(name)
            try:
                industry = response['industry']
                instance = response['instance']
                country = response['country']

                # self.known_organizations[name] = {'industry': industry, 'instance': instance, 'country':
                # country, 'alternative': entity['alternative']}
                entity['industry'] = industry
                entity['instance'] = instance
                entity['country'] = country
                self.handlers.entities.insert_one('organizations', {
                    'key': name,
                    'industry': industry,
                    'instance': instance,
                    'country': country,
                    'alternative': entity['alternative']})
            except TypeError:
                pass
        return entity
