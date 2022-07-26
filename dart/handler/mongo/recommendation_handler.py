from dart.models.Recommendation import Recommendation
from dart.handler.mongo.base_handler import BaseHandler
from datetime import datetime, timedelta


class RecommendationHandler(BaseHandler):

    def __init__(self, connector):
        super(RecommendationHandler, self).__init__(connector)
        self.connector = connector
        self.all_recommendations = None
        self.queue = {}

    def add_recommendation(self, doc, recommendation_type):
        self.connector.insert_one('recommendations', recommendation_type, doc)

    def add_bulk(self):
        # to implement
        for recommendation_type in self.queue:
            self.connector.insert_many('recommendations', recommendation_type, self.queue[recommendation_type])
        self.queue = {}

    def get_all_recommendations(self, recommendation_type):
        if self.all_recommendations is None:
            recommendations = super(RecommendationHandler, self).find('recommendations', recommendation_type, {})
            self.all_recommendations = [Recommendation(i) for i in recommendations]
        return self.all_recommendations

    @staticmethod
    def create_json_doc(user_id, date, recommendation_type, articles):
        date = datetime.strptime(date, "%Y-%m-%d")
        doc = {
            "recommendation": {
                "user_id": user_id,
                "date": date,
                "type": recommendation_type
            },
            "articles": articles
        }
        return doc

    def add_to_queue(self, date, user_id, rec_type, article):
        doc = self.create_json_doc(user_id, date, rec_type, article)
        if rec_type not in self.queue:
            self.queue[rec_type] = []
        self.queue[rec_type].append(doc)

    def get_users_with_recommendations_at_date(self, date, recommendation_type):
        user_ids = []
        date = datetime.strptime(date, "%Y-%m-%d")
        query = {"date": date}

        cursor = self.connector.find('recommendations', recommendation_type, query)
        for entry in cursor:
            user_ids.append(entry['recommendation']['user_id'])
        return user_ids

    def find_recommendations_with_article_and_type(self, recommendation_type, article_id):
        query = {
            "articles": article_id
        }
        response = self.connector.find('recommendations', recommendation_type, query)
        return [Recommendation(i) for i in response]

    def get_recommendation_types(self):
        return self.connector.collection_names('recommendations')

    def get_recommendations_to_user(self, user_id, recommendation_type):
        query = {"userid": user_id}
        cursor = self.connector.find('recommendations', recommendation_type, query)
        return [Recommendation(i) for i in cursor]

    def get_recommendations_to_user_at_date(self, user_id, date, recommendation_type):
        date = datetime.strptime(date, "%Y-%m-%d")
        date_upper = date + timedelta(days=1)
        query = {"userid": user_id, "date": {"$gte": date, "$lt": date_upper}}
        cursor = self.connector.find('recommendations', recommendation_type, query)
        return [Recommendation(i) for i in cursor]

    def get_recommendations_at_date(self, date, recommendation_type):
        date = datetime.strptime(date, "%Y-%m-%d")
        date_upper = date + timedelta(days=1)
        query = {"date": {"$gte": date, "$lt": date_upper}}
        cursor = self.connector.find('recommendations', recommendation_type, query)
        return [Recommendation(i) for i in cursor]

    def get_recommendation_with_index_and_type(self, impr_index, recommendation_type):
        query = {"impr_index": impr_index}
        cursor = self.connector.find('recommendations', recommendation_type, query)
        return [Recommendation(i) for i in cursor][0]

