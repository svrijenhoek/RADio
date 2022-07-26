from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch import exceptions
import json

# Class responsible for interacting with the Elasticsearch database. Supports CRUD operations. Might be split up if
# the need arises.


class ElasticsearchConnector:
    def __init__(self):
        self.es = Elasticsearch()

    def execute_search(self, index, body):
        try:
            response = self.es.search(index=index, body=body)
            return response['hits']['hits']
        except exceptions.RequestError:
            # print("Request error")
            # print(body)
            return []

    def execute_multiget(self, index, body):
        try:
            response = self.es.mget(index=index, body=body)
            return response['docs']
        except exceptions.RequestError:
            # print("Request error")
            # print(body)
            return []

    def execute_aggregation(self, index, body, aggregation):
        response = self.es.search(index=index, body=body)
        return response['aggregations'][aggregation]

    def execute_search_with_scroll(self, index, body):
        response = self.es.search(index=index, scroll='2m', body=body)
        return response['_scroll_id'], response['hits']['total'], response

    def scroll(self, sid, scroll):
        return self.es.scroll(scroll_id=sid, scroll=scroll)

    # add document to the specified elastic index
    def add_document(self, index, doc_type, body):
        try:
            self.es.index(index=index, doc_type=doc_type, body=body)
        except exceptions.RequestError as e:
            print(e)
            print(body)

    # add multiple documents at once
    def add_bulk(self, index, bodies):
        actions = []
        for body in bodies:
            dump = json.dumps(body)
            if 'id' in body:
                actions.append({
                        "_id": body['id'],
                        "_index": index,
                        "_source": dump
                })
            else:
                actions.append({
                        "_index": index,
                        "_source": body
                    })

        helpers.bulk(self.es, actions)

    def update_bulk(self, index, bodies):
        actions = [
            {
                "_id": body['id'],
                "_index": index,
                "_type": '_doc',
                "_source": {'doc': body},
                '_op_type': 'update'
            }
            for body in bodies
        ]

        helpers.bulk(self.es, actions)

    # update a small part of the given document
    def update_document(self, index, docid, body):
        try:
            self.es.update(index=index, id=docid, body=body)
        except (exceptions.RequestError, exceptions.TransportError) as e:
            print(e)
            print(body)

    # retrieve the term vector for a given document
    def get_term_vector(self, index, docid):
        return self.es.termvectors(index=index, id=docid, positions=True, term_statistics=True)

    def clear_index(self, index):
        self.es.indices.delete(index=index, ignore=[400, 404])

    def clear_all(self):
        self.clear_index('aggregate_articles')
        self.clear_index('users')
        self.clear_index('recommendations')
        self.clear_index('occupation')
        self.clear_index('personalization')

    def delete(self, index, docid):
        self.es.delete(index, docid)


