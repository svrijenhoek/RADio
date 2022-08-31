import logging
import datetime
from elasticsearch import Elasticsearch
import time
import threading
import pandas as pd

import dart.Util
import dart.preprocess.downloads
import dart.preprocess.add_articles
import dart.preprocess.nlp
import dart.metrics.start_calculations
import dart.models.Handlers
import dart.preprocess.enrich_articles
import dart.preprocess.identify_stories
import dart.handler.elastic.initialize
import dart.handler.mongo.connector
import dart.handler.articles
from dart.models.Article import Article


def main():
    
    ## step 0: load config file
    
    config = dart.Util.read_full_config_file()

    # downloads external data sources
    dart.preprocess.downloads.execute(config)

    # preprocess data
    df = dart.preprocess.nlp.execute()

    # enrich articles
    dart.preprocess.enrich_articles.Enricher(config).enrich(df)

    # identify stories

    # step 1: load articles
    # print(str(datetime.datetime.now())+"\tloading articles")
    # if es.indices.exists(index="articles") and config["append"] == "N":
    #     # delete index
    #     elastic_connector.clear_index('articles')
    #     module_logger.info("Index removed")
    # if not es.indices.exists(index="articles"):
    #     module_logger.info("Index created")
    #     dart.handler.elastic.initialize.InitializeIndex().initialize_articles()
    #     module_logger.info("Started adding documents")
    
    # thread_retrieve_articles.start()
    # time.sleep(60)
    # print(str(datetime.datetime.now()) + "\tenriching articles")
    # thread_enrich_articles.start()
    # # thread_retrieve_articles.join()
    # thread_enrich_articles.join()

    # step 1.7: identify stories in the range specified in the configuration
    # print(str(datetime.datetime.now())+"\tidentifying stories")
    # if dart.handler.mongo.connector.MongoConnector().collection_exists('support', 'stories'):
    #     dart.handler.mongo.connector.MongoConnector().drop_collection('support', 'stories')
    # thread_cluster_stories.start()


if __name__ == "__main__":
    main()
