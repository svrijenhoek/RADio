from random import random


class BaseHandler:

    def __init__(self, connector):
        self.connector = connector

    def get_by_docid(self, database, collection, docid):
        return self.connector.find_one(database, collection, 'id', docid)

    def get_random(self, database, collection):
        count = self.client.count(database, collection)
        number = random.randint(0, count)
        return self.connector.get_at_number(database, collection, number)

    def get_all_documents(self, database, collection):
        return self.connector.find(database, collection, {})

