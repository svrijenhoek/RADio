from dart.models.Document import Document


class Story(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.date = self.source['date']
        self.classification = self.source['classification']
        self.keywords = self.source['keywords']
        self.docids = self.source['docids']
        self.title = self.source['title']
        self.identifier = self.source['identifier']
