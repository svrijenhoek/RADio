import logging
import datetime
from elasticsearch import Elasticsearch
import time
import threading
import pandas as pd

import dart.Util
import dart.preprocess.downloads
import dart.preprocess.add_articles
import dart.metrics.start_calculations
import dart.models.Handlers
import dart.preprocess.enrich_articles
import dart.preprocess.identify_stories
import dart.handler.elastic.initialize
import dart.handler.mongo.connector

def main():    
    
    # logging.basicConfig(filename='dart.log', level=logging.INFO,
    #                     format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
    # module_logger = logging.getLogger('main')
    # elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
    # mongo_connector = dart.handler.mongo.connector.MongoConnector()
    # handlers = dart.models.Handlers.Handlers(elastic_connector, mongo_connector)

    # es = Elasticsearch()

    # thread_retrieve_articles = threading.Thread(
    #     target=dart.preprocess.add_articles.AddArticles(config, handlers).execute,
    #     args=("data/news.tsv",))
    # thread_enrich_articles = threading.Thread(
    #     target=dart.preprocess.enrich_articles.Enricher(handlers, config).enrich,
    #     args=())
    # thread_cluster_stories = threading.Thread(
    #    target=dart.preprocess.identify_stories.StoryIdentifier(handlers, config).execute,
    #    args=())
    # thread_add_users = threading.Thread(
    #     target=dart.preprocess.generate_users.UserSimulator(config, handlers).execute,
    #     args=("data/recommendations/behaviors.tsv",))

    # news = pd.read_csv("data/news.tsv", sep = "\t", header = None)
    # news.iloc[0, :].to_dict()
    
    ## step 0: load config file
    
    config = dart.Util.read_full_config_file()

    # downloads
    dart.preprocess.downloads.execute(config)

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
