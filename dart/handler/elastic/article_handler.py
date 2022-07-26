from dart.handler.elastic.base_handler import BaseHandler
from dart.models.Article import Article

from datetime import datetime


class ArticleHandler(BaseHandler):
    """
    Data handler for all articles. Returns lists of Articles, and adds documents to Elasticsearch.
    Standard queries for:
    - random document
    - all documents (with scroll, should be managed from calculation classes
    - documents where certain fields are still empty
    ....
    """

    def __init__(self, connector):
        super(ArticleHandler, self).__init__(connector)
        self.connector = connector

    def add_document(self, doc):
        self.connector.add_document('articles', '_doc', doc)

    def add_bulk(self, queue):
        self.connector.add_bulk('articles', queue)

    def update(self, docid, field, value):
        body = {
            "doc": {field: value}
        }
        self.connector.update_document('articles', docid, body)

    def update_bulk(self, docs):
        self.connector.update_bulk('articles', docs)

    def update_doc(self, docid, doc):
        body = {
            "doc": doc
        }
        self.connector.update_document('articles', docid, body)

    def get_all_articles(self):
        articles = super(ArticleHandler, self).get_all_documents('articles')
        return [Article(i) for i in articles]

    def get_all_articles_in_dict(self):
        articles = super(ArticleHandler, self).get_all_documents('articles')
        return {Article(i).id: Article(i) for i in articles}

    def add_field(self, docid, field, value):
        body = {
            "doc": {field: value}}
        self.connector.update_document('articles', '_doc', docid, body)

    def get_not_calculated(self, field):
        """
        returns the articles that have a certain field not populated. This is used for example when calculating the
        popularity of articles.
        """
        body = {
            "size": 300,
            "query": {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": field
                            }
                    }
                }
            }
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_most_popular(self, size):
        """
        returns all articles that have been shared on Facebook most often
        """
        body = {
            "size": size,
            "sort": [
                {"popularity": {"order": "desc", "mode": "max", "unmapped_type": "long"}}
            ],
            "query": {
                "match_all": {},
            }}
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_random_article(self):
        """
        Returns a random article
        """
        return Article(super(ArticleHandler, self).get_random('articles'))

    def get_similar_documents(self, docid, size):
        """
        given a document id, retrieve the documents that are most similar to it according to Elastic's
        More Like This functionality.
        """
        body = {
            'size': size,
            'query': {"more_like_this": {
                "fields": ['text'],
                "like": [
                    {
                        "_index": 'articles',
                        "_id": docid,
                    },
                ],
            }}
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_all_in_timerange(self, l, u):
        lower = l.strftime('%Y-%m-%dT%H:%M:%S')
        upper = u.strftime('%Y-%m-%dT%H:%M:%S')
        docs = []
        body = {
            'query': {"range": {
                "publication_date": {
                    "lt": upper,
                    "gte": lower
                }
            }},
            "sort": [
                {"popularity": {"order": "desc", "mode": "max", "unmapped_type": "long"}}
            ]
        }
        sid, scroll_size, result = self.connector.execute_search_with_scroll('articles', body)
        for hit in result['hits']['hits']:
            docs.append(hit)
        # Start retrieving documents
        while len(result['hits']['hits']):
            result = self.connector.scroll(sid, '2m')
            sid = result['_scroll_id']
            for hit in result['hits']['hits']:
                docs.append(hit)
        return [Article(i) for i in docs]

    def get_articles_before(self, d):
        date = datetime.strptime(d, '%d-%m-%Y')
        full_date = date.strftime('%Y-%m-%dT%H:%M:%S')
        docs = []
        body = {
            'query': {"range": {
                "publication_date": {
                    "lt": full_date,
                }
            }}
        }
        sid, scroll_size, result = self.connector.execute_search_with_scroll('articles', body)
        for hit in result['hits']['hits']:
            docs.append(hit)
        # Start retrieving documents
        while len(result['hits']['hits']):
            result = self.connector.scroll(sid, '2m')
            sid = result['_scroll_id']
            for hit in result['hits']['hits']:
                docs.append(hit)
        return [Article(i) for i in docs]

    # get elastic entry by id
    def get_by_id(self, docid):
        return Article(super(ArticleHandler, self).get_by_docid('articles', docid))

    def get_multiple_by_id(self, docids):
        docs = super(ArticleHandler, self).get_multiple_by_docid('articles', docids)
        return [Article(doc) for doc in docs if doc['found']]

    def get_multiple_by_newsid(self, docids):
        articles = []
        error = 0
        for newsid in docids:
            try:
                article = self.get_field_with_value('newsid', newsid)[0]
                articles.append(article)
            except IndexError:
                error += 1
        return articles

    def get_by_url(self, index, url):
        body = {
            "query": {
                "match": {
                    "url": url
                }
            }
        }
        output = self.connector.execute_search(index, body)
        return Article(output[0])

    def get_field_with_value(self, field, value):
        body = {
            "size": 10000,
            "query": {
                "match": {
                    field: value
                }
             }
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_political(self, user, upper, lower):
        upper = upper.strftime('%Y-%m-%dT%H:%M:%S')
        lower = lower.strftime('%Y-%m-%dT%H:%M:%S')

        body = {
            'size': 1000,
            'query': {
                "bool": {
                    "must": [
                        {"range": {
                            "publication_date": {
                                "lt": upper,
                                "gte": lower
                            }
                        }},
                        {"term": {"classification.keyword": 'politics'}},
                    ],
                    "should": [
                        {"term": {"entities.text.keyword": user.party_preference}},
                        {"term": {"entities.parties.keyword": user.party_preference}}
                    ],
                }
            }
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def more_like_this_history(self, user, upper, lower):
        """
        used in the 'more like this' recommendation generator. Finds more articles based on the users reading history
        """
        reading_history = user.select_reading_history(lower, 'more_like_this')
        upper = upper.strftime('%Y-%m-%dT%H:%M:%S')
        lower = lower.strftime('%Y-%m-%dT%H:%M:%S')
        like_query = [{"_index": "articles", "_id": doc} for doc in reading_history]
        body = {
            'query': {
                "bool": {
                    "must": {
                        "range": {
                            "publication_date": {
                                "lt": upper,
                                "gte": lower
                            }
                        },
                    },
                    "should": [
                        {"term": {"classification.keyword": user.classification_preference}},
                        {"term": {"doctype.keyword": user.source_preference}},
                        # {"range": {
                        #     "complexity": {
                        #         "gte": user.complexity_preference+5,
                        #         "lte": user.complexity_preference-5,
                        #     }
                        # }},
                        {"more_like_this": {
                            "fields": ['text'],
                            "like": like_query
                        }}
                    ]
                }
            }
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def simulate_reading_history(self, d, classification, source, complexity, size):
        date = datetime.strptime(d, '%d-%m-%Y')
        full_date = date.strftime('%Y-%m-%dT%H:%M:%S')
        body = {
            "size": size,
            "query": {
                "bool": {
                    "must": {
                        "range": {
                            "publication_date": {
                                "lt": full_date,
                            }
                        },
                    },
                    "should": [
                        {"term": {"classification.keyword": classification}},
                        {"term": {"doctype.keyword": source}},
                        {"range": {
                            "complexity": {
                                "gte": complexity+5,
                                "lte": complexity-5,
                            }
                        }}
                    ]
                }
            }
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_first_and_last_dates(self):
        body_newest = {
            "size": 1,
            "sort": [
                {"publication_date": {"order": "desc"}}
            ],
            "query": {
                "match_all": {},
            }}
        response_newest = self.connector.execute_search('articles', body_newest)
        body_oldest = {
            "size": 1,
            "sort": [
                {"publication_date": {"order": "asc"}}
            ],
            "query": {
                "match_all": {},
            }}
        response_oldest = self.connector.execute_search('articles', body_oldest)
        return Article(response_oldest[0]).publication_date, Article(response_newest[0]).publication_date
