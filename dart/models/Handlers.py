import dart.handler.elastic.article_handler
import dart.handler.elastic.connector
import dart.handler.mongo.recommendation_handler
import dart.handler.mongo.story_handler
import dart.handler.mongo.entity_handler
import dart.handler.mongo.user_handler


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Handlers:

    def __init__(self, elastic_connector, mongo_connector):
        self.articles = dart.handler.elastic.article_handler.ArticleHandler(elastic_connector)
        self.users = dart.handler.mongo.user_handler.UserHandler(mongo_connector)
        self.recommendations = dart.handler.mongo.recommendation_handler.RecommendationHandler(mongo_connector)
        self.stories = dart.handler.mongo.story_handler.StoryHandler(mongo_connector)
        self.entities = dart.handler.mongo.entity_handler.EntityHandler(mongo_connector)
