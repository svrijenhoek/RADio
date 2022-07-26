from pymongo import MongoClient, errors


class MongoConnector:

    def __init__(self):
        self.mongo = MongoClient()
        self.client = self.mongo.client.client

    def find_one(self, database, collection, field, value):
        return self.client[database][collection].find_one({field: value})

    def find(self, database, collection, query):
        return self.client[database][collection].find(query)

    def insert_one(self, database, collection, data):
        try:
            return self.client[database][collection].insert_one(data)
        except errors.DuplicateKeyError:
            return -1

    def insert_many(self, database, collection, documents):
        try:
            self.client[database][collection].insert(documents)
        except errors.DuplicateKeyError:
            print("Error!")
            print(documents)

    def delete(self, database, collection, data):
        self.client[database][collection].remove(data)

    def count(self, database, collection):
        return self.client[database][collection].count()

    def get_at_number(self, database, collection, number):
        return self.client[database][collection].find().limit(-1).skip(number).next()

    def drop_collection(self, database, collection):
        self.client[database][collection].drop()

    def drop_database(self, database):
        self.client.drop_database(database)

    def collection_exists(self, database, collection):
        return collection in self.client[database].list_collection_names()

    def database_exists(self, database):
        return database in self.client.list_database_names()

    def collection_names(self, database):
        return self.client[database].collection_names()

    def update_one(self, database, collection, query, document):
        self.client[database][collection].update_one(query, document)
