from dart.models.Document import Document


class Recommendation(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.date = document['date']
        self.user = document['userid']
        self.type = document['type']
        self.impr_index = document['impr_index']
        self.articles = document['articles']
