from dart.handler.mongo.base_handler import BaseHandler
from dart.models.User import User


class UserHandler(BaseHandler):
    def __init__(self, connector):
        super(UserHandler, self).__init__(connector)
        self.all_users = None
        self.queue = []

    def add_user(self, doc):
        self.connector.insert_one('users', 'users', doc)

    def add_bulk(self, docs):
        self.connector.insert_many('users', 'users', docs)

    def get_all_users(self):
        if self.all_users is None:
            self.all_users = [User(i) for i in super(UserHandler, self).get_all_documents('users', 'users')]
        return self.all_users

    def get_by_id(self, user_id):
        response = self.connector.find('users', 'users', {"userid": user_id})
        return [User(i) for i in response][0]
        # return User(super(UserHandler, self).get_by_docid('users', 'users', user_id))

    def update_reading_history(self, user):
        self.connector.update_one('users', 'users', {"id": user.id},
                                  {"$set": {"reading_history": user.reading_history}})
