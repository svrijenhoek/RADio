from elasticsearch import Elasticsearch


class InitializeIndex:

    def __init__(self):
        self.es = Elasticsearch()

    def index_exists(self, index):
        return self.es.indices.exists(index=index)

    def remove_and_initialize(self, index, mapping):
        if self.index_exists(index):
            self.es.indices.delete(index=index)
        self.es.indices.create(index=index, body=mapping)

    def initialize_stories(self):
        index_name = 'stories'
        mapping = {
            "mappings": {
                    "properties": {
                        "date": {
                            "type": "date"
                        },
                }
            }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_recommendations(self):
        index_name = 'recommendations'
        mapping = {
            "mappings": {
                    "properties": {
                        "recommendation.type": {
                            "type": "text",
                            "fielddata": True
                        },
                        "recommendation.date": {
                            "type": "date",
                            "format": "yyyy-MM-dd"
                        },
                }
            }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_articles(self):
        index_name = 'articles'
        mapping = {
            "mappings": {
                    "properties": {
                        "publication_date": {
                            "type": "date",
                            "format": "dateOptionalTime"
                        },
                        "entities.country_code": {
                            "type": "keyword"
                        },
                        "entities.location": {
                            "type": "geo_point"
                        },
                        "text": {
                            "type": "text",
                            "term_vector": "with_positions_offsets",
                        },
                        "popularity": {
                            "type": "integer"
                        }
                }
            }
        }
        self.remove_and_initialize(index_name, mapping)


    def initialize_aggregated(self):
        index_name = 'aggregated_recommendations'
        mapping = {
          "mappings": {
              "properties": {
                "date": {
                  "type": "date",
                  "format": "dd-MM-YYYY"
                },
                "avg_complexity": {
                  "type": "double"
                },
                "avg_popularity": {
                  "type": "double"
                },
                "avg_nwords": {
                  "type": "double"
                },
                "avg_nsentences": {
                  "type": "double"
                },
            }
          }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_locations(self):
        index_name = 'locations'
        mapping = {
            "mappings": {
                    "properties": {
                        "date": {
                            "type": "date"
                        },
                        "location": {
                            "type": "geo_point"
                        },
                        "country_code": {
                            "type": "keyword"
                        },
                    }
            }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_occupations(self):
        index_name = 'occupations'
        mapping = {
            "mappings": {
                    "properties": {
                        "date": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||dd-MM-YYYY"
                        },
                }
            }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_personalization(self):
        index_name = 'personalization'
        mapping = {
            "mappings": {
                    "properties": {
                        "recommendation.date": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||dd-MM-YYYY"
                        },
                        "article.date": {
                            "type": "date"
                        },
                        "article.text": {
                            "type": "text",
                            "term_vector": "with_positions_offsets",
                            "analyzer": "dutch"
                        },
                        "article.title": {
                            "type": "text",
                            "term_vector": "with_positions_offsets",
                            "analyzer": "dutch"
                        },
                        "article.style.complexity": {
                            "type": "integer"
                        },
                        "article.style.nsentences": {
                            "type": "integer"
                        },
                        "article.style.nwords": {
                            "type": "integer"
                        },
                }
            }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_recommended_articles(self):
        index_name = 'recommended_articles'
        mapping = {
            "mappings": {
                    "properties": {
                        "recommendation.date": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||dd-MM-YYYY"
                        },
                        "article.date": {
                            "type": "date"
                        },
                        "article.text": {
                            "type": "text",
                            "term_vector": "with_positions_offsets",
                            "analyzer": "dutch"
                        },
                        "article.title": {
                            "type": "text",
                            "term_vector": "with_positions_offsets",
                            "analyzer": "dutch"
                        },
                        "article.style.complexity": {
                            "type": "integer"
                        },
                        "article.style.nsentences": {
                            "type": "integer"
                        },
                        "article.style.nwords": {
                            "type": "integer"
                        },
                }
            }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_users(self):
        index_name = 'users'
        mapping = {
            "mappings": {
                "properties": {
                  "reading_history": {
                    "type": "nested"
                  }
                }
  }
        }
        self.remove_and_initialize(index_name, mapping)

    def initialize_all(self):
        self.initialize_articles()
        self.initialize_aggregated()
        self.initialize_locations()
        self.initialize_occupations()
        self.initialize_personalization()
        self.initialize_recommended_articles()

