import pandas as pd

import dart.handler.NLP.annotator
import dart.handler.other.textstat
import dart.handler.NLP.enrich_entities
import dart.handler.NLP.cluster_entities
import dart.handler.other.openstreetmap
import dart.handler.other.wikidata
import dart.handler.NLP.classify_on_entities
import dart.handler.NLP.sentiment
import dart.Util

import sys


class Enricher:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.metrics = config['metrics']
        self.language = config['language']
        self.annotator = dart.handler.NLP.annotator.Annotator(self.language)
        self.textstat = dart.handler.other.textstat.TextStatHandler(self.language)
        self.enricher = dart.handler.NLP.enrich_entities.EntityEnricher(self.metrics, self.language,
                                                                        pd.read_csv(config['politics_file']),
                                                                                    self.handlers)
        self.classifier = dart.handler.NLP.classify_on_entities.Classifier(self.language)
        self.clusterer = dart.handler.NLP.cluster_entities.Clustering(0.9, 'a', 'b', 'metric')
        self.sentiment = dart.handler.NLP.sentiment.Sentiment(self.language)

    def annotate_entities(self, entities):
        annotated_entities = []
        for entity in (entity for entity in entities if 'annotated' not in entity or entity['annotated'] == 'N'):
            entity = self.enricher.enrich(entity)
            annotated_entities.append(entity)
        return annotated_entities

    def annotate_document(self, article):
        doc = {'id': article.id}
        if not article.entities:
            _, entities, tags = self.annotator.annotate(article.text)
        else:
            entities = article.entities
        aggregated_entities = self.clusterer.execute(entities)

        enriched_entities = self.annotate_entities(aggregated_entities)

        doc['entities'] = enriched_entities
        doc['entities_base'] = entities
        doc['sentiment'] = self.sentiment.get_sentiment_score(article.text)

        doc['complexity'] = self.textstat.flesch_kincaid_score(article.text)

        if 'classify' in self.metrics:
            if 'entities' not in doc:
                classification = 'unknown'
            else:
                classification, scope = self.classifier.classify(doc['entities'], article.text)
            doc['classification'] = classification
            doc['scope'] = scope

        doc['annotated'] = 'Y'
        self.handlers.articles.update_doc(article.id, doc)

    def enrich(self):
        try:
            articles = self.handlers.articles.get_not_calculated("annotated")
            while len(articles) > 0:
                for article in articles:
                    self.annotate_document(article)
                articles = self.handlers.articles.get_not_calculated("annotated")
        except ConnectionError:  # in case an error occurs when wikidata does not respond, save recently retrieved items
            print("Connection error!")
            sys.exit()



