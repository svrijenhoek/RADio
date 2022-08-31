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
        df['entities'] = df['entities'].apply(lambda x: self.enrich_document(x))

        # a = list(df.to_dict(orient='index').items())
        # articles = [Article(i) for i in a]
        # for article in articles:
        #     self.annotate_document(article)

        # try:
        #     articles = self.handlers.articles.get_not_calculated("annotated")
        #     while len(articles) > 0:
        #         for article in articles:
        #             self.annotate_document(article)
        #         articles = self.handlers.articles.get_not_calculated("annotated")
        # except ConnectionError:  # in case an error occurs when wikidata does not respond, save recently retrieved items
        #     print("Connection error!")
        #     sys.exit()



