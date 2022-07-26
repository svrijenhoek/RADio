from dart.handler.mongo.base_handler import BaseHandler


class EntityHandler(BaseHandler):

    def __init__(self, connector):
        self.client = connector
        super(EntityHandler, self).__init__(connector)

    def find_one(self, collection, field, value):
        return self.connector.find_one('entities', collection, field, value)

    def find_entity(self, entity_type, label):
        return self.find_one(entity_type, 'key', label)

    def insert_one(self, entity_type, data):
        self.connector.insert_one('entities', entity_type, data)

    def delete(self, entity_type, data):
        self.connector.delete('entities', entity_type, data)

    def delete_with_label(self, entity_type, label):
        self.connector.delete('entities', entity_type, {'key': label})

    def find_alternative_name(self, entity_type, name):
        return self.find_one(entity_type, 'alternative', name)

    def update_entity(self, entity_type, entry):
        # to do
        return
