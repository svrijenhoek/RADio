import pandas as pd

import dart.handler.NLP.annotator
import dart.handler.other.textstat
import dart.handler.NLP.enrich_entities
import dart.handler.NLP.cluster_entities
import dart.handler.other.wikidata
import dart.handler.NLP.sentiment
import dart.Util
from dart.models.Article import Article

import sys


class Enricher:

    def __init__(self, config):
        self.config = config
        self.metrics = config['metrics']
        self.language = config['language']
        self.annotator = dart.handler.NLP.annotator.Annotator(self.language)
        self.enricher = dart.handler.NLP.enrich_entities.EntityEnricher(self.metrics, self.language,
                                                                        pd.read_csv('metadata\\term-116.csv'))
        self.clusterer = dart.handler.NLP.cluster_entities.Clustering(0.9, 'a', 'b', 'metric')

    def annotate_entities(self, entities):
        annotated_entities = []
        for entity in (entity for entity in entities if 'annotated' not in entity or entity['annotated'] == 'N'):
            entity = self.enricher.enrich(entity)
            annotated_entities.append(entity)
        return annotated_entities

    def enrich_document(self, entities):
        aggregated_entities = self.clusterer.execute(entities)
        enriched_entities = self.annotate_entities(aggregated_entities)
        return enriched_entities

    def enrich(self, df):
        df['entities_base'] = df['entities']
        if 'enriched_entities' not in df:
            df["enriched_entities"] = None

        to_process = df[df.enriched_entities.isnull()]
        count = 1
        split = 1000
        length = len(to_process)
        for index, row in to_process.iterrows():
            enriched_entities = self.enrich_document(row['entities'])
            df.at[index, 'enriched_entities'] = enriched_entities

            if count % length/split == 0:
                print("\t{}%".format(count/length*100))
                self.enricher.save()
                df.to_json("data/annotated.json")
            count += 1
        return df



