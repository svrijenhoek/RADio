import logging
import datetime
from elasticsearch import Elasticsearch
import time

import dart.Util
import dart.populate.add_documents
import dart.populate.add_popularity
import dart.populate.simulate_users
import dart.populate.generate_recommendations
import dart.visualize.start_calculations
import dart.models.Handlers
import dart.populate.enrich_articles
import dart.populate.identify_stories
import dart.handler.elastic.initialize
import dart.handler.mongo.connector


def main():

    logging.basicConfig(filename='dart.log', level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
    module_logger = logging.getLogger('main')
    elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
    mongo_connector = dart.handler.mongo.connector.MongoConnector()
    handlers = dart.models.Handlers.Handlers(elastic_connector, mongo_connector)

    # step 0: load config file
    config = dart.Util.read_full_config_file()
    es = Elasticsearch()

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
    # dart.populate.add_documents.AddDocuments(config).execute_tsv('data/news.tsv')
    # # add popularity numbers from file
    # print(str(datetime.datetime.now()) + "\tadding popularity")
    # dart.populate.add_popularity.PopularityQueue().read_from_file(config['popularity_file'])
    #
    # step 1.5: annotate all articles
    # print(str(datetime.datetime.now())+"\tenriching articles")
    # dart.populate.enrich_articles.Enricher(handlers, config).enrich()
    #
    # # step 1.7: identify stories in the range specified in the configuration
    # print(str(datetime.datetime.now())+"\tidentifying stories")
    # if dart.handler.mongo.connector.MongoConnector().collection_database_exists('support', 'stories'):
    #     dart.handler.mongo.connector.MongoConnector().drop_collection('support', 'stories')
    # dart.populate.identify_stories.StoryIdentifier(handlers, config).execute()
    #
    # step 2: simulate users
    # print(str(datetime.datetime.now())+"\tloading users")
    # if dart.handler.mongo.connector.MongoConnector().database_database_exists('users') and config["append"] == "N":
    #     dart.handler.mongo.connector.MongoConnector().drop_database('users')
    # # module_logger.info("Simulating user data")
    # # dart.populate.simulate_users.UserSimulator(config, handlers).execute()
    # dart.populate.simulate_users.UserSimulator(config, handlers).execute_tsv("data/recommendations/behaviors.tsv")
    # time.sleep(5)
    # #
    # step 3: simulate recommendations
    # print(str(datetime.datetime.now())+"\tloading recommendations")
    # if dart.handler.mongo.connector.MongoConnector().database_exists('recommendations') and config["append"] == "N":
    #     dart.handler.mongo.connector.MongoConnector().drop_database('recommendations')
    # module_logger.info("Generating baseline recommendations")
    # # dart.populate.generate_recommendations.RunRecommendations(config, handlers).execute()
    # dart.populate.generate_recommendations.RunRecommendations(config, handlers).execute_tsv()
    # time.sleep(5)

    # step 5: make visualizations
    print(str(datetime.datetime.now()) + "\tZDF calculations")
    # dart.visualize.ZDF_calculations.ZDFCalculator(handlers, config).execute()
    print(str(datetime.datetime.now()) + "\tMetrics")
    dart.visualize.start_calculations.MetricsCalculator(handlers, config).execute()


if __name__ == "__main__":
    main()
